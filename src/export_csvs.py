#!/usr/bin/env python3

"""Export data from local MongoDB database to CSV file for picklist editor spreadsheet.

Timestamps files. Data exports also used for analysts in stands at competition.
"""

import argparse
import csv
from datetime import datetime
from data_transfer import database
from data_transfer import tba_communicator
from data_transfer import cloud_db_updater
import pymongo
import os
import re
from typing import List, Dict, Tuple, Optional, Any
import shutil
import json

import utils
from server import Server
import logging

log = logging.getLogger(__name__)

DATABASE = database.Database()

try:
    CLOUD_CLIENT = pymongo.MongoClient(cloud_db_updater.CloudDBUpdater.get_connection_string())
    """Make sure production is on or cloud database won't return anything"""
    CLOUD_DATABASE = database.Database(
        connection=cloud_db_updater.CloudDBUpdater.get_connection_string()
    )
    CLOUD_CLIENT.close()
except FileNotFoundError:
    log.error("Cloud database password not found")


SCHEMA = utils.read_schema("schema/collection_schema.yml")


class BaseExport:
    def __init__(self):
        """Generates attributes what will be needed for all four subclasses

        The collections schenma, timestamp and teams_list will be used heavily
        in subclasses and to avoid repetition
        """

        self.collections = list(SCHEMA["collections"].keys())
        self.timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.teams_list = self.get_teams_list()
        self.name = None

    @staticmethod
    def load_single_collection(collection_name: str, export_cloud=False) -> List[Dict]:
        """Return a list of all the documents in a given collection"""
        """Will return from cloud database instead of local if export_cloud is true"""
        if export_cloud == True and CLOUD_DATABASE != None:
            return CLOUD_DATABASE.find(collection_name)
        else:
            return DATABASE.find(collection_name)

    def get_data(
        self, collection_names: Optional[List[str]] = None, export_cloud=False
    ) -> Dict[str, List[Dict]]:
        """Return a dictionary of lists of documents of a given list of collections

        Give this a list of collection names and it will make a key value pair
        of the collection_name: List[Dict] with each collection having it's
        own key and the data inside as a collection
        """
        if collection_names is None:
            collection_names = self.collections
        return {a: self.load_single_collection(a, export_cloud) for a in collection_names}

    def create_name(self, name: str) -> str:
        """Generate a file name based on timestamp"""
        return f"{name}_{self.timestamp_str}.csv"

    @staticmethod
    def get_teams_list() -> List[str]:
        """Access all the team numbers via the team_list.csv"""
        with open(
            utils.create_file_path(f"data/{Server.TBA_EVENT_KEY}_team_list.json")
        ) as team_list:
            return list(json.load(team_list))

    @staticmethod
    def order_headers(column_headers: List[str], ordered: List[str]) -> List[str]:
        """These next lines sort the headers and the data to have team_number
        first for easy viewing in the spreadsheet
        """
        # Use the properties of the set to remove the duplicates
        column_headers = list(set(column_headers))
        # A list of things needing to be ordered that have been taken out of the column_headers to
        # be put back in at a later time
        ordered_items = []
        # Go through the ordered parameter and remove that item from column_headers and place it
        # temporarily in ordered_items
        for to_order in ordered:
            if to_order in column_headers:
                index = column_headers.index(to_order)
                ordered_items.append(column_headers.pop(index))
        # Reverse sort the list, this is the best way to push items to the front
        column_headers.sort(reverse=True)
        # Get the items put into ordered_items, and put them back into the last
        column_headers.extend(ordered_items)
        # Reverse is back to what it was
        column_headers.reverse()
        return column_headers

    def build_data(self):
        raise NotImplementedError

    def write_data(self, directory_path: str, export_cloud=False):
        column_headers, final_built_data = self.build_data(export_cloud)

        file_path = os.path.join(directory_path, self.name)
        with open(file_path, "w") as file:
            # Write headers using the column_headers list
            csv_writer = csv.DictWriter(file, fieldnames=column_headers)
            # Write the header as the first thing
            csv_writer.writeheader()
            # For each item, write the data as a dictionary
            for single_data in final_built_data.values():
                csv_writer.writerow(single_data)
        log.info(f"Finished export of {self.name}")

    def __repr__(self):
        """Give representation of the attributes this abstract class has"""
        collections = f"collections=[{self.collections[0]} ... {self.collections[-1]}]"
        team_list = f"teams_list=[{self.teams_list[0]} ... {self.teams_list[-1]}]"
        return f'BaseExport({collections}, timestamp_str="{self.timestamp_str}", {team_list})'


