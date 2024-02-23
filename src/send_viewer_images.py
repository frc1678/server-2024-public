#!/usr/bin/env python3

"""Send pit robot images to the Download folder of the viewer phones."""

import os
import re
from typing import Dict
import utils
from data_transfer import adb_communicator
import logging

log = logging.getLogger(__name__)

IMAGE_PATH_PATTERN = re.compile(r"([0-9]+)_(full_robot|side|front|mechanism_[0-9]+)\.jpg")


def find_robot_images() -> Dict[str, str]:
    """Iterate through the data/devices folder to find all robot images."""
    paths = {}
    for device in os.listdir(utils.create_file_path("data/devices")):
        # Check folder names to only look for images from phones
        if device not in adb_communicator.PHONE_SERIAL_NUMBERS:
            continue
        device_dir = utils.create_file_path(f"data/devices/{device}/")
        for file in os.listdir(device_dir):
            full_local_path = os.path.join(device_dir, file)
            # Tries to match the file name with the regular expression
            result = re.fullmatch(IMAGE_PATH_PATTERN, file)
            # If the regular expression matched
            if result:
                paths.update({file: full_local_path})
    return paths


def send_images() -> None:
    """Push images to the Download folder of the viewer phones."""
    for device in adb_communicator.get_attached_devices():
        if device not in adb_communicator.PHONE_SERIAL_NUMBERS:
            continue
        images_sent = 0
        for filename, full_path in find_robot_images().items():
            adb_communicator.push_file(
                device, full_path, f"storage/emulated/0/Download/robot_pictures/{filename}"
            )
            images_sent += 1
        log.info(f"Sent {images_sent} photos to {adb_communicator.DEVICE_SERIAL_NUMBERS[device]}")


if __name__ == "__main__":
    send_images()
