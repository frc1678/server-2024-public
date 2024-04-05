import pandas as pd
import numpy as np
import statsmodels.api as sm
import utils
from data_transfer import tba_communicator as tba

SCHEMA = utils.read_schema("schema/calc_predicted_aim_schema.yml")


def calc_score_weights(pred_aim: pd.DataFrame):
    """Calculates gamepiece weights by running regressions on past data.

    `predicted_aim`: A pandas DataFrame of predicted_aim data containing all values
                    in the `predicted_values` dataclass and actual scores for auto, tele, and stage.
    """
    # Get score action variables
    weights_schema = SCHEMA["--score_weights"]
    auto_vars = weights_schema["auto"]
    tele_vars = weights_schema["tele"]
    endgame_vars = weights_schema["endgame"]
    score_weights = pd.Series(
        {var: 0 for var in auto_vars + tele_vars + endgame_vars}, dtype=np.float64
    )

    # Auto
    auto_model = sm.OLS(pred_aim["actual_score_auto"], pred_aim[auto_vars]).fit()
    for var in auto_model.params.index:
        score_weights[var] = auto_model.params[var]

    # Tele
    tele_model = sm.OLS(pred_aim["actual_score_tele"], pred_aim[tele_vars]).fit()
    for var in tele_model.params.index:
        score_weights[var] = tele_model.params[var]

    # Endgame
    endgame_model = sm.OLS(pred_aim["actual_score_endgame"], pred_aim[endgame_vars]).fit()
    for var in endgame_model.params.index:
        score_weights[var] = endgame_model.params[var]

    # Update weights to JSON file and return
    score_weights.to_json("data/score_weights.json")
    return score_weights


def get_aim_data():
    """NOTE: this function is currently a placeholder and will be worked on after East Bay
    Function to pull aim data from TBA for specified competitions.
    """
