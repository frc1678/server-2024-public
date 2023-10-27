#!/usr/bin/env python3

"""Houses upload_qr_codes which appends unique QR codes to local competition document.

Checks for duplicates within set of QR codes to add, and the database.
Appends new QR codes to raw.qr.
"""


from data_transfer import database
import utils

import datetime
from ulid import ULID
import logging

log = logging.getLogger(__name__)

local_database = database.Database(port=1678)


def upload_qr_codes(qr_codes):
    """Uploads QR codes into the current competition document.

    Prevents duplicate QR codes from being uploaded to the database.
    qr_codes is a list of QR code strings to upload.
    """
    # Gets the starting character for each QR code type, used to identify QR code type
    schema = utils.read_schema("schema/match_collection_qr_schema.yml")

    # Acquires current qr data using database.py
    qr_data = [qr_code["data"] for qr_code in local_database.find("raw_qr")]

    # Creates a set to store QR codes
    # This is a set in order to prevent addition of duplicate qr codes
    qr = set()

    for qr_code in qr_codes:
        if qr_code in qr_data:
            pass
        # Checks to make sure the qr is valid by checking its starting character. If the starting
        # character doesn't match either of the options, the QR is printed out.
        elif not (
            qr_code.startswith(schema["subjective_aim"]["_start_character"])
            or qr_code.startswith(schema["objective_tim"]["_start_character"])
        ):
            log.warning(f'Invalid QR code not uploaded: "{qr_code}"')
        else:
            qr.add(qr_code)

    # Adds the QR codes to the local database if the set isn't empty
    if qr != set():
        ulid = ULID()
        qr = [
            {
                "data": qr_code,
                "blocklisted": False,
                "override": {},
                "ulid": str(ulid),
                "readable_time": str(ulid.datetime),
            }
            for qr_code in qr
        ]
        local_database.insert_documents("raw_qr", qr)

    return qr
