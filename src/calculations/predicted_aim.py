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
    auto_gamepieces_low: float = 0.0
    auto_cube_mid: float = 0.0
    auto_cube_high: float = 0.0
    auto_cone_mid: float = 0.0
    auto_cone_high: float = 0.0
    auto_dock_successes: float = 0.0
    auto_engage_successes: float = 0.0
    mobility: float = 0.0
    tele_gamepieces_low: float = 0.0
    tele_cube_mid: float = 0.0
    tele_cube_high: float = 0.0
    tele_cone_mid: float = 0.0
    tele_cone_high: float = 0.0
    tele_dock_successes: float = 0.0
    tele_park_successes: float = 0.0
    tele_engage_successes: float = 0.0
    link: float = 0.0
    supercharge: float = 0.0


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
        "auto_gamepieces_low": 3,
        "auto_cube_mid": 4,
        "auto_cube_high": 6,
        "auto_cone_mid": 4,
        "auto_cone_high": 6,
        "auto_dock_successes": 8,
        "auto_engage_successes": 12,
        "mobility": 3,
        "tele_gamepieces_low": 2,
        "tele_cube_mid": 3,
        "tele_cube_high": 5,
        "tele_cone_mid": 3,
        "tele_cone_high": 5,
        "tele_dock_successes": 6,
        "tele_park_successes": 2,
        "tele_engage_successes": 10,
        "link": 5,
        "supercharge": 3,
    }

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["obj_team", "tba_team"]

    def calculate_predicted_link_score(self, predicted_values, obj_team):
        """Calculates the predicted link score

        Predicted link score is calculated using the optimal number of links an
        alliance can score."""
        # low row links
        predicted_values.link += (
            sum(
                [
                    predicted_values.auto_gamepieces_low,
                    predicted_values.tele_gamepieces_low,
                ]
            )
            // 3
        )
        # for the high and mid rows 2 cones and 1 cube is necessary for a link
        predicted_values.link += min(
            (predicted_values.auto_cone_mid + predicted_values.tele_cone_mid) // 2,
            (predicted_values.tele_cube_mid + predicted_values.auto_cube_mid) // 1,
        )
        predicted_values.link += min(
            (predicted_values.auto_cone_high + predicted_values.tele_cone_high) // 2,
            (predicted_values.tele_cube_high + predicted_values.auto_cube_high) // 1,
        )

        # Maximum number of links possible is 9
        predicted_values.link = min(predicted_values.link, 9)

    def set_max_carryover(self, predicted_values, current, max, leftover=None, optional_max=None):
        """Helper function for calculate_predicted_alliance_score, carrying over anything from current over max to leftover"""
        if getattr(predicted_values, current) > max:
            if leftover is not None:
                setattr(
                    predicted_values,
                    leftover,
                    getattr(predicted_values, leftover) + getattr(predicted_values, current) - max,
                )
            setattr(predicted_values, current, max)
        if optional_max is not None and getattr(predicted_values, current) > optional_max:
            if leftover is not None:
                setattr(
                    predicted_values,
                    leftover,
                    getattr(predicted_values, leftover)
                    + getattr(predicted_values, current)
                    - optional_max,
                )
            setattr(predicted_values, current, optional_max)

    def calculate_predicted_alliance_grid(self, predicted_values):
        self.set_max_carryover(predicted_values, "auto_cone_high", 6, "auto_cone_mid")
        self.set_max_carryover(
            predicted_values,
            "auto_cube_high",
            3,
            "auto_cube_mid",
            7 - predicted_values.auto_cone_high,
        )
        self.set_max_carryover(
            predicted_values,
            "auto_cone_mid",
            6,
            "auto_gamepieces_low",
            7 - (predicted_values.auto_cone_high + predicted_values.auto_cube_high),
        )
        self.set_max_carryover(
            predicted_values,
            "auto_cube_mid",
            3,
            "auto_gamepieces_low",
            7
            - (
                predicted_values.auto_cone_high
                + predicted_values.auto_cube_high
                + predicted_values.auto_cone_mid
            ),
        )
        self.set_max_carryover(
            predicted_values,
            "auto_gamepieces_low",
            7
            - (
                predicted_values.auto_cone_high
                + predicted_values.auto_cube_high
                + predicted_values.auto_cone_mid
                + predicted_values.auto_cube_mid
            ),
        )

        self.set_max_carryover(
            predicted_values, "tele_cone_high", 6 - predicted_values.auto_cone_high, "tele_cone_mid"
        )
        self.set_max_carryover(
            predicted_values,
            "tele_cone_mid",
            6 - predicted_values.auto_cone_mid,
            "tele_gamepieces_low",
        )
        self.set_max_carryover(
            predicted_values, "tele_cube_high", 3 - predicted_values.auto_cube_high, "tele_cube_mid"
        )
        self.set_max_carryover(
            predicted_values,
            "tele_cube_mid",
            3 - predicted_values.auto_cube_mid,
            "tele_gamepieces_low",
        )
        # If the grid is full count supercharge
        if all(
            [
                predicted_values.auto_cube_high + predicted_values.tele_cube_high == 3,
                predicted_values.auto_cone_high + predicted_values.tele_cone_high == 6,
                predicted_values.auto_cube_mid + predicted_values.tele_cube_mid == 3,
                predicted_values.auto_cone_mid + predicted_values.tele_cone_mid == 6,
                predicted_values.auto_gamepieces_low + predicted_values.tele_gamepieces_low >= 9,
            ]
        ):
            self.set_max_carryover(
                predicted_values,
                "tele_gamepieces_low",
                9 - predicted_values.auto_gamepieces_low,
                "supercharge",
            )
        else:
            self.set_max_carryover(predicted_values, "tele_gamepieces_low", 9)

    def calculate_predicted_charge_success_rate(self, predicted_values, obj_team):
        # Only one robot can charge in auto, assume that the team sends the robot with
        # the highest expected auto charge score
        new_auto_score = (
            obj_team["auto_engage_percent_success"] * self.POINTS["auto_engage_successes"]
            + obj_team["auto_dock_only_percent_success"] * self.POINTS["auto_dock_successes"]
        )
        current_auto_score = (
            predicted_values.auto_engage_successes * self.POINTS["auto_engage_successes"]
            + predicted_values.auto_dock_successes * self.POINTS["auto_dock_successes"]
        )
        if new_auto_score > current_auto_score:
            predicted_values.auto_dock_successes = obj_team["auto_dock_percent_success"]
            predicted_values.auto_engage_successes = obj_team["auto_engage_percent_success"]
        predicted_values.tele_dock_successes += obj_team["tele_dock_percent_success"]
        predicted_values.tele_engage_successes += obj_team["tele_engage_percent_success"]
        predicted_values.tele_park_successes += obj_team["tele_park_percent_success"]

    def calculate_predicted_grid_score(self, predicted_values, obj_team):
        """Calculates the predicted score from grid.

        predicted_values is a dataclass which stores the predicted number of cones/cubes scored and success rates.
        obj_team is a list of dictionaries of objective team data.
        tba_team is a list of dictionaries of tba team data."""
        # Finds the predicted cubes scored in auto
        predicted_values.auto_gamepieces_low += obj_team["auto_avg_cube_low"]
        predicted_values.auto_cube_mid += obj_team["auto_avg_cube_mid"]
        predicted_values.auto_cube_high += obj_team["auto_avg_cube_high"]

        # Finds the predicted cones scored in auto
        predicted_values.auto_gamepieces_low += obj_team["auto_avg_cone_low"]
        predicted_values.auto_cone_mid += obj_team["auto_avg_cone_mid"]
        predicted_values.auto_cone_high += obj_team["auto_avg_cone_high"]

        # Finds the predicted cubes scored in tele
        predicted_values.tele_gamepieces_low += obj_team["tele_avg_cube_low"]
        predicted_values.tele_cube_mid += obj_team["tele_avg_cube_mid"]
        predicted_values.tele_cube_high += obj_team["tele_avg_cube_high"]

        # Finds the predicted cones score in tele
        predicted_values.tele_gamepieces_low += obj_team["tele_avg_cone_low"]
        predicted_values.tele_cone_mid += obj_team["tele_avg_cone_mid"]
        predicted_values.tele_cone_high += obj_team["tele_avg_cone_high"]

    def calculate_predicted_alliance_auto_score(self, predicted_values):
        """Calculates the predicted auto score for an alliance.

        predicted_values is a dataclass which stores the predicted number of cones/cubes scored and success rates.
        calculate_predicted_alliance_auto_score must be run after predicted_values is populated.
        """
        auto_score = 0
        # Uses dataclasses.asdict to create key: value pairs for predicted datapoints
        for data_field in dataclasses.asdict(predicted_values).keys():
            # Filters tele grid scores and climbs
            if data_field not in [
                "tele_dock_successes",
                "tele_engage_successes",
                "tele_park_successes",
                "tele_gamepieces_low",
                "tele_cube_mid",
                "tele_cube_high",
                "tele_cone_mid",
                "tele_cone_high",
                "link",
                "supercharge",
            ]:
                # Adds auto grid score to auto_score
                auto_score += getattr(predicted_values, data_field) * self.POINTS[data_field]
        return round(auto_score, 5)

    def calculate_predicted_alliance_tele_score(self, predicted_values):
        """Calculates the predicted tele score for an alliance.

        predicted_values is a dataclass which stores the predicted number of cones/cubes scored and success rates.
        calculate_predicted_alliance_tele_score must be run after predicted_values is populated.
        """
        tele_score = 0
        # Uses dataclasses.asdict to create key: value pairs for predicted datapoints
        for data_field in dataclasses.asdict(predicted_values).keys():
            # Filters auto grid scores and climbs
            if data_field not in [
                "tele_dock_successes",
                "tele_engage_successes",
                "tele_park_successes",
                "auto_gamepieces_low",
                "auto_cube_mid",
                "auto_cube_high",
                "auto_cone_mid",
                "auto_cone_high",
                "auto_dock_successes",
                "auto_engage_successes",
                "mobility",
            ]:
                # Adds tele grid score to tele_score
                tele_score += getattr(predicted_values, data_field) * self.POINTS[data_field]
        # Can only engage or dock, so assume the alliance does the one with the highest expected score
        # Finds which charging probability is higher, then adds the score to tele_score
        dock_score, engage_score = [
            getattr(predicted_values, field) * self.POINTS[field]
            for field in ["tele_dock_successes", "tele_engage_successes"]
        ]
        larger_score = ["tele_dock_successes", "tele_engage_successes"][
            int(engage_score > dock_score)
        ]
        dock_or_engage_probability = getattr(predicted_values, larger_score)
        tele_score += dock_or_engage_probability * self.POINTS[larger_score]
        # If a robot doesn't dock/engage, assume it tries to park (/3 to get avg park success chance of alliance)
        tele_score += (
            (3 - dock_or_engage_probability)
            * predicted_values.tele_park_successes
            / 3
            * self.POINTS["tele_park_successes"]
        )
        return round(tele_score, 5)

    def calculate_predicted_alliance_grid_score(self, predicted_values):
        """Calculates the predicted charge score for an alliance

        predicted_values is a dataclass which stores the predicted number of cones/cubes scored and success rates.
        calculate_predicted_alliance_grid_score must be run after predicted_values is populated.
        """
        grid_score = 0
        for data_field in dataclasses.asdict(predicted_values).keys():
            # Filters all climbs
            if data_field not in [
                "tele_dock_successes",
                "tele_engage_successes",
                "tele_park_successes",
                "auto_dock_successes",
                "auto_engage_successes",
                "mobility",
            ]:
                grid_score += getattr(predicted_values, data_field) * self.POINTS[data_field]
        return round(grid_score, 5)

    def calculate_predicted_alliance_charge_score(self, predicted_values):
        """Calculates the predicted charge score for an alliance

        predicted_values is a dataclass which stores the predicted number of cones/cubes scored and success rates.
        calculate_predicted_alliance_charge_score must be run after predicted_values is populated.
        """
        charge_score = 0
        # Can only engage or dock, so assume the alliance does the one with the highest expected score
        # Finds which charging probability is higher, then adds the score to tele_score
        auto_dock_score, auto_engage_score = [
            getattr(predicted_values, field) * self.POINTS[field]
            for field in ["auto_dock_successes", "auto_engage_successes"]
        ]
        auto_larger_score = ["auto_dock_successes", "auto_engage_successes"][
            int(auto_engage_score > auto_dock_score)
        ]
        charge_score += (
            getattr(predicted_values, auto_larger_score) * self.POINTS[auto_larger_score]
        )

        tele_dock_score, tele_engage_score = [
            getattr(predicted_values, field) * self.POINTS[field]
            for field in ["tele_dock_successes", "tele_engage_successes"]
        ]
        tele_larger_score = ["tele_dock_successes", "tele_engage_successes"][
            int(tele_engage_score > tele_dock_score)
        ]
        charge_score += (
            getattr(predicted_values, tele_larger_score) * self.POINTS[tele_larger_score]
        )
        return round(charge_score, 5)

    def calculate_predicted_alliance_score(
        self, predicted_values, obj_team_data, tba_team_data, team_numbers
    ):
        """Calculates the predicted score for an alliance.

        predicted_values is a dataclass which stores the predicted number of cones/cubes scored and success rates.
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

            self.calculate_predicted_grid_score(predicted_values, team)
            self.calculate_predicted_charge_success_rate(predicted_values, team)

            predicted_values.mobility += tba_team["mobility_successes"] / team["matches_played"]
        self.calculate_predicted_alliance_grid(predicted_values)
        self.calculate_predicted_link_score(predicted_values, obj_team)

        for data_field in dataclasses.asdict(predicted_values).keys():
            if data_field not in [
                "tele_dock_successes",
                "tele_engage_successes",
                "tele_park_successes",
            ]:
                total_score += getattr(predicted_values, data_field) * self.POINTS[data_field]
        # Can only engage or dock, so assume the alliance does the one with the highest expected score
        dock_score, engage_score = [
            getattr(predicted_values, field) * self.POINTS[field]
            for field in ["tele_dock_successes", "tele_engage_successes"]
        ]
        larger_score = ["tele_dock_successes", "tele_engage_successes"][
            int(engage_score > dock_score)
        ]
        dock_or_engage_probability = getattr(predicted_values, larger_score)
        total_score += dock_or_engage_probability * self.POINTS[larger_score]
        # If a robot doesn't dock/engage, assume it tries to park (/3 to get avg park success chance of alliance)
        total_score += (
            (3 - dock_or_engage_probability)
            * predicted_values.tele_park_successes
            / 3
            * self.POINTS["tele_park_successes"]
        )
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

    def calculate_predicted_link_rp(self, predicted_values):
        """Calculates whether an alliance is expected to earn the link RP

        predicted_values is a dataclass which stores the predicted number of pieces scored and success rates.
        """
        if getattr(predicted_values, "link") >= 6:
            return 1.0
        elif getattr(predicted_values, "link") == 5:
            # Use the coopertition criteria met percentage to gain the chances of a link RP with 4 links
            # If it doesn't exist use 0.75 (seems to be the average percentage in most comps)
            try:
                return round(
                    (
                        tba_communicator.tba_request(f"event/{self.server.TBA_EVENT_KEY}/insights")[
                            "qual"
                        ]["coopertition"][2]
                    )
                    / 100,
                    2,
                )
            except:
                return 0.75
        return 0.0

    def calculate_predicted_charge_rp(self, predicted_values, obj_team_data, team_numbers):
        """Calculates whether an alliance is expected to earn the endgame RP.
        Assuming the alliance sends the robot with the highest expected auto score
        to charge in auto and the best two robots at engaging to charge in tele

        predicted_values is a dataclass which stores the predicted number of balls scored and success rates.
        """
        obj_team = [
            team_data for team_data in obj_team_data if team_data["team_number"] in team_numbers
        ]
        # Find the chance of the best robot engaging or docking in auto
        auto_dock_or_engage_percent = max([team["auto_dock_percent_success"] for team in obj_team])
        # Find the chance of engaging in tele of the best two robots at engaging
        two_best_engagers = sorted([team["tele_engage_percent_success"] for team in obj_team])[-2:]
        tele_two_engage_percent = two_best_engagers[0] * two_best_engagers[-1]
        # Return the chance of both occuring
        return auto_dock_or_engage_percent * tele_two_engage_percent

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
                and match["score_breakdown"] != {}
            ):
                actual_aim = match["score_breakdown"]
                if aim["alliance_color"] == "R":
                    alliance_color = "red"
                else:
                    alliance_color = "blue"
                actual_match_dict["actual_score"] = actual_aim[alliance_color]["totalPoints"]
                # TBA stores RPs as booleans. If the RP is true, they get 1 RP, otherwise they get 0.
                if actual_aim[alliance_color]["activationBonusAchieved"]:
                    actual_match_dict["actual_rp1"] = 1.0
                if actual_aim[alliance_color]["sustainabilityBonusAchieved"]:
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
            update["predicted_rp1"] = self.calculate_predicted_charge_rp(
                predicted_values, obj_team, aim["team_list"]
            )
            update["predicted_rp2"] = self.calculate_predicted_link_rp(predicted_values)
            update.update(self.get_actual_values(aim, tba_match_data))
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
            update["predicted_grid_score"] = self.calculate_predicted_alliance_grid_score(
                predicted_values
            )
            update["predicted_charge_score"] = self.calculate_predicted_alliance_charge_score(
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
