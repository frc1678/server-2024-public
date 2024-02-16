from data_transfer import tba_communicator
import pytest
import requests
from unittest.mock import patch, mock_open

test_cache = {
    "api_url": "event/2020caln/teams",
    "data": [{"team_name": "Citrus Circuits"}],
    "etag": 'W/"fb0425e78890c8df10daa66401177a80c154eeb2"',
}

test_json = {"teams": ["frc1678", "frc4414", "frc1671"]}


@patch("requests.get")
def test_connection_error(get_mock, caplog):
    get_mock.side_effect = requests.exceptions.ConnectionError()
    with patch("data_transfer.tba_communicator.get_api_key", return_value="api_key"):
        tba_communicator.tba_request("events/2020caln/matches")
    assert ["Error: No internet connection."] == [
        rec.message for rec in caplog.records if rec.levelname == "ERROR"
    ]


@patch("requests.get")
def test_status_code_304(get_mock):
    get_mock.return_value.status_code = 304
    with patch("data_transfer.database.Database.get_tba_cache", return_value=test_cache), patch(
        "data_transfer.tba_communicator.get_api_key", return_value="api_key"
    ):
        assert tba_communicator.tba_request("events/2020caln/teams") == test_cache["data"]


@patch("requests.get")
def test_status_code_200(get_mock):
    get_mock.return_value.status_code = 200
    get_mock.return_value.json.return_value = test_json
    get_mock.return_value.headers = {"etag": 'W/"fb0425e78890c8df10daa66401177a80c154eeb2"'}

    with patch("data_transfer.database.Database.update_tba_cache") as update_mock, patch(
        "data_transfer.tba_communicator.get_api_key", return_value="api_key"
    ):
        assert tba_communicator.tba_request("events/2020caln/teams") == {
            "teams": ["frc1678", "frc4414", "frc1671"]
        }
        update_mock.assert_called_with(
            {"teams": ["frc1678", "frc4414", "frc1671"]},
            "events/2020caln/teams",
            'W/"fb0425e78890c8df10daa66401177a80c154eeb2"',
        )


@patch("requests.get")
def test_error_code(get_mock):
    get_mock.return_value.status_code = "abcd"
    with pytest.raises(Warning, match="Request failed with status code abcd"), patch(
        "data_transfer.tba_communicator.get_api_key", return_value="api_key"
    ):
        tba_communicator.tba_request("events/2020caln/teams")


def test_get_api_key():
    with patch("builtins.open", mock_open(read_data="api_key")):
        assert tba_communicator.get_api_key() == "api_key"
