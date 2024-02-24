#!/usr/bin/env python3

"""Send APK file to tablets over ADB.

Uses subprocess to send an APK to the tablets.
ADB stands for Android Debug Bridge.
"""

import sys
import time
import logging

from data_transfer import adb_communicator

log = logging.getLogger(__name__)


def install_apk(device_serial):
    """Installs chosen APK to either phone or tablet depending on user input.

    Convert serial number to human-readable format.
    """
    device_name = adb_communicator.DEVICE_SERIAL_NUMBERS[device_serial]
    log.info(f"Loading {LOCAL_FILE_PATH} onto {device_name}")
    # Send apk file and get output
    validate = adb_communicator.validate_apk(device_serial, LOCAL_FILE_PATH)
    # If .apk is loaded successfully, ADB will output a string containing 'Success'
    if "Success" in validate:
        DEVICES_WITH_APK.append(device_serial)
        log.info(f"Loaded {LOCAL_FILE_PATH} onto {device_name}")
        log.info(f"APK successfully installed on {device_serial}")
    else:
        log.error(f"Failed Loading {LOCAL_FILE_PATH} onto {device_name}.", file=sys.stderr)


if len(sys.argv) == 2:
    # Extract LOCAL_FILE_PATH from second argument
    # LOCAL_FILE_PATH is a string
    LOCAL_FILE_PATH = sys.argv[1]
else:
    log.error(
        "Error: Local APK file path is not being passed as an argument. Exiting...", file=sys.stderr
    )
    sys.exit(1)

# List of devices to which the apk has already been sent
DEVICES_WITH_APK = []

# Phones and Tablets use different APKs
# This specifies which type of device_serial it will be sent to so it will not send to both
CHOSEN_DEVICE = input("Would you like the apk to be sent to Tablet or Phone?(t/p) ").lower()
if CHOSEN_DEVICE == "t":
    CHOSEN_DEVICE_VALUE = "tablet"
elif CHOSEN_DEVICE == "p":
    CHOSEN_DEVICE_VALUE = "phone"
else:
    log.error("Error: (t)ablet or (p)hone not specified.", file=sys.stderr)
    sys.exit(1)

log.info(f'Attempting to send file "{LOCAL_FILE_PATH}".')

while True:
    DEVICES = adb_communicator.get_attached_devices()
    TABLET_SERIALS, PHONE_SERIALS = [], []
    num_sent = 0

    # Determine if each connected device_serial is a tablet or phone and if it needs the APK
    for serial in DEVICES:
        if serial[0][0] == "H":
            # Only add device_serial if it does not already have the apk
            if serial[0] not in DEVICES_WITH_APK:
                TABLET_SERIALS.append(serial[0])
        if serial[0][0] == "9":
            # Only add device_serial if it does not already have the apk
            if serial[0] not in DEVICES_WITH_APK:
                PHONE_SERIALS.append(serial[0])

    # Wait for USB connection to initialize
    time.sleep(0.1)  #  .1 seconds
    if CHOSEN_DEVICE == "t":
        # APK has been installed onto all connected tablets
        if TABLET_SERIALS == []:
            break
        for device in TABLET_SERIALS:
            install_apk(device)
            num_sent += 1
    if CHOSEN_DEVICE == "p":
        # APK has been installed onto all connected phones
        if PHONE_SERIALS == []:
            break
        for device in PHONE_SERIALS:
            install_apk(device)
            num_sent += 1
    log.info(f"New APK loaded onto {num_sent} devices")
