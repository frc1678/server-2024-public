# Will take a while for csvs to show up
# Might have to switch to new window
from data_transfer import statbotics_communicator as sb
from export_csvs import BaseExport
from typing import List, Dict
import os
from datetime import datetime, date
import csv
import argparse
import logging

log = logging.getLogger(__name__)


def build_matches(comp_key):
    try:
        matches = sb.sb_get_matches(event=comp_key)
    except UserWarning:
        log.error(f"No matches found for event {comp_key}")
        return [], {}
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


def build_specfic_year(year: int):
    events = sb.sb_get_events(year=year)
    event_keys = []
    full_data = []
    failed_events_matches = []
    failed_events_teams = []

    # Specify structure of data by event
    data_by_event: Dict[str, Dict[str, any]] = {}
    column_headers: List[str] = []
    for event in events:
        # Get event key
        event_key = str(event["key"])
        if not data_by_event.get(event_key):
            # Make event key a key
            data_by_event[event_key] = {}
        event_keys.append(event_key)
        for key, value in event.items():
            if key not in column_headers:
                # Add key as a column header
                column_headers.append(key)
            data_by_event[event_key][key] = value
    # Sort column_headers by event key, year, and name first
    full_column_headers = BaseExport.order_headers(column_headers, ["key", "year", "name"])

    match_data = {}
    for event_key in event_keys:
        column_headers_1, built_data_1 = build_matches(event_key)
        if column_headers_1 == [] or built_data_1 == {}:
            failed_events_matches.append(event_key)
            continue
        column_headers_2, built_data_2 = build_teams(event_key)
        if column_headers_2 == [] or built_data_2 == {}:
            failed_events_teams.append(event_key)
            continue

        full_column_headers += column_headers_1
        full_column_headers += column_headers_2
        match_data[event_key] = {**built_data_1, **built_data_2}
        full_data.append({**built_data_1, **built_data_2})
        # Append match_data to full_data
    full_data.append(data_by_event)
    log.error(f"Failed to get matches for events: {', '.join(failed_events_matches)}")
    log.error(f"Failed to get teams for events: {', '.join(failed_events_teams)}")
    return (
        BaseExport.order_headers(
            list(set(full_column_headers)), ["key", "event", "match_number", "year", "name"]
        ),
        full_data,
    )


def write_data(directory_path: str, comp_key=None, type="both", specific_year=None):
    # Specify team, match, or both
    # Both will be a really ugly csv
    if specific_year is not None:
        column_headers, built_data = build_specfic_year(int(specific_year))
        type = "full_year"
    elif type.lower() == "both":
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
        if type == "full_year":
            for single_data in built_data:
                for entry in single_data.values():
                    csv_writer.writerow(entry)
        else:
            for single_data in built_data.values():
                print(single_data)
                csv_writer.writerow(single_data)


def parser():
    """
    Defines the argument options when running the file from the command line

    --comp_key | Define a competition key\n
    --year | Define a specific year\n
    --type | Define if you want team, match, or both
    """
    parse = argparse.ArgumentParser()
    parse.add_argument(
        "--comp_key",
        help="Define a competition key, or enter 'all' for all events",
        default=None,
        action="store",
    )
    parse.add_argument("--year", help="Define a specific year", default=None, action="store")
    parse.add_argument(
        "--type",
        help="Define if you want team, match, or both",
        default=None,
        action="store",
    )
    return parse.parse_args()


if __name__ == "__main__":
    args = parser()

    # find the comp_key
    if args.year is None:
        if args.comp_key is None:
            key = input("Enter a competition key 'all' for all events: ")
        else:
            key = args.comp_key
        specific_year = None
    else:
        key = f"year_{args.year}"
        specific_year = args.year

    # find the type:
    if args.type is None and args.year is None:
        team_or_match = input("What type of csv? team/match/both: ")
    else:
        team_or_match = args.type

    # Currently, csv shows up in server but the file path can be changed
    write_data("data/exports", key, team_or_match, specific_year)