class ExportTBA(BaseExport):
    def __init__(self, cached_data=None):
        """Build and write tba data to csv

        Get tba data from tba_communicator and format it into a dictionary
        structure to write to a csv
        """
        super().__init__()
        self.name = self.create_name("tba_export")
        self.cached_data = self.get_tba_data(cached_data)

    @staticmethod
    def get_tba_data(cached_data=None) -> List:
        """Get data from tba if it is not given"""
        # If the cached data is not given, then get the data from the tba communicator
        if cached_data is None:
            api_url = f"event/{Server.TBA_EVENT_KEY}/matches"
            cached_data = tba_communicator.tba_request(api_url)
        return cached_data

    def build_data(self) -> List:
        """Builds TBA score and foul data as CSV."""
        match_scores = []
        export_fields = ["foulPoints", "totalPoints"]
        for match in self.cached_data:
            if match["score_breakdown"] is None or match["comp_level"] != "qm":
                continue
            for alliance in ["red", "blue"]:
                # Organize data by match number and alliance
                data = {"match_number": match["match_number"], "alliance": alliance}
                # Add the fields in export_fields fields to alliance
                # match_score breakdown
                for field in export_fields:
                    data[field] = match["score_breakdown"][alliance][field]
                # Get the robot number and the team number without the frc prefix in the name
                for i, team in enumerate(match["alliances"][alliance]["team_keys"], start=1):
                    data[f"robot{i}"] = team[3:]
                match_scores.append(data)
                # For each item in match_scores, get the key "match_score"
        return sorted(match_scores, key=lambda x: x["match_number"])

    def write_data(self, directory_path: str):
        """Writes the data from return_tba_data to a csv file"""
        log.info("Starting export of tba_data")
        # Get the path for tba export
        tba_file_path = os.path.join(directory_path, self.name)
        # Get the tba data from this instance
        data = self.build_data()
        # If it can't find data, let the user know because that might be because a mongodb issue or
        # more likely an Internet issue
        if not data:
            log.error("No TBA Data to export")
        # Get all the field_names from the data
        field_names = data[0].keys()
        with open(tba_file_path, "w") as file:
            # Write the headers as a dict
            writer = csv.DictWriter(file, field_names)
            writer.writeheader()
            # Write each row of tba data
            for row in data:
                writer.writerow(row)
        log.info("Finished export of tba_data")


class ExportTIM(BaseExport):
    db_data_paths = ["obj_tim", "tba_tim"]

    def __init__(self, export_cloud=False):
        """Build the TIM data from the database and format it as a directory
        then write it as a csv
        """
        super().__init__()
        self.name = self.create_name("tim_export")
        self.teams_list = self.get_teams_list()

        self.column_headers, self.final_built_data = self.build_data(export_cloud)

    def build_data(
        self, export_cloud=False
    ) -> Tuple[List[str], Dict[Tuple[str, int], List[Dict[str, Any]]]]:
        """Build the raw TIM data into a dictionary format with the key as team

        Gets the TIM data from the database and writes a dictionary where the
        key is the team number and the value is all the data corresponding to
        that specific team in a specific match
        """
        log.info("Starting export of tim_data")
        # Gets the lists of column headers and dictionaries to use in export
        tim_data = self.get_data(ExportTIM.db_data_paths, export_cloud)
        column_headers: List[str] = []
        data_by_team_and_match: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}

        # Goes through all the collections that it got from team data
        for list_of_documents in tim_data.values():
            # Goes through each document in the collection it on
            for document in list_of_documents:
                # Gets the team num from the document
                team_num = str(document["team_number"])
                # Ignore teams not in the teams list
                if team_num not in self.teams_list:
                    continue

                match_num = document["match_number"]
                # Uses a tuple of the team number and the match number as
                # to not write over other data
                team_key = (team_num, match_num)
                # Check if data exists for team and match combo
                if not data_by_team_and_match.get(team_key):
                    data_by_team_and_match[team_key] = {}

                # Goes through each field in the current document
                for key, value in document.items():
                    # Filter out the "_id" field which is not needed for exports
                    if key != "_id":
                        # If the key is a new one, add it to column_headers
                        if key not in column_headers:
                            column_headers.append(key)
                        # Add the key: value to the all the data under the key
                        # (team_num, match_num) like this
                        # {
                        #   ('1678', 1): {"team_number": '1678', ...},
                        #   ('9678', 2): {"team_number": '9678', ...},
                        # }
                        data_by_team_and_match[team_key][key] = value

        column_headers = self.order_headers(column_headers, ["match_number", "team_number"])
        return column_headers, data_by_team_and_match


