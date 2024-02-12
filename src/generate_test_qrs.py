#!/usr/bin/env python3

"""
Generates random QR data given a match schedule.

Uses team skill levels to create realistic random data

OUTLINE
1. Define variables needed
    1.1. Match collection schema
    1.2. Test QR schema
    1.3. Match schedule (as a dict)
    1.4. Team skill levels
    1.5. Raw QRs list

OBJECTIVE QRs
2. Define functions to generate different parts of the QR
    2.1. Function to pull data from schema and generate random values for it
    2.2. Function to generate the generic data section of a QR
    2.3. Function to generate the timeline section of the QR
    2.4. Function to generate the objective TIM section of the QR

3. Define function to generate a whole QR using the separate functions

4. Call the create QR function on the match schedule to create QRs for every robot in every match

5. Write all the new QRs to test_qrs.txt

"""

import random
import utils
import json
import numpy as np
import argparse

if __name__ == "__main__":
    from send_device_jsons import get_team_list

    TEAM_LIST = get_team_list()  # List of team numbers
    print("Created team list\n")
else:
    TEAM_LIST = ["1678"]

# 1.1
MC_SCHEMA = utils.read_schema("schema/match_collection_qr_schema.yml")
# 1.2
TEST_QR_SCHEMA = utils.read_schema("schema/generate_test_qrs_schema.yml")


# 1.4
# Assign each team a skill level from 0 to 1
# Skill level determines the amount each team will score
skill_levels = np.random.normal(0.5, 0.16, len(TEAM_LIST))
skill_levels[skill_levels > 1] = 1
skill_levels[skill_levels < 0] = 0
TEAM_SKILL_LEVELS = {}
for num, team in enumerate(TEAM_LIST):
    TEAM_SKILL_LEVELS[team] = skill_levels[num]

# 1.5
raw_qrs = []

# 2.1
def gen_data_from_schema(schema_section, team_number: str, complete: bool = True):
    """Takes a schema section (such as TEST_QR_SCHEMA['generic_data']),
    and generates random values for each attribute based on given criteria.

    schema_section: a section of the TEST_QR_SCHEMA, such as TEST_QR_SCHEMA['objective_tim']

    team_number: the team number of the objective QR

    complete: if TRUE, returns a string qr with attributes separated by the section separator.
    if FALSE, returns a list with items containing attributes. Use TRUE if you want the complete
    QR form and FALSE if you want to keep editing the data."""

    # str to store the generated QR if complete is True
    qr = ""

    # List to store the randomly generated values, should look like ["A16", "B9AQAY1EV7J", "C42", ...]
    generated_values = []

    # Iterate through each variable in the seciton
    for field_name in schema_section:
        # Store attributes of the variable (ex. "gen", "symbol", "type")
        field_attrs = schema_section[field_name]
        # Place to store the randomly generated value
        field_value = ""
        # Check is variable is generatable
        if field_name[0] != "_" and field_attrs["gen"] == True:
            # Add the compressed name (ex. "A", "B", "C")
            field_value += field_attrs["symbol"]
            # Check if value is independent of skill level
            # If true, a value is randomly selected from the list
            if field_attrs["is_random"] == True:
                # If the variable is an int, generate a random value between the min and max
                if field_attrs["type"] == "int":
                    field_value += str(
                        random.randint(field_attrs["values"][0], field_attrs["values"][1])
                    )
                # If the variable is a str, pick a random item of the list
                elif field_attrs["type"] == "str":
                    field_value += random.choice(field_attrs["values"])

                # If the varible is a bool, pick a random bool. (getrandbits used for opimization purposes, randint or random.choice works fine too)
                elif field_attrs["type"] == "bool":
                    field_value += random.choice(["TRUE", "FALSE"])
            # If false, pick the value closest to skill_level * range
            elif field_attrs["is_random"] == False:
                # If variable is an int, calculate the skill_level * range + min
                if field_attrs["type"] == "int":
                    min = field_attrs["values"][0]
                    max = field_attrs["values"][1]
                    field_value += str(round(TEAM_SKILL_LEVELS[team_number] * (max - min) + min))
                # If variable is a str, pick the value with the index closest to skill_level * last_index
                elif field_attrs["type"] == "str":
                    field_value += field_attrs["values"][
                        round(TEAM_SKILL_LEVELS[team_number] * (len(field_attrs["values"]) - 1))
                    ]

                elif field_attrs["type"] == "bool":
                    if TEAM_SKILL_LEVELS[team_number] >= 0.5:
                        field_value += str(field_attrs["values"])
                    else:
                        field_value += str(not field_attrs["values"])

            # Add new generated value to the list
            generated_values.append(field_value)
    # Sort the generated values so "A16" comes before "B9AQAY1EV7J" and so on
    generated_values.sort()

    # Return either a QR as a str or a list of generated values
    if complete:
        qr += f"{schema_section['_separator']}".join(generated_values)
        return qr
    elif not complete:
        return generated_values


