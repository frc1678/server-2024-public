#!/usr/bin/env python3

"""Holds functions that use ADB."""

import json
import os
import re
import shutil
import time

from data_transfer import database
import qr_code_uploader
import utils
import logging
from calculations import decompressor
from calculations import base_calculations

log = logging.getLogger(__name__)


def delete_tablet_downloads():
    """Deletes all data from the Download folder of tablets"""
    devices = get_attached_devices()
    # Wait for USB connection to initialize
    time.sleep(0.1)
    directory = "/storage/emulated/0/Download"
    for device in devices:
        try:
            utils.run_command(f"adb -s {device} shell rm -r {directory}")
            log.info(f"Removed Downloads on {DEVICE_SERIAL_NUMBERS[device]} ({device})")
        except:
            log.info(f"Found no files to delete on {DEVICE_SERIAL_NUMBERS[device]} ({device})")


def get_attached_devices():
    """Uses ADB to get a list serials of devices attached."""
    # Get output from `adb_devices` command. Example output:
    # "List of devices attached\nHA0XUZA9\tdevice\n9AMAY1E53P\tdevice"
    adb_output = utils.run_command("adb devices", return_output=True)
    # Split output by lines
    # [1:] removes line one, 'List of devices attached'
    adb_output = adb_output.rstrip("\n").split("\n")[1:]
    # Each connected device in `adb_output` will be a list of either [<serial>, "device"] or [<serial>, "unauthorized"]
    return [line.split("\t") for line in adb_output]


def push_file(serial_number, local_path, tablet_path, validate_function=None):
    """Pushes file at `local_path` to `tablet_path` using ADB.

    `validate_function` should return a boolean and take a serial number, local_file_path, and
    `tablet_path` in that order.
    """
    # Calls 'adb push' command, which runs over the Android Debug Bridge (ADB) to copy the file at
    # local_path to the tablet
    # The -s flag specifies the device by its serial number
    push_command = f"adb -s {serial_number} push {local_path} {tablet_path}"
    utils.run_command(push_command)
    # Return bool indicating if file loaded correctly
    if validate_function is not None:
        return validate_function(serial_number, local_path, tablet_path)
    return None


def uninstall_app(device, app_name="com.frc1678.match_collection"):
    """Uninstalls app `app_name` from tablet matching the serial number.

    Match Collection is com.frc1678.match_collection
    Pit Collection is com.frc1678.pit_collection
    Viewer is org.citruscircuits.viewer
    """
    # Gets list of all installed apps. -3 returns only 3rd party apps.
    installed_apps = utils.run_command(
        f"adb -s {device} shell pm list packages -3", return_output=True
    )
    uninstall_command = f"adb -s {device} uninstall {app_name}"
    if app_name in installed_apps:
        utils.run_command(uninstall_command)
        log.info(f"Uninstalled app {app_name} from {DEVICE_SERIAL_NUMBERS[device]}, ({device})")
    else:
        log.info(
            f"Tried to to uninstall app {app_name} from {DEVICE_SERIAL_NUMBERS[device]}, ({device}) but it was not in list of installed apps."
        )


def pull_device_files(local_file_path, tablet_file_path, devices=[]):
    """pull_device_files is a function for pulling data off tablets.

    pull_device_files is given a local path and a tablet path.
    It takes the file or directory that is specified as tablet path and
    puts in the directory specified as local path.
    The directory that is put in the local path is
    a subdirectory of a directory with the name of
    the serial number of the tablet that was pulled from.

    Usage:
    pull_device_files('/path/to/output/directory', '/path/to/tablet/data')
    """
    # Wait for USB connection to initialize
    time.sleep(0.1)
    # List of devices that have been pulled from (finished)
    devices_finished = []
    for device in devices:
        # Checks if device is finished
        if device not in devices_finished:
            # Creates directory for each tablet in data/
            full_local_path = os.path.join(local_file_path, device)
            utils.create_file_path(full_local_path)
            # Deletes and re-creates pull directory, using adb pull to a directory with pre-existing
            # files, adb pull creates another folder inside of directory and pulls to that directory
            if os.path.exists(full_local_path):
                shutil.rmtree(full_local_path)
                utils.create_file_path(full_local_path, True)
            # Calls 'adb push' command, which uses the Android Debug
            # Bridge (ADB) to copy the match schedule file to the tablet.
            # The -s flag specifies the device by its serial number.
            utils.run_command(f"adb -s {device} pull {tablet_file_path} {full_local_path}")
            devices_finished.append(device)


