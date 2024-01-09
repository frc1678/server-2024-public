# Copyright (c) 2023 FRC Team 1678: Citrus Circuits

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
                {"in_teleop": True, "time": 2, "action_type": "end_incap"},
                {"in_teleop": True, "time": 35, "action_type": "start_incap"},
                {"in_teleop": True, "time": 51, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 68, "action_type": "score_amp"},
                {"in_teleop": True, "time": 70, "action_type": "score_trap"},
                {"in_teleop": True, "time": 75, "action_type": "intake_amp"},
                {"in_teleop": True, "time": 81, "action_type": "intake_poach"},
                {"in_teleop": True, "time": 94, "action_type": "intake_center"},
                {"in_teleop": True, "time": 105, "action_type": "intake_far"},
                {"in_teleop": True, "time": 110, "action_type": "shoot_other"},
                {"in_teleop": True, "time": 117, "action_type": "score_fail"},
                {"in_teleop": True, "time": 125, "action_type": "amplified"},
                {"in_teleop": True, "time": 130, "action_type": "end_incap"},
                {"in_teleop": True, "time": 132, "action_type": "start_incap"},
                {"in_teleop": False, "time": 138, "action_type": "auto_intake_spike_1"},
                {"in_teleop": False, "time": 139, "action_type": "auto_intake_spike_2"},
                {"in_teleop": False, "time": 141, "action_type": "score_amp"},
                {"in_teleop": False, "time": 140, "action_type": "auto_intake_spike_3"},
                {"in_teleop": False, "time": 142, "action_type": "score_trap"},
                {"in_teleop": False, "time": 143, "action_type": "auto_intake_center_1"},
                {"in_teleop": False, "time": 144, "action_type": "score_amp"},
                {"in_teleop": False, "time": 145, "action_type": "auto_intake_center_2"},
                {"in_teleop": False, "time": 147, "action_type": "score_trap"},
                {"in_teleop": False, "time": 146, "action_type": "auto_intake_center_3"},
                {"in_teleop": False, "time": 148, "action_type": "auto_intake_center_4"},
                {"in_teleop": False, "time": 150, "action_type": "auto_intake_center_5"},
            ],
            "stage_level": "P",
            "start_position": "1",
            "has_preload": False,
            "override": {"failed_scores": 0},
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
                {"in_teleop": True, "time": 2, "action_type": "end_incap"},
                {"in_teleop": True, "time": 35, "action_type": "start_incap"},
                {"in_teleop": True, "time": 51, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 68, "action_type": "score_amp"},
                {"in_teleop": True, "time": 70, "action_type": "score_trap"},
                {"in_teleop": True, "time": 75, "action_type": "intake_amp"},
                {"in_teleop": True, "time": 81, "action_type": "intake_poach"},
                {"in_teleop": True, "time": 94, "action_type": "intake_center"},
                {"in_teleop": True, "time": 105, "action_type": "intake_far"},
                {"in_teleop": True, "time": 110, "action_type": "shoot_other"},
                {"in_teleop": True, "time": 117, "action_type": "score_fail"},
                {"in_teleop": True, "time": 125, "action_type": "amplified"},
                {"in_teleop": True, "time": 130, "action_type": "end_incap"},
                {"in_teleop": True, "time": 132, "action_type": "start_incap"},
                {"in_teleop": False, "time": 138, "action_type": "auto_intake_spike_1"},
                {"in_teleop": False, "time": 139, "action_type": "auto_intake_spike_2"},
                {"in_teleop": False, "time": 141, "action_type": "score_amp"},
                {"in_teleop": False, "time": 140, "action_type": "auto_intake_spike_3"},
                {"in_teleop": False, "time": 142, "action_type": "score_trap"},
                {"in_teleop": False, "time": 143, "action_type": "auto_intake_center_1"},
                {"in_teleop": False, "time": 144, "action_type": "score_amp"},
                {"in_teleop": False, "time": 145, "action_type": "auto_intake_center_2"},
                {"in_teleop": False, "time": 147, "action_type": "score_trap"},
                {"in_teleop": False, "time": 146, "action_type": "auto_intake_center_3"},
                {"in_teleop": False, "time": 148, "action_type": "auto_intake_center_4"},
                {"in_teleop": False, "time": 150, "action_type": "auto_intake_center_5"},
            ],
            "stage_level": "P",
            "start_position": "3",
            "has_preload": False,
            "override": {"failed_scores": 0},
        },
        {
            "schema_version": 6,
            "serial_number": "STR5",
            "match_number": 42,
            "timestamp": 11,
            "match_collection_version_number": "STR6",
            "scout_name": "ADRIAN",
            "alliance_color_is_red": False,
            "team_number": "254",
            "scout_id": 17,
            "timeline": [
                {"in_teleop": True, "time": 2, "action_type": "end_incap"},
                {"in_teleop": True, "time": 45, "action_type": "start_incap"},
                {"in_teleop": True, "time": 51, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 68, "action_type": "score_amp"},
                {"in_teleop": True, "time": 70, "action_type": "score_trap"},
                {"in_teleop": True, "time": 75, "action_type": "intake_amp"},
                {"in_teleop": True, "time": 81, "action_type": "intake_poach"},
                {"in_teleop": True, "time": 94, "action_type": "intake_center"},
                {"in_teleop": True, "time": 105, "action_type": "intake_far"},
                {"in_teleop": True, "time": 110, "action_type": "shoot_other"},
                {"in_teleop": True, "time": 117, "action_type": "score_fail"},
                {"in_teleop": True, "time": 125, "action_type": "amplified"},
                {"in_teleop": True, "time": 130, "action_type": "end_incap"},
                {"in_teleop": True, "time": 132, "action_type": "start_incap"},
                {"in_teleop": False, "time": 138, "action_type": "auto_intake_spike_1"},
                {"in_teleop": False, "time": 139, "action_type": "auto_intake_spike_2"},
                {"in_teleop": False, "time": 141, "action_type": "score_amp"},
                {"in_teleop": False, "time": 140, "action_type": "auto_intake_spike_3"},
                {"in_teleop": False, "time": 142, "action_type": "score_trap"},
                {"in_teleop": False, "time": 143, "action_type": "auto_intake_center_1"},
                {"in_teleop": False, "time": 144, "action_type": "score_amp"},
                {"in_teleop": False, "time": 145, "action_type": "auto_intake_center_2"},
                {"in_teleop": False, "time": 147, "action_type": "score_trap"},
                {"in_teleop": False, "time": 146, "action_type": "auto_intake_center_3"},
                {"in_teleop": False, "time": 148, "action_type": "auto_intake_center_4"},
                {"in_teleop": False, "time": 150, "action_type": "auto_intake_center_5"},
            ],
            "stage_level": "P",
            "start_position": "1",
            "has_preload": False,
            "override": {"failed_scores": 0},
        },
    ]

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
            {"in_teleop": True, "time": 2, "action_type": "end_incap"},
            {"in_teleop": True, "time": 35, "action_type": "start_incap"},
            {"in_teleop": True, "time": 51, "action_type": "score_speaker"},
            {"in_teleop": True, "time": 68, "action_type": "score_amp"},
            {"in_teleop": True, "time": 70, "action_type": "score_trap"},
            {"in_teleop": True, "time": 75, "action_type": "intake_amp"},
            {"in_teleop": True, "time": 81, "action_type": "intake_poach"},
            {"in_teleop": True, "time": 94, "action_type": "intake_center"},
            {"in_teleop": True, "time": 105, "action_type": "intake_far"},
            {"in_teleop": True, "time": 110, "action_type": "shoot_other"},
            {"in_teleop": True, "time": 117, "action_type": "score_fail"},
            {"in_teleop": True, "time": 125, "action_type": "amplified"},
            {"in_teleop": True, "time": 130, "action_type": "end_incap"},
            {"in_teleop": True, "time": 132, "action_type": "start_incap"},
            {"in_teleop": False, "time": 138, "action_type": "auto_intake_spike_1"},
            {"in_teleop": False, "time": 139, "action_type": "auto_intake_spike_2"},
            {"in_teleop": False, "time": 141, "action_type": "score_amp"},
            {"in_teleop": False, "time": 140, "action_type": "auto_intake_spike_3"},
            {"in_teleop": False, "time": 142, "action_type": "score_trap"},
            {"in_teleop": False, "time": 143, "action_type": "auto_intake_center_1"},
            {"in_teleop": False, "time": 144, "action_type": "score_amp"},
            {"in_teleop": False, "time": 145, "action_type": "auto_intake_center_2"},
            {"in_teleop": False, "time": 147, "action_type": "score_trap"},
            {"in_teleop": False, "time": 146, "action_type": "auto_intake_center_3"},
            {"in_teleop": False, "time": 148, "action_type": "auto_intake_center_4"},
            {"in_teleop": False, "time": 150, "action_type": "auto_intake_center_5"},
        ]

    def test_count_timeline_actions(self):
        action_num = self.test_calculator.count_timeline_actions(self.unconsolidated_tims[0])
        assert action_num == 26

    def test_total_time_between_actions(self):
        total_time = self.test_calculator.total_time_between_actions
        assert total_time(self.unconsolidated_tims[0], "start_incap", "end_incap", 8) == 33
        assert total_time(self.unconsolidated_tims[2], "start_incap", "end_incap", 8) == 43

    def test_run_consolidation(self):
        self.test_server.db.insert_documents("unconsolidated_obj_tim", self.unconsolidated_tims)
        with patch("data_transfer.tba_communicator.tba_request", return_value=self.tba_test_data):
            self.test_calculator.run()
        result = self.test_server.db.find("obj_tim")
        assert len(result) == 1
        calculated_tim = result[0]
        assert calculated_tim["confidence_ranking"] == 3
        assert calculated_tim["incap"] == 33
        assert calculated_tim["match_number"] == 42
        assert calculated_tim["team_number"] == "254"
        assert calculated_tim["auto_total_intakes"] == 8
        assert calculated_tim["auto_total_pieces"] == 2
        assert calculated_tim["tele_total_intakes"] == 4
        assert calculated_tim["tele_total_pieces"] == 2
        assert calculated_tim["total_intakes"] == 12
        assert calculated_tim["total_pieces"] == 4
        assert calculated_tim["start_position"] == "1"
        assert calculated_tim["has_preload"] == False
        assert calculated_tim["failed_score"] == 1

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