# 2.2
def gen_generic_data(team_number: str, alliance_color: str, match_num: str) -> str:
    """Function that generates QR data from the generic_data section (ex. 'schema_version', 'serial_number', 'match_number', etc)
    Returns a str containing the QR (ex. 'A16$BHA0Y2FCY$C1$D7346324158...')"""
    qr = ""

    # Generic schema shortcut
    generic_schema = TEST_QR_SCHEMA["generic_data"]

    # Generate all generatable data
    qr_attrs = gen_data_from_schema(generic_schema, team_number, False)

    # Manually add other non-generatable data
    # Insert schema version
    qr_attrs.append(
        generic_schema["schema_version"]["symbol"] + str(MC_SCHEMA["schema_file"]["version"])
    )

    # Add match number
    qr_attrs.append(generic_schema["match_number"]["symbol"] + match_num)

    # Add match collection version number
    qr_attrs.append(
        generic_schema["match_collection_version_number"]["symbol"]
        + f"{random.randint(1, 10)}.{random.randint(1, 10)}.{random.randint(1, 10)}"
    )

    # Add alliance color
    c = ""
    if alliance_color == "red":
        c = "TRUE"
    else:
        c = "FALSE"
    qr_attrs.append(f"{generic_schema['alliance_color_is_red']['symbol']}{c}")

    # Finish generating generic data and combine into a QR list
    qr_attrs.sort()
    qr += f"{generic_schema['_separator']}".join(qr_attrs)

    return qr


# 2.3
def gen_timeline(team_number: str) -> str:
    """Generates a timeline based on team skill level
    Timelines are formatted with the timestamp followed by the action_type
    Ex: 123AA115AO102AG

    1. Set all variables and functions needed for entire procedure:
        timeline, skill_level, count & complement, action_types, search()

    2. Set all variables needed for timeline loop
        tele_pieces, auto_pieces, auto_pieces_scored, tele_pieces_scored
        just_scored, auto_charged, tele_charged

    3. Iterate through the match time from 153s to 0s
        1. Check match time to find segment
            auto scoring 153s-140s, auto charging 140s-135s, to teleop 135s, teleop scoring 135s-(skill_level * 20s), endgame charge (skill_level * 20s)-0s
        2. Scoring segment actions (generate random number random.randint(1, complement_count))
            1. Check if max actions has been reached
            2. Check if just_scored
                1. Intake if random number is 1
                2. Set just_scored to False
            3. Check if random number is 1
                1. Add score to timeline
                2. Add one to pieces scored
                3. Set just_scored to True
        3. Charging segment actions (generate random number random.randint(1, complement_count))
            1. Check if already charged
            2. If random number is 1, add charge to timeline
            3. Set charged to True

    """
    timeline = f"{TEST_QR_SCHEMA['objective_tim']['timeline']['symbol']}"

    skill_level = TEAM_SKILL_LEVELS[team_number]

    # Number used for random.randint
    # count is used for values that increase when skill level increases (ex. num pieces scored)
    count = round(skill_level * 10)
    # complement count is used for values that decrease when skill level increases (ex. cycle time)
    complement_count = round((1 - skill_level) * 10)

    if count == 0:
        count = 1
    if complement_count == 0:
        complement_count = 1

    # Action type schema (dict)
    action_types = TEST_QR_SCHEMA["action_type"]

    # Function that searches action types for a specific phrase
    def search(phrase):
        result = list(filter(lambda x: phrase in x, action_types.keys()))
        return result

    # The amount of pieces a team can score, based on their team level
    tele_pieces = round(skill_level * 15)
    auto_pieces = round(skill_level * 3)

    # Scoring
    auto_pieces_scored = 0
    tele_pieces_scored = 0
    just_scored = False

    # Iterate through the match time
    for time in range(153, 0, -1):
        # Auto scoring
        if time >= 140:
            # Check if team hasn't reached the max they can score
            if auto_pieces_scored < auto_pieces:
                # If their last action was a score, their next action must be an intake
                if just_scored:
                    if random.randint(1, complement_count) == 1:
                        timeline += (
                            f"{time:03d}{action_types[random.choice(search('auto_intake'))]}"
                        )
                        just_scored == False
                # Score a piece and add one to auto_pieces_scored
                elif random.randint(1, complement_count) == 1:
                    timeline += f"{time:03d}{action_types[random.choice(search('score'))]}"
                    auto_pieces_scored += 1
                    # just scored
                    just_scored = True
            else:
                continue
        # Auto charging
        elif time > 135:
            continue
        # To teleop
        elif time == 135:
            # Add to_teleop action
            timeline += f"{time:03d}{action_types[random.choice(search('to_teleop'))]}"
        # Teleop scoring
        elif time > 15:
            # Check if team hasn't reached the max they can score
            if tele_pieces_scored < tele_pieces:
                # If their last action was a score, their next action must be an intake
                if just_scored:
                    if random.randint(1, complement_count) == 1:
                        timeline += f"{time:03d}{action_types[random.choice(list(filter(lambda x: 'auto' not in x, search('intake'))))]}"
                        just_scored == False
                # Score a piece and add one to tele_pieces_scored
                elif random.randint(1, complement_count) == 1:
                    timeline += f"{time:03d}{action_types[random.choice(search('score'))]}"
                    tele_pieces_scored += 1
                    # just scored
                    just_scored = True
            else:
                continue
        # Endgame charge
        else:
            continue
    return timeline


