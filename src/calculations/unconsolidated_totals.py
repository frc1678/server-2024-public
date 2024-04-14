# Copyright (c) 2024 FRC Team 1678: Citrus Circuits

import copy
import utils
from calculations.base_calculations import BaseCalculations
from typing import List, Union, Dict
import logging
from data_transfer import tba_communicator
import time

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


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

    def score_fail_type(self, unconsolidated_tims: List[Dict]):
        for num_1, tim in enumerate(unconsolidated_tims):
            timeline = tim["timeline"]
            # Collects the data for score_fails for amp, and speaker.
            for num, action_dict in enumerate(timeline):
                if action_dict["action_type"] == "fail":
                    for score_type, new_value in self.schema["fail_actions"].items():
                        if (
                            unconsolidated_tims[num_1]["timeline"][num + 1]["action_type"]
                            == score_type
                        ):
                            unconsolidated_tims[num_1]["timeline"][num + 1][
                                "action_type"
                            ] = new_value["name"]
        return unconsolidated_tims

    def calculate_unconsolidated_tims(self, unconsolidated_tims: List[Dict]):
        """Given a list of unconsolidated TIMS, returns the unconsolidated calculated TIMs"""
        if len(unconsolidated_tims) == 0:
            log.warning("calculate_tim: zero TIMs given")
            return {}
        unconsolidated_tims = self.score_fail_type(unconsolidated_tims)
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
            # New section for obj_tim, unconsolidated_totals needs to iterate through these datapoints as well
            for aggregate, filters in self.schema["pre_consolidated_aggregates"].items():
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
                        # if override begins with += or -=, add or subtract respectively instead of just setting
                        if isinstance(override[edited_datapoint], str):
                            if override[edited_datapoint][0:2] == "+=":
                                # removing "+=" and setting override[edited_datapoint] to the right type
                                override[edited_datapoint] = override[edited_datapoint][2:]
                                if override[edited_datapoint].isdecimal():
                                    override[edited_datapoint] = int(override[edited_datapoint])
                                elif (
                                    "." in override[edited_datapoint]
                                    and override[edited_datapoint].replace(".", "0", 1).isdecimal()
                                ):
                                    override[edited_datapoint] = float(override[edited_datapoint])
                                # "adding" to the original value
                                override[edited_datapoint] += calculated_unconsolidated_tim[0][
                                    edited_datapoint
                                ]
                            elif override[edited_datapoint][0:2] == "-=":
                                # removing "-=" and setting override[edited_datapoint] to the right type
                                override[edited_datapoint] = override[edited_datapoint][2:]
                                if override[edited_datapoint].isdecimal():
                                    override[edited_datapoint] = int(override[edited_datapoint])
                                elif (
                                    "." in override[edited_datapoint]
                                    and override[edited_datapoint].replace(".", "0", 1).isdecimal()
                                ):
                                    override[edited_datapoint] = float(override[edited_datapoint])
                                # "subtracting" from the original value
                                override[edited_datapoint] *= -1
                                override[edited_datapoint] += calculated_unconsolidated_tim[0][
                                    edited_datapoint
                                ]
                        # overriding old value
                        calculated_unconsolidated_tim[0][edited_datapoint] = override[
                            edited_datapoint
                        ]
            unconsolidated_totals.extend(calculated_unconsolidated_tim)
        return unconsolidated_totals

    def run(self):
        """Executes the OBJ TIM calculations"""
        # Get calc start time
        start_time = time.time()
        tba_match_data: List[dict] = tba_communicator.tba_request(
            f"event/{utils.TBA_EVENT_KEY}/matches"
        )

        # Get oplog entries
        tims = []
        # Check if changes need to be made to teams
        if entries := self.entries_since_last():
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
                real_matches = [
                    match
                    for match in tba_match_data
                    if match["match_number"] == document["match_number"]
                ]
                real_teams = [
                    team[3:]
                    for real_match in real_matches
                    for team in (
                        real_match["alliances"]["red"]["team_keys"]
                        + real_match["alliances"]["blue"]["team_keys"]
                    )
                ]
                if document["team_number"] in real_teams:
                    self.server.db.update_document(
                        "unconsolidated_totals",
                        document,
                        {
                            "team_number": document["team_number"],
                            "match_number": document["match_number"],
                            "scout_name": document["scout_name"],
                        },
                    )
                else:
                    team_number = document["team_number"]
                    match_number = document["match_number"]
                    log.warning(f"{team_number} not found in match {match_number}")
        end_time = time.time()
        # Get total calc time
        total_time = end_time - start_time
        # Write total calc time to log
        log.info(f"unconsolidated_totals calculation time: {round(total_time, 2)} sec")
