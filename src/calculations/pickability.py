from calculations import base_calculations
import utils
import logging
import time

log = logging.getLogger(__name__)
server_log = logging.FileHandler("server.log")
log.addHandler(server_log)


class PickabilityCalc(base_calculations.BaseCalculations):
    """This class calculates pickability"""

    def __init__(self, server):
        super().__init__(server)
        self.pickability_schema = utils.read_schema("schema/calc_pickability_schema.yml")
        self.get_watched_collections()

    def get_watched_collections(self):
        """Reads from the schema file to generate the correct watched collections"""
        self.watched_collections = set()
        for calc in self.pickability_schema["calculations"]:
            for sub_calc in self.pickability_schema["calculations"][calc]:
                if "." in sub_calc:
                    self.watched_collections.add(sub_calc.split(".")[0])

    def calculate_pickability(self, calc_name: str, team_data: dict) -> float:
        """Calculates first and second pickability

        calc_name is which pickability to calculate (e.g. first or second)
        team_data is the data required to perform the weighted sum
        returns the weighted sum
        """
        weighted_sum = 0
        for calc, weighted_value in self.pickability_schema["calculations"][
            calc_name
        ].items():  # Datapoints of first or second pickability
            # Turn the key and weights into a list to take the product of
            if isinstance(weighted_value, list):
                calcs = [calc] + weighted_value
            else:
                calcs = [calc, weighted_value]
            for c in calcs:
                if isinstance(c, str) and "." not in calc:  # Ignore 'type' in schema
                    break
            else:
                # Find the product of the key and weights
                product = 1
                for c in calcs:
                    if not isinstance(c, str):
                        product *= c
                        continue
                    collection, datapoint = c.split(".")
                    if not (collection in team_data and datapoint in team_data[collection]):
                        return  # Can't calculate this pickability
                    product *= team_data[collection][datapoint]
                weighted_sum += product
        return weighted_sum

    def update_pickability(self):
        """Creates updated pickability documents"""
        updates = []
        for team in self.get_updated_teams():
            # Data that is needed to calculate pickability
            team_data = {}
            # Get each calc name and search for it in the database
            for collection in self.watched_collections:
                if query := self.server.db.find(collection, {"team_number": team}):
                    team_data[collection] = query[0]
            update = {"team_number": team}
            for calc_name in self.pickability_schema["calculations"]:
                value = self.calculate_pickability(calc_name, team_data)
                if value is None:
                    log.error(f"{calc_name} could not be calculated for team: {team}")
                    continue
                update[calc_name] = value
                updates.append(update)
        return updates

    def run(self) -> None:
        """Detects when and for which teams to calculate pickabilty"""
        # Get calc start time
        start_time = time.time()
        # Finds oplog entries in the watched collections
        entries = self.entries_since_last()
        if entries == []:
            return
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("pickability")

        for update in self.update_pickability():
            self.server.db.update_document(
                "pickability", update, {"team_number": update["team_number"]}
            )
        end_time = time.time()
        # Get total calc time
        total_time = end_time - start_time
        # Write total calc time to log
        log.info(f"pickability calculation time: {round(total_time, 2)} sec")
