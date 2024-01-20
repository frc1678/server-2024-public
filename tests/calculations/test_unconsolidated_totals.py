# Copyright (c) 2024 FRC Team 1678: Citrus Circuits

from unittest import mock

from calculations import base_calculations
from calculations import unconsolidated_totals
from server import Server
import pytest
from unittest.mock import patch


@pytest.mark.clouddb
class TestUnconsolidatedTotals:
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
                {"in_teleop": True, "time": 12, "action_type": "start_incap"},
                {"in_teleop": True, "time": 68, "action_type": "score_amp"},
                {"in_teleop": True, "time": 75, "action_type": "score_amp"},
                {"in_teleop": True, "time": 81, "action_type": "score_speaker_amped"},
                {"in_teleop": True, "time": 94, "action_type": "score_speaker_amped"},
                {"in_teleop": True, "time": 105, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 110, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 117, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 125, "action_type": "score_fail"},
                {"in_teleop": True, "time": 126, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 130, "action_type": "end_incap"},
                {"in_teleop": True, "time": 132, "action_type": "start_incap"},
                {"in_teleop": False, "time": 138, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 140, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 143, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 145, "action_type": "score_amp"},
                {"in_teleop": False, "time": 146, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 148, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 150, "action_type": "score_speaker"},
            ],
            "stage_level": "O",
            "start_position": "3",
            "has_preload": True,
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
                {"in_teleop": True, "time": 12, "action_type": "start_incap"},
                {"in_teleop": True, "time": 68, "action_type": "score_amp"},
                {"in_teleop": True, "time": 75, "action_type": "score_amp"},
                {"in_teleop": True, "time": 81, "action_type": "score_speaker_amped"},
                {"in_teleop": True, "time": 94, "action_type": "score_speaker_amped"},
                {"in_teleop": True, "time": 105, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 110, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 117, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 125, "action_type": "score_fail"},
                {"in_teleop": True, "time": 126, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 130, "action_type": "end_incap"},
                {"in_teleop": True, "time": 132, "action_type": "start_incap"},
                {"in_teleop": False, "time": 138, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 140, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 143, "action_type": "score_amp"},
                {"in_teleop": False, "time": 145, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 146, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 148, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 150, "action_type": "score_speaker"},
            ],
            "stage_level": "O",
            "start_position": "3",
            "has_preload": True,
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
                {"in_teleop": True, "time": 12, "action_type": "start_incap"},
                {"in_teleop": True, "time": 68, "action_type": "score_amp"},
                {"in_teleop": True, "time": 75, "action_type": "score_amp"},
                {"in_teleop": True, "time": 81, "action_type": "score_speaker_amped"},
                {"in_teleop": True, "time": 94, "action_type": "score_speaker_amped"},
                {"in_teleop": True, "time": 105, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 110, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 117, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 125, "action_type": "score_fail"},
                {"in_teleop": True, "time": 126, "action_type": "score_speaker"},
                {"in_teleop": True, "time": 130, "action_type": "end_incap"},
                {"in_teleop": True, "time": 132, "action_type": "start_incap"},
                {"in_teleop": False, "time": 138, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 140, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 143, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 145, "action_type": "score_amp"},
                {"in_teleop": False, "time": 146, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 148, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 150, "action_type": "score_speaker"},
            ],
            "stage_level": "O",
            "start_position": "1",
            "has_preload": False,
        },
    ]

    @mock.patch.object(
        base_calculations.BaseCalculations, "get_teams_list", return_value=["3", "254", "1"]
    )
    def setup_method(self, method, get_teams_list_dummy):
        with mock.patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = Server()
        self.test_calculator = unconsolidated_totals.UnconsolidatedTotals(self.test_server)

    def test_filter_timeline_actions(self):
        actions = self.test_calculator.filter_timeline_actions(self.unconsolidated_tims[0])
        assert actions == [
            {"in_teleop": True, "time": 2, "action_type": "end_incap"},
            {"in_teleop": True, "time": 12, "action_type": "start_incap"},
            {"in_teleop": True, "time": 68, "action_type": "score_amp"},
            {"in_teleop": True, "time": 75, "action_type": "score_amp"},
            {"in_teleop": True, "time": 81, "action_type": "score_speaker_amped"},
            {"in_teleop": True, "time": 94, "action_type": "score_speaker_amped"},
            {"in_teleop": True, "time": 105, "action_type": "score_speaker"},
            {"in_teleop": True, "time": 110, "action_type": "score_speaker"},
            {"in_teleop": True, "time": 117, "action_type": "score_speaker"},
            {"in_teleop": True, "time": 125, "action_type": "score_fail"},
            {"in_teleop": True, "time": 126, "action_type": "score_speaker"},
            {"in_teleop": True, "time": 130, "action_type": "end_incap"},
            {"in_teleop": True, "time": 132, "action_type": "start_incap"},
            {"in_teleop": False, "time": 138, "action_type": "score_speaker"},
            {"in_teleop": False, "time": 140, "action_type": "score_speaker"},
            {"in_teleop": False, "time": 143, "action_type": "score_speaker"},
            {"in_teleop": False, "time": 145, "action_type": "score_amp"},
            {"in_teleop": False, "time": 146, "action_type": "score_speaker"},
            {"in_teleop": False, "time": 148, "action_type": "score_speaker"},
            {"in_teleop": False, "time": 150, "action_type": "score_speaker"},
        ]

    def test_count_timeline_actions(self):
        action_num = self.test_calculator.count_timeline_actions(self.unconsolidated_tims[0])
        assert action_num == 20

    def test_calculate_unconsolidated_tims(self):
        self.test_server.db.insert_documents("unconsolidated_obj_tim", self.unconsolidated_tims)
        with patch("data_transfer.tba_communicator.tba_request", return_value=self.tba_test_data):
            self.test_calculator.run()
        result = self.test_server.db.find("unconsolidated_totals")
        assert len(result) == 3
        calculated_tim = result[0]
        del calculated_tim["_id"]
        assert calculated_tim == {
            "team_number": "254",
            "scout_name": "EDWIN",
            "match_number": 42,
            "alliance_color_is_red": True,
            "auto_amp": 1,
            "auto_speaker": 6,
            "auto_total_pieces": 7,
            "auto_total_intakes": 0,
            "dropped_pieces": 0,
            "tele_speaker": 3,
            "tele_speaker_amped": 2,
            "tele_amp": 2,
            "tele_total_pieces": 7,
            "tele_total_intakes": 0,
            "total_intakes": 0,
            "total_pieces": 14,
            "stage_level": "O",
            "trap": 0,
            "failed_score": 1,
            "start_position": "3",
            "has_preload": True,
            "tele_intakes_amp": 0,
            "tele_intakes_poach": 0,
            "tele_intakes_center": 0,
            "tele_intakes_far": 0,
            "auto_intake_center_1": 0,
            "auto_intake_center_2": 0,
            "auto_intake_center_3": 0,
            "auto_intake_center_4": 0,
            "auto_intake_center_5": 0,
            "auto_intake_spike_1": 0,
            "auto_intake_spike_2": 0,
            "auto_intake_spike_3": 0,
            "tele_shoot_other": 0,
        }

    @mock.patch.object(
        unconsolidated_totals.UnconsolidatedTotals,
        "entries_since_last",
        return_value=[{"o": {"team_number": "1", "match_number": 2}}],
    )
    def test_in_list_check1(self, entries_since_last_dummy, caplog):
        with patch("data_transfer.tba_communicator.tba_request", return_value=self.tba_test_data):
            self.test_calculator.run()
        assert len([rec.message for rec in caplog.records if rec.levelname == "WARNING"]) > 0

    @mock.patch.object(
        unconsolidated_totals.UnconsolidatedTotals,
        "entries_since_last",
        return_value=[{"o": {"team_number": "3", "match_number": 2}}],
    )
    @mock.patch.object(
        unconsolidated_totals.UnconsolidatedTotals, "update_calcs", return_value=[{}]
    )
    def test_in_list_check2(self, entries_since_last_dummy, update_calcs_dummy, caplog):
        with patch("data_transfer.tba_communicator.tba_request", return_value=self.tba_test_data):
            self.test_calculator.run()
        assert len([rec.message for rec in caplog.records if rec.levelname == "WARNING"]) == 0
