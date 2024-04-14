import pandas as pd
import numpy as np
import statsmodels.api as sm
import utils
from unittest.mock import patch
import server
from calculations import predicted_aim
from data_transfer import tba_communicator as tba
from typing import Union
import logging

SCHEMA = utils.read_schema("schema/calc_predicted_weights_schema.yml")

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)

with patch("server.Server.ask_calc_all_data", return_value=False):
    test_server = server.Server()
predictions = predicted_aim.PredictedAimCalc(test_server)
log.info("Finished setting up predicted_aim file.")


def calc_predicted_weights(pred_aim: pd.DataFrame, write=False) -> Union[dict, None]:
    """Calculates action weights by running regressions on past data.

    `predicted_aim`: A pandas DataFrame of predicted_aim data containing all values
                    in the `--expectedinfo["values"]` section in schema and actual values.
    `write`: if `True`, writes results to `data/predicted_weights.json`/

    Returns a dict containing predicted weights.
    """
    pred_aim = pred_aim[pred_aim["has_actual_data"]]
    model_types = {"linear": sm.OLS, "logistic": sm.Logit}

    # Get score action variables
    predicted_weights = {mode: dict() for mode in SCHEMA["--regressions"].keys()}

    for prediction, attrs in SCHEMA["--regressions"].items():
        # Make sure variables are ints or floats
        if pred_aim[attrs["dep"]].dtype != np.int64 or pred_aim[attrs["dep"]].dtype != np.float64:
            pred_aim[attrs["dep"]] = pred_aim[attrs["dep"]].astype(np.int64)

        if not attrs["is_joined"]:
            # Run regression
            model = model_types[attrs["model_type"]](
                pred_aim[attrs["dep"]], pred_aim[attrs["indep"]]
            ).fit()
        # Joined variable weights are calculated separately since they require both alliances' data
        # We just take the red alliance's data since the match expected values in each document already contain the joined variables.
        else:
            joined_pred_aim = pred_aim[pred_aim["alliance_color_is_red"]]

            # Run regression
            model = model_types[attrs["model_type"]](
                joined_pred_aim[attrs["dep"]], joined_pred_aim[attrs["indep"]]
            ).fit()

        # Get weights from `params`
        for var in model.params.index:
            predicted_weights[prediction][var] = model.params[var]

    # Write weights to JSON
    if write:
        pd.Series(predicted_weights).to_json("data/predicted_weights.json")

    return predicted_weights


def get_tba_aim_data(event_keys: list) -> pd.DataFrame:
    """NOTE: this function needs to be improved; although it gets the job done and runs rather quickly, code quality is not top tier.
    Function to pull aim data from TBA for specified competitions.

    `event_keys`: list of TBA event keys, e.g. ["2024casj", "2024cada", "2024cabe"]

    Returns an AIM data DataFrame in the same format as a predicted_aim document (without the predictions).
    """
    raw_aim_data = []

    for event_key in event_keys:
        log.info(f"Pulling TBA data for {event_key}...")
        tba_data = tba.tba_request(f"event/{event_key}/matches", event_key)

        for match in tba_data:
            if match["score_breakdown"] is None:
                continue
            match_values = {"red": dict(), "blue": dict()}

            # Get "match values" datapoints listed in schema
            for color in ["red", "blue"]:
                match_values[color]["match_number"] = match["match_number"]
                match_values[color]["team_numbers"] = list(
                    map(lambda team_str: team_str[3:], match["alliances"][color]["team_keys"])
                )
                match_values[color]["alliance_color_is_red"] = color == "red"
                match_values[color]["won_match"] = match["winning_alliance"] == color
                match_values[color]["event_key"] = event_key
                match_values[color]["has_actual_data"] = True

                for var, info in SCHEMA["--match_values"].items():
                    if not info["is_joined"]:
                        if var[0] == "_":
                            name = f"{var}_{color}"
                        else:
                            name = var
                        match_values[color][name] = predictions.calc_variable(
                            match["score_breakdown"][color],
                            info["how"],
                            info["from"],
                            info.get("values", None),
                        )

            # Combine red and blue match values
            combined_values = dict()
            base_values = {"red": dict(), "blue": dict()}
            for color in ["red", "blue"]:
                for datapoint, value in match_values[color].items():
                    if datapoint[0] == "_":
                        combined_values[datapoint] = value
                    else:
                        base_values[color][datapoint] = value

            # Consolidate match value dicts
            for color in ["red", "blue"]:
                base_values[color].update(combined_values)
                match_values[color] = base_values[color]

                # Calculated joined variables
                for var, info in SCHEMA["--match_values"].items():
                    if info["is_joined"]:
                        match_values[color][var] = predictions.calc_variable(
                            match_values[color], info["how"], info["from"], info.get("values", None)
                        )

                # Remove _red and _blue suffixes
                to_delete = []
                to_add = {}
                for var, value in match_values[color].items():
                    if var[0] == "_":
                        if var.split("_")[-1] == color:
                            to_add["_".join(var.split("_")[:-1])] = value
                            to_delete.append(var)
                        elif var.split("_")[-1] in ["red", "blue"]:
                            to_delete.append(var)
                for var in to_delete:
                    del match_values[color][var]
                for var, value in to_add.items():
                    match_values[color][var] = value

            raw_aim_data.extend([match_values["red"], match_values["blue"]])
        log.info(f"Finished pulling data from {event_key}.")
    return pd.DataFrame(raw_aim_data)
