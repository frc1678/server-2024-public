from calculations import predicted_aim
from unittest.mock import patch
import server
import pytest


class TestPredictedAimCalc:
    def setup_method(self, method):
        with patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = server.Server()
        self.test_calc = predicted_aim.PredictedAimCalc(self.test_server)
        self.aims_list = [
            {
                "match_number": 1,
                "alliance_color": "R",
                "team_list": ["1678", "254", "4414"],
            },
            {
                "match_number": 1,
                "alliance_color": "B",
                "team_list": ["125", "1323", "5940"],
            },
            {
                "match_number": 2,
                "alliance_color": "R",
                "team_list": ["1678", "1323", "125"],
            },
            {
                "match_number": 2,
                "alliance_color": "B",
                "team_list": ["254", "4414", "5940"],
            },
            {
                "match_number": 3,
                "alliance_color": "R",
                "team_list": ["1678", "5940", "4414"],
            },
            {
                "match_number": 3,
                "alliance_color": "B",
                "team_list": ["1323", "254", "125"],
            },
        ]
        self.filtered_aims_list = [
            {
                "match_number": 1,
                "alliance_color": "R",
                "team_list": ["1678", "254", "4414"],
            },
            {
                "match_number": 1,
                "alliance_color": "B",
                "team_list": ["125", "1323", "5940"],
            },
            {
                "match_number": 2,
                "alliance_color": "R",
                "team_list": ["1678", "1323", "125"],
            },
            {
                "match_number": 2,
                "alliance_color": "B",
                "team_list": ["254", "4414", "5940"],
            },
            {
                "match_number": 3,
                "alliance_color": "R",
                "team_list": ["1678", "5940", "4414"],
            },
            {
                "match_number": 3,
                "alliance_color": "B",
                "team_list": ["1323", "254", "125"],
            },
        ]
        self.expected_updates = [
            {
                "match_number": 1,
                "alliance_color_is_red": True,
                "predicted_score": 259.15,
                "predicted_rp1": 3.611,
                "predicted_rp2": 0.56,
                "win_chance": 0.773,
                "actual_score": 320,
                "actual_rp1": 0.0,
                "actual_rp2": 1.0,
                "won_match": True,
                "has_actual_data": True,
                "team_numbers": ["1678", "254", "4414"],
            },
            {
                "match_number": 1,
                "alliance_color_is_red": False,
                "predicted_score": 239.817,
                "predicted_rp1": 3.389,
                "predicted_rp2": 0.9,
                "win_chance": 0.22699999999999998,
                "actual_score": 278,
                "actual_rp1": 1.0,
                "actual_rp2": 1.0,
                "won_match": False,
                "has_actual_data": True,
                "team_numbers": ["125", "1323", "5940"],
            },
            {
                "match_number": 2,
                "alliance_color_is_red": True,
                "predicted_score": 267.972,
                "predicted_rp1": 3.778,
                "predicted_rp2": 0.9,
                "win_chance": 0.736,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "has_actual_data": False,
                "team_numbers": ["1678", "1323", "125"],
            },
            {
                "match_number": 2,
                "alliance_color_is_red": False,
                "predicted_score": 226.883,
                "predicted_rp1": 3.222,
                "predicted_rp2": 0.8,
                "win_chance": 0.264,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "has_actual_data": False,
                "team_numbers": ["254", "4414", "5940"],
            },
            {
                "match_number": 3,
                "alliance_color_is_red": True,
                "predicted_score": 246.78300000000002,
                "predicted_rp1": 3.5,
                "predicted_rp2": 0.8,
                "win_chance": 0.5,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "has_actual_data": False,
                "team_numbers": ["1678", "5940", "4414"],
            },
            {
                "match_number": 3,
                "alliance_color_is_red": False,
                "predicted_score": 242.398,
                "predicted_rp1": 3.5,
                "predicted_rp2": 0.9,
                "win_chance": 0.5,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "has_actual_data": False,
                "team_numbers": ["1323", "254", "125"],
            },
        ]
        self.expected_playoffs_updates = [
            {
                "alliance_num": 1,
                "picks": ["1678", "254", "4414"],
                "predicted_auto_score": 35.8,
                "predicted_score": 263.8,
                "predicted_stage_score": 19,
                "predicted_tele_score": 209.0,
            },
            {
                "alliance_num": 9,
                "picks": ["1678", "254", "4414"],
                "predicted_auto_score": 35.8,
                "predicted_score": 263.8,
                "predicted_stage_score": 19,
                "predicted_tele_score": 209.0,
            },
            {
                "alliance_num": 17,
                "picks": ["1678", "254", "4414"],
                "predicted_auto_score": 35.8,
                "predicted_score": 263.8,
                "predicted_stage_score": 19,
                "predicted_tele_score": 209.0,
            },
        ]
        self.expected_results = [
            {
                "alliance_color_is_red": True,
                "match_number": 1,
                "actual_rp1": 0.0,
                "actual_rp2": 1.0,
                "actual_score": 320,
                "has_actual_data": True,
                "predicted_rp1": 3.611,
                "predicted_rp2": 0.56,
                "predicted_score": 259.15,
                "team_numbers": ["1678", "254", "4414"],
                "win_chance": 0.773,
                "won_match": True,
            },
            {
                "alliance_color_is_red": False,
                "match_number": 1,
                "actual_rp1": 1.0,
                "actual_rp2": 1.0,
                "actual_score": 278,
                "has_actual_data": True,
                "predicted_rp1": 3.389,
                "predicted_rp2": 0.9,
                "predicted_score": 239.817,
                "team_numbers": ["125", "1323", "5940"],
                "win_chance": 0.22699999999999998,
                "won_match": False,
            },
            {
                "alliance_color_is_red": True,
                "match_number": 2,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "actual_score": 0,
                "has_actual_data": False,
                "predicted_rp1": 3.778,
                "predicted_rp2": 0.9,
                "predicted_score": 267.972,
                "team_numbers": ["1678", "1323", "125"],
                "win_chance": 0.736,
                "won_match": False,
            },
            {
                "alliance_color_is_red": False,
                "match_number": 2,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "actual_score": 0,
                "has_actual_data": False,
                "predicted_rp1": 3.222,
                "predicted_rp2": 0.8,
                "predicted_score": 226.883,
                "team_numbers": ["254", "4414", "5940"],
                "win_chance": 0.264,
                "won_match": False,
            },
            {
                "alliance_color_is_red": True,
                "match_number": 3,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "actual_score": 0,
                "has_actual_data": False,
                "predicted_rp1": 3.5,
                "predicted_rp2": 0.8,
                "predicted_score": 246.78300000000002,
                "team_numbers": ["1678", "5940", "4414"],
                "win_chance": 0.5,
                "won_match": False,
            },
            {
                "alliance_color_is_red": False,
                "match_number": 3,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "actual_score": 0,
                "has_actual_data": False,
                "predicted_rp1": 3.5,
                "predicted_rp2": 0.9,
                "predicted_score": 242.398,
                "team_numbers": ["1323", "254", "125"],
                "win_chance": 0.5,
                "won_match": False,
            },
        ]
        self.expected_playoffs_alliances = [
            {"alliance_num": 1, "picks": ["1678", "254", "4414"]},
            {"alliance_num": 9, "picks": ["1678", "254", "4414"]},
            {"alliance_num": 17, "picks": ["1678", "254", "4414"]},
        ]
        self.full_predicted_values = predicted_aim.PredictedAimScores(
            park_successes=1.5,
            onstage_successes=0.5,
        )
        self.blank_predicted_values = predicted_aim.PredictedAimScores()
        self.obj_team = [
            {
                "team_number": "1678",
                "matches_played": 5,
                "auto_avg_amp": 1,
                "auto_sd_amp": 0,
                "auto_avg_speaker": 3,
                "auto_sd_speaker": 1,
                "tele_avg_amp": 4,
                "tele_sd_amp": 2,
                "tele_avg_speaker": 0,
                "tele_sd_speaker": 0,
                "tele_sd_amplified": 4,
                "tele_avg_amplified": 17,
                "stage_percent_success_all": 50,
                "parked_percent": 33,
                "climb_after_percent_success": 0,
                "trap_percent_success": 80,
                "endgame_avg_total_points": 5,
                "avg_expected_speaker_cycle_time": 6,
            },
            {
                "team_number": "254",
                "matches_played": 5,
                "auto_avg_amp": 1,
                "auto_sd_amp": 0,
                "auto_avg_speaker": 1,
                "auto_sd_speaker": 1,
                "tele_avg_amp": 2,
                "tele_sd_amp": 2,
                "tele_avg_speaker": 0,
                "tele_sd_speaker": 0,
                "tele_sd_amplified": 4,
                "tele_avg_amplified": 16,
                "stage_percent_success_all": 70,
                "parked_percent": 0,
                "climb_after_percent_success": 20,
                "trap_percent_success": 80,
                "endgame_avg_total_points": 6,
                "avg_expected_speaker_cycle_time": 8,
            },
            {
                "team_number": "4414",
                "matches_played": 5,
                "auto_avg_amp": 1,
                "auto_sd_amp": 0,
                "auto_avg_speaker": 1,
                "auto_sd_speaker": 1,
                "tele_avg_amp": 2,
                "tele_sd_amp": 2,
                "tele_avg_speaker": 0,
                "tele_sd_speaker": 0,
                "tele_sd_amplified": 4,
                "tele_avg_amplified": 16,
                "stage_percent_success_all": 70,
                "parked_percent": 0,
                "climb_after_percent_success": 20,
                "trap_percent_success": 20,
                "endgame_avg_total_points": 6,
                "avg_expected_speaker_cycle_time": 7,
            },
            {
                "team_number": "1323",
                "matches_played": 5,
                "auto_avg_amp": 1,
                "auto_sd_amp": 0,
                "auto_avg_speaker": 3,
                "auto_sd_speaker": 1,
                "tele_avg_amp": 4,
                "tele_sd_amp": 2,
                "tele_avg_speaker": 0,
                "tele_sd_speaker": 0,
                "tele_sd_amplified": 4,
                "tele_avg_amplified": 17,
                "stage_percent_success_all": 50,
                "parked_percent": 33,
                "climb_after_percent_success": 0,
                "trap_percent_success": 90,
                "endgame_avg_total_points": 5,
                "avg_expected_speaker_cycle_time": 9,
            },
            {
                "team_number": "125",
                "matches_played": 5,
                "auto_avg_amp": 1,
                "auto_sd_amp": 0,
                "auto_avg_speaker": 3,
                "auto_sd_speaker": 1,
                "tele_avg_amp": 4,
                "tele_sd_amp": 2,
                "tele_avg_speaker": 0,
                "tele_sd_speaker": 0,
                "tele_sd_amplified": 4,
                "tele_avg_amplified": 10,
                "stage_percent_success_all": 100,
                "parked_percent": 0,
                "climb_after_percent_success": 0,
                "trap_percent_success": 0,
                "endgame_avg_total_points": 5,
                "avg_expected_speaker_cycle_time": 11,
            },
            {
                "team_number": "5940",
                "matches_played": 5,
                "auto_avg_amp": 1,
                "auto_sd_amp": 0,
                "auto_avg_speaker": 3,
                "auto_sd_speaker": 1,
                "tele_avg_amp": 4,
                "tele_sd_amp": 2,
                "tele_avg_speaker": 0,
                "tele_sd_speaker": 0,
                "tele_sd_amplified": 4,
                "tele_avg_amplified": 10,
                "stage_percent_success_all": 100,
                "parked_percent": 0,
                "climb_after_percent_success": 0,
                "trap_percent_success": 0,
                "endgame_avg_total_points": 5,
                "avg_expected_speaker_cycle_time": 5,
            },
        ]
        self.tba_team = [
            {
                "team_number": "1678",
                "leave_successes": 5,
            },
            {
                "team_number": "254",
                "leave_successes": 4,
            },
            {
                "team_number": "4414",
                "leave_successes": 3,
            },
            {
                "team_number": "125",
                "leave_successes": 2,
            },
            {
                "team_number": "5940",
                "leave_successes": 1,
            },
            {
                "team_number": "1323",
                "leave_successes": 4,
            },
        ]
        self.tba_match_data = [
            {
                "match_number": 1,
                "comp_level": "qm",
                "score_breakdown": {
                    "blue": {
                        "melodyBonusAchieved": True,
                        "ensembleBonusAchieved": True,
                        "totalPoints": 278,
                    },
                    "red": {
                        "melodyBonusAchieved": False,
                        "ensembleBonusAchieved": True,
                        "totalPoints": 320,
                    },
                },
                "post_result_time": 182,
                "winning_alliance": "red",
            },
            {
                "match_number": 1,
                "comp_level": "qf",
                "score_breakdown": {
                    "blue": {
                        "melodyBonusAchieved": True,
                        "ensembleBonusAchieved": True,
                        "totalPoints": 300,
                    },
                    "red": {
                        "melodyBonusAchieved": True,
                        "ensembleBonusAchieved": True,
                        "totalPoints": 400,
                    },
                },
                "post_result_time": 182,
                "winning_alliance": "red",
            },
            {
                "match_number": 3,
                "comp_level": "qm",
                "score_breakdown": None,
                "post_result_time": None,
                "winning_alliance": "",
            },
        ]
        self.tba_playoffs_data = [
            {
                "name": "Alliance 1",
                "decines": [],
                "picks": ["frc1678", "frc254", "frc4414"],
                "status": {
                    "playoff_average": None,
                    "level": "f",
                    "record": {"losses": 2, "wins": 6, "ties": 1},
                    "status": "won",
                },
            }
        ]
        self.test_server.db.insert_documents("obj_team", self.obj_team)
        self.test_server.db.insert_documents("tba_team", self.tba_team)

    def test___init__(self):
        """Test if attributes are set correctly"""
        assert self.test_calc.watched_collections == ["obj_team", "tba_team"]
        assert self.test_calc.server == self.test_server

    def test_calc_alliance_score(self):
        """Test the total predicted_score is correct"""
        values = self.test_calc.calc_alliance_score(
            self.blank_predicted_values,
            self.obj_team,
            self.tba_team,
            ["1678", "254", "4414"],
        )
        total_score = 0
        for field in values.__dict__.keys():
            total_score += getattr(values, field) * self.test_calc.POINT_VALUES[field]
        assert total_score == 303.83
        # Make sure there are no errors with empty data
        try:
            self.test_calc.calc_alliance_score(
                self.blank_predicted_values,
                self.obj_team,
                self.tba_team,
                ["1000", "1000", "1000"],
            )
        except ZeroDivisionError as exc:
            assert False, f"calculate_predicted_alliance_score has a {exc}"

    def test_get_playoffs_alliances(self):
        # TODO: need more tests for this, might break
        with patch(
            "data_transfer.tba_communicator.tba_request", return_value=self.tba_playoffs_data
        ):
            assert self.test_calc.get_playoffs_alliances() == self.expected_playoffs_alliances

    def test_calc_ensemble_rp(self):
        assert self.test_calc.calc_ensemble_rp(self.obj_team, ["1678", "254", "4414"]) == 0.56

    def test_calc_melody_rp(self):
        sample_predicted_values = self.blank_predicted_values
        sample_predicted_values.auto_amp = 2
        sample_predicted_values.tele_speaker = 12
        assert self.test_calc.calc_melody_rp(sample_predicted_values) == 0.778

        sample_predicted_values.tele_speaker_amped = 6
        assert self.test_calc.calc_melody_rp(sample_predicted_values) == 1.111

    def test_get_actual_values(self):
        """Test getting actual values from TBA"""
        assert self.test_calc.get_actual_values(
            {
                "match_number": 1,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "7229"],
            },
            self.tba_match_data,
        ) == {
            "has_actual_data": True,
            "actual_score": 320,
            "actual_rp1": 0.0,
            "actual_rp2": 1.0,
            "won_match": True,
        }
        assert self.test_calc.get_actual_values(
            {
                "match_number": 1,
                "alliance_color": "B",
                "team_list": ["1678", "1533", "2468"],
            },
            self.tba_match_data,
        ) == {
            "has_actual_data": True,
            "actual_score": 278,
            "actual_rp1": 1.0,
            "actual_rp2": 1.0,
            "won_match": False,
        }
        assert self.test_calc.get_actual_values(
            {
                "match_number": 3,
                "alliance_color": "B",
                "team_list": ["1678", "1533", "7229"],
            },
            self.tba_match_data,
        ) == {
            "has_actual_data": False,
            "actual_score": 0,
            "actual_rp1": 0.0,
            "actual_rp2": 0.0,
            "won_match": False,
        }
        assert self.test_calc.get_actual_values(
            {
                "match_number": 3,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "2468"],
            },
            self.tba_match_data,
        ) == {
            "has_actual_data": False,
            "actual_score": 0,
            "actual_rp1": 0.0,
            "actual_rp2": 0.0,
            "won_match": False,
        }

    def test_filter_aims_list(self):
        assert (
            self.test_calc.filter_aims_list(self.obj_team, self.tba_team, self.aims_list)
            == self.filtered_aims_list
        )

    def test_update_predicted_aim(self):
        self.test_server.db.delete_data("predicted_aim")
        with patch(
            "data_transfer.tba_communicator.tba_request",
            return_value=self.tba_match_data,
        ):
            assert self.test_calc.update_predicted_aim(self.aims_list) == self.expected_updates

    def test_update_playoffs_alliances(self):
        """Test that we correctly calculate data for each of the playoff alliances"""
        self.test_server.db.delete_data("predicted_aim")
        with patch(
            "calculations.predicted_aim.PredictedAimCalc.get_playoffs_alliances",
            return_value=self.expected_playoffs_alliances,
        ):
            assert self.test_calc.update_playoffs_alliances() == self.expected_playoffs_updates

    def test_calc_win_chance(self):
        assert (
            self.test_calc.calc_win_chance(
                self.obj_team, {"R": ["1678", "254", "4414"], "B": ["125", "1323", "5940"]}, "R"
            )
            == 0.773
        )
        assert (
            self.test_calc.calc_win_chance(
                self.obj_team, {"R": ["1678", "125", "1323"], "B": ["254", "4414", "5940"]}, "B"
            )
            == 0.264
        )

    def test_run(self):
        self.test_server.db.delete_data("obj_team")
        self.test_server.db.delete_data("tba_team")
        self.test_server.db.delete_data("predicted_aim")
        self.test_server.db.insert_documents("obj_team", self.obj_team)
        self.test_server.db.insert_documents("tba_team", self.tba_team)

        with patch(
            "calculations.predicted_aim.PredictedAimCalc.get_aim_list",
            return_value=self.aims_list,
        ), patch(
            "data_transfer.tba_communicator.tba_request",
            side_effect=[self.tba_match_data, self.tba_playoffs_data],
        ):
            self.test_calc.run()

        result = self.test_server.db.find("predicted_aim")
        assert len(result) == 6

        for document in result:
            del document["_id"]
            assert document in self.expected_results

        result2 = self.test_server.db.find("predicted_alliances")
        assert len(result2) == 3

        for document in result2:
            del document["_id"]
            assert document in self.expected_playoffs_updates
