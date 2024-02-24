#!/usr/bin/env python3

"""Run TIM calculations dependent on TBA data."""

import copy
from typing import List, Dict, Tuple, Any

from calculations import base_calculations
from data_transfer import tba_communicator
import utils
from server import Server
import logging
import time

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


class TBATIMCalc(base_calculations.BaseCalculations):
    """Runs TBA Tim calculations"""

    SCHEMA = utils.unprefix_schema_dict(utils.read_schema("schema/calc_tba_tim_schema.yml"))["tba"]

    def __init__(self, server):
        """Creates an empty list to add references of calculated tims to"""
        super().__init__(server)
        self.calculated = set([tim["match_number"] for tim in self.server.db.find("tba_tim")])

    def entries_since_last(self) -> List[Dict[str, Any]]:
        """Checks for uncalculated matches, returns the match data

        Pulls match data from the tba endpoint, and cross refrences the match number with the
        match numbers in self.calculated, and will return the match data if it has not been
        calculated (not in self.calculated)
        """
        tba_match_data = tba_communicator.tba_request(f"event/{Server.TBA_EVENT_KEY}/matches")
        not_calculated: List[Dict[str, Any]] = []

        # Go through the matches that it pulled from tba to check if the each
        # team in match has been calculated already
        for match in tba_match_data:
            if match["comp_level"] != "qm" or match.get("score_breakdown") is None:
                continue
            # If we want to run calcs on all data, add all quals matches to the list
            if self.calc_all_data:
                not_calculated.append(match)
            # If we only want to run calcs on new data, check if the reference is already calculated
            elif match["match_number"] not in self.calculated:
                # Add the actual match data to the not_calculated list, to
                # be calculated when called by update_calc_tba_tims
                not_calculated.append(match)

        return not_calculated

    @staticmethod
    def calc_tba_bool(match_data: Dict, alliance: str, filters: Dict) -> bool:
        """Returns a bool representing if match_data meets all filters defined in filters."""
        for key, value in filters.items():
            if match_data["score_breakdown"][alliance][key] != value:
                return False
        return True

    @staticmethod
    def get_robot_number_and_alliance(team_num: str, match_data: Dict) -> Tuple[int, str]:
        """Gets the robot number (e.g. the `1` in initLineRobot1) and alliance color."""
        team_key = f"frc{team_num}"
        for alliance in ["red", "blue"]:
            for i, key in enumerate(match_data["alliances"][alliance]["team_keys"], start=1):
                if team_key == key:
                    return i, alliance
        raise ValueError(f'Team {team_num} not found in match {match_data["match_number"]}')

    @staticmethod
    def get_team_list_from_match(match_data: Dict) -> List[str]:
        """Extracts list of teams that played in the match with data given in match_data."""
        team_list = []
        for alliance in ["red", "blue"]:
            team_list.extend(
                # This fetches the numeric values from the string
                [team[3:] for team in match_data["alliances"][alliance]["team_keys"]]
            )
        return team_list

    @staticmethod
    def calculate_spotlight(match) -> List[str]:
        """Given match data, return a list of teams that were spotlit"""
        spotlit_teams = []
        # splits into each alliance
        for alliance in ["red", "blue"]:
            team_keys = match["alliances"][alliance]["team_keys"]
            match_data = match["score_breakdown"][alliance]
            for i in range(3):
                # check for spotlight
                if (
                    match_data[f"endGameRobot{i+1}"] == "StageCenter"
                    and match_data["micCenterStage"]
                ):
                    spotlit_teams.append(team_keys[i][3:])
                if match_data[f"endGameRobot{i+1}"] == "StageLeft" and match_data["micStageLeft"]:
                    spotlit_teams.append(team_keys[i][3:])
                if match_data[f"endGameRobot{i+1}"] == "StageRight" and match_data["micStageRight"]:
                    spotlit_teams.append(team_keys[i][3:])
        return spotlit_teams

    @staticmethod
    def calculate_driver_stations(match) -> Dict[str, str]:
        "Given match data, return a list for each alliance with each teams driver position"
        blue_team_keys = match["alliances"]["blue"]["team_keys"]
        red_team_keys = match["alliances"]["red"]["team_keys"]

        blue_driver_positions = {}
        blue_driver_positions[blue_team_keys[0][3:]] = "left"
        blue_driver_positions[blue_team_keys[1][3:]] = "center"
        blue_driver_positions[blue_team_keys[2][3:]] = "right"

        red_driver_positions = {}
        red_driver_positions[red_team_keys[0][3:]] = "left"
        red_driver_positions[red_team_keys[1][3:]] = "center"
        red_driver_positions[red_team_keys[2][3:]] = "right"

        # if alliance seperation is needed in the future. (this will slightly break the calculation)
        # driver_stations = {}
        # driver_stations['blue'] = blue_driver_positions
        # driver_stations['red'] = red_driver_positions

        # combines the two to make it easier to search through. One team can't play on both sides so it does not break anything
        blue_driver_positions.update(red_driver_positions)
        return blue_driver_positions

    def calculate_tim(self, team_number: str, match) -> List[Dict[str, Any]]:
        """Given a team number and a match that it's from, calculate that tim"""
        match_number: int = match["match_number"]
        tim = {"team_number": team_number, "match_number": match_number}

        # Check if an important thing like score_breakdown is in the match data
        if match["score_breakdown"] is None:
            log.warning(f"TBA TIM Calculation on {match_number} missing match data")

        robot_number, alliance = self.get_robot_number_and_alliance(team_number, match)
        match_spotlit_teams = self.calculate_spotlight(match)
        driver_stations = self.calculate_driver_stations(match)
        for calculation, tim_requirements in self.SCHEMA.items():
            # calculation is the name of the field, like "mobility" for example
            # tim_requirements is dict of stuff including {"type": "bool"} and something like
            # {"taxiRobot": "Yes"}
            tim_requirements_copy = copy.deepcopy(tim_requirements)

            if tim_requirements["type"] != "bool":
                log.warning(f"Tried to calc bool on {calculation}")

            # type does not need to be in the final data, so we remove it
            # {"type": "bool", "field": "value"} -> {"field": "value"}
            del tim_requirements_copy["type"]

            # Add a number after each field that ends in Robot
            # {"field": "value"} -> {"field1": "value"}
            for field, expected_value in tim_requirements.items():
                if field.endswith("Robot"):
                    del tim_requirements_copy[field]
                    tim_requirements_copy[f"{field}{robot_number}"] = expected_value

            # calculate driver stations
            if calculation == "driver_station":
                tim[calculation] = driver_stations[team_number]
                continue

            # Fun calc_tba_bool for each calculation, and add it to tim
            if isinstance(tim["match_number"], int):
                # since spotlight doesn't have a tim_requirements field

                if calculation == "spotlight":
                    if team_number in match_spotlit_teams:
                        tim[calculation] = True
                    else:
                        tim[calculation] = False
                else:
                    tim[calculation] = self.calc_tba_bool(
                        match,
                        alliance,
                        tim_requirements_copy,
                    )

        return tim

    def run(self):
        """Executes the TBA Team calculations"""
        # Get calc start time
        start_time = time.time()
        # Get the list of matches that have not been calculated, i.e. their
        # reference is not in the self.calculated
        entries = self.entries_since_last()

        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("tba_tim")

        for match in entries:
            for team_number in self.get_team_list_from_match(match):
                # Calculate the tim, getting the team and match from entry
                calculated_tim = self.calculate_tim(team_number, match)

                # Ensure we don't write results from a calculation that errorred
                if calculated_tim is None:
                    continue

                # Add the tim ref to calculated, right after it gets calculated
                self.calculated.add(match["match_number"])

                self.server.db.update_document(
                    "tba_tim",
                    calculated_tim,
                    {
                        "match_number": calculated_tim["match_number"],
                        "team_number": calculated_tim["team_number"],
                    },
                )
        end_time = time.time()
        # Get total calc time
        total_time = end_time - start_time
        # Write total calc time to log
        log.info(f"tba_tims calculation time: {round(total_time, 2)} sec")