def adb_remove_files(tablet_file_path):
    """This is a function used for removing files on the tablets over ADB

    adb_remove_files finds the list of devices attached then uses the line
    utils.run_command(f'adb -s {device} shell rm -r {tablet_file_path}').
    The adb -s {device} specifies which device to delete from and shell rm -r
    deletes the file from the specified directory that is {tablet_file_path}
    """
    devices = get_attached_devices()
    # Wait for USB connection to initialize
    time.sleep(0.1)
    for device in devices:
        # Calls 'adb push' command, which uses the Android Debug
        # Bridge (ADB) to copy the match schedule file to the tablet
        # The -s flag specifies the devices by their serial numbers
        utils.run_command(f"adb -s {device} shell rm -r {tablet_file_path}")
        log.info(f"removed {tablet_file_path} on {DEVICE_SERIAL_NUMBERS[device]}, ({device})")


def pull_device_data():
    """Pulls tablet data from attached tablets."""
    # Parses 'adb devices' to find num of devices so that don't try to pull from nothing
    devices = get_attached_devices()
    db = database.Database()
    # sorts stand strategist devices from others
    ss_devices = []
    for device in devices:
        if device[:2] == "R8":
            ss_devices.append(device)
    for device in ss_devices:
        devices.remove(device)
    data = {"qr": [], "raw_obj_pit": []}
    if ss_devices == [] and devices == []:
        return data
    device_file_paths = []
    # Stand strategists file paths
    ss_device_file_paths = []
    device_file_path = utils.create_file_path("data/devices/")
    # Pull all files from the 'StandStrategist' folder on the device (if plugged in)
    if ss_devices:
        pull_device_files(
            device_file_path, "/storage/emulated/0/Documents/StandStrategist/profiles", ss_devices
        )
    # Pull all files from the 'Download' folder on the device (if tablets are plugged in)
    if devices:
        pull_device_files(device_file_path, "/storage/emulated/0/Download", devices)
    # Iterates through the 'data' folder
    for device_dir in os.listdir(device_file_path):
        if device_dir in DEVICE_SERIAL_NUMBERS.keys():
            if device_dir[:1] == "R":
                ss_device_file_paths.append(device_dir)
            else:
                device_file_paths.append(device_dir)

    for device in device_file_paths:
        # Iterate through the downloads folder in the device folder
        download_directory = os.path.join(device_file_path, device)
        for file in os.listdir(download_directory):
            for dataset, pattern in FILENAME_REGEXES.items():
                if re.fullmatch(pattern, file):
                    with open(os.path.join(download_directory, file)) as data_file:
                        # QR data is just read
                        if dataset == "qr":
                            file_contents = data_file.read().rstrip("\n")
                        else:
                            file_contents = json.load(data_file)
                        data[dataset].append(file_contents)
                        break  # Filename will only match one regex
    # Pulls data from Stand Strategist (ss)
    # Iterates through the 'data' folder
    # Iterates through the devices
    for device in ss_device_file_paths:
        profiles_directory = os.path.join(device_file_path, device)
        profiles = os.listdir(profiles_directory)

        for profile in profiles:
            # Update Team Data for Stand Strategist
            with open(os.path.join(profiles_directory, profile, "team_data.json")) as f:
                team_data = json.load(f)
                for team_number, document in team_data.items():
                    db.update_document("ss_team", document, {"team_number": team_number})
            # Update TIM Data for Stand Strategist
            with open(os.path.join(profiles_directory, profile, "tim_data.json")) as f:
                tim_data = json.load(f)
                for match, value in tim_data.items():
                    for team_number, tim in value.items():
                        db.update_document(
                            "ss_tim", tim, {"team_number": team_number, "match_number": match}
                        )

        log.info(f"{len(team_data)} items uploaded to ss_team")
        log.info(f"{len(tim_data)} items uploaded to ss_tim")

    if not devices:
        return
    # Add QRs to database and make sure that only QRs that should be decompressed are added to queue
    data["qr"] = qr_code_uploader.upload_qr_codes(data["qr"])

    # Only raw_obj_pit in the 2024 season, but other years also have raw_subj_pit which is why this iterates through datasets
    for dataset in ["raw_obj_pit"]:
        modified_data = []
        for document in data[dataset]:
            # Decompress pit data before uploading
            document = decompressor.Decompressor.decompress_pit_data(
                decompressor.Decompressor, document, dataset
            )
            # Specify query to ensure that each team only has one entry
            db.update_document(dataset, document, {"team_number": document["team_number"]})
            modified_data.append({"team_number": document["team_number"]})
        log.info(f"{len(modified_data)} items uploaded to {dataset}")
        data[dataset] = modified_data
    return data


