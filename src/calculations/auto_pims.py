#!/usr/bin/env python3
# Copyright (c) 2024 FRC Team 1678: Citrus Circuits
"""Holds functions used to determine auto scoring and paths in each match"""

from typing import List, Dict, Union, Any, Tuple
from calculations.base_calculations import BaseCalculations
import logging
import statistics
import utils
import time

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


class AutoPIMCalc(BaseCalculations):
    schema = utils.read_schema("schema/calc_auto_pim.yml")

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["unconsolidated_obj_tim", "sim_precision"]

    def get_unconsolidated_auto_timelines(
        self, unconsolidated_obj_tims: List[Dict[str, List[dict]]]
    ) -> Tuple[List[List[dict]], Union[int, None]]:
        """Given unconsolidated_obj_tims, returns unconsolidated auto timelines
        and the index of the best scout's timeline"""

        unconsolidated_auto_timelines = []
        best_sim_precision, best_scout_index = None, 0
        # Extract auto timelines
        for i, unconsolidated_tim in enumerate(unconsolidated_obj_tims):
            sim = {
                key: unconsolidated_tim[key]
                for key in ["team_number", "match_number", "scout_name"]
            }
            unconsolidated_auto_timelines.append(
                [
                    action
                    for action in unconsolidated_tim["timeline"]
                    if action["in_teleop"] == False
                ]
            )
            sim_precision: List[Dict[str, float]] = self.server.db.find("sim_precision", sim)
            if len(sim_precision) == 0:
                continue
            elif "sim_precision" not in sim_precision[0]:
                continue
            else:
                if len(sim_precision) > 1:
                    log.error(
                        f"auto_pim: multiple sim_precisions found for {sim}, taking first option"
                    )
                precision = abs(sim_precision[0]["sim_precision"])
                if best_sim_precision is None or precision < best_sim_precision:
                    best_sim_precision = precision
                    best_scout_index = i
        return unconsolidated_auto_timelines, best_scout_index

    def consolidate_timelines(
        self, unconsolidated_timelines: List[List[dict]], best_scout_index: int
    ) -> List[dict]:
        """Given a list of unconsolidated auto timelines and the index of the best scout's timeline
        (output from the get_unconsolidated_auto_timelines function), consolidates the timelines into a single timeline.

        If two timelines are the same, use that timeline.
        Else, choose timeline from scout with highest SPR.
        """

        ut = unconsolidated_timelines  # alias
        consolidated_timeline = []
        lengths = list(map(len, ut))

        # Check for identical timelines
        if len(mode := BaseCalculations.modes(lengths)) == 1:
            consolidated_timeline = ut[lengths.index(mode[0])]
        # Else use timeline from best scout
        else:
            consolidated_timeline = ut[best_scout_index]

        return consolidated_timeline

    def get_consolidated_tim_fields(self, calculated_tim: dict) -> dict:
        "Given a calculated_tim, return tim fields directly from other collections"
        # Auto variables we collect
        tim_fields = self.schema["tim_fields"]

        tim_auto_values = {}
        for field in tim_fields:
            collection, datapoint = field.split(".")
            if collection == "obj_tim":
                tim_auto_values[datapoint] = calculated_tim[datapoint]
            else:
                # Get data from other collections, such as subj_team or tba_tim
                data: List[dict] = self.server.db.find(
                    collection,
                    {
                        "match_number": calculated_tim["match_number"],
                        "team_number": calculated_tim["team_number"],
                    },
                )
                if data == []:
                    # Handle no data
                    tim_auto_values[datapoint] = None
                    log.critical(
                        f"auto pim: data not found for {field, calculated_tim['match_number'], calculated_tim['team_number']}"
                    )
                else:
                    tim_auto_values[datapoint] = data[0][datapoint]

        return tim_auto_values

    def create_auto_fields(self, tim: dict) -> dict:
        """Creates auto fields for one tim such as score_1, intake_1, etc using the consolidated_timeline"""
        # counters to cycle through scores and intakes
        counts = {field: 0 for field in self.schema["--timeline_fields"]}
        # set all fields to None (in order to not break exports)
        update = {}
        for field, info in self.schema["--timeline_fields"].items():
            for i in range(info["max_count"]):
                update[f"{field}_{i + 1}"] = "none"

        # For each action in the consolidated timeline, add it to one of the new fields (if it applies)
        for action in tim["auto_timeline"]:
            # BUG: action_type sometimes doesn't exist for a timeline action
            if action.get("action_type") is None:
                log.warning("auto_pim: action_type does not exist")
                continue
            # BUG: action_type can sometimes be null, need better tests in auto_pim, more edge cases
            elif action["action_type"] is None:
                log.warning("auto_pim: action_type is null")
                continue
            # Iterate through each timeline_field
            for field, info in self.schema["--timeline_fields"].items():
                # Check if the action is one of the valid actions for this field
                if action["action_type"] in info["valid_actions"].keys():
                    # Iterate to the next datapoint for that field
                    counts[field] += 1
                    # Calculate the value for the field
                    update[f"{field}_{counts[field]}"] = self.calculate_action(
                        action["action_type"], info["valid_actions"]
                    )
        return update

    def calculate_action(self, action: str, action_dict):
        "Given an action type (e.g. score_speaker), return the short-form name used in auto_pims (e.g. speaker)"
        # Iterate through possible action types
        # Return the short-form name if the full name matches
        for full_name, new_name in action_dict.items():
            if action == full_name:
                return new_name

        # Log if action type is invalid
        log.fatal(f"auto_pims: {action} is not a valid action type")
        return "none"

    def calculate_auto_pims(self, tims: List[dict]) -> List[dict]:
        """Calculates auto data for the given tims, which looks like
        [{"team_number": 1678, "match_number": 42}, {"team_number": 1706, "match_number": 56}, ...]"""
        calculated_pims = []
        for tim in tims:
            # Get data for the tim from MongoDB
            unconsolidated_obj_tims: List[dict] = self.server.db.find("unconsolidated_obj_tim", tim)
            obj_tim: dict = self.server.db.find("obj_tim", tim)[0]

            # Run calculations on the team in match
            tim.update(self.get_consolidated_tim_fields(obj_tim))
            tim.update(
                {
                    "auto_timeline": self.consolidate_timelines(
                        *self.get_unconsolidated_auto_timelines(unconsolidated_obj_tims)
                    )
                }
            )
            tim.update(self.create_auto_fields(tim))
            # Data that is later updated by auto_paths
            tim.update({"match_numbers_played": [], "num_matches_ran": 0, "path_number": 0})

            calculated_pims.append(tim)
        return calculated_pims

    def run(self):
        """Executes the auto_pim calculations"""
        # Get calc start time
        start_time = time.time()
        # Get oplog entries
        tims = []

        # Check if changes need to be made to teams
        if (entries := self.entries_since_last()) != []:
            for entry in entries:
                # Check that the entry is an unconsolidated_obj_tim
                if "timeline" not in entry["o"].keys() or "team_number" not in entry["o"].keys():
                    continue

                # Check that the team is in the team list, ignore team if not in teams list
                team_num = entry["o"]["team_number"]
                if team_num not in self.teams_list:
                    log.warning(f"auto_pim: team number {team_num} is not in teams list")
                    continue

                # Make tims list
                tims.append(
                    {
                        "team_number": team_num,
                        "match_number": entry["o"]["match_number"],
                    }
                )

        # Filter duplicate tims
        unique_tims = []
        for tim in tims:
            if tim not in unique_tims:
                unique_tims.append(tim)
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("auto_pim")

        # Calculate data
        updates = self.calculate_auto_pims(unique_tims)

        # Upload data to MongoDB
        for update in updates:
            if update != {}:
                self.server.db.update_document(
                    "auto_pim",
                    update,
                    {
                        "team_number": update["team_number"],
                        "match_number": update["match_number"],
                    },
                )
        end_time = time.time()
        # Get total calc time
        total_time = end_time - start_time
        # Write total calc time to log
        log.info(f"auto_paths calculation time: {total_time}")
