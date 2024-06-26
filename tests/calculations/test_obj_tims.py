# Copyright (c) 2024 FRC Team 1678: Citrus Circuits

from unittest import mock

from calculations import base_calculations
from calculations import obj_tims
from server import Server
import pytest
from unittest.mock import patch


@pytest.mark.clouddb
class TestObjTIMCalcs:
    tba_test_data = [
        {
            "match_number": 42,
            "actual_time": 1100291640,
            "comp_level": "qm",
            "score_breakdown": {
                "blue": {
                    "foulPoints": 8,
                    "autoMobilityPoints": 15,
                    "autoGamePiecePoints": 12,
                    "teleopGamePiecePoints": 40,
                    "autoCommunity": {
                        "B": [
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                        ],
                        "M": [
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                        ],
                        "T": [
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "Cube",
                            "Cone",
                        ],
                    },
                    "teleopCommunity": {
                        "B": [
                            "Cone",
                            "Cube",
                            "None",
                            "Cone",
                            "Cube",
                            "Cube",
                            "Cube",
                            "Cube",
                            "None",
                        ],
                        "M": [
                            "None",
                            "None",
                            "None",
                            "Cone",
                            "Cube",
                            "None",
                            "None",
                            "None",
                            "None",
                        ],
                        "T": [
                            "Cone",
                            "Cube",
                            "Cone",
                            "None",
                            "None",
                            "None",
                            "Cone",
                            "Cube",
                            "Cone",
                        ],
                    },
                },
                "red": {
                    "foulPoints": 10,
                    "autoMobilityPoints": 0,
                    "autoGamePiecePoints": 6,
                    "teleopGamePiecePoints": 63,
                    "autoCommunity": {
                        "B": [
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                        ],
                        "M": [
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                        ],
                        "T": [
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "None",
                            "Cone",
                        ],
                    },
                    "teleopCommunity": {
                        "B": [
                            "Cone",
                            "Cube",
                            "Cube",
                            "Cone",
                            "Cube",
                            "Cube",
                            "Cube",
                            "Cube",
                            "None",
                        ],
                        "M": [
                            "None",
                            "None",
                            "Cone",
                            "Cone",
                            "Cube",
                            "None",
                            "None",
                            "None",
                            "None",
                        ],
                        "T": [
                            "Cone",
                            "Cube",
                            "Cone",
                            "Cone",
                            "Cube",
                            "Cone",
                            "Cone",
                            "Cube",
                            "Cone",
                        ],
                    },
                },
            },
            "alliances": {
                "blue": {
                    "team_keys": [
                        "frc254",
                    ]
                },
                "red": {
                    "team_keys": [
                        "frc254",
                    ]
                },
            },
        },
    ]
    unconsolidated_tims = [
        {
            "schema_version": 6,
            "serial_number": "STR6",
            "match_number": 42,
            "timestamp": 5,
            "match_collection_version_number": "STR5",
            "scout_name": "EDWIN",
            "alliance_color_is_red": True,
            "team_number": "254",
            "scout_id": 17,
            "timeline": [
                {"in_teleop": False, "time": 148, "action_type": "auto_intake_center_5"},
                {"in_teleop": False, "time": 147, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 135, "action_type": "to_teleop"},
                {"in_teleop": True, "time": 130, "action_type": "intake_amp"},
                {"in_teleop": True, "time": 125, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 120, "action_type": "intake_far"},
                {"in_teleop": True, "time": 115, "action_type": "score_amp"},
                {"in_teleop": True, "time": 114, "action_type": "intake_far"},
                {"in_teleop": True, "time": 110, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 108, "action_type": "intake_poach"},
                {"in_teleop": True, "time": 104, "action_type": "score_amp"},
                {"in_teleop": True, "time": 95, "action_type": "intake_amp"},
                {"in_teleop": True, "time": 90, "action_type": "score_amp"},
                {"in_teleop": True, "time": 80, "action_type": "start_incap_time"},
                {"in_teleop": True, "time": 75, "action_type": "end_incap_time"},
                {"in_teleop": True, "time": 71, "action_type": "intake_poach"},
                {"in_teleop": True, "time": 70, "action_type": "fail"},
                {"in_teleop": True, "time": 63, "action_type": "score_amplify"},
                {"in_teleop": True, "time": 56, "action_type": "intake_far"},
                {"in_teleop": True, "time": 54, "action_type": "score_amp"},
                {"in_teleop": True, "time": 40, "action_type": "intake_poach"},
                {"in_teleop": True, "time": 31, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 28, "action_type": "intake_amp"},
                {"in_teleop": True, "time": 20, "action_type": "fail"},
                {"in_teleop": True, "time": 16, "action_type": "score_amp"},
                {"in_teleop": True, "time": 14, "action_type": "intake_far"},
                {"in_teleop": True, "time": 12, "action_type": "ferry"},
                {"in_teleop": True, "time": 9, "action_type": "start_incap_time"},
                {"in_teleop": False, "time": 3, "action_type": "to_endgame"},
                {"in_teleop": False, "time": 2, "action_type": "end_incap_time"},
            ],
            "stage_level_left": "N",
            "stage_level_center": "O",
            "stage_level_right": "N",
            "start_position": "1",
            "parked": True,
            "has_preload": False,
            "override": {"failed_scores": 0},
            "stage_level_left": "N",
            "stage_level_center": "F",
            "stage_level_right": "O",
            "parked": True,
        },
        {
            "schema_version": 6,
            "serial_number": "STR2",
            "match_number": 42,
            "timestamp": 6,
            "match_collection_version_number": "STR1",
            "scout_name": "RAY",
            "alliance_color_is_red": True,
            "team_number": "254",
            "scout_id": 17,
            "timeline": [
                {"in_teleop": False, "time": 148, "action_type": "auto_intake_center_5"},
                {"in_teleop": False, "time": 147, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 135, "action_type": "to_teleop"},
                {"in_teleop": True, "time": 130, "action_type": "intake_amp"},
                {"in_teleop": True, "time": 125, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 120, "action_type": "intake_far"},
                {"in_teleop": True, "time": 115, "action_type": "score_amp"},
                {"in_teleop": True, "time": 114, "action_type": "intake_far"},
                {"in_teleop": True, "time": 110, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 108, "action_type": "intake_poach"},
                {"in_teleop": True, "time": 104, "action_type": "score_amp"},
                {"in_teleop": True, "time": 95, "action_type": "intake_amp"},
                {"in_teleop": True, "time": 90, "action_type": "score_amp"},
                {"in_teleop": True, "time": 80, "action_type": "start_incap_time"},
                {"in_teleop": True, "time": 75, "action_type": "end_incap_time"},
                {"in_teleop": True, "time": 71, "action_type": "intake_poach"},
                {"in_teleop": True, "time": 70, "action_type": "fail"},
                {"in_teleop": True, "time": 63, "action_type": "score_amplify"},
                {"in_teleop": True, "time": 56, "action_type": "intake_far"},
                {"in_teleop": True, "time": 54, "action_type": "score_amp"},
                {"in_teleop": True, "time": 40, "action_type": "intake_poach"},
                {"in_teleop": True, "time": 31, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 28, "action_type": "intake_amp"},
                {"in_teleop": True, "time": 20, "action_type": "fail"},
                {"in_teleop": True, "time": 16, "action_type": "score_amp"},
                {"in_teleop": True, "time": 14, "action_type": "intake_far"},
                {"in_teleop": True, "time": 12, "action_type": "ferry"},
                {"in_teleop": True, "time": 9, "action_type": "start_incap_time"},
                {"in_teleop": False, "time": 3, "action_type": "to_endgame"},
                {"in_teleop": False, "time": 2, "action_type": "end_incap_time"},
            ],
            "stage_level_left": "N",
            "stage_level_center": "O",
            "stage_level_right": "N",
            "start_position": "3",
            "has_preload": False,
            "parked": False,
            "override": {"failed_scores": 0},
            "parked": True,
        },
        {
            "schema_version": 6,
            "serial_number": "STR5",
            "match_number": 42,
            "timestamp": 11,
            "match_collection_version_number": "STR6",
            "scout_name": "JELLY",
            "alliance_color_is_red": False,
            "team_number": "254",
            "scout_id": 17,
            "timeline": [
                {"in_teleop": False, "time": 148, "action_type": "auto_intake_center_5"},
                {"in_teleop": False, "time": 147, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 135, "action_type": "to_teleop"},
                {"in_teleop": True, "time": 130, "action_type": "intake_amp"},
                {"in_teleop": True, "time": 125, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 120, "action_type": "intake_far"},
                {"in_teleop": True, "time": 115, "action_type": "score_amp"},
                {"in_teleop": True, "time": 114, "action_type": "intake_far"},
                {"in_teleop": True, "time": 110, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 108, "action_type": "intake_poach"},
                {"in_teleop": True, "time": 104, "action_type": "score_amp"},
                {"in_teleop": True, "time": 95, "action_type": "intake_amp"},
                {"in_teleop": True, "time": 90, "action_type": "score_amp"},
                {"in_teleop": True, "time": 80, "action_type": "start_incap_time"},
                {"in_teleop": True, "time": 75, "action_type": "end_incap_time"},
                {"in_teleop": True, "time": 71, "action_type": "intake_poach"},
                {"in_teleop": True, "time": 70, "action_type": "fail"},
                {"in_teleop": True, "time": 63, "action_type": "score_amplify"},
                {"in_teleop": True, "time": 56, "action_type": "intake_far"},
                {"in_teleop": True, "time": 54, "action_type": "score_amp"},
                {"in_teleop": True, "time": 40, "action_type": "intake_poach"},
                {"in_teleop": True, "time": 31, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 28, "action_type": "intake_amp"},
                {"in_teleop": True, "time": 20, "action_type": "fail"},
                {"in_teleop": True, "time": 16, "action_type": "score_amp"},
                {"in_teleop": True, "time": 14, "action_type": "intake_far"},
                {"in_teleop": True, "time": 12, "action_type": "ferry"},
                {"in_teleop": True, "time": 9, "action_type": "start_incap_time"},
                {"in_teleop": False, "time": 3, "action_type": "to_endgame"},
                {"in_teleop": False, "time": 2, "action_type": "end_incap_time"},
            ],
            "stage_level_left": "N",
            "stage_level_center": "O",
            "stage_level_right": "N",
            "start_position": "1",
            "has_preload": False,
            "parked": True,
            "override": {"failed_scores": 0},
            "stage_level_left": "F",
            "stage_level_center": "O",
            "stage_level_right": "N",
            "parked": False,
        },
    ]
    unconsolidated_totals = [
        {
            "auto_speaker": 2,
            "auto_amp": 2,
            "tele_intakes_amp": 1,
            "tele_intakes_poach": 1,
            "tele_intakes_center": 1,
            "tele_intakes_far": 1,
            "tele_unamplified_speaker": 2,
            "tele_amplified": 0,
            "tele_ferry": 0,
            "tele_failed_amp": 0,
            "tele_failed_unamplified_speaker": 1,
            "tele_failed_amplified": 0,
            "auto_failed_amp": 0,
            "auto_failed_speaker": 0,
            "tele_amp": 1,
            "auto_intake_spike_1": 1,
            "auto_intake_spike_2": 1,
            "auto_intake_spike_3": 1,
            "auto_intake_center_1": 1,
            "auto_intake_center_2": 1,
            "auto_intake_center_3": 1,
            "auto_intake_center_4": 1,
            "auto_intake_center_5": 1,
            "tele_drop": 0,
            "incap_time": 33,
            "median_cycle_time": -6,
            "time_from_amp_to_amp": 7,
            "time_from_amp_to_speaker": 24,
            "time_from_poach_to_amp": 13,
            "time_from_poach_to_speaker": 30,
            "time_from_center_to_amp": 26,
            "time_from_center_to_speaker": 43,
            "time_from_far_to_amp": 37,
            "time_from_far_to_speaker": 39,
            "stage_level_left": "N",
            "stage_level_center": "O",
            "stage_level_right": "N",
            "start_position": "1",
            "has_preload": False,
            "parked": True,
            "trap": 1,
            "auto_total_points": 14,
            "tele_total_points": 5,
            "endgame_total_points": 0,
            "total_points": 24,
            "auto_total_intakes": 8,
            "auto_total_pieces": 4,
            "auto_total_failed_pieces": 0,
            "tele_total_intakes": 4,
            "tele_total_pieces": 3,
            "tele_total_failed_pieces": 1,
            "total_intakes": 12,
            "total_pieces": 7,
            "match_number": 42,
            "team_number": "254",
            "scout_name": "BOB",
        },
        {
            "auto_speaker": 2,
            "auto_amp": 2,
            "tele_intakes_amp": 1,
            "tele_intakes_poach": 1,
            "tele_intakes_center": 1,
            "tele_intakes_far": 1,
            "tele_unamplified_speaker": 2,
            "tele_amplified": 0,
            "tele_ferry": 0,
            "tele_failed_amp": 0,
            "tele_failed_unamplified_speaker": 1,
            "tele_failed_amplified": 0,
            "auto_failed_amp": 0,
            "auto_failed_speaker": 0,
            "tele_amp": 1,
            "auto_intake_spike_1": 1,
            "auto_intake_spike_2": 1,
            "auto_intake_spike_3": 1,
            "auto_intake_center_1": 1,
            "auto_intake_center_2": 1,
            "auto_intake_center_3": 1,
            "auto_intake_center_4": 1,
            "auto_intake_center_5": 1,
            "tele_drop": 0,
            "incap_time": 33,
            "median_cycle_time": -6,
            "time_from_amp_to_amp": 7,
            "time_from_amp_to_speaker": 24,
            "time_from_poach_to_amp": 13,
            "time_from_poach_to_speaker": 30,
            "time_from_center_to_amp": 26,
            "time_from_center_to_speaker": 43,
            "time_from_far_to_amp": 37,
            "time_from_far_to_speaker": 39,
            "stage_level_left": "N",
            "stage_level_center": "O",
            "stage_level_right": "N",
            "start_position": "1",
            "has_preload": False,
            "parked": True,
            "trap": 1,
            "auto_total_points": 14,
            "tele_total_points": 5,
            "endgame_total_points": 0,
            "total_points": 24,
            "auto_total_intakes": 8,
            "auto_total_pieces": 4,
            "auto_total_failed_pieces": 0,
            "tele_total_intakes": 4,
            "tele_total_pieces": 3,
            "tele_total_failed_pieces": 1,
            "total_intakes": 12,
            "total_pieces": 7,
            "match_number": 42,
            "team_number": "254",
            "scout_name": "DAVE",
        },
        {
            "auto_speaker": 2,
            "auto_amp": 2,
            "tele_intakes_amp": 1,
            "tele_intakes_poach": 1,
            "tele_intakes_center": 1,
            "tele_intakes_far": 1,
            "tele_unamplified_speaker": 2,
            "tele_amplified": 0,
            "tele_ferry": 0,
            "tele_failed_amp": 0,
            "tele_failed_unamplified_speaker": 1,
            "tele_failed_amplified": 0,
            "auto_failed_amp": 0,
            "auto_failed_speaker": 0,
            "tele_amp": 1,
            "auto_intake_spike_1": 1,
            "auto_intake_spike_2": 1,
            "auto_intake_spike_3": 1,
            "auto_intake_center_1": 1,
            "auto_intake_center_2": 1,
            "auto_intake_center_3": 1,
            "auto_intake_center_4": 1,
            "auto_intake_center_5": 1,
            "tele_drop": 0,
            "incap_time": 33,
            "median_cycle_time": -6,
            "time_from_amp_to_amp": 7,
            "time_from_amp_to_speaker": 24,
            "time_from_poach_to_amp": 13,
            "time_from_poach_to_speaker": 30,
            "time_from_center_to_amp": 26,
            "time_from_center_to_speaker": 43,
            "time_from_far_to_amp": 37,
            "time_from_far_to_speaker": 39,
            "stage_level_left": "N",
            "stage_level_center": "O",
            "stage_level_right": "N",
            "start_position": "1",
            "has_preload": False,
            "parked": True,
            "trap": 1,
            "auto_total_points": 14,
            "tele_total_points": 5,
            "endgame_total_points": 0,
            "total_points": 24,
            "auto_total_intakes": 8,
            "auto_total_pieces": 4,
            "auto_total_failed_pieces": 0,
            "tele_total_intakes": 4,
            "tele_total_pieces": 3,
            "tele_total_failed_pieces": 1,
            "total_intakes": 12,
            "total_pieces": 7,
            "match_number": 42,
            "team_number": "254",
            "scout_name": "ANDY",
        },
    ]

    calculated_tim_data = {
        "auto_speaker": 2,
        "auto_amp": 2,
        "tele_intakes_amp": 1,
        "tele_intakes_poach": 1,
        "tele_intakes_center": 1,
        "tele_intakes_far": 1,
        "tele_unamplified_speaker": 2,
        "tele_amplified": 0,
        "tele_ferry": 0,
        "tele_failed_amp": 0,
        "tele_failed_unamplified_speaker": 1,
        "tele_failed_amplified": 0,
        "auto_failed_amp": 0,
        "auto_failed_speaker": 0,
        "tele_amp": 1,
        "auto_intake_spike_1": 1,
        "auto_intake_spike_2": 1,
        "auto_intake_spike_3": 1,
        "auto_intake_center_1": 1,
        "auto_intake_center_2": 1,
        "auto_intake_center_3": 1,
        "auto_intake_center_4": 1,
        "auto_intake_center_5": 1,
        "tele_drop": 0,
        "incap_time": 33,
        "median_cycle_time": -6,
        "time_from_amp_to_amp": 7,
        "time_from_amp_to_speaker": 24,
        "time_from_poach_to_amp": 13,
        "time_from_poach_to_speaker": 30,
        "time_from_center_to_amp": 26,
        "time_from_center_to_speaker": 43,
        "time_from_far_to_amp": 37,
        "time_from_far_to_speaker": 39,
        "stage_level_left": "N",
        "stage_level_center": "O",
        "stage_level_right": "N",
        "start_position": "1",
        "has_preload": False,
        "parked": True,
        "trap": 1,
        "auto_total_points": 14,
        "tele_total_points": 5,
        "endgame_total_points": 0,
        "total_points": 24,
        "auto_total_intakes": 8,
        "auto_total_pieces": 4,
        "auto_total_failed_pieces": 0,
        "tele_total_intakes": 4,
        "tele_total_pieces": 3,
        "tele_total_failed_pieces": 1,
        "total_intakes": 12,
        "total_pieces": 7,
        "match_number": 42,
        "team_number": "254",
        "confidence_ranking": 3,
    }

    @mock.patch.object(
        base_calculations.BaseCalculations, "get_teams_list", return_value=["3", "254", "1"]
    )
    def setup_method(self, method, get_teams_list_dummy):
        with mock.patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = Server()
        self.test_calculator = obj_tims.ObjTIMCalcs(self.test_server)

    def test_modes(self):
        assert self.test_calculator.modes([3, 3, 3]) == [3]
        assert self.test_calculator.modes([]) == []
        assert self.test_calculator.modes([1, 1, 2, 2]) == [1, 2]
        assert self.test_calculator.modes([1, 1, 2, 2, 3]) == [1, 2]
        assert self.test_calculator.modes([1, 2, 3, 1]) == [1]
        assert self.test_calculator.modes([1, 4, 3, 4]) == [4]
        assert self.test_calculator.modes([9, 6, 3, 9]) == [9]

    def test_consolidate_nums(self):
        assert self.test_calculator.consolidate_nums([3, 3, 3]) == 3
        assert self.test_calculator.consolidate_nums([4, 4, 4, 4, 1]) == 4
        assert self.test_calculator.consolidate_nums([2, 2, 1]) == 2
        assert self.test_calculator.consolidate_nums([]) == 0

    def test_consolidate_bools(self):
        assert self.test_calculator.consolidate_bools([True, True, True]) == True
        assert self.test_calculator.consolidate_bools([False, True, True]) == True
        assert self.test_calculator.consolidate_bools([False, False, True]) == False
        assert self.test_calculator.consolidate_bools([False, False, False]) == False

    def test_filter_timeline_actions(self):
        actions = self.test_calculator.filter_timeline_actions(self.unconsolidated_tims[0])
        assert actions == [
            {"in_teleop": False, "time": 148, "action_type": "auto_intake_center_5"},
            {"in_teleop": False, "time": 147, "action_type": "score_speaker"},
            {"in_teleop": True, "time": 135, "action_type": "to_teleop"},
            {"in_teleop": True, "time": 130, "action_type": "intake_amp"},
            {"in_teleop": True, "time": 125, "action_type": "score_speaker"},
            {"in_teleop": True, "time": 120, "action_type": "intake_far"},
            {"in_teleop": True, "time": 115, "action_type": "score_amp"},
            {"in_teleop": True, "time": 114, "action_type": "intake_far"},
            {"in_teleop": True, "time": 110, "action_type": "score_speaker"},
            {"in_teleop": True, "time": 108, "action_type": "intake_poach"},
            {"in_teleop": True, "time": 104, "action_type": "score_amp"},
            {"in_teleop": True, "time": 95, "action_type": "intake_amp"},
            {"in_teleop": True, "time": 90, "action_type": "score_amp"},
            {"in_teleop": True, "time": 80, "action_type": "start_incap_time"},
            {"in_teleop": True, "time": 75, "action_type": "end_incap_time"},
            {"in_teleop": True, "time": 71, "action_type": "intake_poach"},
            {"in_teleop": True, "time": 70, "action_type": "fail"},
            {"in_teleop": True, "time": 63, "action_type": "score_amplify"},
            {"in_teleop": True, "time": 56, "action_type": "intake_far"},
            {"in_teleop": True, "time": 54, "action_type": "score_amp"},
            {"in_teleop": True, "time": 40, "action_type": "intake_poach"},
            {"in_teleop": True, "time": 31, "action_type": "score_speaker"},
            {"in_teleop": True, "time": 28, "action_type": "intake_amp"},
            {"in_teleop": True, "time": 20, "action_type": "fail"},
            {"in_teleop": True, "time": 16, "action_type": "score_amp"},
            {"in_teleop": True, "time": 14, "action_type": "intake_far"},
            {"in_teleop": True, "time": 12, "action_type": "ferry"},
            {"in_teleop": True, "time": 9, "action_type": "start_incap_time"},
            {"in_teleop": False, "time": 3, "action_type": "to_endgame"},
            {"in_teleop": False, "time": 2, "action_type": "end_incap_time"},
        ]

    def test_count_timeline_actions(self):
        action_num = self.test_calculator.count_timeline_actions(self.unconsolidated_tims[0])
        assert action_num == 30

    def test_total_time_between_actions(self):
        total_time = self.test_calculator.total_time_between_actions
        assert (
            total_time(self.unconsolidated_tims[0], "start_incap_time", "end_incap_time", 1) == 12
        )
        assert (
            total_time(self.unconsolidated_tims[2], "start_incap_time", "end_incap_time", 1) == 12
        )

    def test_calculate_expected_fields(self):
        expected_results = {
            "expected_cycle_time": 19.12,
            "expected_speaker_cycle_time": 56.65,
            "expected_amp_cycle_time": 28.85,
            "expected_cycles": 6.91,
            "expected_speaker_cycles": 2.33,
            "expected_amp_cycles": 4.58,
            "expected_notes": 6.08,
            "expected_speaker_notes": 1.83,
            "expected_amp_notes": 4.25,
        }
        # Fails must be calculated first in order for the calculation to work
        after_fails = self.test_calculator.score_fail_type(self.unconsolidated_tims)
        result = self.test_calculator.calculate_expected_fields(after_fails, {"incap_time": 0})
        assert result == expected_results

    def test_score_fail_type(self):
        score_fails = self.test_calculator.score_fail_type(self.unconsolidated_tims)
        assert score_fails[0]["timeline"][17]["action_type"] == "score_fail_amplify"
        assert score_fails[1]["timeline"][17]["action_type"] == "score_fail_amplify"
        assert score_fails[2]["timeline"][24]["action_type"] == "score_fail_amp"

    def test_calculate_aggregates(self):
        aggregated_values = self.test_calculator.calculate_aggregates(self.calculated_tim_data)
        assert aggregated_values == {
            "auto_total_intakes": 8,
            "auto_intakes_spike": 3,
            "auto_intakes_center": 5,
            "auto_total_pieces": 4,
            "auto_total_failed_pieces": 0,
            "tele_total_intakes": 4,
            "total_intakes": 12,
        }

    def test_calculate_point_values(self):
        point_values = self.test_calculator.calculate_point_values(self.calculated_tim_data)
        assert point_values == {
            "auto_total_points": 14,
            "endgame_total_points": 6,
            "tele_total_points": 5,
            "total_points": 19,
            "points_per_note": 3.0,
        }

    def test_calculate_harmony(self):
        test_calculated_tims = [
            {
                "alliance_color_is_red": True,
                "auto_speaker": 2,
                "auto_amp": 2,
                "tele_intakes_amp": 1,
                "tele_intakes_poach": 1,
                "tele_intakes_center": 1,
                "tele_intakes_far": 1,
                "tele_unamplified_speaker": 2,
                "tele_amplified": 0,
                "tele_ferry": 0,
                "tele_failed_amp": 0,
                "tele_failed_unamplified_speaker": 1,
                "tele_failed_amplified": 0,
                "auto_failed_amp": 0,
                "auto_failed_speaker": 0,
                "tele_amp": 1,
                "auto_intake_spike_1": 1,
                "auto_intake_spike_2": 1,
                "auto_intake_spike_3": 1,
                "auto_intake_center_1": 1,
                "auto_intake_center_2": 1,
                "auto_intake_center_3": 1,
                "auto_intake_center_4": 1,
                "auto_intake_center_5": 1,
                "tele_drop": 0,
                "incap_time": 33,
                "median_cycle_time": -6,
                "time_from_amp_to_amp": 7,
                "time_from_amp_to_speaker": 24,
                "time_from_poach_to_amp": 13,
                "time_from_poach_to_speaker": 30,
                "time_from_center_to_amp": 26,
                "time_from_center_to_speaker": 43,
                "time_from_far_to_amp": 37,
                "time_from_far_to_speaker": 39,
                "stage_level_left": "N",
                "stage_level_center": "O",
                "stage_level_right": "N",
                "start_position": "1",
                "has_preload": False,
                "parked": True,
                "auto_total_points": 14,
                "tele_total_points": 5,
                "endgame_total_points": 0,
                "total_points": 19,
                "auto_total_intakes": 8,
                "auto_total_pieces": 4,
                "auto_total_failed_pieces": 0,
                "tele_total_intakes": 4,
                "tele_total_pieces": 3,
                "tele_total_failed_pieces": 1,
                "total_intakes": 12,
                "total_pieces": 7,
                "match_number": 42,
                "team_number": "254",
                "confidence_ranking": 3,
            },
            {
                "alliance_color_is_red": True,
                "auto_speaker": 2,
                "auto_amp": 2,
                "tele_intakes_amp": 1,
                "tele_intakes_poach": 1,
                "tele_intakes_center": 1,
                "tele_intakes_far": 1,
                "tele_unamplified_speaker": 2,
                "tele_amplified": 0,
                "tele_ferry": 0,
                "tele_failed_amp": 0,
                "tele_failed_unamplified_speaker": 1,
                "tele_failed_amplified": 0,
                "auto_failed_amp": 0,
                "auto_failed_speaker": 0,
                "tele_amp": 1,
                "auto_intake_spike_1": 1,
                "auto_intake_spike_2": 1,
                "auto_intake_spike_3": 1,
                "auto_intake_center_1": 1,
                "auto_intake_center_2": 1,
                "auto_intake_center_3": 1,
                "auto_intake_center_4": 1,
                "auto_intake_center_5": 1,
                "tele_drop": 0,
                "incap_time": 33,
                "median_cycle_time": -6,
                "time_from_amp_to_amp": 7,
                "time_from_amp_to_speaker": 24,
                "time_from_poach_to_amp": 13,
                "time_from_poach_to_speaker": 30,
                "time_from_center_to_amp": 26,
                "time_from_center_to_speaker": 43,
                "time_from_far_to_amp": 37,
                "time_from_far_to_speaker": 39,
                "stage_level_left": "N",
                "stage_level_center": "O",
                "stage_level_right": "N",
                "start_position": "1",
                "has_preload": False,
                "parked": True,
                "auto_total_points": 14,
                "tele_total_points": 5,
                "endgame_total_points": 0,
                "total_points": 19,
                "auto_total_intakes": 8,
                "auto_total_pieces": 4,
                "auto_total_failed_pieces": 0,
                "tele_total_intakes": 4,
                "tele_total_pieces": 3,
                "tele_total_failed_pieces": 1,
                "total_intakes": 12,
                "total_pieces": 7,
                "match_number": 42,
                "team_number": "1678",
                "confidence_ranking": 3,
            },
            {
                "alliance_color_is_red": False,
                "auto_speaker": 2,
                "auto_amp": 2,
                "tele_intakes_amp": 1,
                "tele_intakes_poach": 1,
                "tele_intakes_center": 1,
                "tele_intakes_far": 1,
                "tele_unamplified_speaker": 2,
                "tele_amplified": 0,
                "tele_ferry": 0,
                "tele_failed_amp": 0,
                "tele_failed_unamplified_speaker": 1,
                "tele_failed_amplified": 0,
                "auto_failed_amp": 0,
                "auto_failed_speaker": 0,
                "tele_amp": 1,
                "auto_intake_spike_1": 1,
                "auto_intake_spike_2": 1,
                "auto_intake_spike_3": 1,
                "auto_intake_center_1": 1,
                "auto_intake_center_2": 1,
                "auto_intake_center_3": 1,
                "auto_intake_center_4": 1,
                "auto_intake_center_5": 1,
                "tele_drop": 0,
                "incap_time": 33,
                "median_cycle_time": -6,
                "time_from_amp_to_amp": 7,
                "time_from_amp_to_speaker": 24,
                "time_from_poach_to_amp": 13,
                "time_from_poach_to_speaker": 30,
                "time_from_center_to_amp": 26,
                "time_from_center_to_speaker": 43,
                "time_from_far_to_amp": 37,
                "time_from_far_to_speaker": 39,
                "stage_level_left": "N",
                "stage_level_center": "O",
                "stage_level_right": "N",
                "start_position": "1",
                "has_preload": False,
                "parked": True,
                "auto_total_points": 14,
                "tele_total_points": 5,
                "endgame_total_points": 0,
                "total_points": 19,
                "auto_total_intakes": 8,
                "auto_total_pieces": 4,
                "auto_total_failed_pieces": 0,
                "tele_total_intakes": 4,
                "tele_total_pieces": 3,
                "tele_total_failed_pieces": 1,
                "total_intakes": 12,
                "total_pieces": 7,
                "match_number": 42,
                "team_number": "123",
                "confidence_ranking": 3,
            },
        ]
        harmonized_teams = self.test_calculator.calculate_harmony(test_calculated_tims)
        expected_result = [
            {"team_number": "254", "match_number": 42},
            {"team_number": "1678", "match_number": 42},
        ]
        assert harmonized_teams == expected_result

    def test_calculate_tim_times(self):
        calculated_tim = self.test_calculator.calculate_tim_times(self.unconsolidated_tims)
        assert calculated_tim["incap_time"] == 0

    def test_run_consolidation(self):
        self.test_server.db.insert_documents("unconsolidated_obj_tim", self.unconsolidated_tims)
        self.test_server.db.delete_data("unconsolidated_totals")
        self.test_server.db.insert_documents("unconsolidated_totals", self.unconsolidated_totals)
        with patch("data_transfer.tba_communicator.tba_request", return_value=self.tba_test_data):
            self.test_calculator.run()
        result = self.test_server.db.find("obj_tim")
        assert len(result) == 1
        calculated_tim = result[0]
        assert calculated_tim["confidence_ranking"] == 3
        assert calculated_tim["expected_speaker_cycle_time"] == 56.65
        assert calculated_tim["expected_amp_cycle_time"] == 28.85
        assert calculated_tim["incap_time"] == 0
        assert calculated_tim["match_number"] == 42
        assert calculated_tim["team_number"] == "254"
        assert calculated_tim["auto_total_intakes"] == 1
        assert calculated_tim["auto_total_pieces"] == 1
        assert calculated_tim["tele_total_intakes"] == 10
        assert calculated_tim["tele_total_pieces"] == 4
        assert calculated_tim["total_intakes"] == 11
        assert calculated_tim["total_pieces"] == 8
        assert calculated_tim["tele_ferry_drive"] == 0
        assert calculated_tim["tele_ferry_shoot"] == 0
        assert calculated_tim["start_position"] == "1"
        assert calculated_tim["has_preload"] == False
        assert calculated_tim["expected_speaker_cycles"] == 2.33
        assert calculated_tim["expected_amp_cycles"] == 4.58
        assert calculated_tim["expected_speaker_notes"] == 1.83
        assert calculated_tim["expected_amp_notes"] == 4.25
        assert calculated_tim["expected_cycle_time"] == 19.12
        assert calculated_tim["expected_notes"] == 6.08
        assert calculated_tim["expected_cycles"] == 6.91
        assert calculated_tim["climbed"] == True

    @mock.patch.object(
        obj_tims.ObjTIMCalcs,
        "entries_since_last",
        return_value=[{"o": {"team_number": "1", "match_number": 2}}],
    )
    def test_in_list_check1(self, entries_since_last_dummy, caplog):
        with patch("data_transfer.tba_communicator.tba_request", return_value=self.tba_test_data):
            self.test_calculator.run()
        assert len([rec.message for rec in caplog.records if rec.levelname == "WARNING"]) > 0

    @mock.patch.object(
        obj_tims.ObjTIMCalcs,
        "entries_since_last",
        return_value=[{"o": {"team_number": "3", "match_number": 2}}],
    )
    @mock.patch.object(obj_tims.ObjTIMCalcs, "update_calcs", return_value=[{}])
    def test_in_list_check2(self, entries_since_last_dummy, update_calcs_dummy, caplog):
        with patch("data_transfer.tba_communicator.tba_request", return_value=self.tba_test_data):
            self.test_calculator.run()
        assert len([rec.message for rec in caplog.records if rec.levelname == "WARNING"]) == 0
