#!/usr/bin/env python3

"""Sets up a machine for use or testing of the server.

To be run for every new clone of server.
"""

import os
import subprocess
import venv
import logging

import utils

log = logging.getLogger(__name__)


class Logger:
    def __enter__(self):
        """Creates file and returns self"""
        self.name = "setup_environment.log"
        self.path = utils.create_file_path(self.name)
        self.log_file = open(self.path, "w")
        self.should_destroy_log = False
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Checks if the discard method has been called

        i.e. if it ran successfully and if we should discard the log"""
        self.log_file.close()
        if self.should_destroy_log:
            os.remove(self.path)
        else:
            log.warning("\n\nSomething broke! Check setup_environment.log for details")

    def log(self, message: str, should_output: bool = True):
        """Adds something to the file, prints it by default"""
        self.log_file.write(f"\n{message}")
        if should_output:
            log.info(message)

    def discard(self):
        """Changes the state of the file being destroyed"""
        self.should_destroy_log = True


# Creates data folder
utils.create_file_path("data/")

# Creates path by joining the base directory and the target directory
TARGET_PATH = utils.create_file_path(".venv", False)

# Only run if file is directly called
if __name__ == "__main__":
    with Logger() as LOGGER:
        log = LOGGER.log
        # Create virtual environment
        log("Creating Virtual Environment...")
        # Clear any existing environments with clear=True
        # Install pip directly into installation
        # Set prompt to 'venv' instead of '.venv'
        venv.create(TARGET_PATH, clear=True, with_pip=True, prompt="venv")
        log("Virtual Environment Created")

        # Install pip packages
        # Set create_directories to false to avoid trying to create directory for pip
        if os.name == "nt":
            # Windows uses a Scripts directory instead of a bin directory
            PIP_PATH = utils.create_file_path(".venv/Scripts/pip", False)
        else:
            PIP_PATH = utils.create_file_path(".venv/bin/pip", False)
        REQUIREMENTS_PATH = utils.create_file_path("requirements.txt")
        log("Installing PyPI Packages...")
        # Runs /path/to/pip install -r /path/to/requirements.txt
        # Sets check to True to force check that pip exited without errors
        # Pipes pip output to /dev/null to avoid cluttering the terminal
        # All pip warnings/errors still print to terminal because stderr is not redirected
        install_wheel = subprocess.run(
            [PIP_PATH, "install", "wheel"],
            check=True,
            stdout=LOGGER.log_file,
            stderr=LOGGER.log_file,
        )
        install_reqs = subprocess.run(
            [PIP_PATH, "install", "-r", REQUIREMENTS_PATH],
            check=True,
            stdout=LOGGER.log_file,
            stderr=LOGGER.log_file,
        )
        log("Environment Setup Complete")
        if install_wheel.returncode == 0 and install_reqs.returncode == 0:
            LOGGER.discard()
