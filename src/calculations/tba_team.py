#!/usr/bin/env python3

"""Runs team calculations dependent on TBA data"""

from typing import Dict, List
from calculations import base_calculations
import utils
from server import Server
from data_transfer import tba_communicator
import numpy as np
import numpy.linalg as nl
from cc import cc, CCEvent
import logging
import time

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


class TBATeamCalc(base_calculations.BaseCalculations):
    """Runs TBA Team calculations"""

    # Get the last section of each entry (so foo.bar.baz becomes baz)
    SCHEMA = utils.unprefix_schema_dict(utils.read_schema("schema/calc_tba_team_schema.yml"))

    def __init__(self, server):
        """Overrides watched collections, passes server object"""
        super().__init__(server)
        self.watched_collections = ["obj_tim", "tba_tim"]

    def tim_counts(self, obj_tims, tba_tims):
        """Gets the counts for each schema entry for the given tims"""
        matches = {}
        # Split tims by match for each team and combine TBA and scouted data
        for tim in obj_tims + tba_tims:
            if tim["match_number"] in matches:
                matches[tim["match_number"]].update(tim)
            else:
                matches[tim["match_number"]] = tim
        lfm = sorted(matches, key=lambda tim: matches[tim]["match_number"])[-4:]
        out = {}
        for name, keys in self.SCHEMA["counts"].items():
            match_count = 0
            count = 0
            schema_entry = keys["tim_fields"]
            for match in matches.values():
                match_count += 1
                # Check for TBA TIM and objective TIM fields in the match
                # Skip match if either field is missing to avoid inaccurate data
                if not ("leave" in match):
                    continue
                for key, value in schema_entry.items():
                    # Handle `not` field
                    if isinstance(value, dict) and "not" in value:
                        # Avoid crashing if tim is missing a value by using `.get` and setting the
                        # default such that if `name` is not in the TIM, then `.get` will return the
                        # value that should not be True, and the loop will `break`
                        if match.get(key, value["not"]) == value["not"]:
                            break
                    else:
                        # Similarly to the previous case, use `.get` to avoid crashing. However, here,
                        # the default value is set to be the opposite of the boolean representation,
                        # such that it will never equal the target value
                        if match.get(key, not value) != value:
                            break
                else:
                    # `for` loop exited normally, so all values matched what they are supposed to, so
                    # the `count` should be incremented

                    # For lfms, check if the match is in the last four matches
                    if "lfm" in name:
                        if match["match_number"] in lfm:
                            count += 1
                    else:
                        count += 1

            out[name] = count
            out["leave_success_rate"] = out["leave_successes"] / (match_count)
        return out

    def calculate_cc(self, cc_type, precision: int = 2) -> Dict[str, float]:
        """
        Calculates the amount of foul/link points each team contributes.

        Calculated contribution (a.k.a. OPR) is a method of estimating the amount of something a team contributes to an alliance.

        It uses a numpy matrix and calculates a least squares solution for each team.

        See Also
        ---------
        TBA Blog post discussing OPR https://blog.thebluealliance.com/2017/10/05/the-math-behind-opr-an-introduction/
        """
        matches_endpoint = f"event/{Server.TBA_EVENT_KEY}/matches"
        matches_resp = self.server.db.get_tba_cache(matches_endpoint)
        if matches_resp is None:
            matches_resp = {"data": tba_communicator.tba_request(matches_endpoint)}
        tba_matches = matches_resp.get("data", [])
        cc_aims: List[CCEvent] = []
        if cc_type == "foul":
            # For each AIM, add the foul points for the other alliance in a dictionary
            # with the team numbers and foul points contributed
            for match in tba_matches:
                if match.get("score_breakdown", None) is None:
                    continue
                cc_aims.append(
                    {
                        "parties": utils.get_teams_in_match(match, "red"),
                        "value": match["score_breakdown"]["blue"]["foulPoints"],
                    }
                )
                cc_aims.append(
                    {
                        "parties": utils.get_teams_in_match(match, "blue"),
                        "value": match["score_breakdown"]["red"]["foulPoints"],
                    }
                )
        solved = cc(cc_aims)
        return solved

    def update_team_calcs(self, teams: list) -> list:
        """Returns updates to team calculations based on refs"""

        teams_api_endpoint = f"event/{Server.TBA_EVENT_KEY}/teams/simple"
        team_request_output = self.server.db.get_tba_cache(teams_api_endpoint)
        if team_request_output is None:
            team_request_output = {"data": tba_communicator.tba_request(teams_api_endpoint)}
        team_request_output = team_request_output.get("data", [])
        team_names = {str(team["team_number"]): team["nickname"] for team in team_request_output}

        tba_team_updates = {}

        foul_ccs = self.calculate_cc(cc_type="foul")
        link_ccs = self.calculate_cc(cc_type="link")
        for team in teams:
            # Load team data from database
            obj_tims = self.server.db.find("obj_tim", {"team_number": team})
            tba_tims = self.server.db.find("tba_tim", {"team_number": team})
            # Because of database structure, returns as a list
            team_data = self.tim_counts(obj_tims, tba_tims)
            team_data["team_number"] = team
            # Add foul_cc and link cc
            if team in foul_ccs:
                team_data["foul_cc"] = foul_ccs[team]
            if team in link_ccs:
                team_data["link_cc"] = link_ccs[team]
            # Load team names
            if team in team_names:
                team_data["team_name"] = team_names[team]
            else:
                # Set team name to "UNKNOWN NAME" if the team is not already in the database
                # If the team is, it is assumed that the name in the database will be more accurate
                if not self.server.db.find("tba_team", {"team_number": team}):
                    team_data["team_name"] = "UNKNOWN NAME"
                # Warn that the team is not in the team list for event if there is team data
                if team_names:
                    log.warning(f"Team {team} not found in team list from TBA")

            tba_team_updates[team] = team_data
        # Add remaining regression results as regression can change for every team, so data must be
        # updated for every team
        return list(tba_team_updates.values())

    def run(self):
        """Executes the TBA Team calculations"""
        # Get calc start time
        start_time = time.time()
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("tba_team")
        for update in self.update_team_calcs(self.get_updated_teams()):
            self.server.db.update_document(
                "tba_team", update, {"team_number": update["team_number"]}
            )
        end_time = time.time()
        # Get total calc time
        total_time = end_time - start_time
        # Write total calc time to log
        log.info(f"tba_team calculation time: {round(total_time, 2)} sec")
