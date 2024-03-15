#!/usr/bin/env python3

"""Decompresses objective and subjective match collection QR codes."""

import enum
import os
import re

import yaml
import time
import utils
from calculations import base_calculations
from calculations import qr_state
from calculations.qr_state import QRState
import logging
from data_transfer import database

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


class QRType(enum.Enum):
    """Enum that stores QR types."""

    OBJECTIVE = 0
    SUBJECTIVE = 1


class Decompressor(base_calculations.BaseCalculations):

    # Load latest match collection compression QR code schema
    SCHEMA = qr_state.SCHEMA
    OBJ_TIM_SCHEMA = utils.read_schema("schema/calc_obj_tim_schema.yml")
    OBJ_PIT_SCHEMA = utils.read_schema("schema/obj_pit_collection_schema.yml")
    SUBJ_PIT_SCHEMA = utils.read_schema("schema/subj_pit_collection_schema.yml")
    _GENERIC_DATA_FIELDS = QRState._get_data_fields("generic_data")
    OBJECTIVE_QR_FIELDS = _GENERIC_DATA_FIELDS.union(QRState._get_data_fields("objective_tim"))
    SUBJECTIVE_QR_FIELDS = _GENERIC_DATA_FIELDS.union(QRState._get_data_fields("subjective_aim"))
    TIMELINE_FIELDS = QRState.get_timeline_info()

    MISSING_TIM_IGNORE_FILE_PATH = utils.create_file_path("data/missing_tim_ignore.yml")

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["raw_qr"]

    def convert_data_type(self, value, type_, name=None):
        """Convert from QR string representation to database data type."""
        # Enums are stored as int in the database
        if type_ == "int":
            return int(value)
        if type_ == "float":
            return float(value)
        if type_ == "bool":
            return utils.get_bool(value)
        if type_ == "str":
            return value  # Value is already a str
        if "Enum" in type_:
            return self.get_decompressed_name(value, name)
        raise ValueError(f"Type {type_} not recognized")

    def get_decompressed_name(self, compressed_name, section):
        """Returns decompressed variable name from schema.

        compressed_name: str - Compressed variable name within QR code
        section: str - Section of schema that name comes from.
        """
        for key, value in self.SCHEMA[section].items():
            if isinstance(value, list):
                if value[0] == compressed_name:
                    return key
            else:
                if value == compressed_name:
                    return key
        raise ValueError(f"Retrieving Variable Name {compressed_name} from {section} failed.")

    def get_decompressed_type(self, name, section):
        """Returns server-side data type from schema.

        name: str - Decompressed variable name within Schema
        section: str - Section of schema that name comes from.
        """
        # Type all items after the first item
        type_ = self.SCHEMA[section][name][1:]
        # Detect special case of data type being a list
        if len(type_) > 1:
            return type_  # Returns list of the type (list) and the type of data stored in the list
        return type_[0]  # Return the type of the value

    def decompress_data(self, data, section):
        """Decompress (split) data given the section of the QR it came from.

        This matches compressed data names to actual variable names. It treats embedded dictionaries as
        special cases, a parsing function needs to be written for each (e.g. timeline).
        """
        decompressed_data = {}
        # Iterate through data
        for data_field in data:
            compressed_name = data_field[0]  # Compressed name is always first character
            value = data_field[1:]  # Actual data value is everything after the first character
            # Get uncompressed name and the target data type
            uncompressed_name = self.get_decompressed_name(compressed_name, section)
            uncompressed_type = self.get_decompressed_type(uncompressed_name, section)
            # Detect special cases in typing (e.g. value is list)
            if isinstance(uncompressed_type, list):
                # If second data type is dictionary, it should be handled separately
                if "dict" in uncompressed_type:
                    # Decompress timeline
                    if uncompressed_name == "timeline":
                        typed_value = self.decompress_timeline(value)
                    # Value is not one of the currently known dictionaries
                    else:
                        raise NotImplementedError(
                            f"Decompression of {uncompressed_name} as a dict not supported."
                        )
                # Decompress list of none-dicts
                elif uncompressed_type[1] in ["int", "float", "bool", "str"]:
                    if len(uncompressed_type) == 2:
                        # Default case, use _list_data_separator to seperate value into list items
                        split_values = value.split(self.SCHEMA["_list_data_separator"])
                    else:
                        # Use the specified length of each item to seperate
                        split_values = [
                            value[i : i + uncompressed_type[2]]
                            for i in range(0, len(value), uncompressed_type[2])
                        ]
                    # Convert string to appropriate data type
                    typed_value = [
                        self.convert_data_type(split_value, uncompressed_type[1])
                        for split_value in split_values
                    ]
            else:  # Normal data type
                typed_value = self.convert_data_type(value, uncompressed_type, uncompressed_name)
            decompressed_data[uncompressed_name] = typed_value
        return decompressed_data

    def decompress_generic_qr(self, data):
        """Decompress generic section of QR or raise error if schema is outdated."""
        # Split data by separator specified in schema
        data = data.split(self.SCHEMA["generic_data"]["_separator"])
        for entry in data:
            if entry[0] == "A":
                schema_version = int(entry[1:])
                if schema_version != self.SCHEMA["schema_file"]["version"]:
                    raise LookupError(
                        f'QR Schema (v{schema_version}) does not match Server version (v{self.SCHEMA["schema_file"]["version"]})'
                    )
        return self.decompress_data(data, "generic_data")

    def decompress_timeline(self, data):
        """Decompress the timeline based on schema."""
        decompressed_timeline = []  # Timeline is a list of dictionaries
        # Return empty list if timeline is empty

        if data == "":
            return decompressed_timeline

        timeline_length = sum([entry["length"] for entry in self.TIMELINE_FIELDS])

        if len(data) % timeline_length != 0:
            raise ValueError(f"Invalid timeline -- Timeline length invalid: {data}")

        # Split into list of actions. Each action is a string of length timeline_length
        timeline_actions = [
            data[i : i + timeline_length] for i in range(0, len(data), timeline_length)
        ]

        # index of to_teleop action in timeline_actions
        teleop_index = len(timeline_actions)

        for action in timeline_actions:
            decompressed_action = dict()
            current_position = 0
            # check if current action is to_teleop
            if self.SCHEMA["action_type"]["to_teleop"] in action:
                teleop_index = timeline_actions.index(action)
            for entry in self.TIMELINE_FIELDS:
                # Get untyped value by slicing action string from current position to next position
                next_position = current_position + entry["length"]
                untyped_value = action[current_position:next_position]
                # Set action value to the converted data type
                decompressed_action[entry["name"]] = self.convert_data_type(
                    untyped_value, entry["type"], entry["name"]
                )
                current_position = next_position
            # add and set in_teleop key to True or False depending on if it occurred before (False) or after (True) teleop_index
            if timeline_actions.index(action) >= teleop_index:
                decompressed_action["in_teleop"] = True
            else:
                decompressed_action["in_teleop"] = False
            decompressed_timeline.append(decompressed_action)
        return decompressed_timeline

    def get_qr_type(self, first_char):
        """Returns the qr type from QRType enum based on first character."""
        if first_char == self.SCHEMA["objective_tim"]["_start_character"]:
            return QRType.OBJECTIVE
        if first_char == self.SCHEMA["subjective_aim"]["_start_character"]:
            return QRType.SUBJECTIVE
        raise ValueError(f"QR type unknown - Invalid first character for QR: {first_char}")

    def decompress_single_qr(self, qr_data, qr_type, override):
        """Decompress a full QR."""
        # Split into generic data and objective/subjective data
        qr_data = qr_data.split(self.SCHEMA["generic_data"]["_section_separator"])
        # Generic QR is first section of QR
        decompressed_data = []
        # Decompress subjective QR
        if qr_type == QRType.SUBJECTIVE:
            teams_data = qr_data[1].split(self.SCHEMA["subjective_aim"]["_team_separator"])
            """none_generic_data = qr_data[1].split(
                self.SCHEMA["subjective_aim"]["_alliance_data_separator"]
            )
            if len(none_generic_data) != 2:
                raise IndexError("Subjective QR missing whole-alliance data")
            teams_data = none_generic_data[0].split(
                self.SCHEMA["subjective_aim"]["_team_separator"]
            )
            alliance_data = none_generic_data[1].split(
                self.SCHEMA["subjective_aim"]["_alliance_data_separator"]
            )
            """

            if len(teams_data) != 3:
                raise IndexError("Incorrect number of teams in Subjective QR")
            for team in teams_data:
                # Regular expression that finds all occurences of an integer occuring after "B" and "C" and returns the matches as a list of strings
                scores = re.findall(r"(?<=[BC])\d+", team)
                invalid = False
                for score in scores:
                    if score not in ["1", "2", "3"]:
                        invalid = True

                if invalid:
                    continue

                decompressed_document = self.decompress_generic_qr(qr_data[0])
                """
                subjective_data = team.split(self.SCHEMA["subjective_aim"]["_separator"]) + (
                    alliance_data if alliance_data != [""] else []
                )
                decompressed_data.append(decompressed_document)
                """
                subjective_data = team.split(self.SCHEMA["subjective_aim"]["_separator"])
                decompressed_document.update(
                    self.decompress_data(subjective_data, "subjective_aim")
                )
                if set(decompressed_document.keys()) != self.SUBJECTIVE_QR_FIELDS:
                    raise ValueError("QR missing data fields", qr_type)
                decompressed_data.append(decompressed_document)
        elif qr_type == QRType.OBJECTIVE:  # Decompress objective QR
            objective_data = qr_data[1].split(self.SCHEMA["objective_tim"]["_separator"])
            decompressed_document = self.decompress_generic_qr(qr_data[0])
            decompressed_document.update(self.decompress_data(objective_data, "objective_tim"))
            decompressed_data.append(decompressed_document)
            if set(decompressed_document.keys()) != self.OBJECTIVE_QR_FIELDS:
                raise ValueError("QR missing data fields", qr_type)
            decompressed_document.update({"override": override})
        return decompressed_data

    def decompress_qrs(self, split_qrs):
        """Decompresses a list of QRs. Returns dict of decompressed QRs split by type."""
        db = database.Database()
        output = {"unconsolidated_obj_tim": [], "subj_tim": []}
        log.info(f"Started decompression on qr batch")
        for qr in split_qrs:
            qr_type = utils.catch_function_errors(self.get_qr_type, qr["data"][0])
            if qr_type is None:
                continue
            decompressed_qr = utils.catch_function_errors(
                self.decompress_single_qr, qr["data"][1:], qr_type, qr["override"]
            )
            if decompressed_qr is None:
                continue
            # Override non-timeline datapoints at decompression
            for decompressed in decompressed_qr:
                decompressed["ulid"] = qr["ulid"]
                for override in qr["override"]:
                    if override in decompressed and override not in list(
                        self.OBJ_TIM_SCHEMA["timeline_counts"].keys()
                    ):  # Checks that override is not a timeline datapoint
                        decompressed[override] = qr["override"][override]
                # If there were datapoints in override that weren't in decompressed data,
                # add override to data for obj_tim calcs to handle
            if qr_type == QRType.OBJECTIVE:
                output["unconsolidated_obj_tim"].extend(decompressed_qr)
            elif qr_type == QRType.SUBJECTIVE:
                output["subj_tim"].extend(decompressed_qr)
        log.info(f"Finished decompression on qr batch")
        return output

    def decompress_pit_data(self, pit_data, pit_type):
        """Decompresses ONE obj or subj pit data dict

        pit_data: a dict of raw pit data
        pit_type: raw_obj_pit or raw_subj_pit"""
        # Get pit schema file
        if pit_type == "raw_obj_pit":
            pit_schema = self.OBJ_PIT_SCHEMA
        elif pit_type == "raw_subj_pit":
            pit_schema = self.SUBJ_PIT_SCHEMA

        decompressed_data = {}
        db = database.Database()
        # Use team number to find if team already has pit data inserted into MongoDB
        current_data = [
            document
            for document in db.find(pit_type)
            if document["team_number"] == pit_data["team_number"]
        ]

        # Enter data into a dictionary
        for name, value in pit_data.items():
            # if variable is an Enum, decompress it
            if "Enum" in pit_schema["schema"][name]["type"]:
                for enum_name, enum_value in pit_schema["enums"][name].items():
                    if enum_value == value:
                        decompressed_data[name] = enum_name
                        break
            else:
                decompressed_data[name] = value

        # Since Front-End doesn't keep variables empty when they don't
        # have values, we have to iterate through every variable to make
        # sure there's either (a) data or (b) a "None" placeholder
        for var in pit_schema["schema"].keys():
            if var not in decompressed_data:
                decompressed_data[var] = None

        if current_data:
            team_num = decompressed_data["team_number"]
            current_document = current_data[0]
            for name, value in decompressed_data.items():
                if current_document[name] == value:
                    continue
                # If type is a boolean, since default is false, if one is true, that means it was scouted, therefore we put true
                if pit_schema["schema"][name]["type"] == "bool":
                    if current_document[name] or value:
                        decompressed_data.update({name: True})
                # For nums, the default is 0, if the new document has a 0, go with the previously inserted one, else let the new one be inserted
                elif (
                    pit_schema["schema"][name]["type"] == "int"
                    or pit_schema["schema"][name]["type"] == "float"
                ):
                    if current_document[name] != 0 and value == 0:
                        decompressed_data.update({name: current_document[name]})
                    elif current_document[name] != 0 and value != 0:
                        log.warning(
                            f"Both pit scouts collected data on team {team_num} for field {name} and collected different values"
                        )
                # For the enum strings, they must be compared individually
                elif name == "drivetrain":
                    if value != "no_data":
                        continue
                    if current_document[name] != "no_data":
                        decompressed_data.update({name: current_document[name]})
                        continue
                    log.warning(
                        f"Both pit scouts collected data for team: {team_num} for the field: {name} and came up with different values"
                    )
        return decompressed_data

    def check_scout_ids(self):
        """Checks unconsolidated TIMs in `tim_queue` to see which scouts have not sent data.

        This operation is done by `scout_id` -- if a match is missing data, then the scout_id will not
        have sent data for the match.
        returns None -- warnings are issued directly through `log.warning`.
        """
        # Load matches or matches and ids to ignore from ignore file
        if os.path.exists(self.MISSING_TIM_IGNORE_FILE_PATH):
            with open(self.MISSING_TIM_IGNORE_FILE_PATH) as ignore_file:
                items_to_ignore = yaml.load(ignore_file, Loader=yaml.Loader)
        else:
            items_to_ignore = []
        matches_to_ignore = [item["match_number"] for item in items_to_ignore if len(item) == 1]
        tims = self.server.db.find("unconsolidated_obj_tim")
        matches = {}
        for tim in tims:
            match_number = tim["match_number"]
            matches[match_number] = matches.get(match_number, []) + [tim["scout_id"]]

        for match, scout_ids in matches.items():
            if match in matches_to_ignore:
                continue
            unique_scout_ids = []
            for id_ in scout_ids:
                if id_ in unique_scout_ids:
                    if {"match_number": match, "scout_id": id_} not in items_to_ignore:
                        log.warning(f"Duplicate Scout ID {id_} for Match {match}")
                else:
                    unique_scout_ids.append(id_)
            # Scout IDs are from 1-18 inclusive
            for id_ in range(1, 19):
                if id_ not in unique_scout_ids:
                    if {"match_number": match, "scout_id": id_} not in items_to_ignore:
                        log.warning(f"Scout ID {id_} missing from Match {match}")

    @staticmethod
    def decompress_ss_team(data):
        schema = utils.read_schema("schema/calc_ss_team.yml")
        for point, value in schema["schema"].items():
            if point not in list(data.keys()):
                if value["type"] == "int":
                    data[point] = -1
                else:
                    data[point] = False if value["type"] == "bool" else ""
        return data

    @staticmethod
    def decompress_ss_tim(data):
        # If data is an empty dict, return it since the TIM was not scouted
        if not data:
            return data
        schema = utils.read_schema("schema/calc_ss_tim.yml")
        for point, val in schema["schema"].items():
            if point not in list(data.keys()):
                if val["type"] == "bool":
                    data[point] = False
                else:
                    data[point] = 0 if val["type"] == "int" else ""
            elif point == "broken_mechanism":
                data[point] = True if data[point] != "" else False
        return data

    @staticmethod
    def consolidate_ss_team(team_number):
        schema = utils.read_schema("schema/calc_ss_team.yml")
        db = database.Database()
        documents = db.find("unconsolidated_ss_team", {"team_number": team_number})
        if len(documents) == 1:
            return documents[0]
        else:
            final = {}
            for field, val in schema["schema"].items():
                if val["type"] == "bool":
                    if documents[0][field] or documents[1][field]:
                        # Default to True for booleans (if we ever get a different default value we will make schema changes)
                        final[field] = True
                    else:
                        final[field] = False
                elif val["type"] == "str":
                    final[field] = ""
                    if documents[0][field] != "" and documents[1][field] != "":
                        final[field] = f"{documents[0][field]} + {documents[1][field]}"
                    elif documents[0] != "":
                        final[field] = documents[0][field]
                    elif documents[1] != "":
                        final[field] = documents[1][field]
            # Averages will be the same for both (since they both pull from ss_tim)
            for point in schema["averages"].keys():
                final[point] = documents[0][point]
            return final

    def run(self):
        # Get calc start time
        start_time = time.time()
        new_qrs = [
            entry["o"] for entry in self.entries_since_last() if not entry["o"]["blocklisted"]
        ]
        decompressed_qrs = self.decompress_qrs(new_qrs)

        # Checks if two subjective scouts scouted the same alliance in a match
        # If so, delete one of the qrs
        unique_combinations = set()
        filtered_qrs = []

        for qr in decompressed_qrs["subj_tim"]:
            match_number = qr["match_number"]
            alliance_color = qr["alliance_color_is_red"]
            team_number = qr["team_number"]
            if (match_number, alliance_color, team_number) not in unique_combinations:
                unique_combinations.add((match_number, alliance_color, team_number))
                filtered_qrs.append(qr)
        decompressed_qrs["subj_tim"] = filtered_qrs

        for collection in ["unconsolidated_obj_tim", "subj_tim"]:
            if self.calc_all_data:
                # Prevent duplicates when calculating all data by deleting data before inserting
                # Updating doesn't work because unconsolidated_obj_tim doesn't have unique keys
                self.server.db.delete_data(collection)
            self.server.db.insert_documents(collection, decompressed_qrs[collection])
        log.info("UPLOADED ALL RAW QRS TO LOCAL DB")
        end_time = time.time()
        # Get total calc time
        total_time = end_time - start_time
        # Write total calc time to log
        log.info(f"decompressor calculation time: {round(total_time, 2)} sec")
