#!/usr/bin/env python3
"""Calculate objective team data from Team in Match (TIM) data."""

import utils
from typing import List, Dict
from calculations import base_calculations
import statistics
import time
import logging

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


class OBJTeamCalc(base_calculations.BaseCalculations):
    """Runs OBJ Team calculations"""

    # Get the last section of each entry (so foo.bar.baz becomes baz)
    SCHEMA = utils.unprefix_schema_dict(utils.read_schema("schema/calc_obj_team_schema.yml"))
    TIM_SCHEMA = utils.read_schema("schema/calc_obj_tim_schema.yml")

    def __init__(self, server):
        """Overrides watched collections, passes server object"""
        super().__init__(server)
        self.watched_collections = ["obj_tim", "subj_tim"]

    def get_action_counts(self, tims: List[Dict]):
        """Gets a list of times each team completed a certain action by tim for averages
        and standard deviations.
        """
        tim_action_counts = {}
        # Gathers all necessary schema fields
        tim_fields = set()
        for schema in {
            **self.SCHEMA["averages"],
            **self.SCHEMA["standard_deviations"],
        }.values():
            tim_fields.add(schema["tim_fields"][0].split(".")[1])
        for tim_field in tim_fields:
            # Gets the total number of actions across all tims
            tim_action_counts[tim_field] = [tim[tim_field] for tim in tims]
        return tim_action_counts

    def get_action_sum(self, tims: List[Dict]):
        """Gets a list of times each team completed a certain action by tim for medians"""
        tim_action_sum = {}
        # Gathers all necessary schema fields
        tim_fields = set()
        for schema in {**self.SCHEMA["medians"]}.values():
            tim_fields.add(schema["tim_fields"][0].split(".")[1])
        for tim_field in tim_fields:
            tim_action_sum[tim_field] = [tim[tim_field] for tim in tims]
        return tim_action_sum

    def get_action_categories(self, tims: List[Dict]):
        """Gets a list of times each team completed a certain categorical action for counts and modes."""
        tim_action_categories = {}
        # Gathers all necessary schema fields
        tim_fields = set()
        for schema in {**self.SCHEMA["modes"]}.values():
            tim_fields.add(schema["tim_fields"][0].split(".")[1])
        for tim_field in tim_fields:
            # Gets the total number of actions across all tims
            tim_action_categories[tim_field] = [tim[tim_field] for tim in tims]
        return tim_action_categories

    def calculate_averages(self, tim_action_counts, lfm_tim_action_counts):
        """Creates a dictionary of calculated averages, called team_info,
        where the keys are the names of the calculations, and the values are the results
        """
        team_info = {}
        for calculation, schema in self.SCHEMA["averages"].items():
            # Average the values for the tim_fields
            average = 0
            for tim_field in schema["tim_fields"]:
                tim_field = tim_field.split(".")[1]
                if "lfm" in calculation:
                    average += self.avg(lfm_tim_action_counts[tim_field])
                else:
                    average += self.avg(tim_action_counts[tim_field])
            team_info[calculation] = average
        return team_info

    def calculate_standard_deviations(self, tim_action_counts, lfm_tim_action_counts):
        """Creates a dictionary of calculated standard deviations, called team_info,
        where the keys are the names of the calculation, and the values are the results
        """
        team_info = {}
        for calculation, schema in self.SCHEMA["standard_deviations"].items():
            # Take the standard deviation for the tim_field
            tim_field = schema["tim_fields"][0].split(".")[1]
            if "lfm" in calculation:
                standard_deviation = statistics.pstdev(lfm_tim_action_counts[tim_field])
            else:
                standard_deviation = statistics.pstdev(tim_action_counts[tim_field])
            team_info[calculation] = standard_deviation
        return team_info

    def filter_tims_for_counts(self, tims: List[Dict], schema):
        """Filters tims based on schema for count calculations"""
        tims_that_meet_filter = 0
        for field in schema["tim_fields"]:
            if type(field) == dict:
                for key, value in field.items():
                    key = key.split(".")[1]
                    # Checks that the TIMs in their given field meet the filter
                    tims_that_meet_filter += len(list(filter(lambda tim: tim[key] == value, tims)))
            else:
                for key, value in schema["tim_fields"].items():
                    if key != "not":
                        # Checks that the TIMs in their given field meet the filter
                        tims_that_meet_filter += len(
                            list(filter(lambda tim: tim[key] == value, tims))
                        )
                    else:
                        # not_field expects the output to be anything but the given filter
                        # not_value is the filter that not_field shouldn't have
                        # checks if value is a list
                        if isinstance(value, list):
                            for val in value:
                                for not_field, not_value in val.items():
                                    # gets rid of obj_tim or subj_tim in front of datapoint
                                    not_field = not_field.split(".")[1]
                                    tims_that_meet_filter += len(
                                        list(
                                            # filter gets every item that meets the conditions of the lambda function in tims
                                            filter(
                                                lambda tim: tim.get(not_field, not_value)
                                                != not_value,
                                                tims,
                                            )
                                        )
                                    )
                        else:
                            for not_field, not_value in value.items():
                                tims_that_meet_filter += len(
                                    list(
                                        filter(
                                            lambda tim: tim.get(not_field, not_value) != not_value,
                                            tims,
                                        )
                                    )
                                )

        return tims_that_meet_filter

    def calculate_counts(self, tims: List[Dict], lfm_tims: List[Dict]):
        """Creates a dictionary of calculated counts, called team_info,
        where the keys are the names of the calculations, and the values are the results
        """
        team_info = {}
        for calculation, schema in self.SCHEMA["counts"].items():
            if "lfm" in calculation:
                tims_that_meet_filter = self.filter_tims_for_counts(lfm_tims, schema)
            else:
                tims_that_meet_filter = self.filter_tims_for_counts(tims, schema)
            team_info[calculation] = tims_that_meet_filter
        return team_info

    def calculate_special_counts(self, obj_tims, subj_tims, lfm_obj_tims, lfm_subj_tims):
        """Calculates counts of datapoints collected by Objective and Subjective Scouts."""
        team_info = {}
        for calculation, schema in self.SCHEMA["special_counts"].items():
            total = 0
            obj_tims_that_meet_filter = []
            subj_tims_that_meet_filter = []
            if "lfm" in calculation:
                for field in schema["tim_fields"]:
                    for key, value in field.items():
                        # Separates the datapoint into the obj/subj_tim part and the actual datapoint
                        key, name = key.split(".")[1], key.split(".")[0]
                        # Checks that the TIMs in their given field meet the filter
                        if name == "obj_tim":
                            # joins the two lists together
                            # filter gets every item that meets the conditions of the lambda function in tims
                            obj_tims_that_meet_filter = obj_tims_that_meet_filter + list(
                                filter(lambda tim: tim.get(key, value) == value, lfm_obj_tims)
                            )
                        else:
                            subj_tims_that_meet_filter = subj_tims_that_meet_filter + list(
                                filter(lambda tim: tim.get(key, value) == value, lfm_subj_tims)
                            )
            else:
                for field in schema["tim_fields"]:
                    for key, value in field.items():
                        # Separates the datapoint into the obj/subj_tim part and the actual datapoint
                        key, name = key.split(".")[1], key.split(".")[0]
                        # Checks that the TIMs in their given field meet the filter
                        if name == "obj_tim":
                            # joins the two lists together
                            # filter gets every item that meets the conditions of the lambda function in tims
                            obj_tims_that_meet_filter = obj_tims_that_meet_filter + list(
                                filter(lambda tim: tim.get(key, value) == value, obj_tims)
                            )
                        else:
                            subj_tims_that_meet_filter = subj_tims_that_meet_filter + list(
                                filter(lambda tim: tim.get(key, value) == value, subj_tims)
                            )
            for tim in obj_tims_that_meet_filter:
                for s_tim in subj_tims_that_meet_filter:
                    if (
                        tim["match_number"] == s_tim["match_number"]
                        and tim["team_number"] == s_tim["team_number"]
                    ):
                        total += 1
                        break
            team_info[calculation] = total
        return team_info

    def calculate_super_counts(self, tims, lfm_tims):
        """Calculates counts of datapoints collected by Super Scouts."""
        team_info = {}
        for calculation, schema in self.SCHEMA["super_counts"].items():
            total = 0
            tim_field = schema["tim_fields"][0].split(".")[1]
            if "lfm" in calculation:
                for tim in lfm_tims:
                    if tim[tim_field]:
                        total += 1
            else:
                for tim in tims:
                    if tim[tim_field]:
                        total += 1
            team_info[calculation] = total
        return team_info

    def calculate_ss_counts(self, tims, lfm_tims):
        """Calculates counts of datapoints collected by Stand Strategists."""
        team_info = {}
        for calculation, schema in self.SCHEMA["ss_counts"].items():
            total = 0
            tim_field = schema["tim_fields"][0].split(".")[1]
            if "lfm" in calculation:
                for tim in lfm_tims:
                    if tim_field in tim.keys():
                        if tim[tim_field] == True:
                            total += 1
            else:
                for tim in tims:
                    if tim_field in tim.keys():
                        if tim[tim_field] == True:
                            total += 1
            team_info[calculation] = total
        return team_info

    def calculate_extrema(
        self,
        tim_action_counts,
        lfm_tim_action_counts,
    ):
        """Creates a dictionary of extreme values, called team_info,
        where the keys are the names of the calculations, and the values are the results
        """
        team_info = {}
        for calculation, schema in self.SCHEMA["extrema"].items():
            tim_field = schema["tim_fields"][0].split(".")[1]
            if schema["extrema_type"] == "max":
                if "lfm" in calculation:
                    team_info[calculation] = max(lfm_tim_action_counts[tim_field])
                else:
                    team_info[calculation] = max(tim_action_counts[tim_field])
            if schema["extrema_type"] == "min":
                if "lfm" in calculation:
                    team_info[calculation] = min(lfm_tim_action_counts[tim_field])
                else:
                    team_info[calculation] = min(tim_action_counts[tim_field])
        return team_info

    def calculate_medians(self, tim_action_sum, lfm_tim_action_sum):
        """Creates a dictionary of median actions, called team_info,
        where the keys are the names of the calculations, and the values are the results
        """
        team_info = {}
        for calculation, schema in self.SCHEMA["medians"].items():
            median = 0
            for tim_field in schema["tim_fields"]:
                tim_field = tim_field.split(".")[1]
                if "lfm" in calculation:
                    values_to_count = [
                        value
                        for value in lfm_tim_action_sum[tim_field]
                        if value != schema["ignore"]
                    ]
                    if values_to_count == []:
                        continue
                    median += statistics.median(values_to_count)
                else:
                    values_to_count = [
                        value for value in tim_action_sum[tim_field] if value != schema["ignore"]
                    ]
                    if values_to_count == []:
                        continue
                    median += statistics.median(values_to_count)
            team_info[calculation] = median
        return team_info

    def calculate_modes(self, tim_action_categories, lfm_tim_action_categories):
        """Creates a dictionary of mode actions, called team_info,
        where the keys are the names of the calculations, and the values are the results
        """

        team_info = {}
        for calculation, schema in self.SCHEMA["modes"].items():
            values_to_count = []
            for tim_field in schema["tim_fields"]:
                tim_field = tim_field.split(".")[1]
                if "lfm" in calculation:
                    values_to_count = values_to_count + [
                        value
                        for value in lfm_tim_action_categories[tim_field]
                        if value != schema["ignore"]
                    ]
                else:
                    values_to_count = values_to_count + [
                        value
                        for value in tim_action_categories[tim_field]
                        if value != schema["ignore"]
                    ]
            team_info[calculation] = statistics.multimode(values_to_count)
        return team_info

    def calculate_success_rates(self, team_counts: Dict):
        """Creates a dictionary of action success rates, called team_info,
        where the keys are the names of the calculations, and the values are the results
        """
        team_info = {}
        for calculation, schema in self.SCHEMA["success_rates"].items():
            num_attempts = 0
            num_successes = 0
            for attempt_datapoint in schema["team_attempts"]:
                if isinstance(attempt_datapoint, int):
                    num_attempts += attempt_datapoint
                elif attempt_datapoint[0] == "-":
                    num_attempts -= team_counts[attempt_datapoint[1:]]
                else:
                    num_attempts += team_counts[attempt_datapoint]
            for success_datapoint in schema["team_successes"]:
                num_successes += team_counts[success_datapoint]
            if num_attempts != 0:
                team_info[calculation] = num_successes / num_attempts
                if num_successes / num_attempts > 1:
                    team_info[calculation] = 1
            else:
                team_info[calculation] = 0
        return team_info

    # Not used in Crescendo
    """def calculate_average_points(self, team_data):
        team_info = {}
        for calculation, schema in self.SCHEMA["average_points"].items():
            total_successes = 0
            total_points = 0
            for field, value in schema.items():
                if field == "type":
                    continue
                total_successes += team_data[field]
                total_points += team_data[field] * value
            if total_successes > 0:
                team_info[calculation] = total_points / total_successes
            else:
                team_info[calculation] = 0
        return team_info"""

    def calculate_sums(self, team_data, tims: List[Dict], lfm_tims: List[Dict]):
        """Creates a dictionary of sum of weighted data, called team_info
        where the keys are the names of the calculations, and the values are the results
        """
        team_info = {}
        for calculation, schema in self.SCHEMA["sums"].items():
            # incap_time has no point values
            if calculation == "total_incap_time":
                team_info[calculation] = sum(tim["incap_time"] for tim in tims)
            elif calculation == "lfm_total_incap_time":
                # Use lfm_tims instead of tims, also this is the only lfm sum
                team_info[calculation] = sum([tim["incap_time"] for tim in lfm_tims])
            else:
                total_points = 0
                for field, value in schema.items():
                    if field == "type":
                        continue
                    if isinstance(value, list):
                        weight = 1
                        for v in value:
                            weight *= v if not isinstance(v, str) else team_data[v]
                    else:
                        weight = value if not isinstance(value, str) else team_data[value]
                    total_points += (
                        team_data[field] if field in team_data else team_info[field]
                    ) * weight
                team_info[calculation] = total_points
        return team_info

    def update_team_calcs(self, teams: list) -> list:
        """Calculate data for given team using objective calculated TIMs"""
        obj_team_updates = {}
        # Subj aim data for super counts
        for team in teams:
            # Load team data from database
            obj_tims = self.server.db.find("obj_tim", {"team_number": team})
            subj_tims = self.server.db.find("subj_tim", {"team_number": team})
            ss_tims = self.server.db.find("ss_tim", {"team_number": team})
            # Last 4 tims to calculate last 4 matches
            obj_lfm_tims = sorted(obj_tims, key=lambda tim: tim["match_number"])[-4:]
            subj_lfm_tims = sorted(subj_tims, key=lambda tim: tim["match_number"])[-4:]
            ss_lfm_tims = sorted(ss_tims, key=lambda tim: tim["match_number"])[-4:]
            tim_action_counts = self.get_action_counts(obj_tims)
            lfm_tim_action_counts = self.get_action_counts(obj_lfm_tims)
            tim_action_categories = self.get_action_categories(obj_tims)
            lfm_tim_action_categories = self.get_action_categories(obj_lfm_tims)
            tim_action_sum = self.get_action_sum(obj_tims)
            lfm_tim_action_sum = self.get_action_sum(obj_lfm_tims)

            team_data = self.calculate_averages(tim_action_counts, lfm_tim_action_counts)
            team_data["team_number"] = team
            team_data.update(self.calculate_counts(obj_tims, obj_lfm_tims))
            team_data.update(self.calculate_super_counts(subj_tims, subj_lfm_tims))
            team_data.update(self.calculate_ss_counts(ss_tims, ss_lfm_tims))
            team_data.update(
                self.calculate_standard_deviations(tim_action_counts, lfm_tim_action_counts)
            )
            team_data.update(
                self.calculate_extrema(
                    tim_action_counts,
                    lfm_tim_action_counts,
                )
            )
            team_data.update(
                self.calculate_special_counts(obj_tims, subj_tims, obj_lfm_tims, subj_lfm_tims)
            )
            team_data.update(self.calculate_modes(tim_action_categories, lfm_tim_action_categories))
            team_data.update(self.calculate_medians(tim_action_sum, lfm_tim_action_sum))
            team_data.update(self.calculate_success_rates(team_data))
            # team_data.update(self.calculate_average_points(team_data))
            team_data.update(self.calculate_sums(team_data, obj_tims, obj_lfm_tims))
            obj_team_updates[team] = team_data
        return list(obj_team_updates.values())

    def run(self):
        """Executes the OBJ Team calculations"""
        # Get calc start time
        start_time = time.time()
        teams = []
        # Filter out teams that are in subj_tim but not obj_tim
        for team in self.get_updated_teams():
            if self.server.db.find("obj_tim", {"team_number": team}):
                teams.append(team)
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("obj_team")

        for update in self.update_team_calcs(teams):
            self.server.db.update_document(
                "obj_team", update, {"team_number": update["team_number"]}
            )
        end_time = time.time()
        # Get total calc time
        total_time = end_time - start_time
        # Write total calc time to log
        log.info(f"obj_team calculation time: {round(total_time, 2)} sec")
