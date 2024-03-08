from unittest.mock import patch
import pytest
from utils import dict_near_in, dict_near, read_schema

from calculations import sim_precision
import server


class TestSimPrecisionCalc:
    def setup_method(self):
        self.tba_test_data = [
            {
                "match_number": 1,
                "actual_time": 1100291640,
                "comp_level": "qm",
                "score_breakdown": {
                    "blue": {
                        "foulPoints": 0,
                        "teleopTotalNotePoints": 24,
                        "autoTotalNotePoints": 29,
                        "autoMobilityPoints": 0,
                        "autoGamePiecePoints": 0,
                        "teleopGamePiecePoints": 0,
                        "autoSpeakerNotePoints": 25,
                        "autoAmpNotePoints": 4,
                        "teleopSpeakerNotePoints": 2,
                        "teleopSpeakerNoteAmplifiedPoints": 15,
                        "teleopAmpNotePoints": 7,
                    },
                    "red": {
                        "foulPoints": 0,
                        "teleopTotalNotePoints": 53,
                        "autoTotalNotePoints": 34,
                        "autoMobilityPoints": 0,
                        "autoGamePiecePoints": 0,
                        "teleopGamePiecePoints": 0,
                        "autoSpeakerNotePoints": 10,
                        "autoAmpNotePoints": 24,
                        "teleopSpeakerNotePoints": 6,
                        "teleopSpeakerNoteAmplifiedPoints": 40,
                        "teleopAmpNotePoints": 7,
                    },
                },
            },
            {
                "match_number": 2,
                "actual_time": 1087511040,
                "comp_level": "qm",
                "score_breakdown": {
                    "blue": {
                        "foulPoints": 0,
                        "teleopTotalNotePoints": 24,
                        "autoTotalNotePoints": 20,
                        "autoMobilityPoints": 0,
                        "autoGamePiecePoints": 0,
                        "teleopGamePiecePoints": 0,
                        "autoSpeakerNotePoints": 20,
                        "autoAmpNotePoints": 0,
                        "teleopSpeakerNotePoints": 2,
                        "teleopSpeakerNoteAmplifiedPoints": 20,
                        "teleopAmpNotePoints": 2,
                    },
                    "red": {
                        "foulPoints": 0,
                        "teleopTotalNotePoints": 47,
                        "autoTotalNotePoints": 49,
                        "autoMobilityPoints": 0,
                        "autoGamePiecePoints": 0,
                        "teleopGamePiecePoints": 0,
                        "autoSpeakerNotePoints": 45,
                        "autoAmpNotePoints": 4,
                        "teleopSpeakerNotePoints": 6,
                        "teleopSpeakerNoteAmplifiedPoints": 35,
                        "teleopAmpNotePoints": 6,
                    },
                },
            },
            {
                "match_number": 3,
                "actual_time": None,
                "comp_level": "qm",
                "score_breakdown": None,
            },
        ]
        self.scout_tim_test_data = [
            # Match 1
            {
                "scout_name": "ALISON LIN",
                "team_number": "1678",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_speaker": 2,
                "auto_amp": 2,
                "tele_speaker": 1,
                "tele_amplified": 3,
                "tele_amp": 0,
            },
            {
                "scout_name": "NATHAN MILLS",
                "team_number": "1678",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_speaker": 0,
                "auto_amp": 2,
                "tele_speaker": 1,
                "tele_amplified": 0,
                "tele_amp": 0,
            },
            {
                "scout_name": "KATHY LI",
                "team_number": "4414",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_speaker": 0,
                "auto_amp": 2,
                "tele_speaker": 1,
                "tele_amplified": 2,
                "tele_amp": 3,
            },
            {
                "scout_name": "KATE UNGER",
                "team_number": "589",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_speaker": 0,
                "auto_amp": 2,
                "tele_speaker": 1,
                "tele_amplified": 3,
                "tele_amp": 2,
            },
            {
                "scout_name": "NITHMI JAYASUNDARA",
                "team_number": "589",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_speaker": 0,
                "auto_amp": 2,
                "tele_speaker": 1,
                "tele_amplified": 3,
                "tele_amp": 2,
            },
            {
                "scout_name": "RAY FABIONAR",
                "team_number": "589",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_speaker": 0,
                "auto_amp": 2,
                "tele_speaker": 1,
                "tele_amplified": 3,
                "tele_amp": 2,
            },
            # Match 2
            {
                "scout_name": "NATHAN MILLS",
                "team_number": "1678",
                "match_number": 2,
                "alliance_color_is_red": False,
                "auto_speaker": 2,
                "auto_amp": 2,
                "tele_speaker": 2,
                "tele_amplified": 1,
                "tele_amp": 2,
            },
            {
                "scout_name": "KATHY LI",
                "team_number": "4414",
                "match_number": 2,
                "alliance_color_is_red": False,
                "auto_speaker": 3,
                "auto_amp": 0,
                "tele_speaker": 1,
                "tele_amplified": 3,
                "tele_amp": 2,
            },
            {
                "scout_name": "KATE UNGER",
                "team_number": "589",
                "match_number": 2,
                "alliance_color_is_red": False,
                "auto_speaker": 3,
                "auto_amp": 0,
                "tele_speaker": 1,
                "tele_amplified": 3,
                "tele_amp": 2,
            },
        ]

        with patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = server.Server()
        self.test_calc = sim_precision.SimPrecisionCalc(self.test_server)

    def test___init__(self):
        assert self.test_calc.watched_collections == ["unconsolidated_totals"]
        assert self.test_calc.server == self.test_server

    def test_get_scout_tim_score(self, caplog):
        required = self.test_calc.sim_schema["calculations"]["sim_precision"]["requires"]
        self.test_server.db.delete_data("unconsolidated_totals")
        self.test_calc.get_scout_tim_score("RAY FABIONAR", 2, required)
        assert ["No data from Scout RAY FABIONAR in Match 2"] == [
            rec.message for rec in caplog.records if rec.levelname == "WARNING"
        ]
        self.test_server.db.insert_documents("unconsolidated_totals", self.scout_tim_test_data)
        assert self.test_calc.get_scout_tim_score("ALISON LIN", 1, required) == 31
        assert self.test_calc.get_scout_tim_score("NITHMI JAYASUNDARA", 1, required) == 23
        assert self.test_calc.get_scout_tim_score("NATHAN MILLS", 2, required) == 25

    def test_get_aim_scout_scores(self):
        self.test_server.db.delete_data("unconsolidated_totals")
        self.test_server.db.insert_documents("unconsolidated_totals", self.scout_tim_test_data)
        required = self.test_calc.sim_schema["calculations"]["sim_precision"]["requires"]
        assert self.test_calc.get_aim_scout_scores(1, True, required) == {
            "1678": {"ALISON LIN": 31, "NATHAN MILLS": 6},
            "4414": {"KATHY LI": 19},
            "589": {"KATE UNGER": 23, "NITHMI JAYASUNDARA": 23, "RAY FABIONAR": 23},
        }
        assert self.test_calc.get_aim_scout_scores(2, False, required) == {
            "1678": {"NATHAN MILLS": 25},
            "4414": {"KATHY LI": 34},
            "589": {"KATE UNGER": 34},
        }

    def test_get_aim_scout_avg_errors(self, caplog):
        assert (
            self.test_calc.get_aim_scout_avg_errors(
                {
                    "1678": {"KATHY LI": 31, "RAY FABIONAR": 31},
                    "589": {"NITHMI JAYASUNDARA": 23},
                },
                100,
                1,
                True,
            )
            == {}
        )
        assert ["Missing red alliance scout data for Match 1"] == [
            rec.message for rec in caplog.records if rec.levelname == "WARNING"
        ]
        aim_scout_scores = {
            "1678": {"ALISON LIN": 31, "NATHAN MILLS": 6},
            "4414": {"KATHY LI": 19},
            "589": {"KATE UNGER": 23, "NITHMI JAYASUNDARA": 23, "RAY FABIONAR": 23},
        }
        assert self.test_calc.get_aim_scout_avg_errors(aim_scout_scores, 73, 1, True) == {
            "ALISON LIN": 0.0,
            "NATHAN MILLS": 25.0,
            "KATHY LI": 12.5,
            "KATE UNGER": 12.5,
            "NITHMI JAYASUNDARA": 12.5,
            "RAY FABIONAR": 12.5,
        }

    def test_calc_sim_precision(self):
        self.test_server.db.insert_documents("unconsolidated_totals", self.scout_tim_test_data)
        with patch(
            "calculations.sim_precision.SimPrecisionCalc.get_aim_scout_avg_errors",
            return_value={},
        ):
            assert (
                self.test_calc.calc_sim_precision(self.scout_tim_test_data[1], self.tba_test_data)
                == {}
            )
        sim_precision_result = self.test_calc.calc_sim_precision(
            self.scout_tim_test_data[3], self.tba_test_data
        )

        fields_to_keep = {"sim_precision"}
        # Remove fields we are not testing
        for field in list(sim_precision_result.keys()):
            if field not in fields_to_keep:
                sim_precision_result.pop(field)

        assert dict_near(sim_precision_result, {"sim_precision": -8.833333333333333})

    def test_update_sim_precision_calcs(self):
        self.test_server.db.insert_documents("unconsolidated_totals", self.scout_tim_test_data)
        expected_updates = [
            {
                "scout_name": "ALISON LIN",
                "match_number": 1,
                "team_number": "1678",
                "sim_precision": 5,
                "alliance_color_is_red": True,
            }
        ]
        with patch(
            "data_transfer.tba_communicator.tba_request",
            return_value=self.tba_test_data,
        ), patch(
            "calculations.sim_precision.SimPrecisionCalc.calc_sim_precision",
            return_value={"sim_precision": 5},
        ):
            updates = self.test_calc.update_sim_precision_calcs(
                [
                    {
                        "scout_name": "ALISON LIN",
                        "match_number": 1,
                        "alliance_color_is_red": True,
                    }
                ]
            )
            # Remove timestamp field since it's difficult to test, figure out later
            updates[0].pop("timestamp")
            assert updates == expected_updates

    def test_get_tba_value(self):
        required = {
            "something_that_should_be_ignored": {
                "weight": 1000,
                "calculation": [
                    ["autoCommunity", "T", "+2*count=Cube"],
                    ["foulPoints", "-2*value"],
                    ["+1*constant"],
                ],
            },
            "another_thing_that_doesn't_matter": {
                "weight": -0,
                "calculation": ["teleopCommunity", "B", "+1*count=Cone"],
            },
        }

    def test_run(self):
        expected_sim_precision = [
            {
                "scout_name": "ALISON LIN",
                "match_number": 1,
                "team_number": "1678",
                "sim_precision": 3.666666666666668,
                "alliance_color_is_red": True,
            },
            {
                "scout_name": "NATHAN MILLS",
                "match_number": 1,
                "team_number": "1678",
                "sim_precision": -21.333333333333336,
                "alliance_color_is_red": True,
            },
            {
                "scout_name": "KATHY LI",
                "match_number": 1,
                "team_number": "4414",
                "sim_precision": -8.833333333333333,
                "alliance_color_is_red": True,
            },
            {
                "scout_name": "KATE UNGER",
                "match_number": 1,
                "team_number": "589",
                "sim_precision": -8.833333333333333,
                "alliance_color_is_red": True,
            },
        ]
        self.test_server.db.delete_data("unconsolidated_totals")
        self.test_calc.update_timestamp()
        self.test_server.db.insert_documents("unconsolidated_totals", self.scout_tim_test_data)
        with patch(
            "data_transfer.tba_communicator.tba_request",
            return_value=self.tba_test_data,
        ):
            self.test_calc.run()
        sim_precision_result = self.test_server.db.find("sim_precision")
        fields_to_keep = {
            "sim_precision",
            "scout_name",
            "match_number",
            "team_number",
            "alliance_color_is_red",
        }
        schema = read_schema("schema/calc_sim_precision_schema.yml")
        calculations = schema["calculations"]
        for document in sim_precision_result:
            for calculation in calculations:
                assert calculation in document
            assert "_id" in document
            assert "timestamp" in document
            # Remove fields we are not testing
            for field in list(document.keys()):
                if field not in fields_to_keep:
                    document.pop(field)

        for document in expected_sim_precision:
            assert dict_near_in(document, sim_precision_result)
