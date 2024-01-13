#!/usr/bin/env python3
"""Makes predictive calculations for alliances in matches in a competition."""

import utils
import dataclasses
import numpy as np

from calculations.base_calculations import BaseCalculations
from data_transfer import tba_communicator
import logging

log = logging.getLogger(__name__)


@dataclasses.dataclass
class PredictedAimScores:
    auto_amp: float = 0.0
    auto_speaker: float = 0.0
    leave: float = 0.0
    tele_amp: float = 0.0
    tele_speaker: float = 0.0
    tele_speaker_amped: float = 0.0
    trap: float = 0.0
    tele_park_successes: float = 0.0
    tele_onstage_successes: float = 0.0


class LogisticRegression:
    """Logistic regression,
    used to calculate the win chance of an alliance"""

    def __init__(self, learning_rate=0.01, iterations=1000):
        self.learning_rate = learning_rate
        self.iterations = iterations

    # Function for model training
    def fit(self, X, Y):
        # no_of_training_examples, no_of_features
        self.m, self.n = X.shape
        # weight initialization
        self.W = np.zeros(self.n)
        self.b = 0
        self.X = X
        self.Y = Y

        # gradient descent learning

        for i in range(self.iterations):
            self.update_weights()
        return self

    # Helper function to update weights in gradient descent

    def update_weights(self):
        A = 1 / (1 + np.exp(-(self.X.dot(self.W) + self.b)))

        # calculate gradients
        tmp = A - self.Y.T
        tmp = np.reshape(tmp, self.m)
        dW = np.dot(self.X.T, tmp) / self.m
        db = np.sum(tmp) / self.m

        # update weights
        self.W = self.W - self.learning_rate * dW
        self.b = self.b - self.learning_rate * db

        return self

    def predict(self, X):
        Z = 1 / (1 + np.exp(-(X.dot(self.W) + self.b)))
        return Z