class ExportTeam(BaseExport):
    db_data_paths = [
        "raw_obj_pit",
        "obj_team",
        "subj_team",
        "tba_team",
        "pickability",
    ]

    def __init__(self, export_cloud=False):
        """Get the team data, format it and write it as a csv

        Get the column_headers from the data as well as the final_built_data
        then write this data to the csv as a dictionary
        """
        super().__init__()
        self.name = self.create_name("team_export")
        self.teams_list = self.get_teams_list()

        self.column_headers, self.final_built_data = self.build_data(export_cloud)

    def build_data(
        self, export_cloud=False
    ) -> Tuple[List[str], Dict[Tuple[str, int], List[Dict[str, Any]]]]:
        """Takes data team data and writes to CSV

        Merges raw and processed team data into one dictionary
        Puts team export files into their own directory
        to separate them from team in match export files.
        """
        log.info("Starting export of team_data")
        # Get the lists of column headers and dictionaries to use in export
        team_data = self.get_data(ExportTeam.db_data_paths, export_cloud)

        column_headers: List[str] = []
        data_by_team_num: Dict[str, List[Dict[str, Any]]] = {}

        # Goes through all the collections that it got from team data
        for list_of_documents in team_data.values():
            # Goes through each document in the collection it on
            for document in list_of_documents:
                # Gets the team num from the document
                team_num = str(document["team_number"])

                # Filter out teams not in teams list
                if team_num not in self.teams_list:
                    continue

                # Check if data exists for team_num
                if not data_by_team_num.get(team_num):
                    data_by_team_num[team_num] = {}

                # Goes through each field in the current document
                for key, value in document.items():
                    # Don't export datapoints we don't need
                    if key not in [
                        "_id",
                        "test_first_pickability",
                        "test_second_pickability",
                        "test_driver_ability",
                    ]:
                        # If the key is a new one, add it to column_headers
                        if key not in column_headers:
                            column_headers.append(key)
                        # Add the key: value to the all the data under the key
                        # just team_num like this
                        # {
                        #   '1678': {"team_number": '1678', ...},
                        #   '9678': {"team_number": '9678', ...},
                        # }
                        data_by_team_num[team_num][key] = value

        column_headers = self.order_headers(column_headers, ["team_number"])
        return column_headers, data_by_team_num


class ExportScout(BaseExport):
    db_data_paths = ["sim_precision"]

    def __init__(self, export_cloud=False):
        """Build the scout data from the database and format it as a directory
        then write it as a csv
        """
        super().__init__()
        self.name = self.create_name("scout_export")

        self.column_headers, self.final_built_data = self.build_data(export_cloud)

    def build_data(
        self, export_cloud=False
    ) -> Tuple[List[str], Dict[Tuple[str, int], List[Dict[str, Any]]]]:
        """Build the scout data into a dictionary format with the key as scout

        Gets the scout data from the database and writes a dictionary where the
        key is the scout name and the value is all the data corresponding to
        that specific scout in a specific match
        """
        log.info("Starting export of scout_data")
        # Gets the lists of column headers and dictionaries to use in export
        scout_data = self.get_data(ExportScout.db_data_paths, export_cloud)
        column_headers: List[str] = []
        data_by_scout_and_match: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}

        # Goes through all the collections that it got from scout data
        for list_of_documents in scout_data.values():
            # Goes through each document in the collection it on
            for document in list_of_documents:
                # Gets the scout name from the document
                scout_name = document["scout_name"]
                match_num = document["match_number"]
                # Uses a tuple of the scout name and the match number as
                # to not write over other data
                scout_key = (scout_name, match_num)
                # Check if data exists for scout and match combo
                if not data_by_scout_and_match.get(scout_key):
                    data_by_scout_and_match[scout_key] = {}

                # Goes through each field in the current document
                for key, value in document.items():
                    # Filter out the "_id" field which is not needed for exports
                    if key != "_id":
                        # If the key is a new one, add it to column_headers
                        if key not in column_headers:
                            column_headers.append(key)
                        # Add the key: value to the all the data under the key
                        # (scout_name, match_num) like this
                        # {
                        #   ('person', 1): {"scout_name": 'person', ...},
                        #   ('someone', 2): {"scout_name": 'someone', ...},
                        # }
                        data_by_scout_and_match[scout_key][key] = value

        column_headers = self.order_headers(column_headers, ["match_number", "scout_name"])
        return column_headers, data_by_scout_and_match


