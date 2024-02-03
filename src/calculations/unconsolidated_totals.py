# Copyright (c) 2024 FRC Team 1678: Citrus Circuits

import copy
import utils
from calculations.base_calculations import BaseCalculations
from typing import List, Union, Dict
import logging
from data_transfer import tba_communicator

log = logging.getLogger(__name__)


class UnconsolidatedTotals(BaseCalculations):
    schema = utils.read_schema("schema/calc_obj_tim_schema.yml")
    type_check_dict = {"float": float, "int": int, "str": str, "bool": bool}

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["unconsolidated_obj_tim"]

    def filter_timeline_actions(self, tim: dict, **filters) -> list:
        """Removes timeline actions that don't meet the filters and returns all the actions that do"""
        actions = tim["timeline"]
        for field, required_value in filters.items():
            if field == "time":
                # Times are given as closed intervals: either [0,134] or [135,150]
                actions = filter(
                    lambda action: required_value[0] <= action["time"] <= required_value[1],
                    actions,
                )
            else:
                # Removes actions for which action[field] != required_value
                actions = filter(lambda action: action[field] == required_value, actions)
            # filter returns an iterable object
            actions = list(actions)
        return actions

    def count_timeline_actions(self, tim: dict, **filters) -> int:
        """Returns the number of actions in one TIM timeline that meets the required filters"""
        return len(self.filter_timeline_actions(tim, **filters))

    def calculate_unconsolidated_tims(self, unconsolidated_tims: List[Dict]):
        """Given a list of unconsolidated TIMS, returns the unconsolidated calculated TIMs"""
        if len(unconsolidated_tims) == 0:
            log.warning("calculate_tim: zero TIMs given")
            return {}

        for num_1, tim in enumerate(unconsolidated_tims):
            timeline = tim["timeline"]
            # Collects the data for score_fails for amp, and speaker.
            for num, action_dict in enumerate(timeline):
                if action_dict["action_type"] == "score_fail":
                    for score_type, new_value in self.schema["fail_actions"].items():
                        if (
                            unconsolidated_tims[num_1]["timeline"][num + 1]["action_type"]
                            == score_type
                        ):
                            unconsolidated_tims[num_1]["timeline"][num + 1][
                                "action_type"
                            ] = new_value

        unconsolidated_totals = []
        # Calculates unconsolidated tim counts
        for tim in unconsolidated_tims:
            tim_totals = {}
            tim_totals["scout_name"] = tim["scout_name"]
            tim_totals["match_number"] = tim["match_number"]
            tim_totals["team_number"] = tim["team_number"]
            tim_totals["alliance_color_is_red"] = tim["alliance_color_is_red"]
            # Calculate unconsolidated tim counts
            for aggregate, filters in self.schema["aggregates"].items():
                total_count = 0
                aggregate_counts = filters["counts"]
                for calculation, filters in self.schema["timeline_counts"].items():
                    filters_ = copy.deepcopy(filters)
                    expected_type = filters_.pop("type")
                    new_count = self.count_timeline_actions(tim, **filters_)
                    if not isinstance(new_count, self.type_check_dict[expected_type]):
                        raise TypeError(f"Expected {new_count} calculation to be a {expected_type}")
                    tim_totals[calculation] = new_count
                    # Calculate unconsolidated aggregates
                    for count in aggregate_counts:
                        if calculation == count:
                            total_count += new_count
                    tim_totals[aggregate] = total_count
            # Calculate unconsolidated categorical actions
            for category in self.schema["categorical_actions"]:
                tim_totals[category] = tim[category]
            unconsolidated_totals.append(tim_totals)
        return unconsolidated_totals

    def update_calcs(self, tims: List[Dict[str, Union[str, int]]]) -> List[dict]:
        """Calculate data for each of the given TIMs. Those TIMs are represented as dictionaries:
        {'team_number': '1678', 'match_number': 69}"""
        unconsolidated_totals = []
        for tim in tims:
            unconsolidated_obj_tims = self.server.db.find("unconsolidated_obj_tim", tim)
            # check for overrides
            override = {}
            for t in unconsolidated_obj_tims:
                if "override" in t:
                    override.update(t.pop("override"))
            calculated_unconsolidated_tim = self.calculate_unconsolidated_tims(
                unconsolidated_obj_tims
            )
            # implement overrides
            if override != {}:
                for edited_datapoint in override:
                    if edited_datapoint in calculated_unconsolidated_tim[0]:
                        calculated_unconsolidated_tim[0][edited_datapoint] = override[
                            edited_datapoint
                        ]
            unconsolidated_totals.extend(calculated_unconsolidated_tim)
        return unconsolidated_totals

    def get_grid_status(self, matches):
        grid_status = {}
        for match in matches:
            alliance_status = {}
            if match["score_breakdown"] is not None and match["comp_level"] == "qm":
                for alliance in ["red", "blue"]:
                    alliance_status[alliance] = True
                    for row in match["score_breakdown"][alliance]["teleopCommunity"].values():
                        if "None" in row:
                            alliance_status[alliance] = False

                    grid_status[match["match_number"]] = alliance_status

        return grid_status

    def run(self):
        """Executes the OBJ TIM calculations"""

        tba_match_data: List[dict] = tba_communicator.tba_request(
            f"event/{utils.TBA_EVENT_KEY}/matches"
        )

        self.grid_status = self.get_grid_status(tba_match_data)

        # Get oplog entries
        tims = []
        # Check if changes need to be made to teams
        if (entries := self.entries_since_last()) != []:
            for entry in entries:
                team_num = entry["o"]["team_number"]
                if team_num not in self.teams_list:
                    log.warning(f"obj_tims: team number {team_num} is not in teams list")
                    continue
                tims.append(
                    {
                        "team_number": team_num,
                        "match_number": entry["o"]["match_number"],
                    }
                )
        unique_tims = []
        for tim in tims:
            if tim not in unique_tims:
                unique_tims.append(tim)
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("unconsolidated_totals")

        updates = self.update_calcs(unique_tims)
        if len(updates) > 1:
            for document in updates:
                self.server.db.update_document(
                    "unconsolidated_totals",
                    document,
                    {
                        "team_number": document["team_number"],
                        "match_number": document["match_number"],
                        "scout_name": document["scout_name"],
                    },
                )