class PredictedAimCalc(BaseCalculations):
    POINTS = {
        "auto_amp": 2,
        "auto_speaker": 5,
        "leave": 2,
        "tele_amp": 1,
        "tele_speaker": 2,
        "tele_speaker_amped": 5,
        "trap": 5,
        "tele_park_successes": 1,
        "tele_onstage_successes": 3,
    }

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["obj_team", "tba_team"]

    def calculate_predicted_stage_success_rate():
        pass

    def calculate_predicted_alliance_auto_score(self, predicted_values):
        """Calculates the predicted auto score for an alliance.

        predicted_values is a dataclass which stores the predicted number of notes scored and success rates.
        calculate_predicted_alliance_auto_score must be run after predicted_values is populated.
        """
        auto_score = 0
        # Uses dataclasses.asdict to create key: value pairs for predicted datapoints
        for data_field in dataclasses.asdict(predicted_values).keys():
            # Filters out non-auto scores
            if data_field not in [
                "tele_park_successes",
                "tele_onstage_successes",
                "tele_amp",
                "tele_speaker",
                "tele_speaker_amped",
                "trap",
            ]:
                # Adds to predicted auto score
                auto_score += getattr(predicted_values, data_field) * self.POINTS[data_field]
        return round(auto_score, 5)

    def calculate_predicted_alliance_tele_score(self, predicted_values):
        """Calculates the predicted tele score for an alliance.

        predicted_values is a dataclass which stores the predicted number of notes scored and success rates.
        calculate_predicted_alliance_tele_score must be run after predicted_values is populated.
        """
        tele_score = 0
        # Uses dataclasses.asdict to create key: value pairs for predicted datapoints
        for data_field in dataclasses.asdict(predicted_values).keys():
            # Filters auto scores and stage stuff
            if data_field not in [
                "tele_park_successes",
                "tele_onstage_successes",
                "auto_amp",
                "auto_speaker",
                "leave",
            ]:
                # Adds to tele score
                tele_score += getattr(predicted_values, data_field) * self.POINTS[data_field]

        return round(tele_score, 5)

    def calculate_predicted_alliance_stage_score(self, predicted_values):
        pass

    def calculate_predicted_alliance_score(
        self, predicted_values, obj_team_data, tba_team_data, team_numbers
    ):
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
        # Gets tba_team data for teams in team_numbers
        for team in obj_team:
            tba_team = [
                team_data
                for team_data in tba_team_data
                if team_data["team_number"] == team["team_number"]
            ][0]

            predicted_values.auto_speaker += team["auto_avg_speaker"]
            predicted_values.auto_amp += team["auto_avg_amp"]
            predicted_values.tele_speaker += team["tele_avg_speaker"]
            predicted_values.tele_speaker_amped += team["tele_avg_speaker_amped"]
            predicted_values.tele_amp += team["tele_avg_amp"]
            predicted_values.trap += team["avg_trap"]

            predicted_values.leave += tba_team["leave_successes"] / team["matches_played"]

        for data_field in dataclasses.asdict(predicted_values).keys():
            if data_field not in [
                "tele_park_successes",
                "tele_onstage_successes",
            ]:
                total_score += getattr(predicted_values, data_field) * self.POINTS[data_field]
        return round(total_score, 5)

    def get_playoffs_alliances(self):
        """Gets the
        obj_team is all the obj_team data in the database. tba_team is all the tba_team data in the database.
        """
        tba_playoffs_data = tba_communicator.tba_request(
            f"event/{self.server.TBA_EVENT_KEY}/alliances"
        )
        playoffs_alliances = []

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

    def calculate_predicted_ensemble_rp(self, predicted_values, obj_team_data, team_numbers):
        pass

    def calculate_predicted_melody_rp(self, predicted_values):
        pass

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
        obj_team is all the obj_team data in the database. tba_team is all the tba_team data in the database.
        aims_list is all the aims before filtering."""
        filtered_aims_list = []

        # List of all teams that have existing documents in obj_team and tba_team
        obj_team_numbers = [team_data["team_number"] for team_data in obj_team]
        tba_team_numbers = [team_data["team_number"] for team_data in tba_team]

        for aim in aims_list:
            has_data = True
            for team in aim["team_list"]:
                # has_data is False if any of the teams in the aim are missing obj_team or tba_team data
                if team not in obj_team_numbers or team not in tba_team_numbers:
                    has_data = False
                    log.warning(
                        f'Incomplete team data for Alliance {aim["alliance_color"]} in Match {aim["match_number"]}'
                    )
                    break
            if has_data == True:
                filtered_aims_list.append(aim)

        return filtered_aims_list

    def update_predicted_aim(self, aims_list):
        updates = []
        obj_team = self.server.db.find("obj_team")
        tba_team = self.server.db.find("tba_team")
        tba_match_data = tba_communicator.tba_request(f"event/{self.server.TBA_EVENT_KEY}/matches")
        filtered_aims_list = self.filter_aims_list(obj_team, tba_team, aims_list)

        for aim in filtered_aims_list:
            predicted_values = PredictedAimScores()
            update = {
                "match_number": aim["match_number"],
                "alliance_color_is_red": aim["alliance_color"] == "R",
            }
            update["predicted_score"] = self.calculate_predicted_alliance_score(
                predicted_values, obj_team, tba_team, aim["team_list"]
            )
            update.update(self.get_actual_values(aim, tba_match_data))
            update["team_numbers"] = aim["team_list"]
            updates.append(update)
        return updates

    def update_playoffs_alliances(self):
        """Runs the calculations for predicted values in playoffs matches
        obj_team is all the obj_team data in the database. tba_team is all the tba_team data in the database.
        playoffs_alliances is a list of alliances with team numbers
        """
        updates = []
        obj_team = self.server.db.find("obj_team")
        tba_team = self.server.db.find("tba_team")
        playoffs_alliances = self.get_playoffs_alliances()

        if playoffs_alliances == updates:
            return updates

        for alliance in playoffs_alliances:
            predicted_values = PredictedAimScores()
            update = alliance
            update["predicted_score"] = self.calculate_predicted_alliance_score(
                predicted_values, obj_team, tba_team, alliance["picks"]
            )
            update["predicted_auto_score"] = self.calculate_predicted_alliance_auto_score(
                predicted_values
            )
            update["predicted_tele_score"] = self.calculate_predicted_alliance_tele_score(
                predicted_values
            )
            update["predicted_stage_score"] = self.calculate_predicted_alliance_stage_score(
                predicted_values
            )
            updates.append(update)
        return updates

    def calculate_predicted_win_chance(self):
        new_aims = []
        aims = self.server.db.find("predicted_aim")
        match_list = {aim["match_number"] for aim in aims}
        win_chance = self.get_predicted_win_chance(match_list, aims)
        for match in match_list:
            aims_in_match = [aim for aim in aims if aim["match_number"] == match]
            if len(aims_in_match) < 2:
                break
            aim_score = aims_in_match[0]["predicted_score"]
            opponent_score = aims_in_match[1]["predicted_score"]
            # Make the point difference always positive for more accurate calculations
            point_difference = aim_score - opponent_score
            flipped = point_difference < 0
            predicted_win_chance = round(win_chance(point_difference * (-1 if flipped else 1)), 5)
            (
                aims_in_match[1 if flipped else 0]["win_chance"],
                aims_in_match[0 if flipped else 1]["win_chance"],
            ) = (
                predicted_win_chance,
                1 - predicted_win_chance,
            )
            new_aims.append(aims_in_match[0])
            new_aims.append(aims_in_match[1])
        return new_aims

    def get_predicted_win_chance(self, match_list, aims):
        """Returns a function that calculates the probability that an alliance wins,
        based on the predicted point different between that alliance and the opponent alliance"""

        point_differences = []
        won = []
        for match in match_list:
            aims_in_match = [aim for aim in aims if aim["match_number"] == match]
            if len(aims_in_match) < 2:
                break
            aim_score = aims_in_match[0]["predicted_score"]
            opponent_score = aims_in_match[1]["predicted_score"]
            point_difference = aim_score - opponent_score
            # Make point difference always positive for more accurate calculations
            flipped = point_difference < 0
            if aims_in_match[0]["has_actual_data"]:
                point_differences.append(point_difference * (-1 if flipped else 1))
                win = aims_in_match[0]["won_match"]
                won.append(int(not win if flipped else win))
        point_differences_array = np.array(point_differences).reshape(-1, 1)
        won_array = np.array(won)
        logr = LogisticRegression()
        logr.fit(point_differences_array, won_array)
        # Return prediction lambda
        return lambda difference: logr.predict(np.array([difference]))

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

        for update in self.update_predicted_aim(aims):
            self.server.db.update_document(
                "predicted_aim",
                update,
                {
                    "match_number": update["match_number"],
                    "alliance_color_is_red": update["alliance_color_is_red"],
                },
            )

        for update in self.calculate_predicted_win_chance():
            self.server.db.update_document(
                "predicted_aim",
                update,
                {
                    "match_number": update["match_number"],
                    "alliance_color_is_red": update["alliance_color_is_red"],
                },
            )

        for update in self.update_playoffs_alliances():
            self.server.db.update_document(
                "predicted_alliances", update, {"alliance_num": update["alliance_num"]}
            )
