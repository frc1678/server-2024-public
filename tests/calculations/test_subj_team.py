#!/usr/bin/env python3

import pytest
from unittest.mock import patch
from calculations import subj_team
from server import Server
from utils import dict_near


@pytest.mark.clouddb
class TestSubjTeamCalcs:
    def setup_method(self, method):
        with patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = Server()
        self.test_calcs = subj_team.SubjTeamCalcs(self.test_server)

    def test___init__(self):
        """Test if attributes are set correctly"""
        assert self.test_calcs.watched_collections == ["subj_tim"]
        assert self.test_calcs.server == self.test_server

    def test_teams_played_with(self):
        tims = [
            {
                "match_number": 1,
                "team_number": "1678",
                "alliance_color_is_red": True,
            },
            {
                "match_number": 1,
                "team_number": "4414",
                "alliance_color_is_red": True,
            },
            {
                "match_number": 1,
                "team_number": "1323",
                "alliance_color_is_red": True,
            },
            {
                "match_number": 1,
                "team_number": "3",
                "alliance_color_is_red": False,
            },
            {
                "match_number": 2,
                "team_number": "4",
                "alliance_color_is_red": True,
            },
            {
                "match_number": 3,
                "team_number": "1678",
                "alliance_color_is_red": False,
            },
            {
                "match_number": 3,
                "team_number": "2910",
                "alliance_color_is_red": False,
            },
        ]
        self.test_server.db.insert_documents("subj_tim", tims)
        assert self.test_calcs.teams_played_with("1678") == [
            "1678",
            "4414",
            "1323",
            "1678",
            "2910",
        ]

    def test_all_calcs(self):
        tims = [
            {
                "match_number": 1,
                "team_number": "118",
                "quickness_score": 2,
                "field_awareness_score": 1,
                "alliance_color_is_red": True,
            },
            {
                "match_number": 1,
                "team_number": "1678",
                "quickness_score": 1,
                "field_awareness_score": 2,
                "alliance_color_is_red": True,
            },
            {
                "match_number": 1,
                "team_number": "254",
                "quickness_score": 3,
                "field_awareness_score": 3,
                "alliance_color_is_red": True,
            },
            {
                "match_number": 2,
                "team_number": "118",
                "quickness_score": 2,
                "field_awareness_score": 1,
                "alliance_color_is_red": True,
            },
            {
                "match_number": 2,
                "team_number": "1678",
                "quickness_score": 3,
                "field_awareness_score": 3,
                "alliance_color_is_red": True,
            },
            {
                "match_number": 2,
                "team_number": "254",
                "quickness_score": 1,
                "field_awareness_score": 2,
                "alliance_color_is_red": True,
            },
            {
                "match_number": 3,
                "team_number": "118",
                "quickness_score": 1,
                "field_awareness_score": 3,
                "alliance_color_is_red": False,
            },
            {
                "match_number": 3,
                "team_number": "1678",
                "quickness_score": 2,
                "field_awareness_score": 2,
                "alliance_color_is_red": False,
            },
            {
                "match_number": 3,
                "team_number": "254",
                "quickness_score": 1,
                "field_awareness_score": 3,
                "alliance_color_is_red": False,
            },
        ]
        self.test_server.db.delete_data("subj_tim")
        self.test_server.db.insert_documents("subj_tim", tims)
        self.test_calcs.run()
        robonauts = self.test_server.db.find("subj_team", {"team_number": "118"})[0]
        citrus = self.test_server.db.find("subj_team", {"team_number": "1678"})[0]
        chezy = self.test_server.db.find("subj_team", {"team_number": "254"})[0]

        for team in [robonauts, citrus, chezy]:
            for datapoint in [
                "_id",
                "unadjusted_field_awareness",
                "unadjusted_quickness",
                "test_driver_ability",
            ]:
                team.pop(datapoint)

        expected_robonauts = {
            "team_number": "118",
            "driver_field_awareness": 0.9259,
            "driver_quickness": 0.5556,
            "driver_ability": -1.3439,
            "defensive_driver_ability": 0.6335,
            "proxy_driver_ability": 2.6682,
        }
        assert dict_near(expected_robonauts, robonauts, 0.01)
        expected_citrus = {
            "team_number": "1678",
            "driver_field_awareness": 1.2963,
            "driver_quickness": 0.6667,
            "driver_ability": 1.0533,
            "defensive_driver_ability": 2.3679,
            "proxy_driver_ability": 11.3428,
        }
        assert dict_near(expected_citrus, citrus, 0.01)
        expected_chezy = {
            "team_number": "254",
            "driver_field_awareness": 1.4815,
            "driver_quickness": 0.5556,
            "driver_ability": 0.2906,
            "defensive_driver_ability": 2.9986,
            "proxy_driver_ability": 15.9889,
        }
        assert dict_near(expected_chezy, chezy, 0.01)