class ExportImagePaths(BaseExport):
    PATH_PATTERN = re.compile(r"([0-9]+)_(full_robot|drivetrain|mechanism_[0-9]+)\.jpg")

    def __init__(self):
        """Get access to all the attributes and methods from the BaseExport"""
        super().__init__()
        self.csv_rows = self.get_dict_for_teams()

    def get_dict_for_teams(self) -> Dict[str, Any]:
        """Get the teams list and make the base structure of the teams list"""
        csv_rows = {}
        for team in self.teams_list:
            # Makes the team key a list with the team number in it.
            csv_rows[team] = {
                "full_robot": "",
                "drivetrain": "",
                "mechanism": [],
            }
            return csv_rows

    def get_image_paths(self) -> Dict[str, Any]:
        """Gets dictionary of image paths"""
        # Iterates through each device in the tablets folder
        for device in os.listdir(utils.create_file_path("data/devices")):
            # If the device is a phone serial number
            if device not in ["9AQAY1EV7J", "9AMAY1E54G", "9AMAY1E53P"]:
                continue
            device_dir = utils.create_file_path(f"data/devices/{device}/")
            # Iterates through all of files in the phone's folder
            for file in os.listdir(device_dir):
                # Tries to match the file name with the regular expression
                result = re.fullmatch(ExportImagePaths.PATH_PATTERN, file)
                # If the regular expression matched
                if result:
                    # Team number is the result of the first capture type
                    team_num = result.group(1)
                    if team_num not in self.teams_list:
                        continue
                    # Photo type is the result of the second capture group
                    photo_type = result.group(2)

                    # There can be multiple mechanism photos, so we need to handle differently
                    if photo_type.startswith("mechanism"):
                        self.csv_rows[team_num]["mechanism"].append(os.path.join(device_dir, file))
                    # Otherwise just add the photo path to its specified place in csv_rows
                    else:
                        self.csv_rows[team_num][photo_type] = os.path.join(device_dir, file)
        return self.csv_rows


def make_zip(directory_path: str):
    """Create a zip based on the directory_path

    Get the newly made export and generation a zip archive of this and move
    it to the correct export directory
    """
    log.info("Making zip archive...")
    dir_name = directory_path.split("/")[-1]
    archive_name = dir_name + ".zip"

    to_archive_path = os.path.join(utils.create_file_path("data/exports"), directory_path)
    move_location = os.path.join(utils.create_file_path("data/exports"), archive_name)

    shutil.make_archive(dir_name, "zip", to_archive_path)
    shutil.move(archive_name, move_location)
    log.info("Zip archive complete!")


def full_data_export(should_zip, should_return_scout_data, export_cloud=False) -> None:
    """Generate each of the types of data

    Instantiate each exporter class and write the csv to a directory shared by
    each of the three exports
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    directory_path = utils.create_file_path(f"data/exports/export_{timestamp}")

    if not should_return_scout_data:
        # Generate and export Tim data
        tim_exporter = ExportTIM(export_cloud)
        tim_exporter.write_data(directory_path, export_cloud)

        # Generate and export Team data
        team_exporter = ExportTeam(export_cloud)
        team_exporter.write_data(directory_path, export_cloud)

        # Generate and export TBA data
        tba_exporter = ExportTBA()
        tba_exporter.write_data(directory_path)
    else:
        # Generate and export Scout data
        scout_exporter = ExportScout(export_cloud)
        scout_exporter.write_data(directory_path, export_cloud)

    # This is default to yes but is not necessary
    if should_zip:
        make_zip(directory_path)


def parser():
    """
    Defines the argument options when running the file from the command line

    --dont_zip | Won't zip the exported file
    --scout_data | Will return the scout data
    --export_cloud | Will return from the cloud database
    """
    parse = argparse.ArgumentParser()
    parse.add_argument(
        "--dont_zip", help="Should create a zip archive", default=True, action="store_false"
    )
    parse.add_argument(
        "--scout_data", help="Should return scout data", default=False, action="store_true"
    )
    parse.add_argument(
        "--export_cloud",
        help="Should return from cloud database",
        default=False,
        action="store_true",
    )
    return parse.parse_args()


if __name__ == "__main__":
    args = parser()
    full_data_export(args.dont_zip, args.scout_data, args.export_cloud)
