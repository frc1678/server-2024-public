from datetime import datetime

from calculations.base_calculations import BaseCalculations
from data_transfer import tba_communicator
import utils
import time
import logging
from typing import List, Dict, Union

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


class SimPrecisionCalc(BaseCalculations):
    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["unconsolidated_totals"]
        self.sim_schema = utils.read_schema("schema/calc_sim_precision_schema.yml")

    def get_scout_tim_score(
        self, scout: str, match_number: int, required: Dict[str, Dict[str, Union[int, List[str]]]]
    ) -> Union[int, None]:
        """Gets the score for a team in a match reported by a scout.
        required is the dictionary of required datapoints: {weight: value, calculation: [calculations]} from schema
        """
        scout_data = self.server.db.find(
            "unconsolidated_totals", {"match_number": match_number, "scout_name": scout}
        )

        if scout_data == []:
            log.warning(f"No data from Scout {scout} in Match {match_number}")
            return

        scout_document = scout_data[0]
        total_score = 0
        for datapoint, weight in required.items():
            # split using . to get rid of collection name
            collection, datapoint = datapoint.split(".")
            # Check if the collection is valid
            if collection != "unconsolidated_totals":
                log.fatal(
                    f"Getting data from {collection} is not implemented. Only uncosolidated_totals."
                )
                raise NotImplementedError
            total_score += scout_document[datapoint] * weight
        return total_score

    def get_aim_scout_scores(
        self,
        match_number: int,
        alliance_color_is_red: bool,
        required: Dict[str, Dict[str, Union[int, List[str]]]],
    ) -> Dict[str, Dict[str, int]]:
        """Gets the individual TIM scores reported by each scout for an alliance in a match.
        required is the dictionary of required datapoints: {weight: value, calculation: [calculations]} from schema.
        Returns a dictionary where keys are team numbers and values are dictionaries of scout name: tim score.
        """
        scores_per_team = {}
        scout_data = self.server.db.find(
            "unconsolidated_totals",
            {
                "match_number": match_number,
                "alliance_color_is_red": alliance_color_is_red,
            },
        )
        teams = set([document["team_number"] for document in scout_data])
        # Populate dictionary with teams in alliance
        for team in teams:
            scores_per_team[team] = {}
        for document in scout_data:
            scout_tim_score = self.get_scout_tim_score(
                document["scout_name"], match_number, required
            )
            scores_per_team[document["team_number"]].update(
                {document["scout_name"]: scout_tim_score}
            )

        return scores_per_team

    def get_aim_scout_avg_errors(
        self,
        aim_scout_scores: Dict[str, Dict[str, int]],
        tba_aim_score: int,
        match_number: int,
        alliance_color_is_red: bool,
    ):
        """Gets the average error from TBA of each scout's linear combinations in an AIM."""
        if len(aim_scout_scores) != 3:
            log.warning(
                f"Missing {'red' if alliance_color_is_red else 'blue'} alliance scout data for Match {match_number}"
            )
            return {}

        # Get the reported values for each scout
        team1_scouts, team2_scouts, team3_scouts = aim_scout_scores.values()

        all_scout_errors = {}
        for scout1, score1 in team1_scouts.items():
            scout1_errors = all_scout_errors.get(scout1, [])
            for scout2, score2 in team2_scouts.items():
                scout2_errors = all_scout_errors.get(scout2, [])
                for scout3, score3 in team3_scouts.items():
                    scout3_errors = all_scout_errors.get(scout3, [])
                    error = tba_aim_score - (score1 + score2 + score3)
                    scout1_errors.append(error)
                    scout2_errors.append(error)
                    scout3_errors.append(error)
                    all_scout_errors[scout3] = scout3_errors
                all_scout_errors[scout2] = scout2_errors
            all_scout_errors[scout1] = scout1_errors
        scout_avg_errors = {scout: self.avg(errors) for scout, errors in all_scout_errors.items()}
        return scout_avg_errors

    def get_tba_value(
        self,
        tba_match_data: List[dict],
        tba_points: List,
        match_number: int,
        alliance_color_is_red: bool,
    ) -> int:
        """Get the total value for the required datapoints caclculated using tba match data"""
        alliance_color = ["blue", "red"][int(alliance_color_is_red)]

        for match in tba_match_data:
            if match["match_number"] == match_number and match["comp_level"] == "qm":
                tba_match_data = match["score_breakdown"][alliance_color]
        total = 0
        for datapoint in tba_points:
            total += tba_match_data[datapoint]

        return total

    def calc_sim_precision(self, sim, aim_match_errors, aim_match_reported_values, tba_aim_scores):
        """Calculates the average difference between errors where the scout was part of the combination, and errors where the scout wasn't.
        sim is a scout-in-match document."""
        calculations = {}
        for calculation, schema in self.sim_schema["calculations"].items():
            required = schema["requires"]

            # Value reported for datapoint by a specific scout for a robot in a match
            scout_reported_value = self.get_scout_tim_score(
                sim["scout_name"], sim["match_number"], required
            )

            # Use match number, calculation type, and alliance color to query for the necessary data
            tba_aim_score = tba_aim_scores[sim["match_number"]][calculation][
                sim["alliance_color_is_red"]
            ]
            aim_scout_errors = aim_match_errors[sim["match_number"]][calculation][
                sim["alliance_color_is_red"]
            ]
            aim_scouts_reported_values = aim_match_reported_values[sim["match_number"]][
                calculation
            ][sim["alliance_color_is_red"]]

            if aim_scout_errors == {}:
                return {}

            # Find alliance partners
            count = 0
            for team, aim_data in aim_scouts_reported_values.items():
                # Excludes the scout's own team
                if team == sim["team_number"]:
                    continue
                if count == 0:
                    ally1_scouts = aim_data
                    count += 1
                else:
                    ally2_scouts = aim_data

            # Calculate the sim precision using the avg errors of the scout vs the avg error of each scout
            sim_errors = []
            for scout1, ally1_score in ally1_scouts.items():
                for scout2, ally2_score in ally2_scouts.items():
                    current_combo_error = tba_aim_score - (
                        scout_reported_value + ally1_score + ally2_score
                    )
                    # Each aim_scout_error value represents the average error of 3 scouts, so divide by 3
                    average_partner_error = (
                        aim_scout_errors[scout1] + aim_scout_errors[scout2]
                    ) / 3
                    error_difference = average_partner_error - current_combo_error
                    sim_errors.append(error_difference)
            calculations[calculation] = self.avg(sim_errors)
        return calculations

    def update_sim_precision_calcs(self, unconsolidated_sims):
        """Creates scout-in-match precision updates"""
        tba_match_data: List[dict] = tba_communicator.tba_request(
            f"event/{utils.TBA_EVENT_KEY}/matches"
        )
        # When we're running server at competition, we have to wait until TBA updates
        # match data, so we get the latest TBA match and our latest match
        latest_match = max([s["match_number"] for s in unconsolidated_sims] + [0])
        latest_tba_match = max(
            [
                t["match_number"]
                for t in tba_match_data
                if t["score_breakdown"] is not None and t["comp_level"] == "qm"
            ]
            + [0]
        )
        updates = []
        # Create dicts for shared data between scouts
        tba_aim_scores = {}
        aim_match_errors = {}
        aim_match_reported_values = {}
        # Iterate up to either the latest tba match or match where we have data (To avoid crashing)
        for match_number in range(1, min(latest_match, latest_tba_match) + 1):
            # Create match_number keys
            tba_aim_scores[match_number] = {}
            aim_match_errors[match_number] = {}
            aim_match_reported_values[match_number] = {}
            # Calculate data for each calculation
            for calculation, schema in self.sim_schema["calculations"].items():
                required = schema["requires"]
                tba_points = schema["tba_datapoints"]

                # Get the scores from TBA
                red_tba_aim_score = self.get_tba_value(
                    tba_match_data, tba_points, match_number, True
                )

                blue_tba_aim_score = self.get_tba_value(
                    tba_match_data, tba_points, match_number, False
                )

                # Get the scores of all scouts in a match
                red_aim_scouts_reported_values = self.get_aim_scout_scores(
                    match_number, True, required
                )

                blue_aim_scouts_reported_values = self.get_aim_scout_scores(
                    match_number, False, required
                )

                # Get the average errors of all scouts in a match
                red_aim_scout_errors = self.get_aim_scout_avg_errors(
                    red_aim_scouts_reported_values,
                    red_tba_aim_score,
                    match_number,
                    True,
                )

                blue_aim_scout_errors = self.get_aim_scout_avg_errors(
                    blue_aim_scouts_reported_values,
                    blue_tba_aim_score,
                    match_number,
                    False,
                )

                # Update to their respective dictionaries
                # True is for red alliance and False is for blue alliance
                tba_aim_scores[match_number][calculation] = {
                    True: red_tba_aim_score,
                    False: blue_tba_aim_score,
                }
                aim_match_errors[match_number][calculation] = {
                    True: red_aim_scout_errors,
                    False: blue_aim_scout_errors,
                }
                aim_match_reported_values[match_number][calculation] = {
                    True: red_aim_scouts_reported_values,
                    False: blue_aim_scouts_reported_values,
                }

        for sim in unconsolidated_sims:
            sim_data = self.server.db.find("unconsolidated_totals", sim)[0]
            if sim_data["match_number"] > latest_tba_match:
                continue
            update = {
                "scout_name": sim_data["scout_name"],
                "match_number": sim_data["match_number"],
                "team_number": sim_data["team_number"],
                "alliance_color_is_red": sim_data["alliance_color_is_red"],
            }
            for match in tba_match_data:
                if (
                    match["match_number"] == sim_data["match_number"]
                    and match["comp_level"] == "qm"
                ):
                    # Convert match timestamp from Unix time (on TBA) to human-readable
                    update["timestamp"] = datetime.fromtimestamp(match["actual_time"])
                    break
            else:
                continue
            if (
                sim_precision := self.calc_sim_precision(
                    sim_data, aim_match_errors, aim_match_reported_values, tba_aim_scores
                )
            ) != {}:
                update.update(sim_precision)
            updates.append(update)
        return updates

    def run(self):

        # Get calc start time
        start_time = time.time()
        entries = self.entries_since_last()
        sims = []
        for entry in entries:
            sims.append(
                {
                    "scout_name": entry["o"]["scout_name"],
                    "match_number": entry["o"]["match_number"],
                }
            )
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("sim_precision")

        for update in self.update_sim_precision_calcs(sims):
            self.server.db.update_document(
                "sim_precision",
                update,
                {
                    "scout_name": update["scout_name"],
                    "match_number": update["match_number"],
                    "alliance_color_is_red": update["alliance_color_is_red"],
                },
            )
        end_time = time.time()
        # Get total calc time
        total_time = end_time - start_time
        # Write total calc time to log
        log.info(f"sim_precision calculation time: {round(total_time, 2)} sec")
        log.info(f"SIM_PRECISON_RAN")
