#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Sets up the MongoDB document for a competition, should be run before every competition."""

import re

from pymongo import MongoClient

import utils


def setup_connection(specifier, COMPETITION_KEY):
    # Makes connection with local database through port 27017, the default listening port of MongoDB
    CLIENT = MongoClient(specifier)
    # Checks that the competition inputted by the user is not already in the database
    if COMPETITION_KEY in CLIENT.list_database_names():
        print(f'WARNING: The competition {COMPETITION_KEY} already exists.')
        if input("Continue anyway? (y or n): ").lower().strip() not in ['y', 'yes']:
            raise Exception('Database already exists')
    # Creates the competition.txt file
    # Also writes the competition code to it so it can be used in other scripts
    with open(utils.create_file_path(utils._TBA_EVENT_KEY_FILE), 'w') as file:
        file.write(COMPETITION_KEY)

    return CLIENT


print('Competition setup started')
COMPETITION_KEY = input('Input the competition code from TBA: ')
# Use a regular expression to determine if competition code is in the correct format
# First capture group: Matches 4 digits
# Second capture group: Matches 1 or more letters
CODE_MATCH = re.fullmatch(r'(?P<year>[0-9]{4})(?P<comp_code>.+)', COMPETITION_KEY)
if CODE_MATCH is None:
    raise ValueError('Competition code is not in the correct format')

setup_connection("mongodb://localhost:1678", COMPETITION_KEY)

from data_transfer import database

DB = database.Database()

# Creates indexes for the database
DB.set_indexes()

CLOUD_DB_PERMISSION = input('Would you like to add this database to the cloud? (y or n): ')

if CLOUD_DB_PERMISSION.lower().strip() in ['y', 'yes']:
    from data_transfer import cloud_db_updater

    connection_string = cloud_db_updater.CloudDBUpdater.get_connection_string()
    # Checks if competition key exists in the cloud
    setup_connection(connection_string, COMPETITION_KEY)
    CDB = database.Database(connection_string)
    # Created indexes for the database
    CDB.set_indexes()
print('Competition setup finished')
