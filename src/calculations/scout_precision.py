#!/usr/bin/env python3
"""Calculates scout precisions to determine scout accuracy compared to TBA."""

from datetime import datetime

from calculations.base_calculations import BaseCalculations
from data_transfer import tba_communicator
import utils
import time
import logging

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


class ScoutPrecisionCalc(BaseCalculations):
    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["unconsolidated_totals"]
        self.overall_schema = utils.read_schema("schema/calc_scout_precision_schema.yml")

    def find_updated_scouts(self):
        """Returns a list of scout names that appear in entries_since_last"""
        scouts = set()
        for entry in self.entries_since_last():
            # Prevents error from not having a team num
            if "scout_name" in entry["o"].keys():
                scouts.add(entry["o"]["scout_name"])
            # If the doc was updated, need to manually find the document
            elif entry["op"] == "u":
                document_id = entry["o2"]["_id"]
                if (
                    query := self.server.db.find(entry["ns"].split(".")[-1], {"_id": document_id})
                ) and "scout_name" in query[0].keys():
                    scouts.add(query[0]["scout_name"])
        return list(scouts)

    def calc_scout_precision(self, scout_sims):
        """Averages all of a scout's in-match errors to get their overall error in a competition."""
        calculations = {}
        for calculation, schema in self.overall_schema["calculations"].items():
            required = schema["requires"]
            datapoint = required.split(".")[1]
            all_sim_errors = []
            for document in scout_sims:
                if document.get(datapoint) is not None:
                    all_sim_errors.append(document[datapoint])
            if all_sim_errors:
                calculations[calculation] = abs(self.avg(all_sim_errors))
        return calculations

    def calc_ranks(self, scouts):
        """Ranks a scout based on their overall precision."""
        for rank, schema in self.overall_schema["ranks"].items():
            for scout in scouts:
                # If there is no scout precision, set it to None
                if schema["requires"].split(".")[1] not in scout.keys():
                    scout[schema["requires"].split(".")[1]] = None

            # This is a bit complex, but works as follows. It constructs a tuple for every scout in the list, where the first value
            # is whether the scout precision is None, and the second is the value itself. Tuples are sorted item by item, so those
            # with False as the first value (if its not None) will come before those where it is true (if it is None), because False < True
            scouts = sorted(
                scouts,
                key=lambda s: (
                    s[schema["requires"].split(".")[1]] is None,
                    s[schema["requires"].split(".")[1]],
                ),
            )

            # Go through the list and assign the ranks accordingly
            for i in range(len(scouts)):
                scouts[i][rank] = i + 1

            # Delete scout_precision if it is None (So it doesn't break validation)
            for scout in scouts:
                if scout[schema["requires"].split(".")[1]] == None:
                    del scout[schema["requires"].split(".")[1]]

        return scouts

    def update_scout_precision_calcs(self, scouts):
        """Creates overall precision updates."""
        updates = []
        for scout in scouts:
            scout_sims = self.server.db.find("sim_precision", {"scout_name": scout})
            update = {}
            update["scout_name"] = scout
            if (scout_precision := self.calc_scout_precision(scout_sims)) != {}:
                update.update(scout_precision)
            updates.append(update)
        updates = self.calc_ranks(updates)
        return updates

    def run(self):
        # Get calc start time
        start_time = time.time()
        scouts = self.find_updated_scouts()

        if self.calc_all_data:
            self.server.db.delete_data("scout_precision")

        for update in self.update_scout_precision_calcs(scouts):
            self.server.db.update_document(
                "scout_precision", update, {"scout_name": update["scout_name"]}
            )
        end_time = time.time()
        # Get total calc time
        total_time = end_time - start_time
        # Write total calc time to log
        log.info(f"scout_precision calculation time: {round(total_time, 2)} sec")
