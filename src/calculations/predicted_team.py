#!/usr/bin/env python3
"""Makes predictive calculations for teams in a competition."""

import utils
from data_transfer import tba_communicator
from calculations.base_calculations import BaseCalculations
import logging
import time

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


class PredictedTeamCalc(BaseCalculations):
    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["predicted_aim"]

    def calculate_current_values(self, ranking_data, team_number):
        for team_data in ranking_data:
            # TBA return team numbers as a string, eg. 'frc1678'. This drops 'frc'.
            if team_number == team_data["team_key"][3:]:
                current_values = {}
                current_values["current_rank"] = team_data["rank"]
                current_values["current_rps"] = team_data["extra_stats"][0]
                current_values["matches_played"] = team_data["matches_played"]
                if team_data["matches_played"] > 0:
                    current_values["current_avg_rps"] = (
                        team_data["extra_stats"][0] / team_data["matches_played"]
                    )
                else:
                    current_values["current_avg_rps"] = 0
                return current_values

    def calculate_predicted_alliance_rps(self, predicted_aims):
        predicted_alliance_rps = {}
        match_list = set([aim["match_number"] for aim in predicted_aims])
        for match in match_list:
            aims_in_match = [aim for aim in predicted_aims if aim["match_number"] == match]
            # set match to empty dict to avoid key error
            predicted_alliance_rps[match] = {}
            if len(aims_in_match) < 2:
                log.warning(f"Incomplete AIM data for Match {match}")
                continue
            for aim in range(2):
                # if match has data use actual rps from match, else use predicted rps
                if aims_in_match[aim]["has_actual_data"]:
                    rps = aims_in_match[aim]["actual_rp1"] + aims_in_match[aim]["actual_rp2"]
                    # (aim + 1) % 2 alternates between 0 and 1 to represent opposing alliance
                    if (
                        aims_in_match[aim]["actual_score"]
                        > aims_in_match[(aim + 1) % 2]["actual_score"]
                    ):
                        rps += 2
                    elif (
                        aims_in_match[aim]["actual_score"]
                        == aims_in_match[(aim + 1) % 2]["actual_score"]
                    ):
                        rps += 1
                    else:
                        rps += 0
                    alliance_color = "R" if aims_in_match[aim]["alliance_color_is_red"] else "B"
                    predicted_alliance_rps[match][alliance_color] = rps
                else:
                    rps = aims_in_match[aim]["predicted_rp1"] + aims_in_match[aim]["predicted_rp2"]
                    # (aim + 1) % 2 alternates between 0 and 1 to represent opposing alliance
                    if (
                        aims_in_match[aim]["predicted_score_constant"]
                        > aims_in_match[(aim + 1) % 2]["predicted_score_constant"]
                    ):
                        rps += 2
                    elif (
                        aims_in_match[aim]["predicted_score_constant"]
                        == aims_in_match[(aim + 1) % 2]["predicted_score_constant"]
                    ):
                        rps += 1
                    else:
                        rps += 0
                    alliance_color = "R" if aims_in_match[aim]["alliance_color_is_red"] else "B"
                    predicted_alliance_rps[match][alliance_color] = rps

        return predicted_alliance_rps

    def calculate_predicted_team_rps(self, team_number, aim_list, predicted_alliance_rps):
        predicted_rps = 0
        for aim in aim_list:
            if team_number in aim["team_list"]:
                if aim["match_number"] not in predicted_alliance_rps.keys():
                    log.warning(f'Missing predicted RPs for Match {aim["match_number"]}')
                    continue
                if aim["alliance_color"] not in predicted_alliance_rps[aim["match_number"]].keys():
                    log.warning(
                        f'Missing predicted RPs for Alliance {aim["alliance_color"]} in Match {aim["match_number"]}'
                    )
                    continue
                predicted_rps += predicted_alliance_rps[aim["match_number"]][aim["alliance_color"]]
        return predicted_rps

    def calculate_predicted_ranks(self, updates, aim_list, ranking_data):
        predicted_rps = {update["team_number"]: update["predicted_rps"] for update in updates}

        # stores teams that have finished all their scheduled matches. stores the team and their finishing
        # rank. like {1678: 2}
        finished_teams = {}
        for team in predicted_rps.keys():
            current_team_data = self.calculate_current_values(ranking_data, team)
            scheduled_matches = 0
            for aim in aim_list:
                if team in aim["team_list"]:
                    scheduled_matches += 1
            if scheduled_matches > 0:
                predicted_rps[team] = predicted_rps[team] / scheduled_matches
            else:
                predicted_rps[team] = 0
            if current_team_data != None:
                # adds team to finished teams if their matches played equals their scheduled matches
                if current_team_data["matches_played"] == scheduled_matches:
                    finished_teams[team] = current_team_data["current_rank"]

        predicted_ranks = sorted(predicted_rps.keys(), key=lambda x: predicted_rps[x], reverse=True)

        for num, update in enumerate(updates):
            rank = predicted_ranks.index(update["team_number"]) + 1
            updates[num]["predicted_rank"] = rank
            # if the team has finished, use their finished rank instead of a predicted one
            if current_team_data != None:
                if updates[num]["team_number"] in finished_teams:
                    updates[num]["predicted_rank"] = updates[num]["current_rank"]

        return updates

    def update_predicted_team(self, predicted_aim):
        updates = []
        ranking_data = tba_communicator.tba_request(f"event/{self.server.TBA_EVENT_KEY}/rankings")[
            "rankings"
        ]
        predicted_alliance_rps = self.calculate_predicted_alliance_rps(predicted_aim)
        teams = self.get_teams_list()
        aim_list = self.get_aim_list()
        for team in teams:
            update = {"team_number": team}
            current_values = self.calculate_current_values(ranking_data, team)
            if current_values:
                update.update(current_values)

            predicted_rps = self.calculate_predicted_team_rps(
                team, aim_list, predicted_alliance_rps
            )
            update["predicted_rps"] = predicted_rps
            updates.append(update)
        final_updates = self.calculate_predicted_ranks(updates, aim_list, ranking_data)

        return final_updates

    def run(self):
        # Get calc start time
        start_time = time.time()
        # Get oplog entries
        entries = self.entries_since_last()
        if entries:
            self.server.db.delete_data("predicted_team")
            predicted_aim = self.server.db.find("predicted_aim")
            self.server.db.insert_documents(
                "predicted_team", self.update_predicted_team(predicted_aim)
            )
        self.update_timestamp()
        end_time = time.time()
        # Get total calc time
        total_time = end_time - start_time
        # Write total calc time to log
        log.info(f"predicted_team calculation time: {round(total_time, 2)} sec")