# 2.4
def gen_obj_tim(team_number: str) -> str:
    qr_attrs = []

    # objective_tim schema shortcut
    objective_tim = TEST_QR_SCHEMA["objective_tim"]

    # Generate generatable data
    qr_attrs = gen_data_from_schema(objective_tim, team_number, False)

    # Add team number
    qr_attrs.append(f"{TEST_QR_SCHEMA['objective_tim']['team_number']['symbol']}{team_number}")

    # Add timeline
    qr_attrs.append(gen_timeline(team_number))

    # Finish generating objective_tim data and return QR string
    qr_attrs.sort()
    return f"{objective_tim['_separator']}".join(qr_attrs)


def gen_subj_aim(team_number: str) -> str:
    qr_attrs = []

    # Subjective_aim schema shortcut
    subjective_aim = TEST_QR_SCHEMA["subjective_aim"]

    # Generate Generatable data
    qr_attrs = gen_data_from_schema(subjective_aim, team_number, False)

    # Add team number
    qr_attrs.append(f"{TEST_QR_SCHEMA['subjective_aim']['team_number']['symbol']}{team_number}")

    # Finish generating subjective_aim data and return QR string
    qr_attrs.sort()
    return f"{subjective_aim['_separator']}".join(qr_attrs)


# Creates a single objective tim qr
def create_single_obj_qr(
    team_num: str, alliance_color: str, match_num: str, single: bool = False
) -> str:
    qr = str(TEST_QR_SCHEMA["objective_tim"]["_start_character"])

    # Generate generic data
    qr += gen_generic_data(team_num, alliance_color, match_num)

    # add separator
    qr += str(TEST_QR_SCHEMA["generic_data"]["_section_separator"])

    # Generate objective data
    qr += gen_obj_tim(team_num)

    if single:
        raw_qrs.append(qr)
    else:
        return qr


# Creates a single subjective aim qr
def create_single_subj_qr(
    team_nums: list, alliance_color: str, match_num: str, single: bool = False
) -> str:
    qr = str(TEST_QR_SCHEMA["subjective_aim"]["_start_character"])

    # Generate generic data
    qr += gen_generic_data(team_nums, alliance_color, match_num)

    # add separator
    qr += str(TEST_QR_SCHEMA["generic_data"]["_section_separator"])

    # loop through all three teams
    for team in team_nums:
        qr_part = ""
        # Generate subjective data for 1 team
        qr_part += gen_subj_aim(team)
        # Add alliance separator
        qr_part += str(TEST_QR_SCHEMA["subjective_aim"]["_team_separator"])
        qr += qr_part

    # Cut off extra alliance separator
    qr = qr[:-1]
    # Add in alliance data seperator
    qr += TEST_QR_SCHEMA["subjective_aim"]["_alliance_data_separator"]
    if single:
        raw_qrs.append(qr)
    else:
        return qr


