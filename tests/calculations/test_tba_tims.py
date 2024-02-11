import pytest
from unittest import mock
from unittest.mock import PropertyMock

from server import Server
from calculations import tba_tims


TEST_DATA = [
    {
        "alliances": {
            "blue": {
                "team_keys": ["frc33", "frc25", "frc257"],
            },
            "red": {
                "team_keys": ["frc34", "frc973", "frc254"],
            },
        },
        "comp_level": "qm",
        "match_number": 1,
        "score_breakdown": {
            "blue": {
                "leaveRobot1": "Yes",
                "leaveRobot2": "Yes",
                "leaveRobot3": "Yes",
                "spotlitRobot1": "No",
                "spotlitRobot2": "No",
                "spotlitRobot3": "No",
            },
            "red": {
                "leaveRobot1": "Yes",
                "leaveRobot2": "Yes",
                "leaveRobot3": "No",
                "spotlitRobot1": "No",
                "spotlitRobot2": "No",
                "spotlitRobot3": "No",
            },
        },
    },
    {
        "alliances": {
            "blue": {
                "team_keys": ["frc97", "frc3", "frc37"],
            },
            "red": {
                "team_keys": ["frc47", "frc57", "frc67"],
            },
        },
        "comp_level": "qm",
        "match_number": 2,
        "score_breakdown": {
            "blue": {
                "leaveRobot1": "Yes",
                "leaveRobot2": "Yes",
                "leaveRobot3": "Yes",
                "spotlitRobot1": "No",
                "spotlitRobot2": "No",
                "spotlitRobot3": "No",
            },
            "red": {
                "leaveRobot1": "Yes",
                "leaveRobot2": "Yes",
                "leaveRobot3": "Yes",
                "spotlitRobot1": "No",
                "spotlitRobot2": "No",
                "spotlitRobot3": "No",
            },
        },
    },
]

TIMS = [
    {
        "team_number": "254",
        "match_number": 1,
        "leave": False,
    },
    {
        "team_number": "973",
        "match_number": 1,
        "leave": True,
    },
    {
        "team_number": "34",
        "match_number": 1,
        "leave": False,
    },
    {
        "team_number": "33",
        "match_number": 1,
        "leave": False,
    },
    {
        "team_number": "25",
        "match_number": 1,
        "leave": False,
    },
    {
        "team_number": "257",
        "match_number": 1,
        "leave": False,
    },
    {
        "team_number": "97",
        "match_number": 2,
        "leave": True,
    },
    {
        "team_number": "3",
        "match_number": 2,
        "leave": True,
    },
    {
        "team_number": "37",
        "match_number": 2,
        "leave": True,
    },
    {
        "team_number": "47",
        "match_number": 2,
        "leave": True,
    },
    {
        "team_number": "57",
        "match_number": 2,
        "leave": True,
    },
    {
        "team_number": "67",
        "match_number": 2,
        "leave": True,
    },
]


@pytest.fixture(autouse=True, scope="function")
def mock_entries_since_last():
    with mock.patch.object(tba_tims.TBATIMCalc, "entries_since_last", return_value=TEST_DATA) as _:
        yield


@pytest.mark.clouddb
class TestTBATimCalc:
    def setup_method(self):
        with mock.patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = Server()
        self.test_calc = tba_tims.TBATIMCalc(self.test_server)

    def test_calc_tba_bool(self):
        # Creates example match data to test calc_tba_bool()
        match_data = {
            "score_breakdown": {
                "blue": {
                    "leaveRobot1": "Yes",
                    "leaveRobot2": "Yes",
                    "leaveRobot3": "Yes",
                    "spotlitRobot1": "No",
                    "spotlitRobot2": "No",
                    "spotlitRobot3": "No",
                },
                "red": {
                    "leaveRobot1": "Yes",
                    "leaveRobot2": "No",
                    "leaveRobot3": "Yes",
                    "spotlitRobot1": "No",
                    "spotlitRobot2": "No",
                    "spotlitRobot3": "No",
                },
            }
        }

        # Tests calc_tba_bool() using the example match data above
        assert tba_tims.TBATIMCalc.calc_tba_bool(match_data, "blue", {"leaveRobot1": "Yes"})
        assert not tba_tims.TBATIMCalc.calc_tba_bool(match_data, "red", {"leaveRobot2": "Yes"})

    def test_get_robot_number_and_alliance(self):
        # Generates example team keys to test get_robot_number_and_alliance()
        match_data = {
            "alliances": {
                "blue": {"team_keys": ["frc1678", "frc254", "frc413"]},
                "red": {"team_keys": ["frc612", "frc1024", "frc687"]},
            },
            "match_number": 1,
        }

        # Uses example team keys above to test get_robot_number_and_alliance()
        assert tba_tims.TBATIMCalc.get_robot_number_and_alliance(1678, match_data) == (
            1,
            "blue",
        )
        assert tba_tims.TBATIMCalc.get_robot_number_and_alliance(1024, match_data) == (
            2,
            "red",
        )
        assert tba_tims.TBATIMCalc.get_robot_number_and_alliance(413, match_data) == (
            3,
            "blue",
        )
        with pytest.raises(ValueError):
            tba_tims.TBATIMCalc.get_robot_number_and_alliance(977, match_data)

    def test_get_team_list_from_match(self):
        # Creates example match data for testing get_team_list_from_match()
        match_data = {
            "alliances": {
                "blue": {"team_keys": ["frc1678", "frc254", "frc413"]},
                "red": {"team_keys": ["frc612", "frc1024", "frc687"]},
            }
        }

        # Ensures the team data is reformatted correctly in get_team_list_from_match()
        assert sorted(tba_tims.TBATIMCalc.get_team_list_from_match(match_data)) == sorted(
            ["612", "1024", "687", "1678", "254", "413"]
        )

    def test_calculate_tim(self):
        for match in TEST_DATA:
            for team_number in self.test_calc.get_team_list_from_match(match):
                calc = self.test_calc.calculate_tim(team_number, match)
                assert isinstance(calc, dict)
                assert isinstance(calc["team_number"], str)
                assert isinstance(calc["match_number"], int)
                assert isinstance(calc["leave"], bool)

    def test_run(self):
        entries = self.test_calc.entries_since_last()
        for entry in entries:
            for _ in self.test_calc.get_team_list_from_match(entry):
                assert entry["match_number"] not in self.test_calc.calculated

        self.test_calc.run()
        for entry in entries:
            for _ in self.test_calc.get_team_list_from_match(entry):
                assert entry["match_number"] in self.test_calc.calculated
