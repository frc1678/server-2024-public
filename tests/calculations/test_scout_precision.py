from unittest.mock import patch

from calculations import scout_precision
import server


class TestScoutPrecisionCalc:
    def setup_method(self):
        self.tba_test_data = [
            {
                "match_number": 1,
                "actual_time": 1100291640,
                "comp_level": "qm",
                "score_breakdown": {
                    "blue": {
                        "foulPoints": 8,
                        "autoTaxiPoints": 15,
                        "totalPoints": 87,
                        "endgamePoints": 6,
                    },
                    "red": {
                        "foulPoints": 10,
                        "autoTaxiPoints": 0,
                        "totalPoints": 159,
                        "endgamePoints": 15,
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
                        "autoTaxiPoints": 0,
                        "totalPoints": 149,
                        "endgamePoints": 25,
                    },
                    "red": {
                        "foulPoints": 10,
                        "autoTaxiPoints": 0,
                        "totalPoints": 98,
                        "endgamePoints": 4,
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
                "auto_cube_high": 0,
                "auto_cube_mid": 0,
                "auto_cube_low": 1,
                "tele_cube_high": 2,
                "tele_cube_mid": 0,
                "tele_cube_low": 2,
                "auto_cone_high": 0,
                "auto_cone_mid": 2,
                "auto_cone_low": 0,
                "tele_cone_high": 4,
                "tele_cone_mid": 0,
                "tele_cone_low": 2,
            },
            {
                "scout_name": "NATHAN MILLS",
                "team_number": "1678",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_cube_high": 0,
                "auto_cube_mid": 0,
                "auto_cube_low": 3,
                "tele_cube_high": 2,
                "tele_cube_mid": 0,
                "tele_cube_low": 2,
                "auto_cone_high": 0,
                "auto_cone_mid": 2,
                "auto_cone_low": 0,
                "tele_cone_high": 2,
                "tele_cone_mid": 2,
                "tele_cone_low": 0,
            },
            {
                "scout_name": "KATHY LI",
                "team_number": "4414",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_cube_high": 2,
                "auto_cube_mid": 1,
                "auto_cube_low": 0,
                "tele_cube_high": 3,
                "tele_cube_mid": 0,
                "tele_cube_low": 2,
                "auto_cone_high": 1,
                "auto_cone_mid": 0,
                "auto_cone_low": 0,
                "tele_cone_high": 0,
                "tele_cone_mid": 0,
                "tele_cone_low": 2,
            },
            {
                "scout_name": "KATE UNGER",
                "team_number": "589",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_cube_high": 1,
                "auto_cube_mid": 1,
                "auto_cube_low": 0,
                "tele_cube_high": 2,
                "tele_cube_mid": 0,
                "tele_cube_low": 2,
                "auto_cone_high": 1,
                "auto_cone_mid": 0,
                "auto_cone_low": 0,
                "tele_cone_high": 1,
                "tele_cone_mid": 2,
                "tele_cone_low": 0,
            },
            {
                "scout_name": "NITHMI JAYASUNDARA",
                "team_number": "589",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_cube_high": 1,
                "auto_cube_mid": 0,
                "auto_cube_low": 0,
                "tele_cube_high": 2,
                "tele_cube_mid": 0,
                "tele_cube_low": 1,
                "auto_cone_high": 1,
                "auto_cone_mid": 0,
                "auto_cone_low": 0,
                "tele_cone_high": 2,
                "tele_cone_mid": 2,
                "tele_cone_low": 0,
            },
            {
                "scout_name": "RAY FABIONAR",
                "team_number": "589",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_cube_high": 1,
                "auto_cube_mid": 1,
                "auto_cube_low": 0,
                "tele_cube_high": 2,
                "tele_cube_mid": 0,
                "tele_cube_low": 1,
                "auto_cone_high": 1,
                "auto_cone_mid": 0,
                "auto_cone_low": 0,
                "tele_cone_high": 1,
                "tele_cone_mid": 0,
                "tele_cone_low": 0,
            },
            # Match 2
            {
                "scout_name": "NATHAN MILLS",
                "team_number": "1678",
                "match_number": 2,
                "alliance_color_is_red": False,
                "auto_cube_high": 0,
                "auto_cube_mid": 0,
                "auto_cube_low": 0,
                "tele_cube_high": 3,
                "tele_cube_mid": 0,
                "tele_cube_low": 1,
                "auto_cone_high": 1,
                "auto_cone_mid": 2,
                "auto_cone_low": 0,
                "tele_cone_high": 1,
                "tele_cone_mid": 0,
                "tele_cone_low": 2,
            },
            {
                "scout_name": "KATHY LI",
                "team_number": "4414",
                "match_number": 2,
                "alliance_color_is_red": False,
                "auto_cube_high": 2,
                "auto_cube_mid": 2,
                "auto_cube_low": 0,
                "tele_cube_high": 2,
                "tele_cube_mid": 0,
                "tele_cube_low": 2,
                "auto_cone_high": 1,
                "auto_cone_mid": 0,
                "auto_cone_low": 0,
                "tele_cone_high": 0,
                "tele_cone_mid": 3,
                "tele_cone_low": 0,
            },
            {
                "scout_name": "KATE UNGER",
                "team_number": "589",
                "match_number": 2,
                "alliance_color_is_red": False,
                "auto_cube_high": 0,
                "auto_cube_mid": 1,
                "auto_cube_low": 0,
                "tele_cube_high": 2,
                "tele_cube_mid": 0,
                "tele_cube_low": 1,
                "auto_cone_high": 0,
                "auto_cone_mid": 1,
                "auto_cone_low": 0,
                "tele_cone_high": 3,
                "tele_cone_mid": 0,
                "tele_cone_low": 4,
            },
        ]

        with patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = server.Server()
        self.test_calc = scout_precision.ScoutPrecisionCalc(self.test_server)

    def test___init__(self):
        assert self.test_calc.watched_collections == ["unconsolidated_totals"]
        assert self.test_calc.server == self.test_server

    def test_find_updated_scouts(self):
        self.test_server.db.delete_data("unconsolidated_totals")
        self.test_calc.update_timestamp()
        self.test_server.db.insert_documents(
            "unconsolidated_totals",
            [{"scout_name": "REED WANG", "other": 9}, {"scout_name": "NATHAN MILLS"}],
        )
        assert sorted(self.test_calc.find_updated_scouts()) == sorted(["REED WANG", "NATHAN MILLS"])
        self.test_calc.update_timestamp()
        self.test_server.db.update_document(
            "unconsolidated_totals", {"other": 1}, {"scout_name": "NATHAN MILLS"}
        )
        assert self.test_calc.find_updated_scouts() == ["NATHAN MILLS"]

    def test_calc_scout_precision(self):
        assert self.test_calc.calc_scout_precision([{"scout_name": "REED WANG"}]) == {}
        test_data = [
            {
                "scout_name": "KATHY LI",
                "sim_precision": 0.5,
                "auto_speaker_precision": 0.5,
                "auto_amp_precision": 3,
                "tele_amplified_precision": 2,
                "tele_speaker_precision": 1,
                "tele_amp_precision": 1,
                "match_number": 1,
            },
            {
                "scout_name": "KATHY LI",
                "sim_precision": 0,
                "auto_speaker_precision": -1,
                "auto_amp_precision": 1,
                "tele_amplified_precision": 2,
                "tele_speaker_precision": 1,
                "tele_amp_precision": 1,
                "match_number": 2,
            },
            {
                "scout_name": "KATHY LI",
                "sim_precision": -1,
                "auto_speaker_precision": 0.5,
                "auto_amp_precision": 0.5,
                "tele_amplified_precision": 2,
                "tele_speaker_precision": 1,
                "tele_amp_precision": 1,
                "match_number": 3,
            },
            {
                "scout_name": "KATHY LI",
                "sim_precision": 0.7243,
                "auto_speaker_precision": 0.5,
                "auto_amp_precision": 3,
                "tele_amplified_precision": 2,
                "tele_speaker_precision": 1,
                "tele_amp_precision": 1,
                "match_number": 4,
            },
            {
                "scout_name": "KATHY LI",
                "sim_precision": 5,
                "auto_speaker_precision": 0.5,
                "auto_amp_precision": 3,
                "tele_amplified_precision": 2,
                "tele_speaker_precision": 1,
                "tele_amp_precision": 1,
                "match_number": 5,
            },
        ]
        assert self.test_calc.calc_scout_precision(test_data) == {
            "auto_speaker_precision": 0.2,
            "auto_amp_precision": 2.1,
            "tele_amplified_precision": 2,
            "scout_precision": 1.0448600000000001,
            "tele_speaker_precision": 1,
            "tele_amp_precision": 1,
        }

    def test_calc_ranks(self):
        test_data = [
            {
                "scout_name": "REED WANG",
                "scout_precision": 0.39,
            },
            {
                "scout_name": "KATHY LI",
                "scout_precision": 3.61111111111111,
            },
            {
                "scout_name": "NATHAN MILLS",
                "scout_precision": 4.111111111111111,
            },
            {
                "scout_name": "ALISON LIN",
                "scout_precision": 8.222222222222221,
            },
            {
                "scout_name": "CYRUS BROWN",
            },
        ]
        expected_output = [
            {
                "scout_name": "REED WANG",
                "scout_precision": 0.39,
                "scout_precision_rank": 1,
            },
            {
                "scout_name": "KATHY LI",
                "scout_precision": 3.61111111111111,
                "scout_precision_rank": 2,
            },
            {
                "scout_name": "NATHAN MILLS",
                "scout_precision": 4.111111111111111,
                "scout_precision_rank": 3,
            },
            {
                "scout_name": "ALISON LIN",
                "scout_precision": 8.222222222222221,
                "scout_precision_rank": 4,
            },
            {
                "scout_name": "CYRUS BROWN",
                "scout_precision": None,
                "scout_precision_rank": 5,
            },
        ]
        assert self.test_calc.calc_ranks(test_data) == expected_output

    def test_update_scout_precision_calcs(self):
        with patch(
            "calculations.scout_precision.ScoutPrecisionCalc.calc_scout_precision",
            return_value={
                "scout_precision": 0.39,
                "auto_speaker_precision": 0.1,
                "auto_amp_precision": 0.49,
                "tele_amplified_precision": 2.1,
                "tele_speaker_precision": 2.9,
                "tele_amp_precision": 1.5,
            },
        ):
            assert self.test_calc.update_scout_precision_calcs(["REED WANG"]) == [
                {
                    "scout_name": "REED WANG",
                    "scout_precision": 0.39,
                    "scout_precision_rank": 1,
                    "auto_speaker_precision": 0.1,
                    "auto_amp_precision": 0.49,
                    "tele_amplified_precision": 2.1,
                    "tele_speaker_precision": 2.9,
                    "tele_amp_precision": 1.5,
                }
            ]

    def test_run(self):

        scout_precision_data = [
            {
                "scout_name": "ALISON LIN",
                "scout_precision": 8.222222222222221,
                "auto_speaker_precision": 0.1,
                "auto_amp_precision": 0.49,
                "tele_amplified_precision": 2.1,
                "tele_speaker_precision": 2.9,
                "tele_amp_precision": 1.5,
            },
            {
                "scout_name": "NATHAN MILLS",
                "scout_precision": 4.111111111111111,
                "auto_speaker_precision": 0.1,
                "auto_amp_precision": 0.49,
                "tele_amplified_precision": 2.1,
                "tele_speaker_precision": 2.9,
                "tele_amp_precision": 1.5,
            },
            {
                "scout_name": "KATHY LI",
                "scout_precision": 3.61111111111111,
                "auto_speaker_precision": 0.1,
                "auto_amp_precision": 0.49,
                "tele_amplified_precision": 2.1,
                "tele_speaker_precision": 2.9,
                "tele_amp_precision": 1.5,
            },
            {
                "scout_name": "KATE UNGER",
                "scout_precision": 3.7777777777777777,
                "auto_speaker_precision": 0.1,
                "auto_amp_precision": 0.49,
                "tele_amplified_precision": 2.1,
                "tele_speaker_precision": 2.9,
                "tele_amp_precision": 1.5,
            },
            {
                "scout_name": "NITHMI JAYASUNDARA",
                "scout_precision": 7.555555555555555,
                "auto_speaker_precision": 0.1,
                "auto_amp_precision": 0.49,
                "tele_amplified_precision": 2.1,
                "tele_speaker_precision": 2.9,
                "tele_amp_precision": 1.5,
            },
            {
                "scout_name": "RAY FABIONAR",
                "scout_precision": 10.555555555555555,
                "auto_speaker_precision": 0.1,
                "auto_amp_precision": 0.49,
                "tele_amplified_precision": 2.1,
                "tele_speaker_precision": 2.9,
                "tele_amp_precision": 1.5,
            },
        ]

        expected_scout_precision = [
            {
                "scout_name": "ALISON LIN",
                "scout_precision": 8.222222222222221,
                "scout_precision_rank": 5,
                "auto_speaker_precision": 0.1,
                "auto_amp_precision": 0.49,
                "tele_amplified_precision": 2.1,
                "tele_speaker_precision": 2.9,
                "tele_amp_precision": 1.5,
            },
            {
                "scout_name": "NATHAN MILLS",
                "scout_precision": 4.111111111111111,
                "scout_precision_rank": 3,
                "auto_speaker_precision": 0.1,
                "auto_amp_precision": 0.49,
                "tele_amplified_precision": 2.1,
                "tele_speaker_precision": 2.9,
                "tele_amp_precision": 1.5,
            },
            {
                "scout_name": "KATHY LI",
                "scout_precision": 3.61111111111111,
                "scout_precision_rank": 1,
                "auto_speaker_precision": 0.1,
                "auto_amp_precision": 0.49,
                "tele_amplified_precision": 2.1,
                "tele_speaker_precision": 2.9,
                "tele_amp_precision": 1.5,
            },
            {
                "scout_name": "KATE UNGER",
                "scout_precision": 3.7777777777777777,
                "scout_precision_rank": 2,
                "auto_speaker_precision": 0.1,
                "auto_amp_precision": 0.49,
                "tele_amplified_precision": 2.1,
                "tele_speaker_precision": 2.9,
                "tele_amp_precision": 1.5,
            },
            {
                "scout_name": "NITHMI JAYASUNDARA",
                "scout_precision": 7.555555555555555,
                "scout_precision_rank": 4,
                "auto_speaker_precision": 0.1,
                "auto_amp_precision": 0.49,
                "tele_amplified_precision": 2.1,
                "tele_speaker_precision": 2.9,
                "tele_amp_precision": 1.5,
            },
            {
                "scout_name": "RAY FABIONAR",
                "scout_precision": 10.555555555555555,
                "scout_precision_rank": 6,
                "auto_speaker_precision": 0.1,
                "auto_amp_precision": 0.49,
                "tele_amplified_precision": 2.1,
                "tele_speaker_precision": 2.9,
                "tele_amp_precision": 1.5,
            },
        ]
        self.test_server.db.delete_data("unconsolidated_totals")
        self.test_calc.update_timestamp()
        self.test_server.db.insert_documents("unconsolidated_totals", self.scout_tim_test_data)
        with patch(
            "calculations.scout_precision.ScoutPrecisionCalc.calc_scout_precision",
            side_effect=scout_precision_data,
        ):
            with patch(
                "data_transfer.tba_communicator.tba_request",
                return_value=self.tba_test_data,
            ):
                self.test_calc.run()
        scout_precision_result = self.test_server.db.find("scout_precision")
        for document in scout_precision_result:
            document.pop("_id")
            assert document in expected_scout_precision
