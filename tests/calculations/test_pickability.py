import pytest

from unittest import mock

from calculations import pickability
from server import Server


FAKE_SCHEMA = {
    "calculations": {
        "first_pickability": {
            "type": "float",
            "test.datapoint1": [1, "test.datapoint1"],
            "test.datapoint2": 1,
            "test2.datapoint1": 1,
        },
        "offensive_second_pickability": {
            "type": "float",
            "test.datapoint1": 1,
            "test.datapoint2": 1,
            "test2.datapoint1": 4,
        },
        "defensive_second_pickability": {
            "type": "float",
            "test.datapoint1": [2.5, 2],
            "test.datapoint2": 1,
            "test2.datapoint1": 2,
        },
    },
}


@pytest.mark.clouddb
class TestPickability:
    @staticmethod
    def test__init__():
        with mock.patch("server.Server.ask_calc_all_data", return_value=False):
            m_server = Server()
        with mock.patch("utils.read_schema", return_value=FAKE_SCHEMA):
            test_calc = pickability.PickabilityCalc(m_server)
        assert test_calc.server == m_server
        assert "test" in test_calc.watched_collections and "test2" in test_calc.watched_collections

    @staticmethod
    @mock.patch("server.Server.ask_calc_all_data", return_value=False)
    @mock.patch("utils.read_schema", return_value=FAKE_SCHEMA)
    def test_calculate_pickabilty(mock, calc_all_data_mock):
        test_calc = pickability.PickabilityCalc(Server())
        calc_data = {
            "test": {
                "team_number": "0",
                "datapoint1": 2,
                "datapoint2": 1,
                "useless": None,
            },
            "test2": {"team_number": "0", "datapoint1": 3, "useless": None},
        }
        assert test_calc.calculate_pickability("first_pickability", calc_data) == 8
        assert test_calc.calculate_pickability("offensive_second_pickability", calc_data) == 15
        assert test_calc.calculate_pickability("defensive_second_pickability", calc_data) == 17
        assert test_calc.calculate_pickability("first_pickability", {}) is None
        # Check that if the datapoint is missing that it correctly returns None
        calc_data = {
            "test": {
                "team_number": "0",
                "datapoint2": 1,
                "useless": None,
            },
            "test2": {"team_number": "0", "datapoint1": 3, "useless": None},
        }
        assert test_calc.calculate_pickability("first_pickability", calc_data) is None

    @staticmethod
    @mock.patch("utils.read_schema", return_value=FAKE_SCHEMA)
    @mock.patch("server.Server.ask_calc_all_data", return_value=False)
    def test_run(calc_all_data_mock, schema_mock):
        server_obj = Server()
        test_calc = pickability.PickabilityCalc(server_obj)

        # This is not enough to do a pickability calc, it needs the test2 datapoint
        server_obj.db.insert_documents(
            "test", {"team_number": "0", "datapoint1": 1, "datapoint2": 5}
        )
        test_calc.run()
        assert server_obj.db.find("pickability") == []

        # Insert all the required data
        server_obj.db.insert_documents(
            "test2", {"team_number": "0", "datapoint1": 1, "datapoint2": 3}
        )
        test_calc.run()
        result = server_obj.db.find("pickability")
        del result[0]["_id"]
        assert result[0] == {
            "team_number": "0",
            "defensive_second_pickability": 12,
            "first_pickability": 7,
            "offensive_second_pickability": 10,
        }

        # Test updating the function
        server_obj.db.delete_data("test2")
        server_obj.db.insert_documents(
            "test2", {"team_number": "0", "datapoint1": 2000000, "datapoint2": 20}
        )
        test_calc.run()
        new_result = server_obj.db.find("pickability")
        del new_result[0]["_id"]
        assert result != new_result
