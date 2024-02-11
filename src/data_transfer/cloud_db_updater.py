#!/usr/bin/env python3

"""Replicates local MongoDB database to cloud MongoDB Atlas database."""

import collections
import re
from typing import Any, Dict, List, Optional, Union

import pymongo

from data_transfer import database
import utils
import logging

log = logging.getLogger(__name__)


class CloudDBUpdater:

    BASE_CONNECTION_STRING = "mongodb+srv://server:{}@scouting-system-3das1.gcp.mongodb.net/test?authSource=admin&replicaSet=scouting-system-shard-0&w=majority&readPreference=primary&appname=MongoDB%20Compass&retryWrites=true&ssl=true"
    OPERATION_MAP = {"i": pymongo.InsertOne, "u": pymongo.UpdateOne, "d": pymongo.DeleteOne}

    def __init__(self):
        self.cloud_db = self.get_cloud_db()
        self.db = database.Database()
        self.db_pattern = re.compile(r"^{}\..*".format(self.db.name))
        self.oplog = self.db.client.local.oplog.rs
        # Get an initial timestamp
        self.update_timestamp()

    def entries_since_last(self) -> List[Dict]:
        """Returns the oplog entries since the last update

        These updates are filtered to only include Update, Insert, and Delete operations
        """
        return list(
            self.oplog.find({"ts": {"$gt": self.last_timestamp}, "op": {"$in": ["d", "i", "u"]}})
        )

    def create_db_changes(self) -> collections.defaultdict:
        """Creates bulk write operations from oplog"""
        changes = collections.defaultdict(list)
        for entry in self.entries_since_last():
            # 'ns' in the entry is of the format <database>.<collection> and shows where the changes
            # were written
            location: str = entry["ns"]
            # Ignore writes to a database other than the current local database
            if not self.db_pattern.match(location):
                continue
            # Get collection name from full location
            collection = location[location.index(".") + 1 :]
            if (bulk_op := self.create_bulk_operation(entry)) is None:
                continue
            else:
                changes[collection].append(bulk_op)
        return changes

    def write_db_changes(self) -> Dict[str, pymongo.results.BulkWriteResult]:
        """Writes oplog changes to cloud database"""
        # Try connecting to cloud db if connection does not exist
        if self.cloud_db is None:
            self.cloud_db = self.get_cloud_db()
            # Don't try to continue if above connection failed
            if self.cloud_db is None:
                return {}
        results = {}
        for collection, bulk_ops in self.create_db_changes().items():
            try:
                results[collection] = self.cloud_db.bulk_write(collection, bulk_ops)
            except pymongo.errors.BulkWriteError as bulk_errmsg:
                bulk_errmsg = str(bulk_errmsg)
                if "E11000 duplicate key error" in bulk_errmsg:
                    log.info(
                        f"cloud_db_updater: skipped upload of {len(bulk_ops)} duplicate documents in {collection}"
                    )
                else:
                    log.error(f"cloud_db_updater: {bulk_errmsg}")
                    current_documents = self.db.find(collection)
                    self.cloud_db.delete_data(collection)
                    self.cloud_db.insert_documents(collection, current_documents)
            except pymongo.errors.ServerSelectionTimeoutError:
                log.critical(
                    f"cloud_db_updater: unable to write {len(bulk_ops)} documents to {collection} due to poor internet (ServerSelectionTimeoutError)"
                )
                break  # Don't delay server cycle with more operations without internet
            # Catches errors when updating to the cloud DB on non-server computers
            except TypeError as type_e:
                log.critical(
                    f"cloud_db_updater: error writing {len(bulk_ops)} documents to {collection} ({type_e})"
                )
        # Update timestamp if loop exited properly
        else:
            self.update_timestamp()
        return results

    def update_timestamp(self):
        """Updates the timestamp to the most recent oplog entry timestamp"""
        last_op = self.oplog.find({}).sort("ts", pymongo.DESCENDING).limit(1)
        self.last_timestamp = last_op.next()["ts"]

    def create_bulk_operation(
        self, entry: Dict[str, Any]
    ) -> Optional[Union[pymongo.DeleteOne, pymongo.InsertOne, pymongo.UpdateOne]]:
        """Creates a pymongo bulk write operation for the entry.

        Note: this does not handle the collection that is written to, and the operations need to be
        applied to a specific collection to work.
        """
        operation = self.OPERATION_MAP.get(entry["op"])

        if operation is None:
            return None
        if "o" in entry and "$v" in entry["o"]:
            entry["o"].pop("$v")

        if entry["op"] == "u" and "$set" not in entry["o"]:
            return None

        if "o2" in entry:
            try:
                return operation(entry["o2"], entry["o"])
            # Tries to InsertOne with an o2
            except:
                return operation(entry["o"])

        return operation(entry["o"])

    @classmethod
    def get_cloud_db(cls) -> Optional[database.Database]:
        """Connects to the cloud database and returns a database object.

        This function mainly exists to facilitate testing by mocking the function return
        """
        try:
            return database.Database(connection=cls.get_connection_string())
        except pymongo.errors.ConfigurationError:
            # Raised when DNS operation times out, effectively means no internet
            log.error("cloud_db_updater: cannot connect to Cloud DB")
            return None

    @classmethod
    def get_connection_string(cls) -> str:
        """Adds the password to the class connection string"""
        try:
            with open(utils.create_file_path("data/api_keys/cloud_password.txt")) as f:
                password = f.read().rstrip()
        except FileNotFoundError:
            raise FileNotFoundError(
                "Missing Cloud DB password file (data/api_keys/cloud_password.txt)"
            )
        return cls.BASE_CONNECTION_STRING.format(password)


def cloud_db_connector():
    """Connects to the cloud database and returns a database object."""
    for attempt in range(3):
        # Tries to connect 3 times before raising an error
        cloud_db = CloudDBUpdater.get_cloud_db()
        if cloud_db is not None:
            return cloud_db
    raise IOError("Three connection attempts failed to the CloudDB")
