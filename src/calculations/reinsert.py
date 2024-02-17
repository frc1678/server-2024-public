"""Re-inserts obj_pit, ss_team, ss_tim, and raw_qr data in the
   local database every time ask_calc_all_data == True.
   
   We do this because if the server loop crashes between insertion
   in the local DB and insertion in the cloud DB, re-running server
   will not upload certain data into the cloud since it is never calculated"""

from calculations import base_calculations


class ReinsertCalc(base_calculations.BaseCalculations):
    def __init__(self, server):
        super().__init__(server)
        self.collections = ["obj_pit", "ss_team", "ss_tim", "raw_qr"]

    def run(self):
        for collection in self.collections:
            data = self.server.db.find(collection)
            if data != []:
                self.server.db.delete_data(collection)
                self.server.db.insert_documents(collection, data)
