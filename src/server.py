#! /usr/bin/env python3

"""Contains the server class."""
import console  # DON'T DELETE THIS LINE. This initializes the logging system
import importlib
from typing import List, Type

import yaml

from calculations import reinsert
from calculations import base_calculations
from data_transfer import database, cloud_db_updater
import utils
import logging


log = logging.getLogger(__name__)


class Server:
    """Contains the logic that runs calculations in proper order.

    Calculation classes should contain a `run` method that accepts one argument, an instance of this
    class. They should use the `db` attribute of this server class to communicate with the local
    database.
    """

    CALCULATIONS_FILE = utils.create_file_path("src/calculations.yml")
    TBA_EVENT_KEY = utils.load_tba_event_key_file(utils._TBA_EVENT_KEY_FILE)

    def __init__(self, write_cloud=False):
        self.db = database.Database()
        self.oplog = self.db.client.local.oplog.rs
        if write_cloud:
            self.cloud_db_updater = cloud_db_updater.CloudDBUpdater()
        else:
            self.cloud_db_updater = None
        self.calc_all_data = self.ask_calc_all_data()

        # Option to reinsert raw_qrs, obj_pit, and such
        if write_cloud and self.calc_all_data:
            self.reinsert = input("Reinsert ALL data? (y/N): ")

        self.calculations = self.load_calculations()

    # TODO: optimize this function, this takes a really long time (especially on the old server computer)
    def load_calculations(self) -> List["base_calculations.BaseCalculations"]:
        """Imports calculation modules and creates instances of calculation classes."""
        with open(self.CALCULATIONS_FILE) as f:
            calculation_load_list = yaml.load(f, Loader=yaml.Loader)
        loaded_calcs = []
        # `calculations.yml` is a list of dictionaries, each with an "import_path" and "class_name"
        # key. We need to import the module and then get the class from the imported module.
        for calc in calculation_load_list:
            # Import the module
            try:
                module = importlib.import_module(calc["import_path"])
            except Exception as e:
                log.error(f'{e.__class__.__name__} importing {calc["import_path"]}: {e}')
                continue
            # Get calculation class from module
            try:
                cls: Type["base_calculations.BaseCalculations"] = getattr(
                    module, calc["class_name"]
                )
                # Append an instance of calculation class to the calculations list
                # We pass `self` as the only argument to the `__init__` method of the calculation
                # class so the calculations can get access to server instance variables such as the
                # oplog or the database
                loaded_calcs.append(cls(self))
            except Exception as e:
                log.error(
                    f'{e.__class__.__name__} instantiating {calc["import_path"]}.{calc["class_name"]}: {e}'
                )
        return loaded_calcs

    def run_calculations(self):
        """Run each calculation in `self.calculations` in order"""
        for calc in self.calculations:
            if calc != reinsert.ReinsertCalc:
                calc.run()
            # Run the re-insertion if user entered 'y'
            elif self.reinsert:
                calc.run()

    def ask_calc_all_data(self):
        calc_all_data = input("Run calculations on all data? (y/N): ").lower()

        if calc_all_data in ["y", "yes"]:
            return True
        else:
            return False

    # TODO: make a new input that asks for reinsert
    # if true, run reinsert.py
    def run(self):
        """Starts server cycles, runs in infinite loop"""
        while True:
            self.run_calculations()
            if write_cloud:
                self.cloud_db_updater.write_db_changes()
            self.calc_all_data = self.ask_calc_all_data()


if __name__ == "__main__":
    write_cloud_question = input("Write changes to cloud DB? (y/N): ").lower()
    if write_cloud_question in ["y", "yes"]:
        write_cloud = True
    else:
        write_cloud = False
    server = Server(write_cloud)
    server.run()
