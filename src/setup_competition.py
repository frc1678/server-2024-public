#!/usr/bin/env python3

"""Sets up the MongoDB document for a competition, should be run before every competition."""

import re

from pymongo import MongoClient

import utils
import logging

log = logging.getLogger(__name__)


def setup_connection(specifier, COMPETITION_KEY):
    CLIENT = MongoClient(specifier)
    # Checks that the competition inputted by the user is not already in the database
    if COMPETITION_KEY in CLIENT.list_database_names():
        log.warning(f"WARNING: The competition {COMPETITION_KEY} already exists.")
        if not utils.get_boolean_input("Continue anyway?"):
            raise Exception("Database already exists")
    # Creates the competition.txt file
    # Also writes the competition code to it so it can be used in other scripts
    with open(utils.create_file_path(utils._TBA_EVENT_KEY_FILE), "w") as file:
        file.write(COMPETITION_KEY)

    return CLIENT


log.info("Competition setup started")
COMPETITION_KEY = input("Input the competition code from TBA: ")
# Use a regular expression to determine if competition code is in the correct format
# First capture group: Matches 4 digits
# Second capture group: Matches 1 or more letters
CODE_MATCH = re.fullmatch(r"(?P<year>[0-9]{4})(?P<comp_code>.+)", COMPETITION_KEY)
if CODE_MATCH is None:
    raise ValueError("Competition code is not in the correct format")

setup_connection("mongodb://localhost:1678", COMPETITION_KEY)

from data_transfer import database

DB = database.Database()
DB.setup_db()

CLOUD_DB_PERMISSION = utils.get_boolean_input("Would you like to add this database to the cloud?")
if CLOUD_DB_PERMISSION:
    from data_transfer import cloud_db_updater

    connection_string = cloud_db_updater.CloudDBUpdater.get_connection_string()
    # Checks if competition key exists in the cloud
    setup_connection(connection_string, COMPETITION_KEY)
    CLOUD_DB = database.Database(connection=connection_string)
    # Created indexes for the database
    CLOUD_DB.setup_db()

log.info("Competition setup finished")