def validate_apk(device_serial, local_file_path):
    """Loads a .apk file onto a device and checks whether it was done successfully.

    Calls 'adb push' command, which uses the Android Debug Bridge (ADB) to send the APK file
    The -s flag specifies the device_serial by its serial number.
    return_output=True returns the output of adb.
    device_serial is the serial number of the device that apk is being installed on.
    local_file_path is the local APK file path.
    """
    check_success = utils.run_command(
        f"adb -s {device_serial} install -r {local_file_path}", return_output=True
    )
    return check_success


def adb_font_size_enforcer():
    """Enforce tablet font size to 1.30, the largest supported size"""
    devices = get_attached_devices()
    # Wait for USB connection to initialize
    time.sleep(0.1)
    for device in devices:
        # The -s flag specifies the device by its serial number.
        utils.run_command(
            f"adb -s {device} shell settings put system font_scale 1.30", return_output=False
        )


def get_tablet_file_path_hash(device_id, tablet_file_path):
    """Find the hash of `tablet_file_path`

    The -s flag to adb specifies a device by its serial number.
    The -b flag to sha256sum specifies 'brief,' meaning that only the hash is output.
    """
    tablet_hash = utils.run_command(
        f"adb -s {device_id} shell sha256sum -b {tablet_file_path}", return_output=True
    )
    return tablet_hash.strip("\n")


# Store regex patterns to match files containing either pit or match data
FILENAME_REGEXES = {
    # Matches either objective or subjective QR filenames
    # Format of objective QR file pattern: <qual_num>_<team_num>_<serial_num>_<timestamp>.txt
    # Format of subjective QR file pattern: <qual_num>_<serial_num>_<timestamp>.txt
    "qr": re.compile(
        r"([0-9]{1,3}_[0-9]{1,4}_[A-Z0-9]+_[0-9]+\.txt)|([0-9]{1,3}_[0-9A-Z]+_[0-9]+\.txt)"
    ),
    # Format of objective pit file pattern: <team_number>_pit.json
    "raw_obj_pit": re.compile(r"[0-9]{1,4}_obj_pit\.json"),
}

# Open the tablet serials file to find all device serials
with open(utils.create_file_path("data/tablet_serials.json")) as serial_numbers:
    DEVICE_SERIAL_NUMBERS = json.load(serial_numbers)
TABLET_SERIAL_NUMBERS = {
    serial: key for serial, key in DEVICE_SERIAL_NUMBERS.items() if "Tab" in key
}
PHONE_SERIAL_NUMBERS = {
    serial: key for serial, key in DEVICE_SERIAL_NUMBERS.items() if "Pixel" in key
}