# 3
def create_obj_qrs(match_schedule: dict) -> None:
    for match_num, teams in match_schedule.items():
        for team in teams["teams"]:
            team_number = team["number"]
            alliance_color = team["color"]

            raw_qrs.append(create_single_obj_qr(team_number, alliance_color, match_num))


def create_subj_qrs(match_schedule: dict) -> None:
    for match_num, teams in match_schedule.items():

        # Gets all blue teams
        blue_teams = [team["number"] for team in teams["teams"] if team["color"] == "blue"]
        # Gets all red teams
        red_teams = [team["number"] for team in teams["teams"] if team["color"] == "red"]

        raw_qrs.append(create_single_subj_qr(blue_teams, "blue", match_num))
        raw_qrs.append(create_single_subj_qr(red_teams, "red", match_num))


def parser():
    """
    Defines the argument options when running the file from the command line

    --subj_aim | Will generate a subjective_aim qr instead of objective_tim
    """
    parse = argparse.ArgumentParser()
    parse.add_argument(
        "--subj_aim", help="Should create a subjective QR", default=False, action="store_true"
    )

    parse.add_argument("--single", help="Creates a single qr", default=False, action="store_true")

    parse.add_argument(
        "--print",
        help="Will print to the command line instead of in test_qrs.txt, only works if -used with --single",
        default=False,
        action="store_true",
    )

    # Removed for now, but could be implemented later if more control is wanted
    """parse.add_argument(
        "--team_num", 
        help="Lets you define a team to use for single qrs, otherwise it will be randomly generated. Up to 1 for objective and up to 3 for subjective", 
        default=None, 
        action="extend")"""
    return parse.parse_args()


# 4
if __name__ == "__main__":

    # Get arguments
    args = parser()

    # Get Match Schedule
    MATCH_SCHEDULE_LOCAL_PATH = f"data/{utils.TBA_EVENT_KEY}_match_schedule.json"
    try:
        with open(MATCH_SCHEDULE_LOCAL_PATH, "r") as match_schedule_json:
            MATCH_SCHEDULE_DICT = dict(json.load(match_schedule_json))
    except FileNotFoundError:
        print(
            f"\033[31mError: \033[0m Match schedule for {utils.TBA_EVENT_KEY} not found. \033[32m  Make sure you are running this file from a directory out! \033[0m (Try python src/generate_test_qrs.py) \n"
        )
    with open(MATCH_SCHEDULE_LOCAL_PATH, "r") as match_schedule_json:
        MATCH_SCHEDULE_DICT = dict(json.load(match_schedule_json))

    # Generate a random alliance/a random team
    random_match_num = random.choice(list(MATCH_SCHEDULE_DICT.keys()))
    RANDOM_MATCH = MATCH_SCHEDULE_DICT[random_match_num]

    random_alliance_color = random.choice(["red", "blue"])
    RANDOM_ALLIANCE = [
        team["number"] for team in RANDOM_MATCH["teams"] if team["color"] == random_alliance_color
    ]

    RANDOM_TEAM = random.choice(RANDOM_ALLIANCE)

    if args.single == True:
        if args.print == True:

            # generating to command line
            if args.subj_aim == True:
                print(
                    create_single_subj_qr(RANDOM_ALLIANCE, random_alliance_color, random_match_num)
                )
            else:
                print(create_single_obj_qr(RANDOM_TEAM, random_alliance_color, random_match_num))

        # generating in file
        else:
            if args.subj_aim == True:
                create_single_subj_qr(
                    RANDOM_ALLIANCE, random_alliance_color, random_match_num, single=True
                )
            else:
                create_single_obj_qr(
                    RANDOM_TEAM, random_alliance_color, random_match_num, single=True
                )

    # generating multiple
    else:
        if args.subj_aim == True:
            create_subj_qrs(MATCH_SCHEDULE_DICT)
        else:
            create_obj_qrs(MATCH_SCHEDULE_DICT)

    if args.print == True:
        print("\n".join(raw_qrs))
    else:
        with open("test_qrs.txt", "w") as qr_file:
            for qr in raw_qrs:
                qr_file.write(f"{qr}\n")
        print(
            f"Wrote {len(raw_qrs)} {'subjective aim' if args.subj_aim else 'objective tim'} QR(s) to test_qrs.txt"
        )
