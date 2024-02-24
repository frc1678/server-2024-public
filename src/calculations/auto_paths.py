#!/usr/bin/env python3

"""
Holds functions used to determine auto scoring and paths

1. Collect all existing pims
2. Group by team, start position, and scoring
3. Calculate success and score info for each unique auto
4. Add unique paths to database
"""

from typing import List
from calculations.base_calculations import BaseCalculations
import logging
import console
import utils
import time

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


class AutoPathCalc(BaseCalculations):
    schema = utils.read_schema("schema/calc_auto_paths.yml")

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["auto_pim"]

    def group_auto_paths(self, pim: dict, calculated_paths: List[dict]) -> dict:
        """
        Creates an auto path given a pim and a list of existing paths.
        Checks if the new pim already has an existing path or if it's a new path.
        """
        # Find all current auto paths with this team number and start position
        current_documents: List[dict] = self.server.db.find(
            "auto_paths",
            {"team_number": pim["team_number"], "start_position": pim["start_position"]},
        )
        # Add the current calculated_tims into current documents (because these tims aren't in server yet)
        current_documents.extend(
            [
                calculated_path
                for calculated_path in calculated_paths
                if (
                    calculated_path["team_number"] == pim["team_number"]
                    and calculated_path["start_position"] == pim["start_position"]
                )
            ]
        )

        path = {"team_number": pim["team_number"]}

        # Finy any matching paths
        for document in current_documents:
            # Checks to see if it's the same path
            if self.is_same_path(pim, document):
                # Set path values to pim
                for field in self.schema["--path_groups"]["exact_match"]:
                    # Don't update if failed score unless old path doesn't have any info there
                    if "fail" not in str(pim[field]) or document[field] == "none":
                        path[field] = pim[field]
                    else:
                        path[field] = document[field]

                # Add number of score successes
                for new_datapoint, count_datapoint in self.schema["path_increment"].items():
                    # Must have scored to increment
                    for name, values in count_datapoint.items():
                        if name != "type":
                            if pim[name] in values:
                                path[new_datapoint] = document[new_datapoint] + 1
                            else:
                                path[new_datapoint] = document[new_datapoint]

                # Increment all information
                path["num_matches_ran"] = document["num_matches_ran"] + 1
                path["match_numbers_played"] = [pim["match_number"]]
                path["match_numbers_played"].extend(document["match_numbers_played"])
                path["path_number"] = document["path_number"]
                break
        else:
            # If there are no matching documents, that means this is a new auto path
            path["num_matches_ran"] = 1
            path["path_number"] = len(current_documents) + 1
            path["match_numbers_played"] = [pim["match_number"]]
            for field in self.schema["--path_groups"]["exact_match"]:
                path[field] = pim[field]

            # Start at 1 for each incremented datapoint if it a success, else a 0
            for new_datapoint, count_datapoint in self.schema["path_increment"].items():
                # All conditions must be true to increment
                for name, values in count_datapoint.items():
                    if name != "type":
                        if pim[name] in values:
                            path[new_datapoint] = 1
                        else:
                            path[new_datapoint] = 0
        return path

    def is_same_path(self, pim: dict, document: dict) -> bool:
        """Finds if the tim path is the same as the document path"""
        # All exact path_groups in schema must have the same value
        for datapoint in self.schema["--path_groups"]["exact_match"]:
            # If score was fail, count it as the same
            if (
                pim[datapoint] != document[datapoint]
                and "fail" not in str(pim[datapoint])
                and "fail" not in str(document[datapoint])
            ):
                return False
        return True

    def update_auto_pims(self, path: dict) -> None:
        """Updates existing auto pims with incremented path number and num matches ran"""
        update = {"path_number": path["path_number"], "num_matches_ran": path["num_matches_ran"]}
        query = {
            "match_number": {"$in": path["match_numbers_played"]},
            "team_number": path["team_number"],
            "start_position": path["start_position"],
        }
        self.server.db.update_many("auto_pim", update, query)

    def is_updated_path(self, new_path, old_path):
        "Checks if new_path is an updated version of old_path. Used in calculate_auto_paths() below."
        # Check if old path is a subset of new path
        if new_path["team_number"] == old_path["team_number"]:
            if set(old_path["match_numbers_played"]).issubset(
                set(new_path["match_numbers_played"])
            ):
                return True
        return False

    def calculate_auto_paths(self, empty_pims: List[dict]) -> List[dict]:
        """Calculates auto data for the given empty pims, which looks like
        [{"team_number": "1678", "match_number": 42}, {"team_number": "1706", "match_number": 56}, ...]"""
        calculated_paths = []
        for pim in empty_pims:
            auto_pims: List[dict] = self.server.db.find("auto_pim", pim)
            if len(auto_pims) != 1:
                log.error(f"Auto_paths: Multiple pims found for {pim}")

            path = self.group_auto_paths(auto_pims[0], calculated_paths)
            # Check to see if an outdated version of the path is in calculated_paths and remove it
            for calculated_path in calculated_paths:
                if self.is_updated_path(path, calculated_path):
                    calculated_paths.remove(calculated_path)
            calculated_paths.append(path)

        for path in calculated_paths:
            self.update_auto_pims(path)
        return calculated_paths

    def run(self):
        """Executes the auto_path calculations"""
        # Get calc start time
        start_time = time.time()
        # Get oplog entries
        empty_pims = []

        # Check if changes need to be made to teams
        if entries := self.entries_since_last():
            for entry in entries:
                if "team_number" not in entry["o"].keys():
                    continue
                # Check that the team is in the team list, ignore team if not in teams list
                team_num = entry["o"]["team_number"]
                if team_num not in self.teams_list:
                    log.warning(f"auto_paths: team number {team_num} is not in teams list")
                    continue

                # Make pims list
                empty_pims.append(
                    {
                        "team_number": team_num,
                        "match_number": entry["o"]["match_number"],
                    }
                )

        # Filter duplicate pims
        unique_empty_pims = []
        for pim in empty_pims:
            if pim not in unique_empty_pims:
                unique_empty_pims.append(pim)

        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("auto_paths")

        # Calculate data
        updates = self.calculate_auto_paths(unique_empty_pims)

        # Upload data to MongoDB
        for update in updates:
            if update != {}:
                self.server.db.update_document(
                    "auto_paths",
                    update,
                    {
                        "team_number": update["team_number"],
                        "start_position": update["start_position"],
                        "path_number": update["path_number"],
                    },
                )
        end_time = time.time()
        # Get total calc time
        total_time = end_time - start_time
        # Write total calc time to log
        log.info(f"auto_pims calculation time: {round(total_time, 2)} sec")
