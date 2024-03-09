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
    unconsolidated_totals = [
        {
            "scout_name": "EDWIN",
            "match_number": 42,
            "team_number": "254",
            "alliance_color_is_red": True,
            "auto_speaker": 2,
            "auto_total_intakes": 8,
            "auto_amp": 2,
            "tele_intakes_amp": 1,
            "tele_intakes_poach": 1,
            "tele_intakes_center": 1,
            "tele_intakes_far": 1,
            "tele_speaker": 3,
            "tele_amplified": 0,
            "tele_ferry": 0,
            "tele_failed_amp": 0,
            "tele_failed_speaker": 2,
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
            "auto_intakes_spike": 3,
            "auto_intakes_center": 5,
            "auto_total_pieces": 4,
            "auto_total_failed_pieces": 0,
            "tele_total_intakes": 4,
            "tele_total_pieces": 4,
            "tele_total_failed_pieces": 2,
            "total_intakes": 12,
            "total_pieces": 8,
            "stage_level_left": "N",
            "stage_level_center": "F",
            "stage_level_right": "O",
            "start_position": "1",
            "trap": "F",
            "has_preload": False,
            "parked": True,
            "incap_time": 33,
            "median_cycle_time": 0,
            "time_from_amp_to_amp": 7,
            "time_from_amp_to_speaker": 24,
            "time_from_poach_to_amp": 13,
            "time_from_poach_to_speaker": 30,
            "time_from_center_to_amp": 26,
            "time_from_center_to_speaker": 43,
            "time_from_far_to_amp": 37,
            "time_from_far_to_speaker": 54,
            "expected_speaker_cycle_time": 49.62,
            "expected_amp_cycle_time": 36.87,
            "expected_speaker_cycles": 2.66,
            "expected_amp_cycles": 3.58,
            "expected_speaker_notes": 1.58,
            "expected_amp_notes": 2.58,
            "expected_cycle_time": 24.04,
            "expected_notes": 4.16,
            "expected_cycles": 5.49,
        },
        {
            "scout_name": "RAY",
            "match_number": 42,
            "team_number": "254",
            "alliance_color_is_red": True,
            "auto_speaker": 2,
            "auto_total_intakes": 8,
            "auto_amp": 2,
            "tele_intakes_amp": 1,
            "tele_intakes_poach": 1,
            "tele_intakes_center": 1,
            "tele_intakes_far": 1,
            "tele_speaker": 2,
            "tele_amplified": 0,
            "tele_ferry": 0,
            "tele_failed_amp": 1,
            "tele_failed_speaker": 1,
            "tele_failed_amplified": 0,
            "auto_failed_amp": 0,
            "auto_failed_speaker": 0,
            "tele_amp": 2,
            "auto_intake_spike_1": 1,
            "auto_intake_spike_2": 1,
            "auto_intake_spike_3": 1,
            "auto_intake_center_1": 1,
            "auto_intake_center_2": 1,
            "auto_intake_center_3": 1,
            "auto_intake_center_4": 1,
            "auto_intake_center_5": 1,
            "tele_drop": 0,
            "auto_intakes_spike": 3,
            "auto_intakes_center": 5,
            "auto_total_pieces": 4,
            "auto_total_failed_pieces": 0,
            "tele_total_intakes": 4,
            "tele_total_pieces": 4,
            "tele_total_failed_pieces": 2,
            "total_intakes": 12,
            "total_pieces": 8,
            "stage_level_left": "N",
            "stage_level_center": "O",
            "stage_level_right": "N",
            "start_position": "3",
            "trap": "S",
            "has_preload": False,
            "parked": True,
            "incap_time": 33,
            "median_cycle_time": 0,
            "time_from_amp_to_amp": 7,
            "time_from_amp_to_speaker": 5,
            "time_from_poach_to_amp": 13,
            "time_from_poach_to_speaker": 11,
            "time_from_center_to_amp": 26,
            "time_from_center_to_speaker": 24,
            "time_from_far_to_amp": 37,
            "time_from_far_to_speaker": 35,
            "expected_speaker_cycle_time": 49.62,
            "expected_amp_cycle_time": 36.87,
            "expected_speaker_cycles": 2.66,
            "expected_amp_cycles": 3.58,
            "expected_speaker_notes": 1.58,
            "expected_amp_notes": 2.58,
            "expected_cycle_time": 24.04,
            "expected_notes": 4.16,
            "expected_cycles": 5.49,
        },
        {
            "scout_name": "ADRIAN",
            "match_number": 42,
            "team_number": "254",
            "alliance_color_is_red": False,
            "auto_speaker": 2,
            "auto_total_intakes": 8,
            "auto_amp": 2,
            "tele_intakes_amp": 1,
            "tele_intakes_poach": 1,
            "tele_intakes_center": 1,
            "tele_intakes_far": 2,
            "tele_speaker": 2,
            "tele_amplified": 1,
            "tele_ferry": 0,
            "tele_failed_amp": 0,
            "tele_failed_speaker": 1,
            "tele_failed_amplified": 1,
            "auto_failed_amp": 0,
            "auto_failed_speaker": 0,
            "tele_amp": 0,
            "auto_intake_spike_1": 1,
            "auto_intake_spike_2": 1,
            "auto_intake_spike_3": 1,
            "auto_intake_center_1": 1,
            "auto_intake_center_2": 1,
            "auto_intake_center_3": 1,
            "auto_intake_center_4": 1,
            "auto_intake_center_5": 1,
            "tele_drop": 0,
            "auto_intakes_spike": 3,
            "auto_intakes_center": 5,
            "auto_total_pieces": 4,
            "auto_total_failed_pieces": 0,
            "tele_total_intakes": 5,
            "tele_total_pieces": 3,
            "tele_total_failed_pieces": 1,
            "total_intakes": 13,
            "total_pieces": 7,
            "stage_level_left": "F",
            "stage_level_center": "O",
            "stage_level_right": "N",
            "start_position": "1",
            "trap": "O",
            "has_preload": False,
            "parked": False,
            "incap_time": 43,
            "median_cycle_time": 0,
            "time_from_amp_to_amp": 0,
            "time_from_amp_to_speaker": 24,
            "time_from_poach_to_amp": 0,
            "time_from_poach_to_speaker": 30,
            "time_from_center_to_amp": 0,
            "time_from_center_to_speaker": 43,
            "time_from_far_to_amp": 0,
            "time_from_far_to_speaker": 38,
            "expected_speaker_cycle_time": 49.62,
            "expected_amp_cycle_time": 36.87,
            "expected_speaker_cycles": 2.66,
            "expected_amp_cycles": 3.58,
            "expected_speaker_notes": 1.58,
            "expected_amp_notes": 2.58,
            "expected_cycle_time": 24.04,
            "expected_notes": 4.16,
            "expected_cycles": 5.49,
        },
    ]

    calculated_tim_data = {
        "auto_speaker": 2,
        "auto_amp": 2,
        "tele_intakes_amp": 1,
        "tele_intakes_poach": 1,
        "tele_intakes_center": 1,
        "tele_intakes_far": 1,
        "tele_speaker": 2,
        "tele_amplified": 0,
        "tele_ferry": 0,
        "tele_failed_amp": 0,
        "tele_failed_speaker": 1,
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
        "trap": "F",
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
        "tele_total_pieces": 4,
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

    def test_calculate_point_values(self):
        point_values = self.test_calculator.calculate_point_values(self.calculated_tim_data)
        assert point_values == {
            "auto_total_points": 14,
            "endgame_total_points": 1,
            "tele_total_points": 5,
            "total_points": 19,
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
                "tele_speaker": 2,
                "tele_amplified": 0,
                "tele_ferry": 0,
                "tele_failed_amp": 0,
                "tele_failed_speaker": 1,
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
                "trap": "F",
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
                "tele_speaker": 2,
                "tele_amplified": 0,
                "tele_ferry": 0,
                "tele_failed_amp": 0,
                "tele_failed_speaker": 1,
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
                "trap": "F",
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
                "tele_speaker": 2,
                "tele_amplified": 0,
                "tele_ferry": 0,
                "tele_failed_amp": 0,
                "tele_failed_speaker": 1,
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
                "trap": "F",
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

    def test_run_consolidation(self):
        self.test_server.db.insert_documents("unconsolidated_totals", self.unconsolidated_totals)
        with patch("data_transfer.tba_communicator.tba_request", return_value=self.tba_test_data):
            self.test_calculator.run()
        result = self.test_server.db.find("obj_tim")
        assert len(result) == 1
        calculated_tim = result[0]
        print(result)
        assert calculated_tim["confidence_ranking"] == 3
        assert calculated_tim["expected_speaker_cycle_time"] == 50
        assert calculated_tim["expected_amp_cycle_time"] == 37
        assert calculated_tim["incap_time"] == 33
        assert calculated_tim["match_number"] == 42
        assert calculated_tim["team_number"] == "254"
        assert calculated_tim["auto_total_intakes"] == 8
        assert calculated_tim["auto_total_pieces"] == 4
        assert calculated_tim["tele_total_intakes"] == 4
        assert calculated_tim["tele_total_pieces"] == 4
        assert calculated_tim["total_intakes"] == 12
        assert calculated_tim["total_pieces"] == 8
        assert calculated_tim["start_position"] == "1"
        assert calculated_tim["has_preload"] == False
        assert calculated_tim["expected_speaker_cycles"] == 3
        assert calculated_tim["expected_amp_cycles"] == 4
        assert calculated_tim["expected_speaker_notes"] == 2
        assert calculated_tim["expected_amp_notes"] == 3
        assert calculated_tim["expected_cycle_time"] == 24
        assert calculated_tim["expected_notes"] == 4
        assert calculated_tim["expected_cycles"] == 5
        assert calculated_tim["expected_speaker_cycles"] == 3
        assert calculated_tim["expected_amp_cycles"] == 4
        assert calculated_tim["expected_speaker_notes"] == 2
        assert calculated_tim["expected_amp_notes"] == 3
        assert calculated_tim["expected_cycle_time"] == 24
        assert calculated_tim["expected_notes"] == 4
        assert calculated_tim["expected_cycles"] == 5
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
