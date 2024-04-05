#!/usr/bin/env python3
"""Makes predictive calculations for alliances in matches in a competition."""

import utils
import numpy as np
from statistics import NormalDist as Norm
from calculations.base_calculations import BaseCalculations
from data_transfer import tba_communicator
import logging
import time
import pandas as pd
import statsmodels.api as sm

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


# Data class to score alliance scores, used in prediction calculations
class PredictedAimScores:
    # Allows setting score values when initializing class
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    auto_amp = 0.0
    auto_speaker = 0.0
    # Leave rate
    num_leave = 0.0
    tele_amp = 0.0
    tele_speaker = 0.0
    tele_amplified = 0.0
    tele_speaker_all = 0.0
    num_trap = 0.0
    # Park/stage rate
    num_park = 0.0
    num_onstage = 0.0


class PredictedAimCalc(BaseCalculations):
    schema = utils.read_schema("schema/calc_predicted_aim_schema.yml")

    POINT_VALUES = {
        "auto_amp": 2,
        "auto_speaker": 5,
        "num_leave": 2,
        "tele_amp": 1,
        "tele_speaker": 2,
        "tele_amplified": 5,
        "tele_speaker_all": 3.4,  # Placeholder so tests don't break
        "num_trap": 5,
        "num_park": 1,
        "num_onstage": 3,
    }

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["obj_team", "tba_team"]

    def calc_alliance_auto_score(self, predicted_values):
        """Calculates the predicted auto score for an alliance.

        predicted_values: dataclass which stores the predicted number of notes scored and success rates.

        other_predicted_values: dataclass for the opposing alliance
        """
        # TODO: when alliances are expected to intake (combined) more than 5 pieces from the center,
        #       scale down the scores from the center so that they sum to 5 and their ratios are preserved.
        auto_scores = {"dynamic": 0, "reg": self.calc_weighted_score(predicted_values, "auto")}

        for data_field in predicted_values.__dict__.keys():
            # Filters out non-auto scores
            if "auto" in data_field or data_field == "leave":
                # Adds to predicted auto score
                auto_scores["dynamic"] += (
                    getattr(predicted_values, data_field) * self.POINT_VALUES[data_field]
                )

        return auto_scores

    def calc_alliance_tele_score(self, predicted_values, obj_team, team_numbers):
        """Calculates the predicted tele score for an alliance.

        `predicted_values`: dataclass which stores the predicted number of notes scored and success rates.

        `obj_team`: all the obj_team data from the database

        `team_numbers`: list of teams in the alliance

        This function must be run after predicted_values is populated.
        """
        tele_schema = self.schema["--tele_fields"]
        alliance_data = []
        predicted_scores = {"dynamic": 0, "reg": self.calc_weighted_score(predicted_values, "tele")}

        # Get data needed from obj_team
        fields = tele_schema["score"] + tele_schema["cycle_time"]
        for team in team_numbers:
            obj = list(filter(lambda obj_item: obj_item["team_number"] == team, obj_team))
            if obj != []:
                obj = obj[0]
            else:
                log.critical(
                    f"predicted_aim: no obj_team data found for team {team} in alliance {team_numbers}"
                )
                alliance_data.append({var: 0 for var in fields})
                continue
            alliance_data.append({var: obj[var] for var in fields})

        # Constant predicted score
        predicted_scores["constant"] = 3.4 * sum(
            [
                team["tele_avg_speaker"] + team["tele_avg_amp"] + team["tele_avg_amplified"]
                for team in alliance_data
            ]
        )

        # Dynamic predicted score using avg_expected_notes
        N = sum([team["avg_expected_notes"] for team in alliance_data])
        T = 115 / N if N != 0 else 150
        predicted_scores["dynamic"] = 5 * N - (4 * N) / (T + 5)

        return predicted_scores

    def calc_alliance_stage_score(self, obj_team, team_numbers, predicted_values):
        """Calculates an alliance's predicted endgame score

        `obj_team`: obj_team data from the database

        `team_numbers`: teams on the alliance

        `predicted_values`: predicted values dataclass
        """
        # List of dicts containing success rates for each team
        endgame_data = self.get_endgame_fields(obj_team, team_numbers)

        predicted_scores = {
            "dynamic": 0,
            "reg": self.calc_weighted_score(predicted_values, "endgame"),
        }

        ## Scuffed formula to predict endgame score ##
        # Probability cutoff to be considered as capable
        cutoff = 0.75
        # Number of teams that can do the action
        num_can_climb = sum([1 for team in endgame_data if team["onstage_rate"] >= cutoff])
        num_can_climb_after = sum(
            [1 for team in endgame_data if team["climb_after_rate"] >= cutoff]
        )
        num_can_trap = sum([1 for team in endgame_data if team["trap_rate"] >= cutoff])
        num_can_park = sum([1 for team in endgame_data if team["park_rate"] >= cutoff])

        if num_can_climb_after > 2:
            num_can_climb_after = 2

        # Iterate through endgame scenarios
        if num_can_climb == 3:
            # Double harmony
            if num_can_climb_after == 2:
                if num_can_trap >= 1:
                    predicted_scores["dynamic"] = 18
                else:
                    predicted_scores["dynamic"] = 13
            # Harmony + climb
            elif num_can_climb_after == 1:
                if num_can_trap != 3:
                    predicted_scores["dynamic"] = 11 + num_can_trap * 5
                else:
                    predicted_scores["dynamic"] = 21
            # Triple climb
            elif num_can_climb_after == 0:
                predicted_scores["dynamic"] = 9 + num_can_trap * 5
        # Assume other team parks
        elif num_can_climb == 2:
            # Harmony
            if num_can_climb_after >= 1:
                if num_can_trap >= 1:
                    predicted_scores["dynamic"] = 14
                else:
                    predicted_scores["dynamic"] = 9
            # Double climb
            if num_can_climb_after == 0:
                predicted_scores["dynamic"] = 7 + num_can_trap * 5
        # Assume other teams park
        elif num_can_climb == 1:
            # Climb
            predicted_scores["dynamic"] = 5 + num_can_trap * 5
        # All teams park
        else:
            predicted_scores["dynamic"] = num_can_park

        return predicted_scores

    def calc_alliance_score(self, predicted_values, obj_team_data, tba_team_data, team_numbers):
        """Calculates the predicted_values dataclass for an alliance.

        predicted_values is a dataclass which stores the predicted number of notes scored and success rates.

        obj_team is a list of dictionaries of objective team data.

        tba_team is a list of dictionaries of tba team data.

        team_numbers is a list of team numbers (strings) on the alliance.

        other_team_numbers is a list of team numbers on the opposing alliance
        """
        # Gets obj_team data for teams in team_numbers
        obj_team = [
            team_data for team_data in obj_team_data if team_data["team_number"] in team_numbers
        ]

        # Updates predicted_values using obj_team and tba_team data
        for team in obj_team:
            tba_team = [
                team_data
                for team_data in tba_team_data
                if team_data["team_number"] == team["team_number"]
            ]
            if tba_team:
                tba_team = tba_team[0]
            else:
                log.warning(
                    f"predicted_aim: tba_team data not found for team {team['team_number']}"
                )
                tba_team = {"leave_successes": 0}

            # Update predicted values
            predicted_values.auto_speaker += team["auto_avg_speaker"]
            predicted_values.auto_amp += team["auto_avg_amp"]
            predicted_values.tele_speaker += team["tele_avg_speaker"]
            predicted_values.tele_speaker_all += (
                team["tele_avg_speaker"] + team["tele_avg_amplified"]
            )
            predicted_values.tele_amplified += team["tele_avg_amplified"]
            predicted_values.tele_amp += team["tele_avg_amp"]
            predicted_values.num_leave += (
                tba_team["leave_successes"] / team["matches_played"]
                if team["matches_played"] != 0
                else 0
            )
            predicted_values.num_park += team["parked_percent"]
            predicted_values.num_onstage += team["stage_percent_success_all"]
            predicted_values.num_trap += team["trap_percent_success"]

        return predicted_values

    def get_playoffs_alliances(self):
        """
        Gets playoff alliances from TBA.

        obj_team is all the obj_team data in the database.

        tba_team is all the tba_team data in the database.
        """
        tba_playoffs_data = tba_communicator.tba_request(
            f"event/{self.server.TBA_EVENT_KEY}/alliances"
        )
        playoffs_alliances = []

        # Hasn't reached playoffs yet
        if tba_playoffs_data == None:
            return playoffs_alliances

        for num, alliance in enumerate(tba_playoffs_data):
            # Get alliance number (enumerate function is zero-indexed so each number has to be incremented by one)
            alliance_num = num + 1
            # Add captain, 1st, and 2nd pick
            if len(alliance["picks"]) == 3:
                playoffs_alliances.append(
                    {
                        "alliance_num": alliance_num,
                        "picks": [team[3:] for team in alliance["picks"][:3]],
                    }
                )
            elif len(alliance["picks"]) > 3:
                # Add captain, 1st, and 2nd pick
                playoffs_alliances.append(
                    {
                        "alliance_num": alliance_num,
                        "picks": [team[3:] for team in alliance["picks"][:3]],
                    }
                )
                # Add captain, 1st, and 3rd pick
                playoffs_alliances.append(
                    {
                        "alliance_num": alliance_num + 8,
                        "picks": [
                            team[3:]
                            for team in (
                                alliance["picks"][:2]
                                + [
                                    alliance["picks"][3]
                                    if len(alliance["picks"]) > 3
                                    else alliance["picks"][2]
                                ]
                            )
                        ],
                    }
                )
                # Add captain, 2nd, and 3rd pick
                playoffs_alliances.append(
                    {
                        "alliance_num": alliance_num + 16,
                        "picks": [
                            team[3:]
                            for team in (
                                [alliance["picks"][0]] + alliance["picks"][2:4]
                                if len(alliance["picks"]) > 3
                                else alliance["picks"][:3]
                            )
                        ],
                    }
                )
        return playoffs_alliances

    def get_endgame_fields(self, obj_team_data, team_numbers):
        """Gets the endgame score success rates for an alliance or a team.

        obj_team_data: list of obj_team data from the database

        team_numbers: (if calculating for a full alliance) list of three team numbers in the alliance, e.g. ['1678', '254', '4414']
        """
        fields = self.schema["--endgame_fields"]

        # List of endgame data
        alliance_data = []
        # Populate alliance_data with variables needed to calculate the RP
        for team in team_numbers:
            obj_data = list(
                filter(lambda team_data: team_data["team_number"] == team, obj_team_data)
            )
            if obj_data:
                obj_data = obj_data[0]
            else:
                log.critical(
                    f"predicted_aim: no obj_team data found for team {team}, unable to calculate ensemble RP for alliance {team_numbers}"
                )
                alliance_data.append({field: 0 for field in fields.keys()})
                continue
            # Collect needed obj_team variables for each team in the alliance
            alliance_data.append({field: obj_data[var] for field, var in fields.items()})
        return alliance_data

    def calc_ensemble_rp(self, obj_team_data, team_numbers):
        """Calculates the expected ensemble RP for an alliance

        obj_team_data: obj_team data from the database

        team_numbers: teams in the alliance"""

        alliance_data = self.get_endgame_fields(obj_team_data, team_numbers)

        # Calculate expected climb points and probability of RP

        # Method 1: trap + 2 climb
        # P1 = P(Bc)P(At)
        # list of (climb_rate, trap_rate)
        climb_trap_rates = [(team["onstage_rate"], team["trap_rate"]) for team in alliance_data]
        possible_combos = []
        orders = [(0, 1), (1, 0), (1, 2), (2, 1), (0, 2), (2, 0)]
        # Calculate all possible climb + trap combos of different teams
        for order in orders:
            possible_combos.append(climb_trap_rates[order[0]][0] * climb_trap_rates[order[1]][1])
        prob_1 = max(possible_combos)

        # Method 2: harmony + climb
        # P2 = P(Ac)P(Bb)P(Cc)
        # list of (climb_rate, climb_after_rate)
        climb_buddy_rates = [
            (team["onstage_rate"], team["climb_after_rate"]) for team in alliance_data
        ]
        orders = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
        possible_combos = []
        # Get all (Cx, Cy, Bz) permutations
        for order in orders:
            possible_combos.append(
                climb_buddy_rates[order[0]][0]
                * climb_buddy_rates[order[1]][0]
                * climb_buddy_rates[order[2]][1]
            )
        prob_2 = max(possible_combos)

        rp = max(prob_1, prob_2)

        # For the ensemble RP, teams have to have at least a 60% chance of achieving
        # one of the eligible combos in order to reliably get the ensemble RP
        if rp >= 0.6:
            return 1.0
        else:
            return 0.0

    def calc_melody_rp(self, predicted_values):  # , obj_team, team_list, match_number):
        """Calculates predicted melody RP for an alliance.

        `predicted_values`: (non-empty) dataclass storing score data for the whole alliance
        """
        total_gamepieces = (
            predicted_values.auto_amp
            + predicted_values.auto_speaker
            + predicted_values.tele_amp
            + predicted_values.tele_speaker
            + predicted_values.tele_amplified
        )
        rp = total_gamepieces / 15
        # For melody RP, they need to score on average 90% of the gamepieces needed
        # to be able to reliably achieve the melody RP
        if rp > 0.9:
            return 1.0
        else:
            return 0.0

    def get_actual_values(self, aim, tba_match_data):
        """Pulls actual AIM data from TBA if it exists.
        Otherwise, returns dictionary with all values of 0 and has_actual_data of False.

        aim is the alliance in match to pull actual data for."""
        actual_match_dict = {
            "actual_score": 0,
            "actual_rp1": 0.0,
            "actual_rp2": 0.0,
            "won_match": False,
            "has_actual_data": False,
        }
        match_number = aim["match_number"]
        if self.server.db.find("obj_tim", {"match_number": match_number}) != []:
            actual_match_dict["has_actual_data"] = True
        else:
            actual_match_dict["has_actual_data"] = False

        for match in tba_match_data:
            # Checks the value of winning_alliance to determine if the match has data.
            # If there is no data for the match, winning_alliance is an empty string.
            if (
                match["match_number"] == match_number
                and match["comp_level"] == "qm"
                and match["score_breakdown"] is not None
            ):
                actual_aim = match["score_breakdown"]
                if aim["alliance_color"] == "R":
                    alliance_color = "red"
                else:
                    alliance_color = "blue"
                actual_match_dict["actual_score"] = actual_aim[alliance_color]["totalPoints"]
                # TBA stores RPs as booleans. If the RP is true, they get 1 RP, otherwise they get 0.
                if actual_aim[alliance_color]["melodyBonusAchieved"]:
                    actual_match_dict["actual_rp1"] = 1.0
                if actual_aim[alliance_color]["ensembleBonusAchieved"]:
                    actual_match_dict["actual_rp2"] = 1.0
                # Gets whether the alliance won the match by checking the winning alliance against the alliance color/
                actual_match_dict["won_match"] = match["winning_alliance"] == alliance_color
                # Actual values to compare predictions
                actual_match_dict["actual_score_auto"] = actual_aim[alliance_color]["autoPoints"]
                actual_match_dict["actual_score_endgame"] = actual_aim[alliance_color][
                    "endGameTotalStagePoints"
                ]
                actual_match_dict["actual_score_tele"] = (
                    actual_aim[alliance_color]["teleopPoints"]
                    - actual_match_dict["actual_score_endgame"]
                )
                actual_match_dict["actual_foul_points"] = actual_aim[alliance_color]["foulPoints"]
                actual_match_dict["cooperated"] = actual_aim[alliance_color][
                    "coopertitionBonusAchieved"
                ]
                # Sets actual_match_data to true once the actual data has been pulled
                break

        return actual_match_dict

    def filter_aims_list(self, obj_team, tba_team, aims_list):
        """Filters the aims list to only contain aims where all teams have existing data.
        Prevents predictions from crashing due to being run on teams with no data.

        obj_team is all the obj_team data in the database.

        tba_team is all the tba_team data in the database.

        aims_list is all the aims before filtering."""
        filtered_aims_list = []

        # List of all teams that have existing documents in obj_team and tba_team
        obj_team_numbers = [team_data["team_number"] for team_data in obj_team]
        tba_team_numbers = [team_data["team_number"] for team_data in tba_team]

        # Check each aim for data
        for aim in aims_list:
            has_data = True
            for team in aim["team_list"]:
                if team not in tba_team_numbers:
                    log.warning(
                        f'predicted_aim: no tba_team data for team {team} (Alliance {aim["alliance_color"]} in Match {aim["match_number"]})'
                    )
                if team not in obj_team_numbers:
                    has_data = False
                    log.critical(
                        f'predicted_aim: no obj_team data for team {team} (Alliance {aim["alliance_color"]} in Match {aim["match_number"]})'
                    )
                    break
            if has_data == True:
                filtered_aims_list.append(aim)

        return filtered_aims_list

    def calc_win_chance(self, obj_team, team_list, match_number=None):
        """Calculates predicted win probabilities for a RED alliance

        `obj_team`: list of all existing obj_team dicts

        `team_list`: dict containing team numbers in the alliance
                    looks like {"R": ["1678", "254", "4414"], "B": ["125", "6800", "1323"]}

        `match_number`: match to calculate win chance (used for logs)
        """
        # Sets up data needed to calculate win chance
        schema_fields = self.schema["--win_chance"]
        data = {"R": {"mean": 0, "var": 0}, "B": {"mean": 0, "var": 0}}

        # Gets mean and variance for alliance score distribution
        for color in ["R", "B"]:
            for team in team_list[color]:
                obj_data = list(
                    filter(lambda team_data: team_data["team_number"] == team, obj_team)
                )
                if obj_data != []:
                    obj_data = obj_data[0]
                else:
                    log.critical(
                        f"predicted_aim: no obj_team data for team {team}, cannot calculate win chance"
                    )
                    continue
                team_mean = 0
                team_var = 0
                # Add mean and variance for every score datapoint
                for name, attrs in schema_fields.items():
                    team_mean += obj_data[name] * attrs["weight"]
                    team_var += (obj_data[attrs["sd"]] * attrs["weight"]) ** 2
                data[color]["mean"] += team_mean
                data[color]["var"] += team_var

        # Calculate win chance
        # Find probability of red normal distrubution being greater than blue normal distribution
        dist = {
            "mean": data["R"]["mean"] - data["B"]["mean"],
            "var": data["R"]["var"] + data["B"]["var"],
        }
        # Calculates win chance for red, P(R - B) > 0 => 1 - phi(0)
        if dist["var"] > 0:
            prob_red_wins = round(1 - Norm(dist["mean"], dist["var"] ** 0.5).cdf(0), 3)
        else:
            log.critical(
                f"predicted_aim: alliances {team_list['R']} and {team_list['B']} have an invalid score variance of {dist['var']}, cannot calculate win chances for match {match_number}"
            )
            return 1 if dist["mean"] > 0 else 0

        # Return win chance
        return prob_red_wins

    def get_score_weights(self) -> dict:
        """Gets score weights from the `data/score_weights.json` file.

        Returns a dict with keys as variables and values as their weights.
        """
        weights = pd.read_json("data/score_weights.json", typ="series")
        return weights.to_dict()

    def calc_weighted_score(self, predicted_values, mode) -> float:
        """Calculates the predicted score using the score weights in `data/score_weights.json`.

        `predicted_values`: predicted values dataclass
        `mode`: auto, tele, or stage

        Returns the score for that mode based on the predicted values dataclass.
        """
        # Get variables and weights
        weighted_vars = self.schema["--score_weights"][mode]
        weights = self.get_score_weights()
        predicted_score = 0

        # Find variables in the mode
        for data_field in predicted_values.__dict__.keys():
            if f"_{data_field}" in weighted_vars:
                predicted_score += getattr(predicted_values, data_field) * weights[f"_{data_field}"]

        return predicted_score

    def update_predicted_aim(self, aims_list):
        "Updates predicted and actual data with new obj_team and tba_team data"
        updates = []
        obj_team = self.server.db.find("obj_team")
        tba_team = self.server.db.find("tba_team")
        tba_match_data = tba_communicator.tba_request(f"event/{self.server.TBA_EVENT_KEY}/matches")
        filtered_aims_list = self.filter_aims_list(obj_team, tba_team, aims_list)

        finished_matches = []
        # Update every aim
        for aim in filtered_aims_list:
            if aim["match_number"] not in finished_matches:
                # Find opposing alliance
                other_aim = list(
                    filter(
                        lambda some_aim: some_aim["match_number"] == aim["match_number"]
                        and some_aim != aim,
                        filtered_aims_list,
                    )
                )
                if other_aim != []:
                    other_aim = other_aim[0]
                else:
                    log.critical(
                        f"predicted_aim: alliance {aim['team_list']} has no opposing alliance in match {aim['match_number']}"
                    )
                    continue

                # Create updates
                update = {
                    "match_number": aim["match_number"],
                    "alliance_color_is_red": aim["alliance_color"] == "R",
                }
                other_update = {
                    "match_number": other_aim["match_number"],
                    "alliance_color_is_red": other_aim["alliance_color"] == "R",
                }

                # Calculate predicted values data classes
                aim_predicted_values = self.calc_alliance_score(
                    PredictedAimScores(), obj_team, tba_team, aim["team_list"]
                )
                other_aim_predicted_values = self.calc_alliance_score(
                    PredictedAimScores(), obj_team, tba_team, other_aim["team_list"]
                )

                # Add gamepieces
                for action, value in aim_predicted_values.__dict__.items():
                    update[f"_{action}"] = value
                for action, value in other_aim_predicted_values.__dict__.items():
                    other_update[f"_{action}"] = value

                # Calculate predicted scores
                for score_type in ["dynamic", "reg"]:
                    # Calculate scores
                    update[f"predicted_score_{score_type}"] = (
                        (auto := self.calc_alliance_auto_score(aim_predicted_values)[score_type])
                        + (
                            tele := self.calc_alliance_tele_score(
                                aim_predicted_values, obj_team, aim["team_list"]
                            )[score_type]
                        )
                        + (
                            stage := self.calc_alliance_stage_score(
                                obj_team, aim["team_list"], aim_predicted_values
                            )[score_type]
                        )
                    )
                    update[f"predicted_score_{score_type}_auto"] = auto
                    update[f"predicted_score_{score_type}_tele"] = tele
                    update[f"predicted_score_{score_type}_stage"] = stage

                    # Other alliance
                    other_update[f"predicted_score_{score_type}"] = (
                        (
                            other_auto := self.calc_alliance_auto_score(other_aim_predicted_values)[
                                score_type
                            ]
                        )
                        + (
                            other_tele := self.calc_alliance_tele_score(
                                other_aim_predicted_values, obj_team, other_aim["team_list"]
                            )[score_type]
                        )
                        + (
                            other_stage := self.calc_alliance_stage_score(
                                obj_team, other_aim["team_list"], other_aim_predicted_values
                            )[score_type]
                        )
                    )
                    other_update[f"predicted_score_{score_type}_auto"] = other_auto
                    other_update[f"predicted_score_{score_type}_tele"] = other_tele
                    other_update[f"predicted_score_{score_type}_stage"] = other_stage

                # Calculate RPs
                update["predicted_rp1"] = self.calc_melody_rp(aim_predicted_values)
                update["predicted_rp2"] = self.calc_ensemble_rp(obj_team, aim["team_list"])
                other_update["predicted_rp1"] = self.calc_melody_rp(other_aim_predicted_values)
                other_update["predicted_rp2"] = self.calc_ensemble_rp(
                    obj_team, other_aim["team_list"]
                )

                # Calculate win chance
                if aim["alliance_color"] == "R":
                    update["win_chance"] = self.calc_win_chance(
                        obj_team,
                        {
                            aim["alliance_color"]: aim["team_list"],
                            other_aim["alliance_color"]: other_aim["team_list"],
                        },
                        aim["match_number"],
                    )
                    other_update["win_chance"] = 1 - update["win_chance"]
                else:
                    other_update["win_chance"] = self.calc_win_chance(
                        obj_team,
                        {
                            other_aim["alliance_color"]: other_aim["team_list"],
                            aim["alliance_color"]: aim["team_list"],
                        },
                        other_aim["match_number"],
                    )
                    update["win_chance"] = 1 - other_update["win_chance"]

                # Calculate actual values
                update.update(self.get_actual_values(aim, tba_match_data))
                other_update.update(self.get_actual_values(other_aim, tba_match_data))

                # Add aim team list
                update["team_numbers"] = aim["team_list"]
                other_update["team_numbers"] = other_aim["team_list"]

                updates.extend([update, other_update])
                finished_matches.append(aim["match_number"])
        return updates

    def update_playoffs_alliances(self):
        """Runs the calculations for predicted values in playoffs matches

        obj_team is all the obj_team data in the database.

        tba_team is all the tba_team data in the database.

        playoffs_alliances is a list of alliances with team numbers
        """
        updates = []
        obj_team = self.server.db.find("obj_team")
        tba_team = self.server.db.find("tba_team")
        playoffs_alliances = self.get_playoffs_alliances()

        # Check if empty
        if playoffs_alliances == updates:
            return updates

        for alliance in playoffs_alliances:
            predicted_values = self.calc_alliance_score(
                PredictedAimScores(), obj_team, tba_team, alliance["picks"]
            )
            update = alliance

            # Calculate predicted scores
            for score_type in ["dynamic", "reg"]:
                # Calculate scores
                update[f"predicted_score_{score_type}"] = (
                    (auto := self.calc_alliance_auto_score(predicted_values)[score_type])
                    + (
                        tele := self.calc_alliance_tele_score(
                            predicted_values, obj_team, alliance["picks"]
                        )[score_type]
                    )
                    + (
                        stage := self.calc_alliance_stage_score(
                            obj_team, alliance["picks"], predicted_values
                        )[score_type]
                    )
                )
                update[f"predicted_score_{score_type}_auto"] = auto
                update[f"predicted_score_{score_type}_tele"] = tele
                update[f"predicted_score_{score_type}_stage"] = stage

            updates.append(update)
        return updates

    def run(self):
        # Get calc start time
        start_time = time.time()
        match_schedule = self.get_aim_list()
        # Check if changes need to be made to teams
        teams = self.get_updated_teams()
        aims = []
        for alliance in match_schedule:
            for team in alliance["team_list"]:
                if team in teams:
                    aims.append(alliance)
                    break
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("predicted_aim")

        # Inserts predicted_aim data into database
        for update in self.update_predicted_aim(aims):
            self.server.db.update_document(
                "predicted_aim",
                update,
                {
                    "match_number": update["match_number"],
                    "alliance_color_is_red": update["alliance_color_is_red"],
                },
            )

        # Inserts data into predicted_alliances
        for update in self.update_playoffs_alliances():
            self.server.db.update_document(
                "predicted_alliances", update, {"alliance_num": update["alliance_num"]}
            )

        end_time = time.time()
        # Get total calc time
        total_time = end_time - start_time
        # Write total calc time to log
        log.info(f"predicted_aim calculation time: {round(total_time, 2)} sec")
