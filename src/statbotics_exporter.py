# Will take a while for csvs to show up
# Might have to switch to new window
from data_transfer import statbotics_communicator as sb
from export_csvs import BaseExport
from typing import List, Dict
import os
from datetime import datetime, date
import csv


def build_matches(comp_key):
    matches = sb.sb_get_matches(event=comp_key)
    # Specify structure of data by match
    data_by_match: Dict[str, Dict[str, any]] = {}
    column_headers: List[str] = []
    for match in matches:
        # Get match number
        match_num = str(match["match_number"])
        if not data_by_match.get(match_num):
            # Adds match_num as a key
            data_by_match[match_num] = {}
        for key, value in match.items():
            if key not in column_headers:
                # Add key as column header
                column_headers.append(key)
            data_by_match[match_num][key] = value
    # Sort column_headers so match_number is first
    column_headers = BaseExport.order_headers(
        column_headers, ["blue_3", "blue_2", "blue_1", "red_3", "red_2", "red_1", "match_number"]
    )
    return column_headers, data_by_match


def build_teams(comp_key):
    # Statbotics naturally doesn't put in some team data
    teams = sb.sb_get_team_events(event=comp_key)
    # Specify structure of data by team
    data_by_team: Dict[str, Dict[str, any]] = {}
    column_headers: List[str] = []
    for team in teams:
        # Get team number
        team_num = str(team["team"])
        if not data_by_team.get(team_num):
            # Make team number a key
            data_by_team[team_num] = {}
        for key, value in team.items():
            if key not in column_headers:
                # Add key as a column header
                column_headers.append(key)
            data_by_team[team_num][key] = value
    # Sort column_headers by team number first
    column_headers = BaseExport.order_headers(column_headers, ["team_name", "team"])
    return column_headers, data_by_team


def build_all_events():
    events = []
    # There's a limit on how many years get_events can return
    # This is bypassed by doing each year individually
    for i in range(2002, int(date.today().year)):
        # Exclude 2021
        if i != 2021:
            # Join lists together
            events = events + sb.sb_get_events(year=i)
    # Specify structure of data by event
    data_by_event: Dict[str, Dict[str, any]] = {}
    column_headers: List[str] = []
    for event in events:
        # Get event key
        event_key = str(event["key"])
        if not data_by_event.get(event_key):
            # Make event key a key
            data_by_event[event_key] = {}
        for key, value in event.items():
            if key not in column_headers:
                # Add key as a column header
                column_headers.append(key)
            data_by_event[event_key][key] = value
    # Sort column_headers by event key, year, and name first
    column_headers = BaseExport.order_headers(column_headers, ["key", "year", "name"])
    return column_headers, data_by_event


def write_data(directory_path: str, comp_key, type):
    # Specify team, match, or both
    # Both will be a really ugly csv
    if type.lower() == "both":
        column_headers, built_data = build_matches(comp_key)
        team_headers, team_data = build_teams(comp_key)
        # Combine the headers and data
        column_headers = column_headers + team_headers
        built_data = {**built_data, **team_data}
    elif type.lower() == "team":
        column_headers, built_data = build_teams(comp_key)
    elif type.lower() == "match":
        column_headers, built_data = build_matches(comp_key)
    else:
        column_headers, built_data = build_all_events()
    # Write file name
    name = f'statbotics_data_{comp_key}_{type}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
    file_path = os.path.join(directory_path, name)
    with open(file_path, "w") as file:
        # Write headers using the column_headers list
        csv_writer = csv.DictWriter(file, fieldnames=column_headers)
        # Write the header as the first thing
        csv_writer.writeheader()
        # For each item, write the data as a dictionary
        for single_data in built_data.values():
            csv_writer.writerow(single_data)


if __name__ == "__main__":
    key = input("Enter a competition key or 'all' for all events: ")
    if key.lower() != "all":
        team_or_match = input("What type of csv? team/match/both: ")
    else:
        team_or_match = "all"
    # Currently, csv shows up in server but the file path can be changed
    write_data("data/exports", key, team_or_match)
