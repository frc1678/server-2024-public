from calculations.predicted_aim import *
import server
from unittest.mock import patch

# takes in _______ and returns/prints predicted scores for the alliance using functions from predicted_aim.py
# 1. take in three teams
# 2. find obj_team data for all three
# 3. use predicted_aim.py functions to find predicted values for an ALLIANCE with the three teams (somehow)
# 4. return a dictionary with predicted_aim values
# 5. print into terminal

# team numbers are strings
def predict_alliance(team1, team2, team3, server, obj_team_data, tba_team_data):
    output = {}
    team_numbers = [team1, team2, team3]
    calc = PredictedAimCalc(server)
    predicted_values = PredictedAimScores()
    # obj_team_data is all the obj team data in server
    # need to run calc_alliance_score first for everything else to work
    output["predicted_score"] = calc.calc_alliance_score(
        predicted_values, obj_team_data, tba_team_data, team_numbers
    )
    output["predicted_auto_score"] = calc.calc_alliance_auto_score(predicted_values)
    output["predicted_stage_score"] = calc.calc_alliance_stage_score(obj_team_data, team_numbers)
    output["predicted_tele_score"] = calc.calc_alliance_tele_score(predicted_values)
    output["predicted_score"] = (
        output["predicted_auto_score"]
        + output["predicted_stage_score"]
        + output["predicted_tele_score"]
    )
    return output


def main():
    with patch("server.Server.ask_calc_all_data", return_value=False):
        server1 = server.Server()
    log.info(
        predict_alliance(
            input("team 1: "),
            input("team 2: "),
            input("team 3: "),
            server1,
            server1.db.find("obj_team"),
            server1.db.find("tba_team"),
        )
    )


if __name__ == "__main__":
    main()
