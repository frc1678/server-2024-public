#!/usr/bin/env python3

"""Holds functions for database communication.

All communication with the MongoDB local database go through this file.
"""
import os
from collections import OrderedDict
from typing import Any, Optional, Union

import pymongo

import start_mongod
import utils
import logging

log = logging.getLogger(__name__)

# Load collection names
COLLECTION_SCHEMA = utils.read_schema("schema/collection_schema.yml")
COLLECTION_NAMES = [collection for collection in COLLECTION_SCHEMA["collections"].keys()]
VALID_COLLECTIONS = [
    "auto_paths",
    "auto_pim",
    "obj_team",
    "obj_tim",
    "subj_team",
    "subj_tim",
    "tba_team",
    "tba_tim",
    "raw_qr",
    "predicted_aim",
    "predicted_alliances",
    "predicted_team",
    "pickability",
    "raw_obj_pit",
]

# Start mongod and initialize replica set
start_mongod.start_mongod()


def check_collection_name(collection_name: str) -> None:
    """Checks if a collection name exists, prints a warning if it doesn't"""
    if collection_name not in COLLECTION_NAMES:
        log.warning(f'database.py: Unexpected collection name: "{collection_name}"')


class Database:
    """Utility class for the database, performs CRUD functions on local and cloud databases"""

    def __init__(
        self,
        tba_event_key: str = utils.load_tba_event_key_file(utils._TBA_EVENT_KEY_FILE),
        connection: str = "localhost",
        port: int = start_mongod.PORT,
    ) -> None:
        self.connection = connection
        self.port = port
        self.client = pymongo.MongoClient(connection, port)
        production_mode: bool = os.environ.get("SCOUTING_SERVER_ENV") == "production"
        self.name = tba_event_key if production_mode else f"test{tba_event_key}"
        self.db = self.client[self.name]

    def setup_db(self):
        self.set_indexes()
        # All document names and their files
        coll_to_path = self._get_all_schema_names()
        for entry in coll_to_path.keys():
            self._enable_validation(entry, coll_to_path[entry])

    def set_indexes(self) -> None:
        """Adds indexes into competition collections"""
        for collection in COLLECTION_SCHEMA["collections"]:
            collection_dict = COLLECTION_SCHEMA["collections"][collection]
            if collection_dict["indexes"] is not None:
                for index in collection_dict["indexes"]:
                    self.db[collection].create_index(
                        [(field, pymongo.ASCENDING) for field in index["fields"]],
                        unique=index["unique"],
                    )

    def find(self, collection: str, query: dict = {}) -> list:
        """Finds documents in 'collection', filtering by 'filters'"""
        check_collection_name(collection)
        return list(self.db[collection].find(query))

    def get_tba_cache(self, api_url: str) -> Optional[dict]:
        """Gets the TBA Cache of 'api_url'"""
        return self.db.tba_cache.find_one({"api_url": api_url})

    def update_tba_cache(self, data: Any, api_url: str, etag: Optional[str] = None) -> None:
        """Updates one TBA Cache at 'api_url'"""
        write_object = {"data": data}
        if etag is not None:
            write_object["etag"] = etag
        self.db.tba_cache.update_one({"api_url": api_url}, {"$set": write_object}, upsert=True)

    def delete_data(self, collection: str, query: dict = {}) -> None:
        """Deletes data in 'collection' according to 'filters'"""
        check_collection_name(collection)
        if "raw" in collection:
            log.warning(f"Attempted to delete raw data from collection {collection}")
            return
        self.db[collection].delete_many(query)

    def insert_documents(self, collection: str, data: Union[list, dict]) -> None:
        """Inserts documents from 'data' list in 'collection'"""
        check_collection_name(collection)
        if data != [] and isinstance(data, list):
            self.db[collection].insert_many(data)
        elif data != {} and isinstance(data, dict):
            self.db[collection].insert_one(data)
        else:
            log.warning(
                f'database.py: data for insertion to "{collection}" is not a list or dictionary, or is empty'
            )

    def update_document(
        self,
        collection: str,
        new_data: dict,
        query: dict,
    ) -> None:
        """Updates one document that matches 'query' with 'new_data', uses upsert"""
        check_collection_name(collection)
        if collection == "raw_qr":
            log.warning(f"Attempted to modify raw qr data")
            return
        self.db[collection].update_one(query, {"$set": new_data}, upsert=True)

    def update_many(
        self,
        collection: str,
        new_data: dict,
        query: dict,
    ) -> None:
        """Updates many documents that match 'query' with 'new_data', uses upsert"""
        check_collection_name(collection)
        if collection == "raw_qr":
            log.warning(f"Attempted to modify raw qr data")
            return
        self.db[collection].update_many(query, {"$set": new_data}, upsert=True)

    def update_qr_blocklist_status(self, query, blocklist=True) -> None:
        """Changes the status of a raw qr matching 'query' from blocklisted: true to blocklisted: false
        Lowers risk of data loss from using normal update."""
        self.db["raw_qr"].update_one(query, {"$set": {"blocklisted": blocklist}})

    def update_qr_data_override(self, query, datapoint, new_value, clear=False) -> None:
        """Changes the override of a datapoint of a raw qr matching 'query' to new_value
        Lowers risk of data loss from using normal update."""
        if clear:
            self.db["raw_qr"].update_one(query, {"$set": {f"override": {}}})
        else:
            self.db["raw_qr"].update_one(query, {"$set": {f"override.{datapoint}": new_value}})

    def _enable_validation(self, collection: str, file: str):
        sch = utils.read_schema("schema/" + file)
        sch = mongo_convert(sch)
        cmd = OrderedDict(
            [
                ("collMod", collection),
                ("validator", {"$jsonSchema": sch}),
                ("validationLevel", "moderate"),
            ]
        )
        self.db.command(cmd)

    def _get_all_schema_names(self) -> dict:
        out = {}
        for entry in COLLECTION_SCHEMA["collections"].keys():
            out[entry] = COLLECTION_SCHEMA["collections"][entry]["schema"]
            if out[entry] == None:
                out.pop(entry)
        return out

    def bulk_write(self, collection: str, actions: list) -> pymongo.results.BulkWriteResult:
        """Bulk write `actions` into `collection` in order of `actions`"""
        check_collection_name(collection)
        if collection in VALID_COLLECTIONS:
            return self.db[collection].bulk_write(actions)
        else:
            log.info(f'database.py: Invalid collection name: "{collection}"')


def mongo_convert(sch):
    """Converts a schema dictionary into a mongo-usable form."""
    # Dictionary for translating data types in schema to recognized BSON types
    type_to_bson = {
        "int": "int",
        "float": "number",
        "str": "string",
        "bool": "bool",
        "List": "array",
    }
    out = {}
    out["bsonType"] = "object"
    out["required"] = []
    out["properties"] = {}
    for section, datapoints in sch.items():
        # These sections aren't stored in the database; ignore them
        if section in ["schema_file", "enums"] or section[:2] == "--":
            continue
        for datapoint, info in datapoints.items():
            datapoint_dict = {}
            # Every document should have a team number, match number, and/or scout name depending on collection
            if datapoint in ["team_number", "match_number", "scout_name"]:
                out["required"].append(datapoint)
            # Enums include their data type in brackets. Ex: Enum[int] is int.
            datapoint_dict["bsonType"] = type_to_bson[
                t[5:-1] if "Enum" in (t := info["type"]) else t
            ]
            out["properties"].update({datapoint: datapoint_dict})
    return out
