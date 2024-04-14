#!/usr/bin/env python3

"""Sends web requests to The Blue Alliance (TBA) APIv3.

Caches data to prevent duplicate data retrieval from the TBA API.
API documentation: https://www.thebluealliance.com/apidocs/v3.
"""

import requests

from data_transfer import database
import utils
import logging

log = logging.getLogger(__name__)


def tba_request(api_url, write_db: bool = True):
    """Sends a single web request to the TBA API v3.

    `api_url`: suffix of the API request URL (the part after '/api/v3').

    `write_db` (optional): if specified, doesn't write request to the DB cache and doesn't check for duplicates.

    Returns
    """
    log.info(f"tba request from {api_url} started")
    full_url = f"https://www.thebluealliance.com/api/v3/{api_url}"
    request_headers = {"X-TBA-Auth-Key": get_api_key()}
    db = database.Database()

    if write_db:
        cached = db.get_tba_cache(api_url)
        # Check if cache exists
        if cached:
            request_headers["If-None-Match"] = cached["etag"]

    log.info(f"Retrieving TBA data from {full_url}.")
    try:
        request = requests.get(full_url, headers=request_headers)
        log.info(f"TBA request from {api_url} finished.")
    except requests.exceptions.ConnectionError:
        log.error("Error: No internet connection.")
        return None

    # A 200 status code means the request was successful
    # 304 means that data was not modified since the last timestamp
    # specified in request_headers['If-Modified-Since']
    if write_db:
        if request.status_code == 304:
            return cached["data"]
        if request.status_code == 200:
            db.update_tba_cache(request.json(), api_url, request.headers["etag"])
            return request.json()
        raise Warning(f"Request failed with status code {request.status_code}")
    else:
        return request.json()


def get_api_key() -> str:
    with open(utils.create_file_path("data/api_keys/tba_key.txt")) as file:
        api_key = file.read().rstrip("\n")
    return api_key
