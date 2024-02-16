from os.path import exists
from data_transfer.database import Database
from send_device_jsons import get_team_list
from utils import read_csv_file
import logging

log = logging.getLogger(__name__)

if __name__ == "__main__":
    DATABASE = Database()

    # Check if the picklist csv exists
    if not exists("data/picklist_upload.csv"):
        log.error("Picklist upload file not found.")
        exit(1)
    # Load the csv file from picklist
    csvdata = read_csv_file("data/picklist_upload.csv")
    teams = []

    for row in csvdata:
        # Check if the positions are numbers
        if row[1].isnumeric():
            # Add the team to the list of teams
            teams.append({"team_number": row[0], "rank": int(row[1])})

    # Get the list of all the teams from the event
    team_list = get_team_list()

    # Just gets the team numbers from picklist
    picklist_team_numbers = list(map(lambda x: x["team_number"], teams))

    # For each team in the list of all competition teams, if it is not in the list of teams in the picklist, add it to the list
    dnp = [item for item in team_list if item not in picklist_team_numbers]

    # Add each pick list object to the database
    for e in teams:
        DATABASE.update_document("picklist", {**e, "dnp": False}, {"team_number": e["team_number"]})

    # Add each dnp team to the database
    for e in dnp:
        DATABASE.update_document(
            "picklist", {"dnp": True, "team_number": e, "rank": -1}, {"team_number": e}
        )
