#!/usr/bin/env python3

"""Holds functions used to determine auto scoring and paths"""

from typing import List
from calculations.base_calculations import BaseCalculations
import logging
import utils

log = logging.getLogger(__name__)


class AutoPathCalc(BaseCalculations):
    schema = utils.read_schema("schema/calc_auto_paths.yml")

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["auto_pim"]

    def group_auto_paths(self, pim: dict, calculated_paths: List[dict]) -> dict:
        """Compares auto path with other auto paths at the same start position"""
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

        path = {"team_number": pim["team_number"], "start_position": pim["start_position"]}

        for document in current_documents:
            # Checks to see if it's the same path
            if self.is_same_path(pim, document):
                for field in self.schema["--path_groups"]["exact"]:
                    path[field] = pim[field]
                resets = set()  # Datapoints that need to be reset from getting new maxes
                for field, info in self.schema["path_max"].items():
                    # The max is the one with the highest index in the 'order'
                    if info["order"].index(pim[info["datapoint"]]) > info["order"].index(
                        document[field]
                    ):
                        # There is a new max
                        path[field] = pim[info["datapoint"]]
                        # Adds the 'reset' datapoint to be reset back to 0 later (before incrementing)
                        if "reset" in info:
                            resets.add(info["reset"])
                    else:
                        # Keep the same max
                        path[field] = document[field]
                for datapoint, conditions in self.schema["path_increment"].items():
                    # All conditions must be true to increment
                    for field, condition in conditions["conditions"].items():
                        for con in condition:
                            # Values starting with '-' are other datapoints (usually current max so use 'update' data)
                            c = [(i if i[0] != "-" else path[i[1:]]) for i in con]
                            if pim[field] not in c:
                                # Condition is false
                                if datapoint in resets:
                                    # Reset the datapoint if needed
                                    path[datapoint] = 0
                                else:
                                    path[datapoint] = document[datapoint]
                                break
                        else:
                            # All was correct, check next con
                            continue
                        # Condition is false
                        break
                    else:
                        # All conditions are true, increment by one
                        if datapoint in resets:
                            path[datapoint] = 1
                        else:
                            path[datapoint] = 1 + document[datapoint]
                # Because of a lack of subjective data sometimes (usually on the 2nd day), we sometimes do not know the piece
                # that was picked up, but it could still be the same auto path, so we must ignore checking it
                # This code makes sure we don't override values to None when it is the same path
                for field, replace in self.schema["--possible_null"].items():
                    if pim[field] is None and replace in document:
                        pim[field] = document[replace]

                path["matches_ran"] = document["matches_ran"] + 1
                path["match_numbers"] = [pim["match_number"]]
                path["match_numbers"].extend(document["match_numbers"])
                path["path_number"] = document["path_number"]
                break
        else:
            # If there are no matching documents, that means this is a new auto path
            path["matches_ran"] = 1
            path["path_number"] = len(current_documents) + 1
            path["match_numbers"] = [pim["match_number"]]
            for field in self.schema["--path_groups"]["exact"]:
                path[field] = pim[field]
            # The max must be the current value
            for field, info in self.schema["path_max"].items():
                path[field] = pim[info["datapoint"]]
            # Start at 1 for each incremented datapoint if it a success, else a 0
            for datapoint, conditions in self.schema["path_increment"].items():
                for field, condition in conditions["conditions"].items():
                    for con in condition:
                        # Values starting with '-' are other datapoints (usually current max so use 'update' data)
                        c = [(i if i[0] != "-" else path[i[1:]]) for i in con]
                        if pim[field] not in c:
                            # Condition is false
                            path[datapoint] = 0
                            break
                    else:
                        # All was correct, check next con
                        continue
                    # Condition is false
                    break
                else:
                    # All conditions are true, start at one
                    path[datapoint] = 1

        # This is a field, which is added to obj_team, which says if a robot has compatability
        # Find the current team document from the obj_team collection
        current_team: dict = self.server.db.find("obj_team", {"team_number": pim["team_number"]})[0]
        for compatibility, info in self.schema["--compatability"].items():
            # Check if there was a possibility of success
            if all((pim[field] in possible) for field, possible in info["possible"].items()):
                # Check if the path was successful
                success = all(
                    (pim[field] in conditions) for field, conditions in info["success"].items()
                )
                # Find number of matches ran
                matches_ran = pim["matches_ran"]
                for document in current_documents:
                    matches_ran += document["matches_ran"]

                # Calculate  compatibility and add it to current_team
                if compatibility in current_team:
                    current_team.update(
                        {
                            compatibility: (
                                (current_team[compatibility] * (matches_ran - 1))
                                + int(success)  # Add 1 on success
                            )
                            / matches_ran
                        }
                    )
                else:
                    # First time, set to 0% on fail and 100% on success
                    current_team.update({compatibility: int(success)})
                # Update to server
                self.server.db.update_document(
                    "obj_team", current_team, {"team_number": current_team["team_number"]}
                )
            elif compatibility not in current_team:
                # Wasn't possible, but still need datapoint in obj_team, set to 0%
                current_team.update({compatibility: 0})
                self.server.db.update_document(
                    "obj_team", current_team, {"team_number": current_team["team_number"]}
                )

        return path

    def is_same_path(self, pim: dict, document: dict) -> bool:
        """Finds if the tim path is the same as the document path"""
        # All exact path_groups in schema must have the same value
        for datapoint in self.schema["--path_groups"]["exact"]:
            if pim[datapoint] != document[datapoint]:
                return False
        # All unexact path_groups must have values in the same list
        for datapoint, data in self.schema["--path_groups"]["unexact"].items():
            options, document_datapoint = data["options"], data["path_datapoint"]
            # Find the indexes of the lists which contain the value of the datapoint
            pim_indexes = [i for i, option in enumerate(options) if pim[datapoint] in option]
            document_indexes = [
                i for i, option in enumerate(options) if document[document_datapoint] in option
            ]
            if pim_indexes or document_indexes == []:
                log.warning(
                    f"auto_paths: {pim[datapoint]} or {document[document_datapoint]} is not in any option for unexact path_groups"
                )
            # Check if there is any matching index
            for list_index in pim_indexes:
                if list_index in document_indexes:
                    # There is a matching index
                    break
            else:
                # No matching index
                return False
        return True

    def update_auto_pims(self, path: dict) -> None:
        """Updates pim documents with information about its path number and matches played"""
        update = {"path_number": path["path_number"], "matches_ran": path["match_numbers"]}
        query = {
            "match_number": {"$in": path["match_numbers"]},
            "team_number": path["team_number"],
            "start_position": path["start_position"],
        }
        self.server.db.update_many("auto_pim", update, query)

    def calculate_auto_paths(self, pims: List[dict]) -> List[dict]:
        """Calculates auto data for the given pims, which looks like
        [{"team_number": "1678", "match_number": 42}, {"team_number": "1706", "match_number": 56}, ...]"""
        calculated_paths = []
        for pim in pims:
            auto_pims: List[dict] = self.server.db.find("auto_pim", pim)
            if len(auto_pims) != 1:
                log.error(f"Auto_paths: Multiple pims found for {pim}")

            path = self.group_auto_paths(auto_pims[0], calculated_paths)

            # Check to see if an outdated version of the path is in calculated_tims, and remove it if it is
            for calculated_path in calculated_paths:
                if (
                    calculated_path["team_number"] == path["team_number"]
                    and calculated_path["start_position"] == path["start_position"]
                    and calculated_path["path_number"] == path["path_number"]
                ):
                    calculated_paths.remove(calculated_path)
            calculated_paths.append(path)
        for path in calculated_paths:
            self.update_auto_pims(path)
        return calculated_paths

    def run(self):
        """Executes the auto_path calculations"""
        # Get oplog entries
        pims = []

        # Check if changes need to be made to teams
        if (entries := self.entries_since_last()) != []:
            for entry in entries:
                if "team_number" not in entry["o"].keys():
                    continue
                # Check that the team is in the team list, ignore team if not in teams list
                team_num = entry["o"]["team_number"]
                if team_num not in self.teams_list:
                    log.warning(f"auto_paths: team number {team_num} is not in teams list")
                    continue

                # Make pims list
                pims.append(
                    {
                        "team_number": team_num,
                        "match_number": entry["o"]["match_number"],
                    }
                )

        # Filter duplicate pims
        unique_pims = []
        for pim in pims:
            if pim not in unique_pims:
                unique_pims.append(pim)
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("auto_paths")

        # Calculate data
        updates = self.calculate_auto_paths(unique_pims)

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
