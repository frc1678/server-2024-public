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
                "_auto_amp": 3,
                "_auto_speaker": 5,
                "_num_leave": 2.4,
                "_tele_amp": 8,
                "_tele_speaker_all": 49,
                "_total_gamepieces": 57,
                "_num_park": 0.33,
                "_num_onstage": 2.4,
                "_num_trap": 2.0,
                "_rel_score_diff": 1.0283162719518513,
                "_predicted_score": 205.5021890914298,
                "predicted_score": 205.5021890914298,
                "predicted_rp1": 0.8565403064189782,
                "predicted_rp2": 0.9160588199101787,
                "predicted_win_chance": 0.6189819530794729,
                "has_actual_data": True,
                "won_match": True,
                "actual_score": 320,
                "actual_score_no_foul": 318,
                "actual_score_auto": 12,
                "actual_score_tele": 244,
                "actual_score_endgame": 10,
                "actual_foul_points": 2,
                "actual_rp1": 0,
                "actual_rp2": 1,
                "cooperated": True,
                "team_numbers": ["1678", "254", "4414"],
                "event_key": "2024arc",
            },
            {
                "match_number": 1,
                "alliance_color_is_red": False,
                "_auto_amp": 3,
                "_auto_speaker": 9,
                "_num_leave": 1.4000000000000001,
                "_tele_amp": 12,
                "_tele_speaker_all": 37,
                "_total_gamepieces": 49,
                "_num_park": 0.33,
                "_num_onstage": 2.5,
                "_num_trap": 0.9,
                "_rel_score_diff": 1.0283162719518513,
                "_predicted_score": 199.8433698820746,
                "predicted_score": 205.5021890914298,
                "predicted_rp1": 0.8565403064189782,
                "predicted_rp2": 0.9160588199101787,
                "predicted_win_chance": 0.3810180469205271,
                "has_actual_data": True,
                "won_match": False,
                "actual_score": 278,
                "actual_score_no_foul": 276,
                "actual_score_auto": 12,
                "actual_score_tele": 244,
                "actual_score_endgame": 10,
                "actual_foul_points": 2,
                "actual_rp1": 1,
                "actual_rp2": 1,
                "cooperated": True,
                "team_numbers": ["125", "1323", "5940"],
                "event_key": "2024arc",
            },
            {
                "match_number": 2,
                "alliance_color_is_red": True,
                "_auto_amp": 3,
                "_auto_speaker": 9,
                "_num_leave": 2.2,
                "_tele_amp": 12,
                "_tele_speaker_all": 44,
                "_total_gamepieces": 56,
                "_num_park": 0.66,
                "_num_onstage": 2.5,
                "_num_trap": 1.9,
                "_rel_score_diff": 1.2535330749026377,
                "_predicted_score": 225.47442085363585,
                "predicted_score": 225.47442085363585,
                "predicted_rp1": 0.852645053085183,
                "predicted_rp2": 0.8603555691713193,
                "predicted_win_chance": 0.6437096866654367,
                "has_actual_data": False,
                "team_numbers": ["1678", "1323", "125"],
                "event_key": "2024arc",
            },
            {
                "match_number": 2,
                "alliance_color_is_red": False,
                "_auto_amp": 3,
                "_auto_speaker": 5,
                "_num_leave": 1.5999999999999999,
                "_tele_amp": 8,
                "_tele_speaker_all": 42,
                "_total_gamepieces": 50,
                "_num_park": 0,
                "_num_onstage": 2.4,
                "_num_trap": 1.0,
                "_rel_score_diff": 1.2535330749026377,
                "_predicted_score": 179.87113811986853,
                "predicted_score": 225.47442085363585,
                "predicted_rp1": 0.852645053085183,
                "predicted_rp2": 0.8603555691713193,
                "predicted_win_chance": 0.3562903133345633,
                "has_actual_data": False,
                "team_numbers": ["254", "4414", "5940"],
                "event_key": "2024arc",
            },
            {
                "match_number": 3,
                "alliance_color_is_red": True,
                "_auto_amp": 3,
                "_auto_speaker": 7,
                "_num_leave": 1.7999999999999998,
                "_tele_amp": 10,
                "_tele_speaker_all": 43,
                "_total_gamepieces": 53,
                "_num_park": 0.33,
                "_num_onstage": 2.7,
                "_num_trap": 1.2,
                "_rel_score_diff": 0.9868997230584442,
                "_predicted_score": 201.33649184778452,
                "predicted_score": 201.33649184778452,
                "predicted_rp1": 0.8404331518829944,
                "predicted_rp2": 0.7753534296014054,
                "predicted_win_chance": 0.6143622400724514,
                "has_actual_data": False,
                "team_numbers": ["1678", "5940", "4414"],
                "event_key": "2024arc",
            },
            {
                "match_number": 3,
                "alliance_color_is_red": False,
                "_auto_amp": 3,
                "_auto_speaker": 7,
                "_num_leave": 2.0,
                "_tele_amp": 10,
                "_tele_speaker_all": 43,
                "_total_gamepieces": 53,
                "_num_park": 0.33,
                "_num_onstage": 2.2,
                "_num_trap": 1.7000000000000002,
                "_rel_score_diff": 0.9868997230584442,
                "_predicted_score": 204.0090671257199,
                "predicted_score": 201.33649184778452,
                "predicted_rp1": 0.8404331518829944,
                "predicted_rp2": 0.7753534296014054,
                "predicted_win_chance": 0.38563775992754856,
                "has_actual_data": False,
                "team_numbers": ["1323", "254", "125"],
                "event_key": "2024arc",
            },
        ]
        self.expected_playoffs_updates = [
            {
                "alliance_num": 1,
                "picks": ["1678", "254", "4414"],
                "_auto_amp": 3,
                "_auto_speaker": 5,
                "_num_leave": 2.4,
                "_tele_amp": 8,
                "_tele_speaker_all": 49,
                "_total_gamepieces": 57,
                "_num_park": 0.33,
                "_num_onstage": 2.4,
                "_num_trap": 2.0,
                "predicted_score": 205.5021890914298,
                "predicted_rp1": 0.8565403064189782,
                "predicted_rp2": 0.9160588199101787,
                "team_numbers": ["1678", "254", "4414"],
                "event_key": "2024arc",
            },
            {
                "alliance_num": 2,
                "picks": ["189", "345", "200"],
                "_auto_amp": 0,
                "_auto_speaker": 0,
                "_num_leave": 0,
                "_tele_amp": 0,
                "_tele_speaker_all": 0,
                "_total_gamepieces": 0,
                "_num_park": 0,
                "_num_onstage": 0,
                "_num_trap": 0,
                "predicted_score": 0.0,
                "predicted_rp1": 0.5,
                "predicted_rp2": 0.5,
                "team_numbers": ["189", "345", "200"],
                "event_key": "2024arc",
            },
            {
                "alliance_num": 10,
                "picks": ["189", "345", "100"],
                "_auto_amp": 0,
                "_auto_speaker": 0,
                "_num_leave": 0,
                "_tele_amp": 0,
                "_tele_speaker_all": 0,
                "_total_gamepieces": 0,
                "_num_park": 0,
                "_num_onstage": 0,
                "_num_trap": 0,
                "predicted_score": 0.0,
                "predicted_rp1": 0.5,
                "predicted_rp2": 0.5,
                "team_numbers": ["189", "345", "100"],
                "event_key": "2024arc",
            },
            {
                "alliance_num": 18,
                "picks": ["189", "200", "100"],
                "_auto_amp": 0,
                "_auto_speaker": 0,
                "_num_leave": 0,
                "_tele_amp": 0,
                "_tele_speaker_all": 0,
                "_total_gamepieces": 0,
                "_num_park": 0,
                "_num_onstage": 0,
                "_num_trap": 0,
                "predicted_score": 0.0,
                "predicted_rp1": 0.5,
                "predicted_rp2": 0.5,
                "team_numbers": ["189", "200", "100"],
                "event_key": "2024arc",
            },
        ]
        self.expected_results = [
            {
                "alliance_color_is_red": True,
                "match_number": 1,
                "_auto_amp": 3,
                "_auto_speaker": 5,
                "_num_leave": 2.4,
                "_num_onstage": 2.4,
                "_num_park": 0.33,
                "_num_trap": 2.0,
                "_predicted_score": 205.5021890914298,
                "_rel_score_diff": 1.0283162719518513,
                "_tele_amp": 8,
                "_tele_speaker_all": 49,
                "_total_gamepieces": 57,
                "actual_foul_points": 2,
                "actual_rp1": 0,
                "actual_rp2": 1,
                "actual_score": 320,
                "actual_score_auto": 12,
                "actual_score_endgame": 10,
                "actual_score_no_foul": 318,
                "actual_score_tele": 244,
                "cooperated": True,
                "event_key": "2024arc",
                "has_actual_data": True,
                "predicted_rp1": 0.8565403064189782,
                "predicted_rp2": 0.9160588199101787,
                "predicted_score": 205.5021890914298,
                "predicted_win_chance": 0.6189819530794729,
                "team_numbers": ["1678", "254", "4414"],
                "won_match": True,
            },
            {
                "alliance_color_is_red": False,
                "match_number": 1,
                "_auto_amp": 3,
                "_auto_speaker": 9,
                "_num_leave": 1.4000000000000001,
                "_num_onstage": 2.5,
                "_num_park": 0.33,
                "_num_trap": 0.9,
                "_predicted_score": 199.8433698820746,
                "_rel_score_diff": 1.0283162719518513,
                "_tele_amp": 12,
                "_tele_speaker_all": 37,
                "_total_gamepieces": 49,
                "actual_foul_points": 2,
                "actual_rp1": 1,
                "actual_rp2": 1,
                "actual_score": 278,
                "actual_score_auto": 12,
                "actual_score_endgame": 10,
                "actual_score_no_foul": 276,
                "actual_score_tele": 244,
                "cooperated": True,
                "event_key": "2024arc",
                "has_actual_data": True,
                "predicted_rp1": 0.8565403064189782,
                "predicted_rp2": 0.9160588199101787,
                "predicted_score": 205.5021890914298,
                "predicted_win_chance": 0.3810180469205271,
                "team_numbers": ["125", "1323", "5940"],
                "won_match": False,
            },
            {
                "alliance_color_is_red": True,
                "match_number": 2,
                "_auto_amp": 3,
                "_auto_speaker": 9,
                "_num_leave": 2.2,
                "_num_onstage": 2.5,
                "_num_park": 0.66,
                "_num_trap": 1.9,
                "_predicted_score": 225.47442085363585,
                "_rel_score_diff": 1.2535330749026377,
                "_tele_amp": 12,
                "_tele_speaker_all": 44,
                "_total_gamepieces": 56,
                "event_key": "2024arc",
                "has_actual_data": False,
                "predicted_rp1": 0.852645053085183,
                "predicted_rp2": 0.8603555691713193,
                "predicted_score": 225.47442085363585,
                "predicted_win_chance": 0.6437096866654367,
                "team_numbers": ["1678", "1323", "125"],
            },
            {
                "alliance_color_is_red": False,
                "match_number": 2,
                "_auto_amp": 3,
                "_auto_speaker": 5,
                "_num_leave": 1.5999999999999999,
                "_num_onstage": 2.4,
                "_num_park": 0,
                "_num_trap": 1.0,
                "_predicted_score": 179.87113811986853,
                "_rel_score_diff": 1.2535330749026377,
                "_tele_amp": 8,
                "_tele_speaker_all": 42,
                "_total_gamepieces": 50,
                "event_key": "2024arc",
                "has_actual_data": False,
                "predicted_rp1": 0.852645053085183,
                "predicted_rp2": 0.8603555691713193,
                "predicted_score": 225.47442085363585,
                "predicted_win_chance": 0.3562903133345633,
                "team_numbers": ["254", "4414", "5940"],
            },
            {
                "alliance_color_is_red": True,
                "match_number": 3,
                "_auto_amp": 3,
                "_auto_speaker": 7,
                "_num_leave": 1.7999999999999998,
                "_num_onstage": 2.7,
                "_num_park": 0.33,
                "_num_trap": 1.2,
                "_predicted_score": 201.33649184778452,
                "_rel_score_diff": 0.9868997230584442,
                "_tele_amp": 10,
                "_tele_speaker_all": 43,
                "_total_gamepieces": 53,
                "event_key": "2024arc",
                "has_actual_data": False,
                "predicted_rp1": 0.8404331518829944,
                "predicted_rp2": 0.7753534296014054,
                "predicted_score": 201.33649184778452,
                "predicted_win_chance": 0.6143622400724514,
                "team_numbers": ["1678", "5940", "4414"],
            },
            {
                "alliance_color_is_red": False,
                "match_number": 3,
                "_auto_amp": 3,
                "_auto_speaker": 7,
                "_num_leave": 2.0,
                "_num_onstage": 2.2,
                "_num_park": 0.33,
                "_num_trap": 1.7000000000000002,
                "_predicted_score": 204.0090671257199,
                "_rel_score_diff": 0.9868997230584442,
                "_tele_amp": 10,
                "_tele_speaker_all": 43,
                "_total_gamepieces": 53,
                "event_key": "2024arc",
                "has_actual_data": False,
                "predicted_rp1": 0.8404331518829944,
                "predicted_rp2": 0.7753534296014054,
                "predicted_score": 201.33649184778452,
                "predicted_win_chance": 0.38563775992754856,
                "team_numbers": ["1323", "254", "125"],
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
                "tele_avg_speaker": 0,
                "tele_sd_speaker": 0,
                "tele_sd_amplified": 4,
                "tele_avg_amplified": 17,
                "stage_percent_success_all": 1,
                "parked_percent": 0.33,
                "trap_percent_success": 1,
                "endgame_avg_total_points": 5,
                "endgame_sd_total_points": 1.14,
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
                "stage_percent_success_all": 0.7,
                "parked_percent": 0,
                "trap_percent_success": 0.8,
                "endgame_avg_total_points": 6,
                "endgame_sd_total_points": 1.14,
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
                "stage_percent_success_all": 0.7,
                "parked_percent": 0,
                "trap_percent_success": 0.2,
                "endgame_avg_total_points": 6,
                "endgame_sd_total_points": 1.14,
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
                "stage_percent_success_all": 0.5,
                "parked_percent": 0.33,
                "trap_percent_success": 0.9,
                "endgame_avg_total_points": 5,
                "endgame_sd_total_points": 1.14,
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
                "stage_percent_success_all": 1,
                "parked_percent": 0,
                "trap_percent_success": 0,
                "endgame_avg_total_points": 5,
                "endgame_sd_total_points": 1.14,
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
                "stage_percent_success_all": 1,
                "parked_percent": 0,
                "trap_percent_success": 0,
                "endgame_avg_total_points": 5,
                "endgame_sd_total_points": 1.14,
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
            "actual_score_no_foul": 318,
            "actual_rp1": 0,
            "actual_rp2": 1,
            "won_match": True,
            "has_actual_data": True,
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
            "actual_score_no_foul": 276,
            "actual_rp1": 1,
            "actual_rp2": 1,
            "won_match": False,
            "has_actual_data": True,
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
        ), patch(
            "calculations.predicted_aim.PredictedAimCalc.get_predicted_weights",
            return_value={
                "score": {
                    "_auto_speaker": 5.094189959717715,
                    "_auto_amp": -0.18310646490661786,
                    "_num_leave": 1.1173038961040849,
                    "_tele_speaker_all": 2.7174908234017012,
                    "_tele_amp": 3.6388816865690887,
                    "_num_onstage": 1.4758601204058897,
                    "_num_trap": 6.374089117834991,
                    "_num_park": -1.9979303847543055,
                },
                "rp1": {"_total_gamepieces": 0.031348197567197124},
                "rp2": {
                    "_num_onstage": -0.01948135897167234,
                    "_num_trap": 1.4316615720548596,
                    "_num_park": -1.2927382503829667,
                },
                "win_chance": {"_rel_score_diff": 0.47186783802196935},
            },
        ):
            assert self.test_calc.update_predicted_aim(self.aims_list) == self.expected_updates

    def test_update_playoffs_alliances(self):
        """Test that we correctly calculate data for each of the playoff alliances"""
        self.test_server.db.delete_data("predicted_aim")
        with patch(
            "calculations.predicted_aim.PredictedAimCalc.get_playoffs_alliances",
            return_value=self.expected_playoffs_alliances,
        ), patch(
            "calculations.predicted_aim.PredictedAimCalc.get_predicted_weights",
            return_value={
                "score": {
                    "_auto_speaker": 5.094189959717715,
                    "_auto_amp": -0.18310646490661786,
                    "_num_leave": 1.1173038961040849,
                    "_tele_speaker_all": 2.7174908234017012,
                    "_tele_amp": 3.6388816865690887,
                    "_num_onstage": 1.4758601204058897,
                    "_num_trap": 6.374089117834991,
                    "_num_park": -1.9979303847543055,
                },
                "rp1": {"_total_gamepieces": 0.031348197567197124},
                "rp2": {
                    "_num_onstage": -0.01948135897167234,
                    "_num_trap": 1.4316615720548596,
                    "_num_park": -1.2927382503829667,
                },
                "win_chance": {"_rel_score_diff": 0.47186783802196935},
            },
        ):
            assert self.test_calc.update_playoffs_alliances() == self.expected_playoffs_updates

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
        ), patch(
            "calculations.predicted_aim.PredictedAimCalc.get_predicted_weights",
            return_value={
                "score": {
                    "_auto_speaker": 5.094189959717715,
                    "_auto_amp": -0.18310646490661786,
                    "_num_leave": 1.1173038961040849,
                    "_tele_speaker_all": 2.7174908234017012,
                    "_tele_amp": 3.6388816865690887,
                    "_num_onstage": 1.4758601204058897,
                    "_num_trap": 6.374089117834991,
                    "_num_park": -1.9979303847543055,
                },
                "rp1": {"_total_gamepieces": 0.031348197567197124},
                "rp2": {
                    "_num_onstage": -0.01948135897167234,
                    "_num_trap": 1.4316615720548596,
                    "_num_park": -1.2927382503829667,
                },
                "win_chance": {"_rel_score_diff": 0.47186783802196935},
            },
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
