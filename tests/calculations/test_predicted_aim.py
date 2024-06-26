from calculations import predicted_aim
from unittest.mock import patch
import server
import pytest
import pandas as pd
import utils


class TestPredictedAimCalc:
    def setup_method(self):
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
                "_auto_speaker": 5.0,
                "_auto_amp": 3.0,
                "_tele_speaker": 0.0,
                "_tele_speaker_all": 49.0,
                "_tele_amplified": 49.0,
                "_tele_amp": 8.0,
                "_num_park": 0.33,
                "_num_onstage": 2.4,
                "_num_trap": 2.0,
                "predicted_score": 178.06153846153848,
                "predicted_rp1": 1.0,
                "predicted_rp2": 1.0,
                "win_chance": 0.773,
                "actual_score": 320,
                "actual_rp1": 0.0,
                "actual_rp2": 1.0,
                "won_match": True,
                "has_actual_data": False,
                "actual_score_auto": 12,
                "actual_score_endgame": 10,
                "actual_score_tele": 244,
                "actual_foul_points": 2,
                "cooperated": True,
                "team_numbers": ["1678", "254", "4414"],
            },
            {
                "match_number": 1,
                "alliance_color_is_red": False,
                "_auto_speaker": 9.0,
                "_auto_amp": 3.0,
                "_tele_speaker": 0.0,
                "_tele_speaker_all": 37.0,
                "_tele_amplified": 37.0,
                "_tele_amp": 12.0,
                "_num_park": 0.33,
                "_num_onstage": 2.5,
                "_num_trap": 0.9,
                "predicted_score": 234.06229508196722,
                "predicted_rp1": 1.0,
                "predicted_rp2": 1.0,
                "win_chance": 0.22699999999999998,
                "actual_score": 278,
                "actual_rp1": 1.0,
                "actual_rp2": 1.0,
                "won_match": False,
                "has_actual_data": False,
                "actual_score_auto": 12,
                "actual_score_endgame": 10,
                "actual_score_tele": 244,
                "actual_foul_points": 2,
                "cooperated": True,
                "team_numbers": ["125", "1323", "5940"],
            },
            {
                "match_number": 2,
                "alliance_color_is_red": True,
                "_auto_speaker": 9.0,
                "_auto_amp": 3.0,
                "_tele_speaker": 0.0,
                "_tele_speaker_all": 44.0,
                "_tele_amplified": 44.0,
                "_tele_amp": 12.0,
                "_num_park": 0.66,
                "_num_onstage": 2.5,
                "_num_trap": 1.9,
                "predicted_score": 213.10545454545453,
                "predicted_rp1": 1.0,
                "predicted_rp2": 1.0,
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
                "_auto_speaker": 5.0,
                "_auto_amp": 3.0,
                "_tele_speaker": 0.0,
                "_tele_speaker_all": 42.0,
                "_tele_amplified": 42.0,
                "_tele_amp": 8.0,
                "_num_park": 0.0,
                "_num_onstage": 2.4,
                "_num_trap": 1.0,
                "predicted_score": 199.10344827586206,
                "predicted_rp1": 1.0,
                "predicted_rp2": 1.0,
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
                "_auto_speaker": 7.0,
                "_auto_amp": 3.0,
                "_tele_speaker": 0.0,
                "_tele_speaker_all": 43.0,
                "_tele_amplified": 43.0,
                "_tele_amp": 10.0,
                "_num_park": 0.33,
                "_num_onstage": 2.7,
                "_num_trap": 1.2,
                "predicted_score": 193.76296296296297,
                "predicted_rp1": 1.0,
                "predicted_rp2": 1.0,
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
                "_auto_speaker": 7.0,
                "_auto_amp": 3.0,
                "_tele_speaker": 0.0,
                "_tele_speaker_all": 43.0,
                "_tele_amplified": 43.0,
                "_tele_amp": 10.0,
                "_num_park": 0.33,
                "_num_onstage": 2.2,
                "_num_trap": 1.7000000000000002,
                "predicted_score": 218.4271186440678,
                "predicted_rp1": 1.0,
                "predicted_rp2": 1.0,
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
                "predicted_score": 178.06153846153848,
            },
            {"alliance_num": 2, "picks": ["189", "345", "200"], "predicted_score": 0.0},
            {"alliance_num": 10, "picks": ["189", "345", "100"], "predicted_score": 0.0},
            {"alliance_num": 18, "picks": ["189", "200", "100"], "predicted_score": 0.0},
        ]
        self.expected_playoffs_updates_2 = [
            {
                "alliance_num": 1,
                "picks": ["1678", "254", "4414"],
                "predicted_score": 178.06153846153848,
            },
            {"alliance_num": 2, "picks": ["189", "345", "200"], "predicted_score": 0.0},
            {"alliance_num": 10, "picks": ["189", "345", "100"], "predicted_score": 0.0},
            {"alliance_num": 18, "picks": ["189", "200", "100"], "predicted_score": 0.0},
        ]
        self.expected_results = [
            {
                "alliance_color_is_red": True,
                "match_number": 1,
                "_auto_amp": 3.0,
                "_auto_speaker": 5.0,
                "_num_onstage": 2.4,
                "_num_park": 0.33,
                "_num_trap": 2.0,
                "_tele_amp": 8.0,
                "_tele_amplified": 49.0,
                "_tele_speaker": 0.0,
                "_tele_speaker_all": 49.0,
                "actual_foul_points": 2,
                "actual_rp1": 0.0,
                "actual_rp2": 1.0,
                "actual_score": 320,
                "actual_score_auto": 12,
                "actual_score_endgame": 10,
                "actual_score_tele": 244,
                "cooperated": True,
                "has_actual_data": False,
                "predicted_rp1": 1.0,
                "predicted_rp2": 1.0,
                "predicted_score": 178.06153846153848,
                "team_numbers": ["1678", "254", "4414"],
                "win_chance": 0.773,
                "won_match": True,
            },
            {
                "alliance_color_is_red": False,
                "match_number": 1,
                "_auto_amp": 3.0,
                "_auto_speaker": 9.0,
                "_num_onstage": 2.5,
                "_num_park": 0.33,
                "_num_trap": 0.9,
                "_tele_amp": 12.0,
                "_tele_amplified": 37.0,
                "_tele_speaker": 0.0,
                "_tele_speaker_all": 37.0,
                "actual_foul_points": 2,
                "actual_rp1": 1.0,
                "actual_rp2": 1.0,
                "actual_score": 278,
                "actual_score_auto": 12,
                "actual_score_endgame": 10,
                "actual_score_tele": 244,
                "cooperated": True,
                "has_actual_data": False,
                "predicted_rp1": 1.0,
                "predicted_rp2": 1.0,
                "predicted_score": 234.06229508196722,
                "team_numbers": ["125", "1323", "5940"],
                "win_chance": 0.22699999999999998,
                "won_match": False,
            },
            {
                "alliance_color_is_red": True,
                "match_number": 2,
                "_auto_amp": 3.0,
                "_auto_speaker": 9.0,
                "_num_onstage": 2.5,
                "_num_park": 0.66,
                "_num_trap": 1.9,
                "_tele_amp": 12.0,
                "_tele_amplified": 44.0,
                "_tele_speaker": 0.0,
                "_tele_speaker_all": 44.0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "actual_score": 0,
                "has_actual_data": False,
                "predicted_rp1": 1.0,
                "predicted_rp2": 1.0,
                "predicted_score": 213.10545454545453,
                "team_numbers": ["1678", "1323", "125"],
                "win_chance": 0.736,
                "won_match": False,
            },
            {
                "alliance_color_is_red": False,
                "match_number": 2,
                "_auto_amp": 3.0,
                "_auto_speaker": 5.0,
                "_num_onstage": 2.4,
                "_num_park": 0.0,
                "_num_trap": 1.0,
                "_tele_amp": 8.0,
                "_tele_amplified": 42.0,
                "_tele_speaker": 0.0,
                "_tele_speaker_all": 42.0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "actual_score": 0,
                "has_actual_data": False,
                "predicted_rp1": 1.0,
                "predicted_rp2": 1.0,
                "predicted_score": 199.10344827586206,
                "team_numbers": ["254", "4414", "5940"],
                "win_chance": 0.264,
                "won_match": False,
            },
            {
                "alliance_color_is_red": True,
                "match_number": 3,
                "_auto_amp": 3.0,
                "_auto_speaker": 7.0,
                "_num_onstage": 2.7,
                "_num_park": 0.33,
                "_num_trap": 1.2,
                "_tele_amp": 10.0,
                "_tele_amplified": 43.0,
                "_tele_speaker": 0.0,
                "_tele_speaker_all": 43.0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "actual_score": 0,
                "has_actual_data": False,
                "predicted_rp1": 1.0,
                "predicted_rp2": 1.0,
                "predicted_score": 193.76296296296297,
                "team_numbers": ["1678", "5940", "4414"],
                "win_chance": 0.5,
                "won_match": False,
            },
            {
                "alliance_color_is_red": False,
                "match_number": 3,
                "_auto_amp": 3.0,
                "_auto_speaker": 7.0,
                "_num_onstage": 2.2,
                "_num_park": 0.33,
                "_num_trap": 1.7000000000000002,
                "_tele_amp": 10.0,
                "_tele_amplified": 43.0,
                "_tele_speaker": 0.0,
                "_tele_speaker_all": 43.0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "actual_score": 0,
                "has_actual_data": False,
                "predicted_rp1": 1.0,
                "predicted_rp2": 1.0,
                "predicted_score": 218.4271186440678,
                "team_numbers": ["1323", "254", "125"],
                "win_chance": 0.5,
                "won_match": False,
            },
        ]
        self.expected_playoffs_alliances = [
            {"alliance_num": 1, "picks": ["1678", "254", "4414"]},
            {"alliance_num": 2, "picks": ["189", "345", "200"]},
            {"alliance_num": 10, "picks": ["189", "345", "100"]},
            {"alliance_num": 18, "picks": ["189", "200", "100"]},
        ]
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
                "tele_avg_unamplified_speaker": 0,
                "tele_sd_unamplified_speaker": 0,
                "tele_sd_amplified": 4,
                "tele_avg_amplified": 17,
                "stage_percent_success_all": 1,
                "parked_percent": 0.33,
                "trap_percent_success": 1,
                "endgame_avg_total_points": 5,
                "endgame_sd_total_points": 1.14,
                "avg_expected_notes": 10,
                "climb_after_percent_success": 0,
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
                "tele_avg_unamplified_speaker": 0,
                "tele_sd_unamplified_speaker": 0,
                "tele_sd_amplified": 4,
                "tele_avg_amplified": 16,
                "stage_percent_success_all": 0.7,
                "parked_percent": 0,
                "trap_percent_success": 0.8,
                "endgame_avg_total_points": 6,
                "endgame_sd_total_points": 1.14,
                "avg_expected_notes": 14,
                "climb_after_percent_success": 0,
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
                "tele_avg_unamplified_speaker": 0,
                "tele_sd_unamplified_speaker": 0,
                "tele_sd_amplified": 4,
                "tele_avg_amplified": 16,
                "stage_percent_success_all": 0.7,
                "parked_percent": 0,
                "trap_percent_success": 0.2,
                "endgame_avg_total_points": 6,
                "endgame_sd_total_points": 1.14,
                "avg_expected_notes": 5,
                "climb_after_percent_success": 0,
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
                "tele_avg_unamplified_speaker": 0,
                "tele_sd_unamplified_speaker": 0,
                "tele_sd_amplified": 4,
                "tele_avg_amplified": 17,
                "stage_percent_success_all": 0.5,
                "parked_percent": 0.33,
                "trap_percent_success": 0.9,
                "endgame_avg_total_points": 5,
                "endgame_sd_total_points": 1.14,
                "avg_expected_notes": 9,
                "climb_after_percent_success": 0,
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
                "tele_avg_unamplified_speaker": 0,
                "tele_sd_unamplified_speaker": 0,
                "tele_sd_amplified": 4,
                "tele_avg_amplified": 10,
                "stage_percent_success_all": 1,
                "parked_percent": 0,
                "trap_percent_success": 0,
                "endgame_avg_total_points": 5,
                "endgame_sd_total_points": 1.14,
                "avg_expected_notes": 13,
                "climb_after_percent_success": 0,
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
                "tele_avg_unamplified_speaker": 0,
                "tele_sd_unamplified_speaker": 0,
                "tele_sd_amplified": 4,
                "tele_avg_amplified": 10,
                "stage_percent_success_all": 1,
                "parked_percent": 0,
                "trap_percent_success": 0,
                "endgame_avg_total_points": 5,
                "endgame_sd_total_points": 1.14,
                "avg_expected_notes": 16,
                "climb_after_percent_success": 0,
            },
        ]
        self.tba_team = [
            {"team_number": "1678", "leave_successes": 5, "matches_played": 5},
            {"team_number": "254", "leave_successes": 4, "matches_played": 5},
            {"team_number": "4414", "leave_successes": 3, "matches_played": 5},
            {"team_number": "125", "leave_successes": 2, "matches_played": 5},
            {"team_number": "5940", "leave_successes": 1, "matches_played": 5},
            {"team_number": "1323", "leave_successes": 4, "matches_played": 5},
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
                        "autoPoints": 12,
                        "endGameTotalStagePoints": 10,
                        "teleopPoints": 254,
                        "foulPoints": 2,
                        "coopertitionBonusAchieved": True,
                    },
                    "red": {
                        "melodyBonusAchieved": False,
                        "ensembleBonusAchieved": True,
                        "totalPoints": 320,
                        "autoPoints": 12,
                        "endGameTotalStagePoints": 10,
                        "teleopPoints": 254,
                        "foulPoints": 2,
                        "coopertitionBonusAchieved": True,
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
                        "autoPoints": 12,
                        "endGameTotalStagePoints": 10,
                        "teleopPoints": 254,
                        "foulPoints": 2,
                        "coopertitionBonusAchieved": True,
                    },
                    "red": {
                        "melodyBonusAchieved": True,
                        "ensembleBonusAchieved": True,
                        "totalPoints": 400,
                        "autoPoints": 12,
                        "endGameTotalStagePoints": 10,
                        "teleopPoints": 254,
                        "foulPoints": 2,
                        "coopertitionBonusAchieved": True,
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
            },
            {
                "name": "Alliance 2",
                "decines": [],
                "picks": ["frc189", "frc345", "frc200", "frc100"],
                "status": {
                    "playoff_average": None,
                    "level": "f",
                    "record": {"losses": 2, "wins": 6, "ties": 1},
                    "status": "won",
                },
            },
        ]
        self.test_server.db.insert_documents("obj_team", self.obj_team)
        self.test_server.db.insert_documents("tba_team", self.tba_team)

    def test__init_(self):
        """Test if attributes are set correctly"""
        assert self.test_calc.watched_collections == ["obj_team", "tba_team"]
        assert self.test_calc.server == self.test_server

    def test_get_playoffs_alliances(self):
        # TODO: need more tests for this, might break
        with patch(
            "data_transfer.tba_communicator.tba_request", return_value=self.tba_playoffs_data
        ):
            assert self.test_calc.get_playoffs_alliances() == self.expected_playoffs_alliances

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
            "actual_score": 320,
            "actual_rp1": 0,
            "actual_rp2": 1,
            "won_match": True,
            "has_actual_data": False,
            "actual_score_auto": 12,
            "actual_score_endgame": 10,
            "actual_score_tele": 244,
            "actual_foul_points": 2,
            "cooperated": True,
        }

        assert self.test_calc.get_actual_values(
            {
                "match_number": 1,
                "alliance_color": "B",
                "team_list": ["1678", "1533", "2468"],
            },
            self.tba_match_data,
        ) == {
            "actual_score": 278,
            "actual_rp1": 1.0,
            "actual_rp2": 1.0,
            "won_match": False,
            "has_actual_data": False,
            "actual_score_auto": 12,
            "actual_score_endgame": 10,
            "actual_score_tele": 244,
            "actual_foul_points": 2,
            "cooperated": True,
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
            "actual_rp1": 0.0,
            "actual_rp2": 0.0,
            "actual_score": 0,
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
            "actual_rp1": 0.0,
            "actual_rp2": 0.0,
            "actual_score": 0,
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
            # ), patch(
            #     "calculations.predicted_aim.PredictedAimCalc.get_predicted_weights",
            #     return_value={
            #         "score": {
            #             "_auto_speaker": 5.094189959717715,
            #             "_auto_amp": -0.18310646490661786,
            #             "_num_leave": 1.1173038961040849,
            #             "_tele_speaker_all": 2.7174908234017012,
            #             "_tele_amp": 3.6388816865690887,
            #             "_num_onstage": 1.4758601204058897,
            #             "_num_trap": 6.374089117834991,
            #             "_num_park": -1.9979303847543055,
            #         },
            #         "rp1": {"_total_gamepieces": 0.031348197567197124},
            #         "rp2": {
            #             "_num_onstage": -0.01948135897167234,
            #             "_num_trap": 1.4316615720548596,
            #             "_num_park": -1.2927382503829667,
            #         },
            #         "win_chance": {"_rel_score_diff": 0.47186783802196935},
            #     },
        ):
            print(self.test_calc.update_predicted_aim(self.aims_list))
            assert self.test_calc.update_predicted_aim(self.aims_list) == self.expected_updates

    def test_update_playoffs_alliances(self):
        """Test that we correctly calculate data for each of the playoff alliances"""
        self.test_server.db.delete_data("predicted_aim")
        with patch(
            "calculations.predicted_aim.PredictedAimCalc.get_playoffs_alliances",
            return_value=self.expected_playoffs_alliances,
            # ), patch(
            #     "calculations.predicted_aim.PredictedAimCalc.get_predicted_weights",
            #     return_value={
            #         "score": {
            #             "_auto_speaker": 5.094189959717715,
            #             "_auto_amp": -0.18310646490661786,
            #             "_num_leave": 1.1173038961040849,
            #             "_tele_speaker_all": 2.7174908234017012,
            #             "_tele_amp": 3.6388816865690887,
            #             "_num_onstage": 1.4758601204058897,
            #             "_num_trap": 6.374089117834991,
            #             "_num_park": -1.9979303847543055,
            #         },
            #         "rp1": {"_total_gamepieces": 0.031348197567197124},
            #         "rp2": {
            #             "_num_onstage": -0.01948135897167234,
            #             "_num_trap": 1.4316615720548596,
            #             "_num_park": -1.2927382503829667,
            #         },
            #         "win_chance": {"_rel_score_diff": 0.47186783802196935},
            #     },
        ):
            print(self.test_calc.update_playoffs_alliances())
            assert self.test_calc.update_playoffs_alliances() == self.expected_playoffs_updates_2

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

        assert result == self.expected_results

        result2 = self.test_server.db.find("predicted_alliances")
        for document in result2:
            del document["_id"]

        assert result2 == self.expected_playoffs_updates
