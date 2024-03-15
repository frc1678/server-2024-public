#!/usr/bin/env python3
"""Calculate subjective team data"""

import utils
import time
import logging
from calculations import base_calculations
from typing import Dict, List

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


class SubjTeamCalcs(base_calculations.BaseCalculations):
    """Runs subjective team calculations"""

    SCHEMA = utils.read_schema("schema/calc_subj_team_schema.yml")

    def __init__(self, server):
        """Overrides watched collections, passes server object"""
        super().__init__(server)
        self.watched_collections = ["subj_tim"]
        self.teams_that_have_competed = set()

    def teams_played_with(self, team: str) -> List[str]:
        """Returns a list of teams that the given team has played with so far, including themselves
        and including repeats"""
        partners = []
        # matches_played is a dictionary where keys are match numbers and values represent alliance color
        matches_played = {}
        for tim in self.server.db.find("subj_tim", {"team_number": team}):
            matches_played.update({tim["match_number"]: tim["alliance_color_is_red"]})
        for match_num, alliance_color in matches_played.items():
            # Find subj_tim data for robots in the same match and alliance as the team
            alliance_data = self.server.db.find(
                "subj_tim", {"match_number": match_num, "alliance_color_is_red": alliance_color}
            )
            partners.extend([tim["team_number"] for tim in alliance_data])
        return partners

    def unadjusted_ability_calcs(self, team: str) -> Dict[str, float]:
        """Retrieves subjective AIM info for the given team and returns a dictionary with
        calculations for that team"""
        calculations = {}
        # self.SCHEMA['data'] tells us which fields we need to put in the database that don't
        # require calculations
        for data_field, type_dict in self.SCHEMA["data"].items():
            type_as_str = type_dict["type"]
            calculations[data_field] = self.STR_TYPES[type_as_str](team)
        # Next, actually run the calculations
        for calc_name, calc_info in self.SCHEMA["unadjusted_calculations"].items():
            collection_name, _, ranking_name = calc_info["requires"][0].partition(".")
            # For calculations such as driver_field_awareness and driver_quickness,
            # we just pull the rankings from the database and average them
            # Lists average each index, ex: [0, 3], [2, 1] -> [1, 2]
            # If there is "ignore" in calc_info, ignore those values
            team_rankings = []
            ignore_filter = lambda data: not ("ignore" in calc_info and data in calc_info["ignore"])
            is_list = calc_info["type"] == "List"
            for tim in self.server.db.find(collection_name, {"team_number": team}):
                tim_value = tim[ranking_name]
                if is_list:
                    team_rankings.append(tim_value)
                elif ignore_filter(tim_value):
                    team_rankings.append(tim_value)
            average_team_rankings = (
                self.avg(team_rankings)
                if not is_list
                else [  # Average each index
                    self.avg(
                        [value[index] for value in team_rankings if ignore_filter(value[index])]
                    )
                    for index in range(len(team_rankings[0]))
                ]
            )
            calculations[calc_name] = average_team_rankings
        return calculations

    def adjusted_ability_calcs(self) -> Dict[str, Dict[int, float]]:
        """Retrieves subjective AIM data for all teams and recalculates adjusted ability scores
        for each team. Recalculating all of them is necessary because ability scores compensate for
        luck of match schedule, so a team's ability score will depend on the unadjusted
        scores for all of their alliance partners"""
        # If no teams have competed yet, there is not point in running the calculation
        if len(self.teams_that_have_competed) == 0:
            return {}

        calculations = {}
        for calc_name, calc_info in self.SCHEMA["component_calculations"].items():
            collection_name, _, unadjusted_calc = calc_info["requires"][0].partition(".")
            # scores is a dictionary of team numbers to rank score
            scores = {}
            for team in self.teams_that_have_competed:
                tim = self.server.db.find(collection_name, {"team_number": team})
                if tim:
                    scores[team] = tim[0][unadjusted_calc]
            # Now scale the scores so they range from 0 to 1, and use those scaled scores to
            # compensate for alliance partners
            # That way, teams that are always paired with good/bad teams won't have unfair rankings
            if calc_info["type"] == "List":
                # Calculate for each index, ex: [0, 1], [2, 3] calculates 0 & 2 together and 1 & 3 together
                for index in range(len(list(scores.values())[0])):
                    self.scale_scores(
                        {
                            team: score[index] for team, score in scores.items()
                        },  # Only the scores at the index
                        calculations,
                        calc_name,
                        index,
                    )
            else:
                self.scale_scores(scores, calculations, calc_name)
        return calculations

    def scale_scores(
        self,
        scores: Dict[str, float],
        calculations: Dict[str, Dict[str, float]],
        calc_name: str,
        index: int = None,
    ) -> None:
        """Calculates scores adjusted for teammate score and scaled from 0 to 1"""
        worst = min(scores.values())
        best = max(scores.values())
        scaled_scores = {
            team: (((score - worst) / (best - worst)) if best - worst != 0 else 0)
            for team, score in scores.items()
        }
        for team, score in scores.items():
            teammate_scaled_scores = [
                scaled_scores[partner] for partner in self.teams_played_with(team)
            ]
            calculations[team] = calculations.get(team, {})
            # If teammates tend to rank low, the team's score is lowered more than if teammates tend to rank high
            if index is None:
                calculations[team][calc_name] = score * self.avg(teammate_scaled_scores)
            elif index == 0:
                calculations[team][calc_name] = [score * self.avg(teammate_scaled_scores)]
            else:
                calculations[team][calc_name].append(score * self.avg(teammate_scaled_scores))

    def calculate_driver_ability(self):
        """Takes a weighted average of all the adjusted component scores to calculate overall driver ability."""
        calculations = {}
        for calc_name, calc_info in self.SCHEMA["averaged_calculations"].items():
            # ability_dict is a dictionary where keys are team numbers
            # and values are driver_ability scores
            ability_dict = {}
            for team in self.teams_that_have_competed:
                # scores is a list of the normalized, adjusted subjective ability scores for the team
                # For example, if they have good quickness and average
                # field awareness, scores might look like [.8, -.3]
                scores = []
                for requirement in calc_info["requires"]:
                    collection_name, _, score_name = requirement.partition(".")
                    scores.append(
                        self.server.db.find(collection_name, {"team_number": team})[0][score_name]
                    )
                # driver_ability is a weighted average of its component scores
                ability_dict[team] = self.avg(scores, calc_info["weights"])
            # Put the driver abilities of all teams in a list
            driver_ability_list = list(ability_dict.values())
            normalized_abilities = dict(
                zip(ability_dict.keys(), self.get_z_scores(driver_ability_list))
            )
            for team, driver_ability in normalized_abilities.items():
                calculations[team] = calculations.get(team, {})
                if calc_name == "defensive_driver_ability":
                    calculations[team][calc_name] = driver_ability + 2
                elif calc_name == "proxy_driver_ability":
                    calculations[team][calc_name] = (driver_ability + 3) ** 2
                else:
                    calculations[team][calc_name] = driver_ability
        return calculations

    def run(self):
        """Gets oplog entries from watched collection and uses that to calculate subjective team
        info, then puts those calculations in the database"""
        # Get calc start time
        start_time = time.time()
        # Adjusted calcs have to be re-run on all teams that have competed
        # because team data changing for one team affects all teams that played with that team
        self.teams_that_have_competed = set()
        for tim in self.server.db.find("subj_tim"):
            self.teams_that_have_competed.add(tim["team_number"])
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("subj_team")
        # See which teams are affected by new subj TIM data
        updated_teams = self.get_updated_teams()
        for team in updated_teams:
            new_calc = self.unadjusted_ability_calcs(team)
            self.server.db.update_document(
                "subj_team", new_calc, {"team_number": new_calc["team_number"]}
            )
        if len(self.teams_that_have_competed) != 0:
            # Now use the new info to recalculate adjusted ability scores
            adjusted_calcs = self.adjusted_ability_calcs()
            for team in self.teams_that_have_competed:
                self.server.db.update_document(
                    "subj_team", adjusted_calcs[team], {"team_number": team}
                )
            # Use the adjusted ability scores to calculate driver ability
            driver_ability_calcs = self.calculate_driver_ability()
            for team in self.teams_that_have_competed:
                self.server.db.update_document(
                    "subj_team", driver_ability_calcs[team], {"team_number": team}
                )
        end_time = time.time()
        # Get total calc time
        total_time = end_time - start_time
        # Write total calc time to log
        log.info(f"subj_team calculation time: {round(total_time, 2)} sec")
