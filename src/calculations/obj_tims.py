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
        self.watched_collections = ["unconsolidated_obj_tim"]

    def consolidate_nums(self, nums: List[Union[int, float]]) -> int:
        """Given numbers reported by multiple scouts, estimates actual number
        nums is a list of numbers, representing action counts or times, reported by each scout
        Currently tries to consolidate using only the reports from scouts on one robot,
        but future improvements might change the algorithm to account for other alliance members,
        since TBA can give us the total action counts for the alliance
        """
        mean = self.avg(nums)
        if len(nums) == 0 or mean in nums:
            # Avoid getting a divide by zero error when calculating standard deviation
            return round(mean)
        # If two or more scouts agree, automatically go with what they say
        if len(nums) > len(set(nums)):
            # Still need to consolidate, in case there are multiple modes
            return self.consolidate_nums(self.modes(nums))
        # Population standard deviation:
        std_dev = statistics.pstdev(nums)
        # Calculate weighted average, where the weight for each num is its reciprocal square z-score
        # That way, we account less for data farther from the mean
        z_scores = [(num - mean) / std_dev for num in nums]
        weights = [1 / z**2 for z in z_scores]
        float_nums = self.avg(nums, weights)
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
            elif required_value == "score":
                # Removes actions for which required_value is not contained within action[field] (eg score and score_cone_high)
                actions = filter(lambda action: str(required_value) in str(action[field]), actions)
            else:
                # Removes actions for which action[field] != required_value
                actions = filter(lambda action: action[field] == required_value, actions)
            # filter returns an iterable object
            actions = list(actions)
        return actions

    def count_timeline_actions(self, tim: dict, **filters) -> int:
        """Returns the number of actions in one TIM timeline that meets the required filters"""
        return len(self.filter_timeline_actions(tim, **filters))

    def total_time_between_actions(
        self, tim: dict, start_action: str, end_action: str, min_time: int
    ) -> int:
        """Returns total number of seconds spent between two types of actions for a given TIM

        start_action and end_action are the names (types) of those two actions,
        such as start_incap and end_climb.
        min_time is the minimum number of seconds between the two types of actions that we want to count
        """
        # Separate calculation for scoring cycle times
        if start_action == "score":
            scoring_actions = self.filter_timeline_actions(tim, action_type=start_action)
            cycle_times = []

            # Calculates time difference between every pair of scoring actions
            for i in range(1, len(scoring_actions)):
                cycle_times.append(scoring_actions[i - 1]["time"] - scoring_actions[i]["time"])

            # Calculate median cycle time (if cycle times is not an empty list)
            if cycle_times:
                median_cycle_time = statistics.median(cycle_times)
            else:
                median_cycle_time = 0

            # Cycle time has to be an integer
            return round(median_cycle_time)

        # Other time calculations (incap)
        else:
            start_actions = self.filter_timeline_actions(tim, action_type=start_action)
            end_actions = []
            # Takes multiple end actions
            if isinstance(end_action, list):
                for action in end_action:
                    end_actions = end_actions + self.filter_timeline_actions(
                        tim, action_type=action
                    )
            else:
                end_actions = self.filter_timeline_actions(tim, action_type=end_action)
            # Match scout app should automatically add an end action at the end of the match,
            # if there isn't already an end action after the last start action. That way there are the
            # same number of start actions and end actions.
            total_time = 0
            for start, end in zip(start_actions, end_actions):
                if start["time"] - end["time"] >= min_time:
                    total_time += start["time"] - end["time"]
            return total_time

    def score_fail_type(self, unconsolidated_tims: List[Dict]):
        for num_1, tim in enumerate(unconsolidated_tims):
            timeline = tim["timeline"]
            # Collects the data for score_fails for amp, and speaker.
            for num, action_dict in enumerate(timeline):
                if action_dict["action_type"] == "score_fail":
                    if (
                        unconsolidated_tims[num_1]["timeline"][num + 1]["action_type"]
                        == "score_speaker"
                    ):
                        unconsolidated_tims[num_1]["timeline"][num + 1][
                            "action_type"
                        ] = "score_fail_speaker"
                    if (
                        unconsolidated_tims[num_1]["timeline"][num + 1]["action_type"]
                        == "score_amp"
                    ):
                        unconsolidated_tims[num_1]["timeline"][num + 1][
                            "action_type"
                        ] = "score_fail_amp"
                    if (
                        unconsolidated_tims[num_1]["timeline"][num + 1]["action_type"]
                        == "score_amplify"
                    ):
                        unconsolidated_tims[num_1]["timeline"][num + 1][
                            "action_type"
                        ] = "score_fail_amplify"
        return unconsolidated_tims

    def calculate_tim_counts(self, unconsolidated_tims: List[Dict]) -> dict:
        """Given a list of unconsolidated TIMs, returns the calculated count based data fields"""
        calculated_tim = {}
        self.score_fail_type(unconsolidated_tims)
        for calculation, filters in self.schema["timeline_counts"].items():
            unconsolidated_counts = []
            # Variable type of a calculation is in the schema, but it's not a filter
            filters_ = copy.deepcopy(filters)
            expected_type = filters_.pop("type")
            for tim in unconsolidated_tims:
                # Override timeline counts at consolidation
                new_count = 0
                if calculation not in tim["override"]:  # If no overrides
                    new_count = self.count_timeline_actions(tim, **filters_)
                else:
                    for key in list(tim["override"].keys()):
                        if (
                            key == calculation
                        ):  # If datapoint in overrides matches calculation being counted
                            # if override begins with += or -=, add or subtract respectively instead of just setting
                            if isinstance(tim["override"][calculation], str):
                                # removing "+=" and setting override[edited_datapoint] to the right type
                                if tim["override"][calculation][0:2] == "+=":
                                    tim["override"][calculation] = tim["override"][calculation][2:]
                                    if tim["override"][calculation].isdecimal():
                                        tim["override"][calculation] = int(
                                            tim["override"][calculation]
                                        )
                                    elif (
                                        "." in tim["override"][calculation]
                                        and tim["override"][calculation]
                                        .replace(".", "0", 1)
                                        .isdecimal()
                                    ):
                                        tim["override"][calculation] = float(
                                            tim["override"][calculation]
                                        )
                                    # "adding" to the original value
                                    tim["override"][calculation] += self.count_timeline_actions(
                                        tim, **filters_
                                    )
                                elif tim["override"][calculation][0:2] == "-=":
                                    # removing "-=" and setting override[edited_datapoint] to the right type
                                    tim["override"][calculation] = tim["override"][calculation][2:]
                                    if tim["override"][calculation].isdecimal():
                                        tim["override"][calculation] = int(
                                            tim["override"][calculation]
                                        )
                                    elif (
                                        "." in tim["override"][calculation]
                                        and tim["override"][calculation]
                                        .replace(".", "0", 1)
                                        .isdecimal()
                                    ):
                                        tim["override"][calculation] = float(
                                            tim["override"][calculation]
                                        )
                                    # "subtracting" to the original value
                                    tim["override"][calculation] *= -1
                                    tim["override"][calculation] += self.count_timeline_actions(
                                        tim, **filters_
                                    )
                            new_count = tim["override"][calculation]
                if not isinstance(new_count, self.type_check_dict[expected_type]):
                    raise TypeError(f"Expected {new_count} calculation to be a {expected_type}")
                unconsolidated_counts.append(new_count)
            calculated_tim[calculation] = self.consolidate_nums(unconsolidated_counts)
        return calculated_tim

    def calculate_tim_times(self, unconsolidated_tims: List[Dict]) -> dict:
        """Given a list of unconsolidated TIMs, returns the calculated time data fields"""
        calculated_tim = {}
        for calculation, action_types in self.schema["timeline_cycle_time"].items():
            unconsolidated_cycle_times = []
            # Variable type of a calculation is in the schema, but it's not a filter
            filters_ = copy.deepcopy(action_types)
            expected_type = filters_.pop("type")
            for tim in unconsolidated_tims:
                # action_types is a list of dictionaries, where each dictionary is
                # "action_type" to the name of either the start or end action
                new_cycle_time = self.total_time_between_actions(
                    tim,
                    action_types["start_action"],
                    action_types["end_action"],
                    action_types["minimum_time"],
                )
                if not isinstance(new_cycle_time, self.type_check_dict[expected_type]):
                    raise TypeError(
                        f"Expected {new_cycle_time} calculation to be a {expected_type}"
                    )
                unconsolidated_cycle_times.append(new_cycle_time)
            calculated_tim[calculation] = self.consolidate_nums(unconsolidated_cycle_times)
        return calculated_tim

    def calculate_aggregates(self, calculated_tim: List[Dict]):
        """Given a list of consolidated tims by calculate_tim_counts, return consolidated aggregates"""
        final_aggregates = {}
        # Get each aggregate and its associated counts
        for aggregate, filters in self.schema["aggregates"].items():
            total_count = 0
            aggregate_counts = filters["counts"]
            # Add up all the counts for each aggregate and add them to the final dictionary
            for count in aggregate_counts:
                total_count += (
                    calculated_tim[count]
                    if count in calculated_tim
                    else final_aggregates[count]
                    if count in final_aggregates
                    else 0
                )
                final_aggregates[aggregate] = total_count
        return final_aggregates

    def calculate_point_values(self, calculated_tim: List[Dict]):
        """Given a list of consolidated tims by calculate_tim_counts, return consolidated point values"""
        final_points = {}
        # Get each point data point
        for point_datapoint_section, filters in self.schema["point_calculations"].items():
            total_points = 0
            point_aggregates = filters["counts"]
            point_counts = point_aggregates.keys()
            # Add up all the counts for each aggregate, multiplys them by their value, then adds them to the final dictionary
            for point in point_counts:
                count = calculated_tim[point] if point in calculated_tim else 0
                total_points += count * point_aggregates[point]
            final_points[point_datapoint_section] = total_points
        return final_points

    def calculate_tim(self, unconsolidated_tims: List[Dict]) -> dict:
        """Given a list of unconsolidated TIMs, returns a calculated TIM"""
        if len(unconsolidated_tims) == 0:
            log.warning("calculate_tim: zero TIMs given")
            return {}
        calculated_tim = {}
        calculated_tim.update(self.calculate_tim_counts(unconsolidated_tims))
        calculated_tim.update(self.calculate_tim_times(unconsolidated_tims))
        calculated_tim.update(self.consolidate_categorical_actions(unconsolidated_tims))
        calculated_tim.update(self.calculate_aggregates(calculated_tim))
        calculated_tim.update(self.calculate_point_values(calculated_tim))
        # Use any of the unconsolidated TIMs to get the team and match number,
        # since that should be the same for each unconsolidated TIM
        calculated_tim["match_number"] = unconsolidated_tims[0]["match_number"]
        calculated_tim["team_number"] = unconsolidated_tims[0]["team_number"]
        # confidence_rating is the number of scouts that scouted one robot
        calculated_tim["confidence_ranking"] = len(unconsolidated_tims)
        return calculated_tim

    def update_calcs(self, tims: List[Dict[str, Union[str, int]]]) -> List[dict]:
        """Calculate data for each of the given TIMs. Those TIMs are represented as dictionaries:
        {'team_number': '1678', 'match_number': 69}"""
        calculated_tims = []
        for tim in tims:
            unconsolidated_obj_tims = self.server.db.find("unconsolidated_obj_tim", tim)
            calculated_tim = self.calculate_tim(unconsolidated_obj_tims)
            calculated_tims.append(calculated_tim)
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
            self.server.db.delete_data("obj_tim")

        updates = self.update_calcs(unique_tims)
        for update in updates:
            if update != {}:
                self.server.db.update_document(
                    "obj_tim",
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
        log.info(f"obj_tims calculation time: {total_time}")
