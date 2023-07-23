# Copyright (c) 2023 FRC Team 1678: Citrus Circuits

from unittest import mock

from calculations import base_calculations
from calculations import auto_paths
from server import Server
import pytest


class TestAutoPathCalc:

    obj_teams = [{"team_number": "254"}, {"team_number": "4414"}, {"team_number": "1678"}]

    expected_obj_teams = [
        {"team_number": "254", "middle_compatability": 0, "cable_bump_compatability": 0},
        {"team_number": "4414"},
        {"team_number": "1678"},
    ]

    auto_pims = [
        {
            "match_number": 24,
            "team_number": "1678",
            "start_position": "3",
            "preloaded_gamepiece": "U",
            "auto_charge_level": "E",
            "score_piece_1": "cube",
            "score_position_1": "low",
            "score_piece_2": "cone",
            "score_position_2": "mid",
            "intake_piece_1": "cube",
            "intake_position_1": "one",
            "intake_piece_2": "cube",
            "intake_position_2": "two",
            "score_piece_3": "cube",
            "score_position_3": "high",
            "mobility": True,
            "timeline": [{"doesn't matter": "anything"}],
        },
        {
            "match_number": 42,
            "team_number": "254",
            "start_position": "1",
            "preloaded_gamepiece": "U",
            "auto_charge_level": "D",
            "score_piece_1": "cone",
            "score_position_1": "low",
            "score_piece_2": "cube",
            "score_position_2": "mid",
            "intake_piece_1": "cube",
            "intake_position_1": "one",
            "intake_piece_2": "cube",
            "intake_position_2": "two",
            "score_piece_3": "cube",
            "score_position_3": "low",
            "mobility": True,
            "timeline": [{"doesn't matter": "anything"}],
        },
        {
            "match_number": 24,
            "team_number": "254",
            "start_position": "1",
            "preloaded_gamepiece": "U",
            "auto_charge_level": "D",
            "score_piece_1": "cone",
            "score_position_1": "low",
            "score_piece_2": "cube",
            "score_position_2": "mid",
            "intake_piece_1": "cube",
            "intake_position_1": "one",
            "intake_piece_2": None,
            "intake_position_2": None,
            "score_piece_3": None,
            "score_position_3": None,
            "mobility": True,
            "timeline": [{"doesn't matter": "anything"}],
        },
        {
            "match_number": 23,
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level": "E",
            "score_piece_1": "cone",
            "score_position_1": "low",
            "score_piece_2": "cube",
            "score_position_2": "low",
            "intake_piece_1": "cube",
            "intake_position_1": "two",
            "intake_piece_2": "cube",
            "intake_position_2": "one",
            "score_piece_3": "cube",
            "score_position_3": "high",
            "mobility": True,
            "timeline": [{"doesn't matter": "anything"}],
        },
        {
            "match_number": 56,
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level": "E",
            "score_piece_1": "cone",
            "score_position_1": "low",
            "score_piece_2": "cube",
            "score_position_2": "low",
            "intake_piece_1": "cube",
            "intake_position_1": "two",
            "intake_piece_2": "cube",
            "intake_position_2": "one",
            "score_piece_3": "fail",
            "score_position_3": "fail",
            "mobility": True,
            "timeline": [{"doesn't matter": "anything"}],
        },
        {
            "match_number": 70,
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level": "F",
            "score_piece_1": "fail",
            "score_position_1": "fail",
            "score_piece_2": "fail",
            "score_position_2": "fail",
            "intake_piece_1": "cube",
            "intake_position_1": "two",
            "intake_piece_2": None,
            "intake_position_2": "one",
            "score_piece_3": "fail",
            "score_position_3": "fail",
            "mobility": True,
            "timeline": [{"doesn't matter": "anything"}],
        },
    ]

    expected_auto_pims = [
        {
            "match_number": 24,
            "team_number": "1678",
            "start_position": "3",
            "preloaded_gamepiece": "U",
            "auto_charge_level": "E",
            "score_piece_1": "cube",
            "score_position_1": "low",
            "score_piece_2": "cone",
            "score_position_2": "mid",
            "intake_piece_1": "cube",
            "intake_position_1": "one",
            "intake_piece_2": "cube",
            "intake_position_2": "two",
            "score_piece_3": "cube",
            "score_position_3": "high",
            "mobility": True,
            "timeline": [{"doesn't matter": "anything"}],
        },
        {
            "match_number": 42,
            "path_number": 1,
            "matches_ran": [42],
            "team_number": "254",
            "start_position": "1",
            "preloaded_gamepiece": "U",
            "auto_charge_level": "D",
            "score_piece_1": "cone",
            "score_position_1": "low",
            "score_piece_2": "cube",
            "score_position_2": "mid",
            "intake_piece_1": "cube",
            "intake_position_1": "one",
            "intake_piece_2": "cube",
            "intake_position_2": "two",
            "score_piece_3": "cube",
            "score_position_3": "low",
            "mobility": True,
            "timeline": [{"doesn't matter": "anything"}],
        },
        {
            "match_number": 24,
            "team_number": "254",
            "start_position": "1",
            "path_number": 2,
            "matches_ran": [24],
            "preloaded_gamepiece": "U",
            "auto_charge_level": "D",
            "score_piece_1": "cone",
            "score_position_1": "low",
            "score_piece_2": "cube",
            "score_position_2": "mid",
            "intake_piece_1": "cube",
            "intake_position_1": "one",
            "intake_piece_2": None,
            "intake_position_2": None,
            "score_piece_3": None,
            "score_position_3": None,
            "mobility": True,
            "timeline": [{"doesn't matter": "anything"}],
        },
        {
            "match_number": 23,
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level": "E",
            "score_piece_1": "cone",
            "score_position_1": "low",
            "score_piece_2": "cube",
            "score_position_2": "low",
            "intake_piece_1": "cube",
            "intake_position_1": "two",
            "intake_piece_2": "cube",
            "intake_position_2": "one",
            "score_piece_3": "cube",
            "score_position_3": "high",
            "mobility": True,
            "timeline": [{"doesn't matter": "anything"}],
        },
        {
            "match_number": 56,
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level": "E",
            "score_piece_1": "cone",
            "score_position_1": "low",
            "score_piece_2": "cube",
            "score_position_2": "low",
            "intake_piece_1": "cube",
            "intake_position_1": "two",
            "intake_piece_2": "cube",
            "intake_position_2": "one",
            "score_piece_3": "fail",
            "score_position_3": "fail",
            "mobility": True,
            "timeline": [{"doesn't matter": "anything"}],
        },
        {
            "match_number": 70,
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level": "F",
            "score_piece_1": "fail",
            "score_position_1": "fail",
            "score_piece_2": "fail",
            "score_position_2": "fail",
            "intake_piece_1": "cube",
            "intake_position_1": "two",
            "intake_piece_2": None,
            "intake_position_2": "one",
            "score_piece_3": "fail",
            "score_position_3": "fail",
            "mobility": True,
            "timeline": [{"doesn't matter": "anything"}],
        },
    ]

    expected_group_auto_paths = [
        {
            "path_number": 1,
            "match_numbers": [24],
            "matches_ran": 1,
            "team_number": "1678",
            "start_position": "3",
            "preloaded_gamepiece": "U",
            "auto_charge_level_max": "E",
            "auto_charge_successes": 1,
            "score_piece_1_max": "cube",
            "score_1_successes": 1,
            "score_1_max_successes": 1,
            "score_piece_2_max": "cone",
            "score_position_1_max": "low",
            "score_2_successes": 1,
            "score_2_max_successes": 1,
            "score_position_2_max": "mid",
            "score_3_successes": 1,
            "score_3_max_successes": 1,
            "score_piece_3_max": "cube",
            "score_position_3_max": "high",
            "intake_position_1": "one",
            "intake_position_2": "two",
            "mobility": True,
        },
        {
            "path_number": 1,
            "match_numbers": [42],
            "matches_ran": 1,
            "team_number": "254",
            "start_position": "1",
            "preloaded_gamepiece": "U",
            "auto_charge_level_max": "D",
            "auto_charge_successes": 0,
            "score_piece_1_max": "cone",
            "score_1_successes": 1,
            "score_1_max_successes": 1,
            "score_piece_2_max": "cube",
            "score_position_1_max": "low",
            "score_2_successes": 1,
            "score_2_max_successes": 1,
            "score_position_2_max": "mid",
            "intake_position_1": "one",
            "intake_position_2": "two",
            "score_piece_3_max": "cube",
            "score_3_successes": 1,
            "score_3_max_successes": 1,
            "score_position_3_max": "low",
            "mobility": True,
        },
        {
            "path_number": 2,
            "match_numbers": [24],
            "matches_ran": 1,
            "team_number": "254",
            "start_position": "1",
            "preloaded_gamepiece": "U",
            "auto_charge_level_max": "D",
            "auto_charge_successes": 0,
            "score_piece_1_max": "cone",
            "score_1_successes": 1,
            "score_1_max_successes": 1,
            "score_piece_2_max": "cube",
            "score_position_1_max": "low",
            "score_2_successes": 1,
            "score_2_max_successes": 1,
            "score_position_2_max": "mid",
            "intake_position_1": "one",
            "intake_position_2": None,
            "score_piece_3_max": None,
            "score_3_successes": 0,
            "score_3_max_successes": 0,
            "score_position_3_max": None,
            "mobility": True,
        },
        {
            "path_number": 1,
            "match_numbers": [23],
            "matches_ran": 1,
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level_max": "E",
            "auto_charge_successes": 1,
            "score_piece_1_max": "cone",
            "score_1_successes": 1,
            "score_1_max_successes": 1,
            "score_piece_2_max": "cube",
            "score_position_1_max": "low",
            "score_2_successes": 1,
            "score_2_max_successes": 1,
            "score_position_2_max": "low",
            "intake_position_1": "two",
            "intake_position_2": "one",
            "score_piece_3_max": "cube",
            "score_3_successes": 1,
            "score_3_max_successes": 1,
            "score_position_3_max": "high",
            "mobility": True,
        },
        {
            "path_number": 1,
            "match_numbers": [56, 23],
            "matches_ran": 2,
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level_max": "E",
            "auto_charge_successes": 2,
            "score_piece_1_max": "cone",
            "score_1_successes": 2,
            "score_1_max_successes": 2,
            "score_piece_2_max": "cube",
            "score_position_1_max": "low",
            "score_2_successes": 2,
            "score_2_max_successes": 2,
            "score_position_2_max": "low",
            "intake_position_1": "two",
            "intake_position_2": "one",
            "score_piece_3_max": "cube",
            "score_3_successes": 1,
            "score_3_max_successes": 1,
            "score_position_3_max": "high",
            "mobility": True,
        },
        {
            "path_number": 1,
            "match_numbers": [70, 56, 23],
            "matches_ran": 3,
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level_max": "E",
            "auto_charge_successes": 2,
            "score_1_successes": 2,
            "score_piece_1_max": "cone",
            "score_1_max_successes": 2,
            "score_position_1_max": "low",
            "score_piece_2_max": "cube",
            "score_2_successes": 2,
            "score_2_max_successes": 2,
            "score_position_2_max": "low",
            "intake_position_1": "two",
            "intake_position_2": "one",
            "score_3_successes": 1,
            "score_piece_3_max": "cube",
            "score_3_max_successes": 1,
            "score_position_3_max": "high",
            "mobility": True,
        },
    ]
    expected_auto_paths = [
        {
            "path_number": 1,
            "match_numbers": [42],
            "matches_ran": 1,
            "team_number": "254",
            "start_position": "1",
            "auto_charge_level_max": "D",
            "auto_charge_successes": 0,
            "intake_position_1": "one",
            "intake_position_2": "two",
            "mobility": True,
            "preloaded_gamepiece": "U",
            "score_1_max_successes": 1,
            "score_1_successes": 1,
            "score_2_max_successes": 1,
            "score_2_successes": 1,
            "score_3_max_successes": 1,
            "score_3_successes": 1,
            "score_piece_1_max": "cone",
            "score_piece_2_max": "cube",
            "score_piece_3_max": "cube",
            "score_position_1_max": "low",
            "score_position_2_max": "mid",
            "score_position_3_max": "low",
        },
        {
            "path_number": 2,
            "match_numbers": [24],
            "matches_ran": 1,
            "team_number": "254",
            "start_position": "1",
            "auto_charge_level_max": "D",
            "auto_charge_successes": 0,
            "intake_position_1": "one",
            "intake_position_2": None,
            "mobility": True,
            "preloaded_gamepiece": "U",
            "score_1_max_successes": 1,
            "score_1_successes": 1,
            "score_2_max_successes": 1,
            "score_2_successes": 1,
            "score_3_max_successes": 0,
            "score_3_successes": 0,
            "score_piece_1_max": "cone",
            "score_piece_2_max": "cube",
            "score_piece_3_max": None,
            "score_position_1_max": "low",
            "score_position_2_max": "mid",
            "score_position_3_max": None,
        },
    ]

    expected_auto_path = [
        {
            "path_number": 1,
            "match_numbers": [42],
            "matches_ran": 1,
            "team_number": "254",
            "start_position": "1",
            "auto_charge_level_max": "D",
            "auto_charge_successes": 0,
            "intake_position_1": "one",
            "intake_position_2": "two",
            "mobility": True,
            "preloaded_gamepiece": "U",
            "score_1_max_successes": 1,
            "score_1_successes": 1,
            "score_2_max_successes": 1,
            "score_2_successes": 1,
            "score_3_max_successes": 1,
            "score_3_successes": 1,
            "score_piece_1_max": "cone",
            "score_piece_2_max": "cube",
            "score_piece_3_max": "cube",
            "score_position_1_max": "low",
            "score_position_2_max": "mid",
            "score_position_3_max": "low",
        }
    ]

    @mock.patch.object(
        base_calculations.BaseCalculations, "get_teams_list", return_value=["3", "254"]
    )
    def setup_method(self, method, get_teams_list_dummy):
        with mock.patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = Server()
        self.test_calculator = auto_paths.AutoPathCalc(self.test_server)
        # Insert test data into database for testing
        self.test_server.db.insert_documents("auto_pim", self.auto_pims)
        self.test_server.db.insert_documents("obj_team", self.obj_teams)

    def test___init__(self):
        assert self.test_calculator.server == self.test_server
        assert self.test_calculator.watched_collections == [
            "auto_pim",
        ]

    def test_group_auto_paths(self):
        assert (
            self.test_calculator.group_auto_paths(self.auto_pims[0], [])
            == self.expected_group_auto_paths[0]
        )
        self.test_server.db.insert_documents("auto_paths", self.expected_group_auto_paths[0])
        assert (
            self.test_calculator.group_auto_paths(self.auto_pims[1], [])
            == self.expected_group_auto_paths[1]
        )
        self.test_server.db.insert_documents("auto_paths", self.expected_group_auto_paths[1])
        assert (
            self.test_calculator.group_auto_paths(self.auto_pims[2], [])
            == self.expected_group_auto_paths[2]
        )
        self.test_server.db.insert_documents("auto_paths", self.expected_group_auto_paths[2])
        assert (
            self.test_calculator.group_auto_paths(self.auto_pims[3], [])
            == self.expected_group_auto_paths[3]
        )
        self.test_server.db.insert_documents("auto_paths", self.expected_group_auto_paths[3])
        assert (
            self.test_calculator.group_auto_paths(self.auto_pims[4], [])
            == self.expected_group_auto_paths[4]
        )
        self.test_server.db.update_document(
            "auto_paths",
            self.expected_group_auto_paths[4],
            {
                "team_number": self.expected_group_auto_paths[4]["team_number"],
                "start_position": self.expected_group_auto_paths[4]["start_position"],
                "path_number": self.expected_group_auto_paths[4]["path_number"],
            },
        )
        assert (
            self.test_calculator.group_auto_paths(self.auto_pims[5], [])
            == self.expected_group_auto_paths[5]
        )
        self.test_server.db.update_document(
            "auto_paths",
            self.expected_group_auto_paths[5],
            {
                "team_number": self.expected_group_auto_paths[5]["team_number"],
                "start_position": self.expected_group_auto_paths[5]["start_position"],
                "path_number": self.expected_group_auto_paths[5]["path_number"],
            },
        )

    def test_calculate_auto_paths(self):
        calculated_auto_paths = self.test_calculator.calculate_auto_paths(
            [{"match_number": 42, "team_number": "254"}]
        )
        assert len(calculated_auto_paths) == 1
        assert len(self.expected_auto_path) == 1
        assert calculated_auto_paths[0] == self.expected_auto_path[0]

    def test_run(self):
        # Delete any data that is already in the database collections
        self.test_server.db.delete_data("auto_paths")
        self.test_server.db.delete_data("auto_pim")
        self.test_server.db.delete_data("obj_team")
        # Insert test data for the run function
        self.test_server.db.insert_documents("auto_pim", self.auto_pims)
        self.test_server.db.insert_documents("obj_team", self.obj_teams)

        self.test_calculator.run()
        result = self.test_server.db.find("auto_paths")

        for document in result:
            del document["_id"]

        assert result == self.expected_auto_paths

        obj_teams_result = self.test_server.db.find("obj_team")

        for obj_team_document in obj_teams_result:
            del obj_team_document["_id"]

        assert obj_teams_result == self.expected_obj_teams

        pim_result = self.test_server.db.find("auto_pim")

        for pim_document in pim_result:
            del pim_document["_id"]

        assert pim_result == self.expected_auto_pims
