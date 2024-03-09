#!/usr/bin/env python3

"""Defines class methods to consolidate and calculate Team In Match (TIM) data."""

import copy
import statistics
import utils
from calculations.base_calculations import BaseCalculations
from typing import List, Union, Dict
import logging
from data_transfer import tba_communicator
import time

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


class ObjTIMCalcs(BaseCalculations):
    schema = utils.read_schema("schema/calc_obj_tim_schema.yml")
    type_check_dict = {"float": float, "int": int, "str": str, "bool": bool}

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["unconsolidated_totals"]

    def consolidate_nums(self, nums: List[Union[int, float]], decimal=False) -> int:
        """Given numbers reported by multiple scouts, estimates actual number
        nums is a list of numbers, representing action counts or times, reported by each scout
        Currently tries to consolidate using only the reports from scouts on one robot,
        but future improvements might change the algorithm to account for other alliance members,
        since TBA can give us the total action counts for the alliance
        """
        mean = self.avg(nums)
        if len(nums) == 0 or mean in nums:
            # Avoid getting a divide by zero error when calculating standard deviation
            if decimal:
                return round(mean, 2)
            else:
                return round(mean)
        # If two or more scouts agree, automatically go with what they say
        if len(nums) > len(set(nums)):
            # Still need to consolidate, in case there are multiple modes
            return self.consolidate_nums(self.modes(nums), decimal)
        # Population standard deviation:
        std_dev = statistics.pstdev(nums)
        # Calculate weighted average, where the weight for each num is its reciprocal square z-score
        # That way, we account less for data farther from the mean
        z_scores = [(num - mean) / std_dev for num in nums]
        weights = [1 / z**2 for z in z_scores]
        float_nums = self.avg(nums, weights)
        if decimal:
            return round(float_nums, 2)
        return round(float_nums)

    def consolidate_bools(self, bools: list) -> bool:
        """Given a list of booleans reported by multiple scouts, returns the actual value"""
        bools = self.modes(bools)
        if len(bools) == 1:
            # Go with the majority
            return bools[0]
        # Scouts are evenly split, so just go with False
        return False

    def consolidate_categorical_actions(self, unconsolidated_tims: List[Dict]):
        """Given string type obj_tims, return actual string"""
        # Dictionary for final calculated tims
        final_categorical_actions = {}
        for category in self.schema["categorical_actions"]:
            scout_categorical_actions = [scout[category] for scout in unconsolidated_tims]
            # Enums for associated category actions and shortened representation
            actions = self.schema["categorical_actions"][category]["list"]
            # Turn the shortened categorical actions from the scout into full strings
            categorical_actions = []
            for action in scout_categorical_actions:
                for value in actions:
                    if value == action:
                        categorical_actions.append(value)
                        break
            # If at least 2 scouts agree, take their answer
            if len(self.modes(categorical_actions)) == 1:
                final_categorical_actions[category] = self.modes(categorical_actions)[0]
                continue

            # Add up the indexes of the scout responses
            category_avg = self.avg([list(actions).index(value) for value in categorical_actions])
            # Round the average and append the correct action to the final dict
            final_categorical_actions[category] = list(actions)[round(category_avg)]
        return final_categorical_actions

    def consolidate_unconsolidated_numbers(self, unconsolidated_totals: List[Dict]):
        """Given a list of unconsolidated totals dictionaries, consolidate the non-categorical datapoints"""
        consolidated_totals = {}
        for datapoint in unconsolidated_totals[0].keys():
            unconsolidated_data = []
            if datapoint not in ["team_number", "match_number", "scout_name"]:
                # since non-int or float datapoints are all categorical actions, and there's already another function to consolidate those
                if isinstance(unconsolidated_totals[0][datapoint], (int, float)) and not isinstance(
                    unconsolidated_totals[0][datapoint], bool
                ):
                    for tim in unconsolidated_totals:
                        unconsolidated_data.append(tim[datapoint])
                    # consolidate data
                    consolidated_totals[datapoint] = self.consolidate_nums(unconsolidated_data)
        return consolidated_totals

    def calculate_point_values(self, calculated_tim: List[Dict]):
        """Given a list of consolidated tims, return consolidated point values"""
        final_points = {}
        # Get each point data point
        for point_datapoint_section, filters in self.schema["point_calculations"].items():
            total_points = 0
            note_count = 0
            point_aggregates = filters["counts"]
            point_counts = list(point_aggregates.keys())
            # Add up all the counts for each aggregate, multiplys them by their value, then adds them to the final dictionary
            for point in point_counts:
                count = calculated_tim[point] if point in calculated_tim else 0
                if isinstance(count, bool):
                    total_points += point_aggregates[point] if count else 0
                    note_count += 1 if count else 0
                elif isinstance(count, str):
                    total_points += point_aggregates[point] if count not in ["N", "F"] else 0
                    note_count += 1 if count != "N" else 0
                else:
                    total_points += count * point_aggregates[point]
                    note_count += count
            if point_datapoint_section == "points_per_note":
                total_points = total_points / note_count
            final_points[point_datapoint_section] = total_points
        return final_points

    def calculate_harmony(self, calculated_tims: List[Dict]):
        """Given a list of calculated TIMs, returns a list of team and match numbers of the teams that harmonized"""
        harmonized_teams = []
        for tim1 in calculated_tims:
            if calculated_tims == [{}]:
                break
            else:
                if "O" in [
                    tim1["stage_level_left"],
                    tim1["stage_level_right"],
                    tim1["stage_level_center"],
                ]:
                    for tim2 in calculated_tims:
                        if (
                            tim1["match_number"] == tim2["match_number"]
                            and tim1["alliance_color_is_red"] == tim2["alliance_color_is_red"]
                            and tim1["team_number"] != tim2["team_number"]
                        ):
                            if (
                                tim1["stage_level_left"] == tim2["stage_level_left"]
                                and tim1["stage_level_left"] != "N"
                            ):
                                harmonized_teams.append(
                                    {
                                        "team_number": tim1["team_number"],
                                        "match_number": tim1["match_number"],
                                    }
                                )
                                harmonized_teams.append(
                                    {
                                        "team_number": tim2["team_number"],
                                        "match_number": tim2["match_number"],
                                    }
                                )
                            elif (
                                tim1["stage_level_right"] == tim2["stage_level_right"]
                                and tim1["stage_level_right"] != "N"
                            ):
                                harmonized_teams.append(
                                    {
                                        "team_number": tim1["team_number"],
                                        "match_number": tim1["match_number"],
                                    }
                                )
                                harmonized_teams.append(
                                    {
                                        "team_number": tim2["team_number"],
                                        "match_number": tim2["match_number"],
                                    }
                                )
                            elif (
                                tim1["stage_level_center"] == tim2["stage_level_center"]
                                and tim1["stage_level_center"] != "N"
                            ):
                                harmonized_teams.append(
                                    {
                                        "team_number": tim1["team_number"],
                                        "match_number": tim1["match_number"],
                                    }
                                )
                                harmonized_teams.append(
                                    {
                                        "team_number": tim2["team_number"],
                                        "match_number": tim2["match_number"],
                                    }
                                )
            return harmonized_teams

    def calculate_tim(self, unconsolidated_tims: List[Dict]) -> dict:
        """Given a list of unconsolidated TIMs, returns a calculated TIM"""
        if len(unconsolidated_tims) == 0:
            log.warning("calculate_tim: zero TIMs given")
            return {}
        calculated_tim = {}
        calculated_tim.update(self.consolidate_categorical_actions(unconsolidated_tims))
        calculated_tim.update(self.consolidate_unconsolidated_numbers(unconsolidated_tims))
        calculated_tim.update(self.calculate_point_values(calculated_tim))
        # Use any of the unconsolidated TIMs to get the team and match number,
        # since that should be the same for each unconsolidated TIM
        calculated_tim["match_number"] = unconsolidated_tims[0]["match_number"]
        calculated_tim["team_number"] = unconsolidated_tims[0]["team_number"]
        calculated_tim["alliance_color_is_red"] = unconsolidated_tims[0]["alliance_color_is_red"]
        # confidence_rating is the number of scouts that scouted one robot
        calculated_tim["confidence_ranking"] = len(unconsolidated_tims)
        calculated_tim["climbed"] = "O" in [
            calculated_tim["stage_level_left"],
            calculated_tim["stage_level_center"],
            calculated_tim["stage_level_right"],
        ]
        return calculated_tim

    def update_calcs(self, tims: List[Dict[str, Union[str, int]]]) -> List[dict]:
        """Calculate data for each of the given TIMs. Those TIMs are represented as dictionaries:
        {'team_number': '1678', 'match_number': 69}"""
        calculated_tims = []
        for tim in tims:
            unconsolidated_obj_tims = self.server.db.find("unconsolidated_totals", tim)
            calculated_tim = self.calculate_tim(unconsolidated_obj_tims)
            calculated_tims.append(calculated_tim)
        harmonized_teams = self.calculate_harmony(calculated_tims)
        for tim in calculated_tims:
            if tim == {}:
                continue
            else:
                if {
                    "team_number": tim["team_number"],
                    "match_number": tim["match_number"],
                } in harmonized_teams:
                    tim["harmonized"] = True
                else:
                    tim["harmonized"] = False
        return calculated_tims

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
            self.server.db.delete_data("obj_tim")

        updates = self.update_calcs(unique_tims)
        if updates == None:
            pass
        else:
            for update in updates:
                if update != {}:
                    real_matches = [
                        match
                        for match in tba_match_data
                        if match["match_number"] == update["match_number"]
                    ]
                    real_teams = [
                        team[3:]
                        for real_match in real_matches
                        for team in (
                            real_match["alliances"]["red"]["team_keys"]
                            + real_match["alliances"]["blue"]["team_keys"]
                        )
                    ]
                    if update["team_number"] in real_teams:
                        self.server.db.update_document(
                            "obj_tim",
                            update,
                            {
                                "team_number": update["team_number"],
                                "match_number": update["match_number"],
                            },
                        )
                    else:
                        team_number = update["team_number"]
                        match_number = update["match_number"]
                        log.warning(f"{team_number} not found in match {match_number}")
            end_time = time.time()
            # Get total calc time
            total_time = end_time - start_time
            # Write total calc time to log
            log.info(f"obj_tims calculation time: {round(total_time, 2)} sec")
