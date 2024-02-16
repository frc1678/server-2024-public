#!/usr/bin/env python3

"""Generate test data for non-QRs"""

import argparse
from calculations.generate_random_value import generate_random_value
import json
import utils
import json
from dataclasses import dataclass
from typing import List, Optional
from os.path import exists
from os import listdir
from pprint import pprint
import logging
from console import console
from rich.prompt import Prompt

log = logging.getLogger(__name__)


@dataclass
class TIMInstance:
    match_number: int
    team_number: str

    def __retr__(self):
        return f"TIMInstance(match_number={self.match_number}, \
            team_number={self.team_number})"


class TIMInstanceGenerator:
    """Object that represents teams list and its pointer"""

    def __init__(self, match_schedule_file_path):
        self.match_schedule_file_path = match_schedule_file_path
        self.tims: List[TIMInstance] = []
        self.index = 0
        self.match_instance_generator()

    def match_instance_generator(self):
        """Generate match instances for each team in each match

        If a match schedule csv file is not specified, autogenerate match data
        """
        # If the match_schedule_file_path is not provided, we need to generate data with accurate
        # and data that have constant team and match values across data generated for different
        # collections
        if self.match_schedule_file_path is None:
            # Hardcoded constants for how many teams and matches we want
            num_teams = 42
            num_matches = 118
            # Create a fake list of teams
            teams: List[str] = ["1678"] + [str(x**x)[0:4] for x in range(1, num_teams)]

            # Generate a TIM instance for each match
            for match_number in range(1, num_matches + 1):
                # Pick 6 teams from the teams list with a start and an end; ex. 3:9, 9:15, or 15:21
                # the first number being start and the second being end_team_index
                start_team_index = match_number * 6 % len(teams)
                end_team_index = (start_team_index + 6) % num_teams
                # This is needed if the num_teams is not divisible by 6
                if end_team_index < start_team_index:
                    teams_in_match = [teams[x] for x in range(start_team_index, num_teams)]
                    teams_in_match.extend([teams[x] for x in range(0, end_team_index)])
                # This is for the other cases
                else:
                    teams_in_match = [teams[x] for x in range(start_team_index, end_team_index)]

                for team_number in teams_in_match:
                    self.tims.append(TIMInstance(match_number, team_number))

        # The match_schedule was provided
        else:
            # Get all the matches from the schedule
            match_schedule = self.read_match_schedule(self.match_schedule_file_path)
            # Go through each match
            for match in match_schedule:
                # Get the match number
                match_number: int = int(match[0])
                # Get all the team numbers for the match and remove the color
                # prefix, and the dash
                team_numbers: List[str] = [item.split("-")[1] for item in match[1:]]
                # Make a match instance for each team number, using the match number
                for team_number in team_numbers:
                    new_match: TIMInstance = TIMInstance(match_number, team_number)
                    self.tims.append(new_match)

    def read_match_schedule(self, file_path):
        """Reads json as list of the match schedule"""
        with open(file_path, "r") as json_file:
            json_data = list(json.load(json_file))
        return json_data

    def __next__(self) -> TIMInstance:
        """Return a TIM instance based on the index"""
        if self.index == len(self.tims):
            self.index = 0
        tim = self.tims[self.index]
        self.index += 1
        return tim

    def reset(self):
        """Reset the count"""
        self.index = 0


