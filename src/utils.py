#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Holds variables + functions that are shared across server files."""

import logging
import os
from pathlib import Path
import shlex
import subprocess
import sys
import traceback

from calculations.base_calculations import BaseCalculations

try:
    import yaml
except ImportError:
    print("PyYaml not found, load schema is unavailable", file=sys.stderr)

# Set the basic config for logging functions
logging.basicConfig(
    filename='server.log', level='NOTSET', filemode='a', format='%(asctime)s %(message)s'
)


def create_file_path(path_after_main, create_directories=True) -> str:
    """Joins the path of the directory this script is in with the path that is passed

    to this function. path_after_main is the path from inside the main directory.
    For example, the path_after_main for server.py would be 'server.py' because it is located
    directly in the main directory. create_directories will create the directories in the path if
    they do not exist. Assumes that all files names include a period, and all paths are input in
    Linux/Unix style. create_directories defaults to True.
    """
    # Removes trailing slash in 'path_after_main' (if it exists) and split by '/'
    path_after_main = path_after_main.rstrip('/').split('/')
    if create_directories is True:
        # Checks if the last item in the path is a file
        if '.' in path_after_main[-1]:
            # Only try to create directories if there are directories specified before filename
            if len(path_after_main) > 1:
                # The '*' before the variable name expands the list into arguments for the function
                directories = os.path.join(*path_after_main[:-1])
            # Make directories a blank string
            else:
                directories = ''
        # The last item is a directory
        else:
            directories = os.path.join(*path_after_main)
        # 'os.makedirs' recursively creates directories (i.e. it will
        # Create multiple directories, if needed)
        os.makedirs(os.path.join(MAIN_DIRECTORY, directories), exist_ok=True)
    return os.path.join(MAIN_DIRECTORY, *path_after_main)


def get_bool(value: str) -> bool:
    """Get boolean from string."""
    if value.upper() in ["1", "T", "TRUE"]:
        return True
    if value.upper() in ["0", "F", "FALSE"]:
        return False
    raise ValueError(f"Unable to convert {value} to boolean.")


def catch_function_errors(fn, *args, **kwargs):
    """Returns function return value or None if there are errors."""
    try:
        result = fn(*args, **kwargs)
    # Keyboard interrupts should stop server
    except KeyboardInterrupt:
        raise
    # Notify user that error occurred
    except Exception as err:
        logging.error(f'{err}\n{"".join(traceback.format_stack()[:-1])}')
        print(f'Function {fn.__name__}: {err.__class__} - {err}')
        result = None
    return result


def log_warning(warning: str):
    """Logs warnings to server.log 'warning' is the warning message.

    Logs to server.log in this directory.
    """
    # Logs warning
    logging.warning(f'{warning}\n')
    # Prints warning to console
    print(f'WARNING: {warning}', file=sys.stderr)


def log_info(info: str):
    """Logs info to server.log.

    'info' is the information being logged to server.log in this directory.
    """
    # Logs info
    logging.info(f'{info}\n')


def log_debug(debug: str):
    """Logs debug to server.log.

    'debug' is the message being logged to server.log in this directory.
    """
    # Logs debug
    logging.debug(f'{debug}\n')


def run_command(command, return_output=False):
    """Runs a command using subprocess.

    command (string) is the terminal command to be run returns the standard output of the command
    if return_output is True.
    """
    # Use shlex.split to preserve spaces within quotes and preserve the quotes
    command = shlex.split(command, posix=False)
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            delim = f"\n{'-'*20}\n"
            raise Exception(
                delim.join(
                    [
                        f'utils.run_command: error in command \"{" ".join(command)}\"',
                        'Captured stdout:',
                        result.stdout.decode('utf-8'),
                        'Captured stderr:',
                        result.stderr.decode('utf-8'),
                    ]
                )
            )
        return result.stdout.decode('utf-8').replace('\r\n', '\n') if return_output else None
    except FileNotFoundError:
        raise Exception(f'utils.run_command: unknown command {command[0]}')


avg = BaseCalculations.avg


def read_schema(schema_file_path: str) -> dict:
    """Reads schema files and returns them as a dictionary.

    schema_filepath is the relative file path compared to where the script is executed
    returns a dictionary generated by opening the schema document with yaml.
    """
    schema_files = ['schema/' + filename for filename in os.listdir(create_file_path('schema'))]
    # Checks if the schema_file_path is valid
    if schema_file_path not in schema_files:
        raise FileNotFoundError('File does not exist within the Schema Folder')

    # Opens the schema file and returns it as a dictionary
    with open(create_file_path(schema_file_path, False), 'r') as schema_file:
        # Specify loader to avoid warnings about default loader
        return yaml.load(schema_file, yaml.Loader)


def get_schema_filenames() -> set:
    """Get all the file names of schema files from the collection_schema"""
    schema = read_schema("schema/collection_schema.yml")
    schema_filenames = []
    for schema in schema["collections"].values():
        schema_filename = schema["schema"]
        if schema_filename is not None:
            schema_filenames.append(schema_filename)
    return set(schema_filenames)


# The root directory of the project
# Gets two directories up from the current file
MAIN_DIRECTORY = Path(os.path.abspath(__file__)).parents[1]


def load_tba_event_key_file(file_path):
    try:
        # Specifies which event - string such as '2020cada'.
        with open(create_file_path(file_path)) as file:
            # Remove trailing newline (if it exists) from file data.
            # Many file editors will automatically add a newline at the end of files.
            return file.read().rstrip('\n')
    except FileNotFoundError:
        log_warning(f'ERROR Loading TBA Key: File {file_path} NOT FOUND')
        return None


_TBA_EVENT_KEY_FILE = 'data/competition.txt'
TBA_EVENT_KEY = load_tba_event_key_file(_TBA_EVENT_KEY_FILE)