import pandas as pd
import numpy as np
import statsmodels.api as sm
import utils
from unittest.mock import patch
import server
from calculations import predicted_aim
from data_transfer import tba_communicator as tba
from typing import Union

SCHEMA = utils.read_schema("schema/calc_predicted_aim_schema.yml")


def calc_predicted_weights(pred_aim: pd.DataFrame, write=False) -> Union[dict, None]:
    """Calculates action weights by running regressions on past data.

    `predicted_aim`: A pandas DataFrame of predicted_aim data containing all values
                    in the `--expectedinfo["values"]` section in schema and actual values.
    `write`: if `True`, writes results to `data/predicted_weights.json`/

    If `write=True`, returns a dict containing predicted weights.
    """
    pred_aim = pred_aim[pred_aim["has_actual_data"]]

    # Get score action variables
    predicted_weights = {mode: dict() for mode in SCHEMA["--regressions"].keys()}

    for mode, attrs in SCHEMA["--regressions"].items():
        # Run linear regression
        if not attrs["is_joined"]:
            model = sm.OLS(pred_aim[attrs["dep"]], sm.add_constant(pred_aim[attrs["indep"]])).fit()
        # Joined variable weights are calculated separately since they require both alliances' data
        # We just take the red alliance's data since the match expected values in each document already contain both alliances' data.
        else:
            joined_pred_aim = pred_aim[pred_aim["alliance_color_is_red"]]

            # Run logistic regression
            model = sm.Logit(
                joined_pred_aim[attrs["dep"]], sm.add_constant(joined_pred_aim[attrs["indep"]])
            ).fit()

        # Get weights from `params`
        for var in model.params.index:
            predicted_weights[mode][var] = model.params[var]

    # Write weights to JSON
    if write:
        pd.Series(predicted_weights).to_json("data/predicted_weights.json")

    return predicted_weights


def get_aim_data():
    """NOTE: this function is currently a placeholder and will be worked on after East Bay
    Function to pull aim data from TBA for specified competitions.
    """
