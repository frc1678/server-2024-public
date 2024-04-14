#!/usr/bin/env python3
"""Makes predictive calculations using linear regressions for alliances in matches in a competition."""

import utils
import numpy as np
from statistics import NormalDist as Norm
from calculations.base_calculations import BaseCalculations
from data_transfer import tba_communicator
import logging
import time
import pandas as pd
import json
from typing import Union, Optional, List
import statsmodels.api as sm

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


class PredictedAimCalc(BaseCalculations):
    SCHEMA = utils.read_schema("schema/calc_predicted_aim_schema.yml")
    REGRESSIONS_SCHEMA = utils.read_schema("schema/calc_predicted_weights_schema.yml")

    def __init__(self, server):
        "Sets up the `PredictedAimCalc` class."
        super().__init__(server)
        self.watched_collections = ["obj_team", "tba_team"]

    def calc_variable(
        self, data: dict, _how: str, _from: Union[str, List[str]], _values: Optional[list] = None
    ) -> Union[int, float, bool]:
        """Pulls a variable from `data` given the method (sum, diff, rate, or bool)

        `_how`: method to get the variable. "sum", "diff", "rate", or "bool"

        `_from`: raw variable name in `data` to pull from.

        `data`: dict of data to pull from. In 2024, this is either one obj_team or tba_team dict.

        `_values`: if `_how`="bool", convert the `False`/`True` to index 0 or 1 of this list.

        Returns the the pulled variable from `data`.
        """
        if _values is None:
            _values = list()

        value = None

        try:
            if _how == "normal":
                value = data[_from]
            elif _how == "sum":
                value = sum([data[var] for var in _from])
            elif _how == "diff":
                value = data[_from[0]] - data[_from[1]]
            elif _how == "rate":
                if type(_from[1]) != int and type(_from[1]) != float:
                    value = data[_from[0]] / data[_from[1]]
                else:
                    value = data[_from[0]] / _from[1]
            elif _how == "bool":
                value = _values[int(data[_from])]
            elif _how == "threshold":
                value = int(sum([data[var] for var in _from[:-1]]) >= _from[-1])
        except Exception as e:
            log.critical(f"ERROR WHEN PARSING VARIABLE {_from}: {e}. Cannot calculate data.")
            return 0

        return value

    def calc_match_expected_values(
        self, team_numbers: Union[dict, list], data: dict, level: str = "quals"
    ) -> dict:
        """Calculates "expected values" for both alliances in a match. This is a dictionary containing
        all the variables in the `--expected_values` section in schema that will be used to calculate predicted scores and RPs later.

        `team_numbers`: if quals, dict of team numbers in the match, formatted like {"R": ["1678", "254", "1323"], "B": ["125", "8033", "4414"]}.
                        if elims, list of team numbers in the alliance.

        `data`: dict of data from collections that predicted_aim pulls data from. In 2024, these two collections
                were `obj_team` and `tba_team`. The dictionary is formatted like {"obj_team": [{"team_number": "1678", ...}, {...}, ...], "tba_team": [{"team_number": "1678", ...}, {...}, ...]}

        `level`: "quals" or "elims"

        Returns a dictionary containing `--expected_values` variables and their values.
        """
        variables = self.SCHEMA["--expected_values"]
        match_expected_values = dict()

        if level == "quals":
            # Create expected values dict
            for variable, info in variables.items():
                if not info["is_joined"]:
                    match_expected_values[f"{variable}_red"] = 0
                    match_expected_values[f"{variable}_blue"] = 0
                else:
                    match_expected_values[variable] = 0

            # Get values for every variable in the schema
            for color_abbrev in ["R", "B"]:
                color_full = "red" if color_abbrev == "R" else "blue"
                for variable, info in variables.items():
                    # If variable isn't a joined calculation, calculate it for red and blue
                    if not info["is_joined"]:
                        collection_data = data[info["collection"]]

                        # Get values for every team
                        for team_num in team_numbers[color_abbrev]:
                            team_data = list(
                                filter(
                                    lambda item: item["team_number"] == team_num, collection_data
                                )
                            )
                            # Check if there's data
                            if team_data:
                                team_data = team_data[0]
                            else:
                                log.critical(
                                    f"No {info['collection']} data for team {team_num}, cannot calculate predictions."
                                )
                                continue

                            match_expected_values[f"{variable}_{color_full}"] += self.calc_variable(
                                team_data, info["how"], info["from"], info.get("values", list())
                            )
            # Calculate joined variables on already calculated expected values
            # TODO: this is super scuffed, we need predicted scores for red and blue
            #       to calculate win chance but they aren't added to the match expected values,
            #       so we have to calculate them here. We NEED a fix for this, but I don't have time now since champs is next week.
            match_expected_values["_predicted_score_red"] = self.predict_value(
                match_expected_values,
                "score",
                self.REGRESSIONS_SCHEMA["--regressions"]["score"]["model_type"],
                alliance_color="R",
                level="quals",
            )
            match_expected_values["_predicted_score_blue"] = self.predict_value(
                match_expected_values,
                "score",
                self.REGRESSIONS_SCHEMA["--regressions"]["score"]["model_type"],
                alliance_color="B",
                level="quals",
            )
            for variable, info in variables.items():
                if info["is_joined"]:
                    match_expected_values[variable] += self.calc_variable(
                        match_expected_values, info["how"], info["from"], info.get("values", list())
                    )
        # For elims, there are no joined variable or red or blue alliance.
        else:
            match_expected_values = {
                var: 0
                for var in self.SCHEMA["--expected_values"]
                if not self.SCHEMA["--expected_values"][var]["is_joined"]
            }
            for variable, info in variables.items():
                if not info["is_joined"]:
                    collection_data = data[info["collection"]]

                    # Get values for every team
                    for team_num in team_numbers:
                        team_data = list(
                            filter(lambda item: item["team_number"] == team_num, collection_data)
                        )
                        # Check if there's data
                        if team_data:
                            team_data = team_data[0]
                        else:
                            log.critical(
                                f"No {info['collection']} data for team {team_num}, cannot calculate predictions."
                            )
                            continue

                        match_expected_values[variable] += self.calc_variable(
                            team_data, info["how"], info["from"], info.get("values", list())
                        )
        return match_expected_values

    def get_playoffs_alliances(self) -> List[dict]:
        """Gets playoff alliances from TBA.

        Returns a list of dicts of playoff alliances.
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

    def get_actual_values(self, aim: dict, tba_match_data: List[dict]) -> dict:
        """Pulls actual AIM data for one alliance from TBA if it exists.
        Otherwise, returns dictionary with all values of `None` and has_actual_data of `False`.

        `aim`: the alliance in match to pull actual data for.

        `tba_match_data`: AIM data from TBA.

        Returns a dictionary with actual data pulled from TBA.
        """
        variables = self.SCHEMA["--actual_values"]
        actual_match_dict = {
            "has_actual_data": False,
        }

        match_number = aim["match_number"]
        if self.server.db.find("obj_tim", {"match_number": match_number}):
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

                ## Add actual values for each variable

                # `won_match` is added manually
                actual_match_dict["won_match"] = match["winning_alliance"] == alliance_color

                # Iterate through all variables to pull from
                for variable, info in variables.items():
                    actual_match_dict[variable] = self.calc_variable(
                        actual_aim[alliance_color],
                        info["how"],
                        info["from"],
                        info.get("values", list()),
                    )
                # Set has_actual_data to True
                actual_match_dict["has_actual_data"] = True

                break

        return actual_match_dict

    def filter_aims_list(
        self, obj_team: List[dict], tba_team: List[dict], aims_list: List[dict]
    ) -> List[dict]:
        """Filters the aims list to only contain aims where all teams have existing data.
        Prevents predictions from crashing due to being run on teams with no data.

        `obj_team`: obj_team data in the database.

        `tba_team`: tba_team data in the database.

        `aims_list`: aims before filtering.

        Returns a filtered aims list in the same format.
        """
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

    def get_predicted_weights(self) -> dict:
        """Gets predicted weights from the `data/predicted_weights.json` file.

        Returns a dict with separated by prediction, with keys as variables and values as their weights.
        """
        with open("data/predicted_weights.json", "r") as f:
            return json.load(f)

    def predict_value(
        self,
        match_expected_values: dict,
        prediction: str,
        model_type: str,
        alliance_color: str = None,
        level: str = "quals",
    ) -> float:
        """Calculates the predicted score using the predicted weights in `data/predicted_weights.json`.

        `match_expected_values`: match expected values dict

        `prediction`: predictions listed in the `--regressions` section in schema, e.g. "score"

        `model_type`: type of regression model, e.g. "linear" or "logistic".

        `alliance_color`: "R" or "B"

        `level`: "quals" or "elims"

        Returns the predicted value for that prediction.
        """
        alliance_color = "red" if alliance_color == "R" else "blue"
        # Get variables and weights
        weighted_vars = self.REGRESSIONS_SCHEMA["--regressions"][prediction]["indep"]
        weights = self.get_predicted_weights()[prediction]

        if level == "quals":
            # Predict values based on regression formula
            if model_type == "linear":
                return sum(
                    [
                        match_expected_values[f"{var}_{alliance_color}"] * weights[var]
                        if not self.SCHEMA["--expected_values"][var]["is_joined"]
                        else match_expected_values[var] * weights[var]
                        for var in weighted_vars
                    ]
                )
            elif model_type == "logistic":
                return 1 / (
                    1
                    + np.exp(
                        -sum(
                            [
                                match_expected_values[f"{var}_{alliance_color}"] * weights[var]
                                if not self.SCHEMA["--expected_values"][var]["is_joined"]
                                else match_expected_values[var] * weights[var]
                                for var in weighted_vars
                            ]
                        )
                    )
                )
        else:
            if model_type == "linear":
                return sum(
                    [
                        match_expected_values[var] * weights[var]
                        if not self.SCHEMA["--expected_values"][var]["is_joined"]
                        else match_expected_values[var] * weights[var]
                        for var in weighted_vars
                    ]
                )
            elif model_type == "logistic":
                return 1 / (
                    1
                    + np.exp(
                        -sum(
                            [
                                match_expected_values[var] * weights[var]
                                if not self.SCHEMA["--expected_values"][var]["is_joined"]
                                else match_expected_values[var] * weights[var]
                                for var in weighted_vars
                            ]
                        )
                    )
                )

    def update_predicted_aim(self, aims_list: List[dict]) -> List[dict]:
        """Updates predicted and actual data with new obj_team and tba_team data,

        `aims_list`: aims list, same as input to `self.filter_aims_list`

        Returns a list of predicted_aim document dicts.
        """
        updates = []
        obj_team = self.server.db.find("obj_team")
        tba_team = self.server.db.find("tba_team")
        tba_match_data = tba_communicator.tba_request(f"event/{self.server.TBA_EVENT_KEY}/matches")
        filtered_aims_list = self.filter_aims_list(obj_team, tba_team, aims_list)

        finished_matches = []
        # Update every aim
        for aim in filtered_aims_list:
            if aim["match_number"] not in finished_matches and aim["alliance_color"] == "R":
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

                # Calculate match expected values
                match_expected_values = self.calc_match_expected_values(
                    {"R": aim["team_list"], "B": other_aim["team_list"]},
                    {"obj_team": obj_team, "tba_team": tba_team},
                )

                # Add expected values to update
                for action, value in match_expected_values.items():
                    if action.split("_")[-1] == "red":
                        update["_".join(action.split("_")[:-1])] = value
                    elif action.split("_")[-1] == "blue":
                        other_update["_".join(action.split("_")[:-1])] = value
                    else:
                        update[action] = other_update[action] = value

                # Calculate predictions
                for prediction, info in self.REGRESSIONS_SCHEMA["--regressions"].items():
                    update[f"predicted_{prediction}"] = self.predict_value(
                        match_expected_values, prediction, info["model_type"], aim["alliance_color"]
                    )
                    if not info["is_joined"]:
                        other_update[f"predicted_{prediction}"] = self.predict_value(
                            match_expected_values,
                            prediction,
                            info["model_type"],
                            aim["alliance_color"],
                        )
                    # Win chance for blue alliance needs to be the complement of red win chance
                    # This method is a bit hard-coded, needs to be improved
                    # This assumes that all joined variables sum to 1
                    else:
                        other_update[f"predicted_{prediction}"] = (
                            1 - update[f"predicted_{prediction}"]
                        )

                # Calculate actual values
                update.update(self.get_actual_values(aim, tba_match_data))
                other_update.update(self.get_actual_values(other_aim, tba_match_data))

                # Add aim team list
                update["team_numbers"] = aim["team_list"]
                other_update["team_numbers"] = other_aim["team_list"]

                # Add competition code, used in `src/predicted_weights.py`
                update["event_key"] = other_update["event_key"] = utils.TBA_EVENT_KEY

                updates.extend([update, other_update])
                finished_matches.append(aim["match_number"])
        return updates

    def update_playoffs_alliances(self) -> List[dict]:
        """Runs the calculations for predicted values in playoffs matches

        Returns playoffs alliances, a list of dicts of alliances with team numbers and predictions.
        """
        updates = []
        obj_team = self.server.db.find("obj_team")
        tba_team = self.server.db.find("tba_team")
        playoffs_alliances = self.get_playoffs_alliances()

        # Check if empty
        if playoffs_alliances == updates:
            return updates

        for alliance in playoffs_alliances:
            update = alliance

            # Calculate match expected values
            match_expected_values = self.calc_match_expected_values(
                alliance["picks"], {"obj_team": obj_team, "tba_team": tba_team}, "elims"
            )

            # Add expected values to update
            for action, value in match_expected_values.items():
                update[action] = value

            # Calculate predictions
            for prediction, info in self.REGRESSIONS_SCHEMA["--regressions"].items():
                if not info["is_joined"]:
                    update[f"predicted_{prediction}"] = self.predict_value(
                        match_expected_values, prediction, info["model_type"], level="elims"
                    )

            # Add aim team list
            update["team_numbers"] = alliance["picks"]

            # Add competition code, used in `src/predicted_weights.py`
            update["event_key"] = utils.TBA_EVENT_KEY

            updates.append(update)

        return updates

    def run(self):
        "Run the predictions."
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
