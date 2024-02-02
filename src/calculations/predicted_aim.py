#!/usr/bin/env python3
"""Makes predictive calculations for alliances in matches in a competition."""

import utils
import dataclasses
import numpy as np
from statistics import NormalDist as Norm
import warnings

from calculations.base_calculations import BaseCalculations
from data_transfer import tba_communicator
import logging

log = logging.getLogger(__name__)


# Data class to score alliance scores, used in prediction calculations
# @dataclasses.dataclass
class PredictedAimScores:
    # Allows setting score values when initializing class
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    auto_amp = 0.0
    auto_speaker = 0.0
    # Leave rate
    leave = 0.0
    tele_amp = 0.0
    tele_speaker = 0.0
    tele_speaker_amped = 0.0
    trap = 0.0
    # Park/stage rate
    park_successes = 0.0
    onstage_successes = 0.0


class PredictedAimCalc(BaseCalculations):
    schema = utils.read_schema("schema/calc_predicted_aim_schema.yml")

    POINT_VALUES = {
        "auto_amp": 2,
        "auto_speaker": 5,
        "leave": 2,
        "tele_amp": 1,
        "tele_speaker": 2,
        "tele_speaker_amped": 5,
        "trap": 5,
        "park_successes": 1,
        "onstage_successes": 3,
    }

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["obj_team", "tba_team"]

    def calc_alliance_auto_score(self, predicted_values):
        """Calculates the predicted auto score for an alliance.

        predicted_values is a dataclass which stores the predicted number of notes scored and success rates.

        calc_alliance_auto_score must be run after predicted_values is populated.
        """
        auto_score = 0
        # Uses dataclasses.asdict to create key: value pairs for predicted datapoints
        for data_field in predicted_values.__dict__.keys():
            # Filters out non-auto scores
            if "auto" in data_field or data_field == "leave":
                # Adds to predicted auto score
                auto_score += getattr(predicted_values, data_field) * self.POINT_VALUES[data_field]
        return round(auto_score, 3)

    def calc_alliance_tele_score(self, predicted_values):
        """Calculates the predicted tele score for an alliance.

        predicted_values is a dataclass which stores the predicted number of notes scored and success rates.

        This function must be run after predicted_values is populated.
        """
        tele_score = 0
        # Uses dataclasses.asdict to create key: value pairs for predicted datapoints
        for data_field in predicted_values.__dict__.keys():
            # Filters auto endgame scores
            if "tele" in data_field:
                # Adds to tele score
                tele_score += getattr(predicted_values, data_field) * self.POINT_VALUES[data_field]

        return round(tele_score, 3)

    def calc_alliance_stage_score(self, predicted_ensemble_rp):
        "Calculates an alliance's predicted endgame score based on their expected ensemble RP."
        return predicted_ensemble_rp * 13

    def calc_alliance_score(self, predicted_values, obj_team_data, tba_team_data, team_numbers):
        """Calculates the predicted score for an alliance.

        predicted_values is a dataclass which stores the predicted number of notes scored and success rates.

        obj_team is a list of dictionaries of objective team data.

        tba_team is a list of dictionaries of tba team data.

        team_numbers is a list of team numbers (strings) on the alliance.
        """
        total_score = 0

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
            if tba_team != []:
                tba_team = tba_team[0]
            else:
                warnings.warn(f"predicted_aim: tba_team data not found for team {team}")
                continue

            # Update predicted values
            predicted_values.auto_speaker += team["auto_avg_speaker"]
            predicted_values.auto_amp += team["auto_avg_amp"]
            predicted_values.tele_speaker += team["tele_avg_speaker"]
            predicted_values.tele_speaker_amped += team["tele_avg_speaker_amped"]
            predicted_values.tele_amp += team["tele_avg_amp"]
            predicted_values.trap += team["trap_successes"] / (
                team["trap_successes"] + team["trap_fails"]
            )
            predicted_values.leave += tba_team["leave_successes"] / team["matches_played"]

        # Calculate predicted score
        total_score = (
            self.calc_alliance_auto_score(predicted_values)
            + self.calc_alliance_tele_score(predicted_values)
            + self.calc_alliance_stage_score(self.calc_ensemble_rp(obj_team, team_numbers))
        )

        return round(total_score, 3)

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

    def calc_ensemble_rp(self, obj_team_data, team_numbers):
        """Calculates the expected ensemble RP for an alliance

        obj_team_data: obj_team data from the database

        team_numbers: teams in the alliance"""
        fields = self.schema["ensemble_rp"]
        alliance_data = []

        # Populate alliance_data with variables needed to calculate the RP
        for team in team_numbers:
            new_team = {}
            obj_data = list(
                filter(lambda team_data: team_data["team_number"] == team, obj_team_data)
            )
            if obj_data != []:
                obj_data = obj_data[0]
            else:
                warnings.warn(
                    f"predicted_aim: no obj_team data found for team {team}, unable to calculate ensemble RP for alliance {team_numbers}"
                )
                return 0

            # Collect needed obj_team variables for each team in the alliance
            for field, vars in fields.items():
                counts = vars["counts"]
                try:
                    # Attempts is a single variable
                    if len(counts[1]) == 1:
                        # Currently, we can't calculate exact climb_after_rate
                        # An approximate adjustment is used
                        if field == "climb_after_rate":
                            try:
                                new_team[field] = obj_data[counts[0]] / (obj_data[counts[1][0]] - 2)
                            except ZeroDivisionError:
                                new_team[field] = obj_data[counts[0]] / obj_data[counts[1][0]]
                            if new_team[field] <= 0:
                                new_team[field] = 0
                        else:
                            new_team[field] = obj_data[counts[0]] / obj_data[counts[1][0]]
                    # Attempts needs to be calculated through successes + fails
                    elif len(counts[1]) == 2:
                        new_team[field] = obj_data[counts[0]] / (
                            obj_data[counts[1][0]] + obj_data[counts[1][1]]
                        )
                except:
                    new_team[field] = 0
            alliance_data.append(new_team)

        # Calculate expected climb points and probability of RP

        # Method 1: trap + 2 climb
        # P1 = P(Bc)P(At)

        # list of (climb_rate, trap_rate)
        climb_trap_rates = [(team["onstage_rate"], team["trap_rate"]) for team in alliance_data]
        possible_combos = []
        orders = [(0, 1), (1, 0), (1, 2), (2, 1), (0, 2), (2, 0)]
        # Calculate all possible climb + trap combos of different teams
        for order in orders:
            possible_combos.append(climb_trap_rates[order[0]][0] * climb_trap_rates[order[1]][0])
        prob_1 = max(possible_combos)
        # Method 2: harmony + climb
        # P2 = P(Ac)P(Bb)P(Cc)
        # TODO: get climb_after success rate. This can be done during consolidations as we collect if they climb or climb_after in the match.
        #       For now, assume P(Bb) = |Bb| / (|Bc| - 2), cap at 1
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
        return round(max(prob_1, prob_2), 3)

    def calc_melody_rp(self, predicted_values):
        """Calculates the expected melody RP for an alliance.

        predicted_values: populated alliance score dataclass"""
        # TODO: ADD COOPERTITION
        total_gamepieces = (
            predicted_values.auto_amp
            + predicted_values.auto_speaker
            + predicted_values.tele_amp
            + predicted_values.tele_speaker
            + predicted_values.tele_speaker_amped
        )
        return round(total_gamepieces / 18, 3)

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
                # Sets actual_match_data to true once the actual data has been pulled
                actual_match_dict["has_actual_data"] = True
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
        team_numbers = list(
            set([team_data["team_number"] for team_data in obj_team])
            & set([team_data["team_number"] for team_data in tba_team])
        )

        # Check each aim for data
        for aim in aims_list:
            has_data = True
            for team in aim["team_list"]:
                if team not in team_numbers:
                    has_data = False
                    log.warning(
                        f'Incomplete team data for Alliance {aim["alliance_color"]} in Match {aim["match_number"]}'
                    )
                    break
            if has_data == True:
                filtered_aims_list.append(aim)

        return filtered_aims_list

    def calc_win_chance(self, obj_team, team_list, alliance_color):
        """Calculates predicted win probabilities for an alliance,

        obj_teams: list of all existing obj_team dicts

        team_list: dict containing team numbers in the alliance
                    looks like {"R": [1678, 254, 4414], "B": [125, 6800, 1323]}

        alliance_color: "R" or "B"
        """
        # Sets up data needed to calculate win chance
        schema_fields = self.schema["win_chance"]["required_vars"]
        data = {"R": {"mean": 0, "var": 0}, "B": {"mean": 0, "var": 0}}

        # Gets mean and variance for alliance score distribution
        for color in ["R", "B"]:
            for team in team_list[color]:
                obj_data = list(
                    filter(lambda team_data: team_data["team_number"] == team, obj_team)
                )[0]
                team_mean = 0
                team_var = 0
                # Add mean and variance for every score datapoint
                for name, attrs in schema_fields.items():
                    # We don't have SDs for endgame points
                    if name != "avg_endgame_points":
                        team_mean += obj_data[name] * attrs["value"]
                        team_var += (obj_data[attrs["sd"]] * attrs["value"]) ** 2
                    else:
                        team_mean += obj_data[name]
                data[color]["mean"] += team_mean
                data[color]["var"] += team_var

        # Calculate win chance
        # Find probability of red normal distrubution being greater than blue normal distribution
        dist = {
            "mean": data["R"]["mean"] - data["B"]["mean"],
            "var": data["R"]["var"] + data["B"]["var"],
        }
        # Calculates win chance for red, P(R - B) > 0 --> 1 - phi(R - B)
        prob_red_wins = round(1 - Norm(dist["mean"], dist["var"] ** 0.5).cdf(0), 3)

        # Return win chance
        if alliance_color == "R":
            return prob_red_wins
        else:
            return 1 - prob_red_wins

    def update_predicted_aim(self, aims_list):
        "Updates predicted and actual data with new obj_team and tba_team data"
        updates = []
        obj_team = self.server.db.find("obj_team")
        tba_team = self.server.db.find("tba_team")
        tba_match_data = tba_communicator.tba_request(f"event/{self.server.TBA_EVENT_KEY}/matches")
        filtered_aims_list = self.filter_aims_list(obj_team, tba_team, aims_list)

        # Update every aim
        for aim in filtered_aims_list:
            predicted_values = PredictedAimScores()
            update = {
                "match_number": aim["match_number"],
                "alliance_color_is_red": aim["alliance_color"] == "R",
            }

            update["predicted_score"] = self.calc_alliance_score(
                predicted_values, obj_team, tba_team, aim["team_list"]
            )
            # TODO: check TBA for rp1 and rp2
            update["predicted_rp1"] = self.calc_ensemble_rp(obj_team, aim["team_list"])
            update["predicted_rp2"] = self.calc_melody_rp(predicted_values)

            other_aim = list(
                filter(
                    lambda some_aim: some_aim["match_number"] == aim["match_number"]
                    and some_aim != aim,
                    filtered_aims_list,
                )
            )[0]
            update["win_chance"] = self.calc_win_chance(
                obj_team,
                {
                    aim["alliance_color"]: aim["team_list"],
                    other_aim["alliance_color"]: other_aim["team_list"],
                },
                aim["alliance_color"],
            )

            update.update(self.get_actual_values(aim, tba_match_data))
            update["team_numbers"] = aim["team_list"]

            updates.append(update)
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
            predicted_values = PredictedAimScores()
            update = alliance
            update["predicted_score"] = self.calc_alliance_score(
                predicted_values, obj_team, tba_team, alliance["picks"]
            )
            update["predicted_auto_score"] = self.calc_alliance_auto_score(predicted_values)
            update["predicted_tele_score"] = self.calc_alliance_tele_score(predicted_values)
            update["predicted_stage_score"] = self.calc_alliance_stage_score(
                self.calc_ensemble_rp(obj_team, alliance["picks"])
            )
            updates.append(update)
        return updates

    def run(self):
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
