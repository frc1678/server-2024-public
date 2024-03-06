"""This file houses a calculation class that allows the server to input data"""
from data_transfer import adb_communicator
import calculations.base_calculations
import utils

import datetime
from ulid import ULID
import logging
import time

import sys
from console import console

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


class QRInput(calculations.base_calculations.BaseCalculations):
    def __init__(self, server):
        super().__init__(server)
        self.schema = utils.read_schema("schema/match_collection_qr_schema.yml")

    def upload_qr_codes(self, qr_codes):
        # Acquires current qr data
        qr_data = [qr_code["data"] for qr_code in self.server.db.find("raw_qr")]
        qr = set()

        for qr_code in qr_codes:
            # Check for duplicate QR codes
            if qr_code in qr_data:
                log.warning(f"Duplicate QR code not uploaded\t{qr_code}")
                continue
            # Checks to make sure the qr is valid by checking its starting character
            elif qr_code.startswith(
                self.schema["subjective_aim"]["_start_character"]
            ) or qr_code.startswith(self.schema["objective_tim"]["_start_character"]):
                qr.add(qr_code)
            else:
                log.warning(f'Invalid QR code not uploaded: "{qr_code}"')

        if qr != set():
            qr = [
                {
                    "data": qr_code,
                    "blocklisted": False,
                    "override": {},
                    "ulid": str(ULID()),
                    "readable_time": str(ULID().datetime),
                }
                for qr_code in qr
            ]
            self.server.db.insert_documents("raw_qr", qr)

    def run(self, test_input=None):
        """Grabs QR codes from user using stdin.read(), each qr is separated by a newline"""
        # Get calc start time
        start_time = time.time()

        # If test_input is assigned to a value (in tests), set qr_codes to test_input.
        # Otherwise, get input from user.
        # Used because there is no good way to test stdin.read()
        if test_input:
            qr_codes = test_input
        else:
            console.print("[green]ENTER DATA: ")
            qr_codes = (
                sys.stdin.read()
            )  # stdin.read() is used so that pressing enter does not end the input | Use CTRL+D instead

        # Upload qr codes as list
        if qr_codes != "":
            self.upload_qr_codes(qr_codes.strip().split("\n"))
        adb_communicator.pull_device_data()
        end_time = time.time()
        # Get total calc time
        total_time = end_time - start_time
        # Write total calc time to log
        log.info(f"qr_input calculation time: {round(total_time, 2)} sec")
