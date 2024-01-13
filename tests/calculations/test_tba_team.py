#!/usr/bin/env python3

"""This file tests the functions provided in tba_team that
don't require the database.
"""

from cmath import exp
from calculations import tba_team
from data_transfer import database
import utils
from server import Server
import pytest
from unittest.mock import patch


@pytest.mark.clouddb
class TestTBATeamCalc:
    test_server: Server
    test_calc: tba_team.TBATeamCalc

    def setup_method(self, method):
        with patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = Server()
        self.test_calc = tba_team.TBATeamCalc(self.test_server)

    def test___init__(self):
        """Test if attributes are set correctly"""
        assert self.test_calc.watched_collections == ["obj_tim", "tba_tim"]
        assert self.test_calc.server == self.test_server

    def test_run(self):
        tba_cache = [
            {
                "api_url": f"event/{Server.TBA_EVENT_KEY}/teams/simple",
                "data": [
                    {
                        "city": "Atascadero",
                        "country": "USA",
                        "key": "frc973",
                        "nickname": "Greybots",
                        "state_prov": "California",
                        "team_number": "973",
                    },
                    {
                        "city": "Davis",
                        "country": "USA",
                        "key": "frc1678",
                        "nickname": "Citrus Circuits",
                        "state_prov": "California",
                        "team_number": "1678",
                    },
                    {"team_number": "3478", "nickname": "LamBot"},
                    {"team_number": "1577", "nickname": "Steampunk"},
                ],
            },
            # Test data created from TBA blog https://blog.thebluealliance.com/2017/10/05/the-math-behind-opr-an-introduction/
            {
                "api_url": f"event/{Server.TBA_EVENT_KEY}/matches",
                "data": [
                    {
                        "alliances": {
                            "red": {"team_keys": ["frc973", "frc1678"]},
                            "blue": {"team_keys": ["frc973", "frc3478"]},
                        },
                        "score_breakdown": {
                            "red": {"foulPoints": 13},
                            "blue": {"foulPoints": 10},
                        },
                    },
                    {
                        "alliances": {
                            "red": {"team_keys": ["frc1678", "frc3478"]},
                            "blue": {"team_keys": ["frc973", "frc1577"]},
                        },
                        "score_breakdown": {
                            "red": {"foulPoints": 15},
                            "blue": {"foulPoints": 7},
                        },
                    },
                ],
            },
        ]
        obj_tims = [
            {
                "auto_low_cones": 66,
                "auto_high_cones": 61,
                "tele_low_cones": 18,
                "tele_high_cones": 45,
                "incap": 14,
                "confidence_rating": 30,
                "team_number": "973",
                "match_number": 1,
            },
            {
                "auto_low_cones": 30,
                "auto_high_cones": 59,
                "tele_low_cones": 57,
                "tele_high_cones": 1,
                "incap": 22,
                "confidence_rating": 68,
                "team_number": "973",
                "match_number": 2,
            },
            {
                "auto_low_cones": 84,
                "auto_high_cones": 92,
                "tele_low_cones": 40,
                "tele_high_cones": 67,
                "incap": 18,
                "confidence_rating": 2,
                "team_number": "973",
                "match_number": 3,
            },
            {
                "auto_low_cones": 47,
                "auto_high_cones": 76,
                "tele_low_cones": 34,
                "tele_high_cones": 81,
                "incap": 17,
                "confidence_rating": 31,
                "team_number": "1678",
                "match_number": 1,
            },
            {
                "auto_low_cones": 25,
                "auto_high_cones": 54,
                "tele_low_cones": 81,
                "tele_high_cones": 59,
                "incap": 93,
                "confidence_rating": 14,
                "team_number": "1678",
                "match_number": 2,
            },
            {
                "auto_low_cones": 54,
                "auto_high_cones": 49,
                "tele_low_cones": 88,
                "tele_high_cones": 74,
                "incap": 15,
                "confidence_rating": 77,
                "team_number": "1678",
                "match_number": 3,
            },
            {
                "auto_low_cones": 47,
                "auto_high_cones": 76,
                "tele_low_cones": 34,
                "tele_high_cones": 81,
                "incap": 17,
                "confidence_rating": 31,
                "team_number": "3478",
                "match_number": 1,
            },
            {
                "auto_low_cones": 25,
                "auto_high_cones": 54,
                "tele_low_cones": 81,
                "tele_high_cones": 59,
                "incap": 93,
                "confidence_rating": 14,
                "team_number": "3478",
                "match_number": 2,
            },
            {
                "auto_low_cones": 54,
                "auto_high_cones": 49,
                "tele_low_cones": 88,
                "tele_high_cones": 74,
                "incap": 15,
                "confidence_rating": 77,
                "team_number": "3478",
                "match_number": 3,
            },
            {
                "auto_low_cones": 47,
                "auto_high_cones": 76,
                "tele_low_cones": 34,
                "tele_high_cones": 81,
                "incap": 17,
                "confidence_rating": 31,
                "team_number": "1577",
                "match_number": 1,
            },
            {
                "auto_low_cones": 25,
                "auto_high_cones": 54,
                "tele_low_cones": 81,
                "tele_high_cones": 59,
                "incap": 93,
                "confidence_rating": 14,
                "team_number": "1577",
                "match_number": 2,
            },
            {
                "auto_low_cones": 54,
                "auto_high_cones": 49,
                "tele_low_cones": 88,
                "tele_high_cones": 74,
                "incap": 15,
                "confidence_rating": 77,
                "team_number": "1577",
                "match_number": 3,
            },
        ]
        tba_tims = [
            {
                "leave": False,
                "match_number": 1,
                "team_number": "973",
            },
            {
                "leave": False,
                "match_number": 2,
                "team_number": "973",
            },
            {
                "leave": True,
                "match_number": 3,
                "team_number": "973",
            },
            {
                "leave": True,
                "match_number": 4,
                "team_number": "973",
            },
            {
                "leave": True,
                "match_number": 5,
                "team_number": "973",
            },
            {
                "leave": True,
                "match_number": 1,
                "team_number": "1678",
            },
            {
                "leave": False,
                "match_number": 2,
                "team_number": "1678",
            },
            {
                "leave": True,
                "match_number": 3,
                "team_number": "1678",
            },
            {
                "leave": True,
                "match_number": 4,
                "team_number": "1678",
            },
            {
                "leave": True,
                "match_number": 5,
                "team_number": "1678",
            },
            {
                "leave": True,
                "match_number": 1,
                "team_number": "3478",
            },
            {
                "leave": False,
                "match_number": 2,
                "team_number": "3478",
            },
            {
                "leave": True,
                "match_number": 3,
                "team_number": "3478",
            },
            {
                "leave": True,
                "match_number": 4,
                "team_number": "3478",
            },
            {
                "leave": True,
                "match_number": 5,
                "team_number": "3478",
            },
            {
                "leave": True,
                "match_number": 1,
                "team_number": "1577",
            },
            {
                "leave": False,
                "match_number": 2,
                "team_number": "1577",
            },
            {
                "leave": True,
                "match_number": 3,
                "team_number": "1577",
            },
            {
                "leave": True,
                "match_number": 4,
                "team_number": "1577",
            },
            {
                "leave": True,
                "match_number": 5,
                "team_number": "1577",
            },
        ]
        expected_results = [
            # Team A
            {
                "team_number": "973",
                "foul_cc": 8.0,
                "leave_successes": 3,
                "lfm_leave_successes": 3,
                "team_name": "Greybots",
            },
            # Team B
            {
                "team_number": "1678",
                "foul_cc": 2.0,
                "leave_successes": 4,
                "lfm_leave_successes": 3,
                "team_name": "Citrus Circuits",
            },
            # Team C
            {
                "team_number": "3478",
                "foul_cc": 5.0,
                "leave_successes": 4,
                "lfm_leave_successes": 3,
                "team_name": "LamBot",
            },
            # Team D
            {
                "team_number": "1577",
                "foul_cc": 7.0,
                "leave_successes": 4,
                "lfm_leave_successes": 3,
                "team_name": "Steampunk",
            },
        ]
        self.test_server.db.insert_documents("tba_cache", tba_cache)
        self.test_server.db.insert_documents("obj_tim", obj_tims)
        self.test_server.db.insert_documents("tba_tim", tba_tims)
        self.test_calc.run()
        result = self.test_server.db.find("tba_team")
        assert len(result) == 4
        for document in result:
            del document["_id"]
            assert document in expected_results
