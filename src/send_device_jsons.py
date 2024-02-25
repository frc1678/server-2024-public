#!/usr/bin/env python3

"""Create match schedule and team list files and send them to devices.
Retrieve match schedule from TBA,
Create team list from match schedule,
send match schedule file to scout tablets over ADB,
and verify that the file is successfully transferred.
ADB stands for Android Debug Bridge.
"""

import hashlib
import json
import time

from data_transfer import adb_communicator
from data_transfer import tba_communicator
import utils
import logging

log = logging.getLogger(__name__)


def create_match_schedule_json(local_file_path, tba_request_url):
    """Creates a JSON file based on database's cached matches
    Parameters: local_file_path (string): path to match_schedule.json
    tba_request_url: api_url for calling tba_communicator.tba_request()
    :returns None on success, 1 on failure
    """
    # Get matches from database
    matches = tba_communicator.tba_request(tba_request_url)
    # Don't try to create match schedule if matches returns a blank list
    if matches == []:
        return 1
    # Filter out elimination matches; we don't use them for scouting
    matches = [match for match in matches if match["comp_level"] == "qm"]
    match_schedule_dict = {}
    for match in matches:
        # match['key'] has event code, and underscore, then the match
        # example: '2019carv_qm118'
        match_key = match["key"].split("_qm")[1]
        team_dicts = []
        for alliance in ["blue", "red"]:
            teams = match["alliances"][alliance]["team_keys"]
            teams = [{"number": str(team[3:]), "color": alliance} for team in teams]
            team_dicts.extend(teams)
        match_schedule_dict[match_key] = {"teams": team_dicts}
    with open(local_file_path, "w") as json_file:
        json.dump(match_schedule_dict, json_file)

    log.info(f"Match schedule created at {local_file_path}, url is {tba_request_url}")


def get_team_list():
    """Returns team list from match schedule file"""
    teams = set()
    if not SEND_MATCH_SCHEDULE:
        teams = tba_communicator.tba_request(f"event/{utils.TBA_EVENT_KEY}/teams/simple")
        # TBA returns a dictionary of information about teams at the event, so extract team numbers
        team_numbers = [str(team["team_number"]) for team in teams]
        return sorted(team_numbers)
    with open(MATCH_SCHEDULE_LOCAL_PATH) as file:
        match_schedule_reader = json.load(file)
        for match, team_info in match_schedule_reader.items():
            for team_dict in team_info["teams"]:
                teams.add(team_dict["number"])
    # Return a list of teams sorted by team number
    return sorted(map(str, teams))


def write_team_list(output_file_path):
    """Writes team list to file"""
    team_list = get_team_list()
    with open(output_file_path, "w") as file:
        json.dump(team_list, file)


def validate_file(device_id, local_file_path, tablet_file_path):
    """Validates that `local_file_path` file was successfully transferred.
    Compares the `tablet_file_path` on the tablet to the locally stored
    version of the same file.
    Parameter 'device_id' is the serial number of the device
    """
    # Find the hash of `tablet_file_path`
    tablet_data = adb_communicator.get_tablet_file_path_hash(device_id, tablet_file_path)
    if local_file_path == MATCH_SCHEDULE_LOCAL_PATH:
        return tablet_data == LOCAL_MATCH_SCHEDULE_HASH
    raise ValueError(f"File path {local_file_path} not recognized.")


# Set paths to read from and write to
MATCH_SCHEDULE_TABLET_PATH = "/storage/emulated/0/Download/match_schedule.json"
MATCH_SCHEDULE_LOCAL_PATH = utils.create_file_path(
    f"data/{utils.TBA_EVENT_KEY}_match_schedule.json"
)
TEAM_LIST_LOCAL_PATH = utils.create_file_path(f"data/{utils.TBA_EVENT_KEY}_team_list.json")

log.info(f"You are working with the competition {utils.TBA_EVENT_KEY}. Is that right?")
while True:
    if input("Hit enter to continue, or Ctrl-C to exit:") == "":
        break

# Match schedule must be created before local copy is loaded
if (
    create_match_schedule_json(
        MATCH_SCHEDULE_LOCAL_PATH, f"event/{utils.TBA_EVENT_KEY}/matches/simple"
    )
    == 1
):
    SEND_MATCH_SCHEDULE = False
else:
    SEND_MATCH_SCHEDULE = True

# LOCAL_MATCH_SCHEDULE contains the text of the match_schedule.json file, which we compare with the
# output of cat (run on tablets through adb shell) for file validations
if SEND_MATCH_SCHEDULE:
    with open(MATCH_SCHEDULE_LOCAL_PATH, "rb") as match_schedule_file:
        # Store sha256 sum of match schedule
        LOCAL_MATCH_SCHEDULE_HASH = hashlib.sha256(match_schedule_file.read()).hexdigest()
# Team list must be created after local match schedule copy is loaded
write_team_list(TEAM_LIST_LOCAL_PATH)

# Only upload schedules if file is ran, not imported
if __name__ == "__main__":
    # List of devices to which 'match_schedule.json' has already been sent
    DEVICES_WITH_SCHEDULE = set()
    get_devices = adb_communicator.get_attached_devices()
    new_get_devices = []
    for device in get_devices:
        new_get_devices.append(device[0])
    DEVICES = set(new_get_devices)

    if SEND_MATCH_SCHEDULE:
        log.info(f'{MATCH_SCHEDULE_LOCAL_PATH}"\n')
    else:
        log.warning(f'Match Schedule for "{utils.TBA_EVENT_KEY}" not available')

    while True:
        # Wait for USB connection to initialize
        time.sleep(0.1)
        for device in DEVICES:
            device_name = adb_communicator.DEVICE_SERIAL_NUMBERS[device]
            if device not in DEVICES_WITH_SCHEDULE and SEND_MATCH_SCHEDULE:
                log.info(f"\nAttempting to load {MATCH_SCHEDULE_LOCAL_PATH} onto {device_name}")
                if adb_communicator.push_file(
                    device, MATCH_SCHEDULE_LOCAL_PATH, MATCH_SCHEDULE_TABLET_PATH, validate_file
                ):
                    DEVICES_WITH_SCHEDULE.add(device)
                    log.info(f"Loaded {MATCH_SCHEDULE_LOCAL_PATH} onto {device_name}")
                else:
                    # Give both serial number and device name in warning
                    log.warning(
                        f"FAILED sending {MATCH_SCHEDULE_LOCAL_PATH} to {device_name} ({device})"
                    )

        # Update connected devices before checking if program should exit
        get_devices = adb_communicator.get_attached_devices()
        new_get_devices = []
        for device in get_devices:
            new_get_devices.append(device[0])
        DEVICES = set(new_get_devices)
        if DEVICES == DEVICES_WITH_SCHEDULE:
            # Print blank lines for visual distinction
            log.info("\n")
            # Schedule has been loaded onto all connected devices
            if SEND_MATCH_SCHEDULE:
                if len(DEVICES_WITH_SCHEDULE) != 1:
                    log.info(f"Match schedule loaded onto {len(DEVICES_WITH_SCHEDULE)} devices.")
                else:
                    log.info("Match schedule loaded onto 1 device.")
            break