class DataGenerator:
    """Given a schema file, find and fill in all the datapoints with random
    data for testing

    1. Given a schema file name, find datapoints that
    need data to be generated for them
    2. Generate data for each datapoint
    3. Get a number or raw data structures in need or generation and return a
    list of them with get_data()

    generate_test_data = DataGenerator("<schema_file_path>")

    schema file path must follow sytax of the utils.read_schema()
    format is "schema/<schema_filename>.yml"

    data = generate_test_data.get_data(<number_of_data>)

    data will be a list of dictionary's that are datapoint field filled in
    with auto generated data
    """

    def __init__(
        self,
        schema_filename: str,
        match_schedule_file_path: Optional[str] = None,
        seed=None,
    ):
        """Get schema filename and seed for generation"""
        self.seed = seed
        self.match_schedule_file_path = match_schedule_file_path
        self.tim_instance_generator = TIMInstanceGenerator(self.match_schedule_file_path)
        self.schema_filename = schema_filename

    def open_schema_file(self, schema_filename: str) -> dict:
        """Get schema file name and return opened schema"""
        schema = utils.read_schema(schema_filename)
        return schema

    def get_datapoint_collections_generation(self) -> dict:
        """Get the datapoints from the schema that we want to generate for."""
        schema = self.open_schema_file(self.schema_filename)
        datapoint_collections = {}
        for key, value in schema.items():
            # "schema_file" is not needed
            if key not in ["schema_file", "enums"]:
                datapoint_collections[key] = value

        return datapoint_collections

    def generate_for_each_datapoint_collection(self) -> dict:
        """Go through the dictionary with all the datapoint collections and
        then go through all the datapoints inside those collections. After this
        get the type listed under the datapoint and generate a value for it
        """
        datapoint_collections = self.get_datapoint_collections_generation()
        generated_structure = {}

        # Go through each datapoint collection
        for datapoint_collection_name, datapoint_collection_values in datapoint_collections.items():
            if datapoint_collection_name[:2] == "--":
                continue
            # Go through each datapoint in the datapoint collections
            for (
                datapoints_values_key,
                datapoints_values_value,
            ) in datapoint_collection_values.items():
                if datapoints_values_value.get("type") is not None:
                    value_type = datapoints_values_value["type"]
                    # Generate random datapoint values using the generate_random_value function in src/calculations/generate_random_values.py
                    generated_structure[datapoints_values_key] = generate_random_value(
                        value_type, datapoints_values_key, self.seed
                    )

        return generated_structure

    def format_raw_data(self) -> dict:
        """Get the data and format it correctly"""
        data = self.generate_for_each_datapoint_collection()

        match_instance = self.tim_instance_generator.__next__()

        # We use isinstance here because if the get() returns a numeric zero,
        # it will be False and it will not replace the zeros in the data
        if isinstance(data.get("team_number"), str):
            data["team_number"] = match_instance.team_number

        if isinstance(data.get("match_number"), int):
            data["match_number"] = match_instance.match_number

        return data

    def request_single_data_struct(self) -> dict:
        """Important to be a single item of data returned as a dict instead of
        needing to request a list, and getting items from it"""
        return self.format_raw_data()

    def get_data(self, times: int = 1) -> list:
        """Send requests for a single thing of data, return as many as
        requested as a list"""
        list_of_data = []

        for num in range(times):
            data = self.request_single_data_struct()
            list_of_data.append(data)

        return list_of_data


def name_sample_data(filename: str, number_of_data: int):
    """Return the data with a name for easy demonstration of data"""
    generate_test_data = DataGenerator(filename)
    data = generate_test_data.get_data(number_of_data)
    return {filename: data[0]}


def parse_args():
    """Parse out the needed args"""
    parser = argparse.ArgumentParser()
    # Add arguments for input and output
    parser.add_argument(
        "-i",
        "--infile",
        help="Input schema file; e.g. schema/calc_subj_team_schema.yml",
        required=False,
    )
    parser.add_argument(
        "-o",
        "--outfile",
        help="Output file for json; e.g. output.json",
        required=False,
    )
    parser.add_argument(
        "-n",
        "--number",
        help="Number of data structures; e.g. 2",
        required=False,
    )
    parser.add_argument(
        "-p",
        "--pretty",
        help="Pretty output",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--teamfile",
        help="Teams list file path",
        required=False,
    )
    parsed = parser.parse_args()
    return parsed


def ask_input_filename():
    # Find where the schema folder is
    if exists("../schema"):
        schema_location = "../schema"
    elif exists("./schema"):
        schema_location = "./schema"
    else:
        schema_location = None

    # Get all the schema files from the found schema directory
    if schema_location:
        schema_files = [
            x
            for x in listdir(schema_location)
            if x[-4:] == ".yml"
            and x != "collection_schema.yml"
            and x != "match_collection_qr_schema.yml"
        ]

        if len(schema_files) == 0:
            log.warning(
                "There are no files in the schema directory that end with .yml\
                make sure the directory is up to date with https://github.com/frc1678/schema"
            )

        return "schema/" + Prompt.ask(
            "What schema data structure do you want?", console=console, choices=schema_files
        )
    else:

        log.error(
            "Make sure the schema dir exists.\n\
You may need to clone it inside the 'server/' dir.\n\
Repo: https://github.com/frc1678/schema\n\n"
        )

        log.error("Schema folder not found")
        exit(1)


def ask_number() -> int:
    number = input("What number of schema data structure do you want? ")
    return int(number)


if __name__ == "__main__":
    """This script is both something that can be imported and used in the
    command line (import instructions at top of class)

    CLI instructions; use -h option for detail
    python3 generate_test_data.py -i <input_schema_file> -n <number_of_data>

    The input_schema_file uses the same syntax as utils.read_schema
    "schema/<schema_file_name>.yml"

    The number_of_data is an int of how many raw data structures you want
    """
    parsed = parse_args()

    # Set schema filenames
    input_filename = parsed.infile if parsed.infile else ask_input_filename()
    number_of_data = int(parsed.number) if parsed.number else ask_number()

    teams_list_file_path = parsed.teamfile

    generate_test_data = DataGenerator(input_filename, teams_list_file_path)
    data = generate_test_data.get_data(number_of_data)

    # Write the data as a json file if an outfile is provided
    if parsed.outfile:
        with open(parsed.outfile, "w") as file:
            json.dump(data, file)

        log.info(f"Wrote to {parsed.outfile}")
    else:
        if parsed.pretty:
            log.info(data)
        else:
            log.info(data)
