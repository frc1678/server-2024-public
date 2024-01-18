#!/usr/bin/env python3

"""Adds QR codes to a blocklist in the local database based on match number, blocklists
a specific QR code based on match number and tablet serial number, or overrides datatapoins
for specific TIMs based on match number and team number.

If rollback match is selected, all QR codes from matches with the user inputted match number are
blocklisted. If blocklist a specific QR is selected, all QR codes from a specific
tablet serial number, and match number are added to the blocklist. If edit team data for a
specific match is selected, all QR codes from a specific TIM are overriden.
"""

import re
import sys

from data_transfer import database
import utils
import logging
import console

db = database.Database()

log = logging.getLogger(__name__)
# Takes user input to find which operation to do
ROLLBACK_BLOCKLIST_OR_DATA = input(
    "Rollback a match (0), blocklist specific qrs (1), or edit scout data for a specific match (2)? (0,1,2): "
)

# If user doesn't enter a valid option, exit
if ROLLBACK_BLOCKLIST_OR_DATA not in ["0", "1", "2"]:
    print("Please enter a valid number", file=sys.stderr)
    sys.exit()

# Find if the user wants to UNDO this action
UNDO = input(
    f"Do you want to {'UNDO blocklisting' if ROLLBACK_BLOCKLIST_OR_DATA != '2' else 'CLEAR overrides on'} this {['match', 'qr', 'qr'][int(ROLLBACK_BLOCKLIST_OR_DATA)]}? (y/N)"
    # There's two occurences of 'qr' because that's what the code was written to handle and I wasn't about to change it when I could just add 'qr'
)
UNDO = UNDO.lower() == "y"


log.warning(
    f"Data from matching QR codes will be {'reset' if UNDO else 'blocklisted' if ROLLBACK_BLOCKLIST_OR_DATA != '2' else 'overriden at consolidation'}"
)

# User input for match to delete
MATCH = input(
    f"Enter the match to {'blocklist' if ROLLBACK_BLOCKLIST_OR_DATA != '2' else 'edit'}: "
)

# If the user inputted match number is not a number, exit
if not MATCH.isnumeric():
    print("Please enter a number")
    sys.exit()

# Opens the schema document, to be used in regexes
SCHEMA = utils.read_schema("schema/match_collection_qr_schema.yml")

# Stores all of the elements of the regex to be joined to a string later
PATTERN_ELEMENTS = [
    ".*",  # Matches any character
    SCHEMA["generic_data"]["match_number"][0] + MATCH,  # Matches the match number
    "\\" + SCHEMA["generic_data"]["_separator"],  # Matches the generic separator
    ".*",  # Matches any character
]

# If the user requests to blocklist a specific QR code
if ROLLBACK_BLOCKLIST_OR_DATA == "1":
    # Takes user input for scout name
    SCOUT_NAME = input("Enter the scout name of the QR code to blocklist: ").upper()
    # Modifies the regex pattern elements to include the scout name
    PATTERN_ELEMENTS.insert(4, (SCHEMA["generic_data"]["scout_name"][0] + SCOUT_NAME + ".*"))
elif ROLLBACK_BLOCKLIST_OR_DATA == "2":
    # Takes user input for scout name
    SCOUT_NAME = input("Enter the scout name of the QR to override: ").upper()
    # Creates pattern used to check for the scout name surrounded by text on either side
    PATTERN_ELEMENTS.insert(4, (SCHEMA["generic_data"]["scout_name"][0] + SCOUT_NAME + ".*"))
    # Takes user input for data point name
    DATA_NAME = input(
        f"Enter the name of the TIM data point to edit for {SCOUT_NAME} in match {MATCH}: "
    )
    # Takes user input for the new value
    NEW_VALUE = input(
        f'Enter the new value for the data point {DATA_NAME} (input is converted to int/float/bool if possible unless in ""): '
    )

    # Convert new value to correct type I think I didn't write this
    if NEW_VALUE.isdecimal():
        NEW_VALUE = int(NEW_VALUE)
    elif "." in NEW_VALUE and NEW_VALUE.replace(".", "0", 1).isdecimal():
        NEW_VALUE = float(NEW_VALUE)
    elif (l := NEW_VALUE.lower()) in ["true", "false"]:
        NEW_VALUE = {"true": True, "false": False}[l]
    elif NEW_VALUE[0] == NEW_VALUE[-1] == '"':
        NEW_VALUE = NEW_VALUE[1:-1]

# Stores all regex pattern objects
PATTERNS = []

# Compiles PATTERN_ELEMENTS into a regex pattern object
PATTERNS.append(re.compile("".join(PATTERN_ELEMENTS)))

# Stores the already blocklisted QR codes from the local database
BLOCKLISTED_QRS = db.find("raw_qr", {"blocklisted": True})

# Counts the numbers of QR codes newly blocklisted in this run
num_blocklisted = 0

for qr_code in db.find("raw_qr"):
    # If the QR code is already blocklisted, go to the next QR code
    if (not UNDO) and qr_code in BLOCKLISTED_QRS:
        continue
    # Iterates through all regex pattern objects
    # Regex patterns in PATTERN are used to find QRs with specified scout names or other strings
    for PATTERN in PATTERNS:
        if re.search(PATTERN, qr_code["data"]) is None:
            # If the pattern doesn't match, go to the next QR code
            break
    # If none of the other statements are true, blocklist it
    else:
        if ROLLBACK_BLOCKLIST_OR_DATA == "2":
            # Uses the update_qr_data_override function to change the value of override[DATA_NAME] to NEW_VALUE
            db.update_qr_data_override({"data": qr_code["data"]}, DATA_NAME, NEW_VALUE, clear=UNDO)
            log.debug(f"Updated overrides for {SCOUT_NAME} in match {MATCH}")
        else:
            # Uses the update_qr_blocklist_status function to change the value of blocklisted to True, or False if undoing
            db.update_qr_blocklist_status({"data": qr_code["data"]}, blocklist=not UNDO)
        num_blocklisted += 1

if num_blocklisted == 0:
    log.warning(
        f"No QR codes were {'overriden' if ROLLBACK_BLOCKLIST_OR_DATA == '2' else 'blocklisted'}"
    )
else:
    log.debug(f"Successfully updated {num_blocklisted} QR codes")
