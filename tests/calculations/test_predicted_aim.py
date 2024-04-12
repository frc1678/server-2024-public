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
                "_auto_amp_red": 3,
                "_auto_speaker_red": 5,
                "_num_leave_red": 2.4,
                "_tele_amp_red": 8,
                "_tele_speaker_all_red": 49,
                "_num_park_red": 0.33,
                "_num_onstage_red": 2.4,
                "_num_trap_red": 2.0,
                "predicted_score_red": 158.54667309336998,
                "predicted_score": 158.54667309336998,
                "predicted_rp1": 0.8854458416321949,
                "predicted_rp2": 0.727488403131397,
                "predicted_win_chance": 0.40419390147006296,
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
                "event_key": utils.TBA_EVENT_KEY,
            },
            {
                "match_number": 1,
                "alliance_color_is_red": False,
                "_auto_amp_blue": 3,
                "_auto_speaker_blue": 9,
                "_num_leave_blue": 1.4000000000000001,
                "_tele_amp_blue": 12,
                "_tele_speaker_all_blue": 37,
                "_num_park_blue": 0.33,
                "_num_onstage_blue": 2.5,
                "_num_trap_blue": 0.9,
                "_rel_score_diff": 1.1062357903405726,
                "predicted_score_blue": 143.32086746584,
                "predicted_score": 158.54667309336998,
                "predicted_rp1": 0.8854458416321949,
                "predicted_rp2": 0.727488403131397,
                "predicted_win_chance": 0.595806098529937,
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
                "event_key": utils.TBA_EVENT_KEY,
            },
            {
                "match_number": 2,
                "alliance_color_is_red": True,
                "_auto_amp_red": 3,
                "_auto_speaker_red": 9,
                "_num_leave_red": 2.2,
                "_tele_amp_red": 12,
                "_tele_speaker_all_red": 44,
                "_num_park_red": 0.66,
                "_num_onstage_red": 2.5,
                "_num_trap_red": 1.9,
                "predicted_score_red": 169.04080734664998,
                "predicted_score": 169.04080734664998,
                "predicted_rp1": 0.921041385963257,
                "predicted_rp2": 0.7177317233522308,
                "predicted_win_chance": 0.5560264545383701,
                "has_actual_data": False,
                "team_numbers": ["1678", "1323", "125"],
                "event_key": utils.TBA_EVENT_KEY,
            },
            {
                "match_number": 2,
                "alliance_color_is_red": False,
                "_auto_amp_blue": 3,
                "_auto_speaker_blue": 5,
                "_num_leave_blue": 1.5999999999999999,
                "_tele_amp_blue": 8,
                "_tele_speaker_all_blue": 42,
                "_num_park_blue": 0,
                "_num_onstage_blue": 2.4,
                "_num_trap_blue": 1.0,
                "_rel_score_diff": 1.272641457470292,
                "predicted_score_blue": 132.82673321256,
                "predicted_score": 169.04080734664998,
                "predicted_rp1": 0.921041385963257,
                "predicted_rp2": 0.7177317233522308,
                "predicted_win_chance": 0.4439735454616299,
                "has_actual_data": False,
                "team_numbers": ["254", "4414", "5940"],
                "event_key": utils.TBA_EVENT_KEY,
            },
            {
                "match_number": 3,
                "alliance_color_is_red": True,
                "_auto_amp_red": 3,
                "_auto_speaker_red": 7,
                "_num_leave_red": 1.7999999999999998,
                "_tele_amp_red": 10,
                "_tele_speaker_all_red": 43,
                "_num_park_red": 0.33,
                "_num_onstage_red": 2.7,
                "_num_trap_red": 1.2,
                "predicted_score_red": 149.24616035142998,
                "predicted_score": 149.24616035142998,
                "predicted_rp1": 0.8935666937803423,
                "predicted_rp2": 0.6618379483839812,
                "predicted_win_chance": 0.29715337874545394,
                "has_actual_data": False,
                "team_numbers": ["1678", "5940", "4414"],
                "event_key": utils.TBA_EVENT_KEY,
            },
            {
                "match_number": 3,
                "alliance_color_is_red": False,
                "_auto_amp_blue": 3,
                "_auto_speaker_blue": 7,
                "_num_leave_blue": 2.0,
                "_tele_amp_blue": 10,
                "_tele_speaker_all_blue": 43,
                "_num_park_blue": 0.33,
                "_num_onstage_blue": 2.2,
                "_num_trap_blue": 1.7000000000000002,
                "_rel_score_diff": 0.9778850128877424,
                "predicted_score_blue": 152.62138020778,
                "predicted_score": 149.24616035142998,
                "predicted_rp1": 0.8935666937803423,
                "predicted_rp2": 0.6618379483839812,
                "predicted_win_chance": 0.7028466212545461,
                "has_actual_data": False,
                "team_numbers": ["1323", "254", "125"],
                "event_key": utils.TBA_EVENT_KEY,
            },
        ]
        self.expected_playoffs_updates = [
            {
                "alliance_num": 1,
                "_auto_amp": 3,
                "_auto_speaker": 5,
                "_num_leave": 2.4,
                "_num_onstage": 2.4,
                "_num_park": 0.33,
                "_num_trap": 2.0,
                "_tele_amp": 8,
                "_tele_speaker_all": 49,
                "event_key": utils.TBA_EVENT_KEY,
                "picks": ["1678", "254", "4414"],
                "predicted_rp1": 0.8854458416321949,
                "predicted_rp2": 0.727488403131397,
                "predicted_score": 158.54667309336998,
                "team_numbers": ["1678", "254", "4414"],
            },
            {
                "alliance_num": 2,
                "_auto_amp": 0,
                "_auto_speaker": 0,
                "_num_leave": 0,
                "_num_onstage": 0,
                "_num_park": 0,
                "_num_trap": 0,
                "_tele_amp": 0,
                "_tele_speaker_all": 0,
                "event_key": utils.TBA_EVENT_KEY,
                "picks": ["189", "345", "200"],
                "predicted_rp1": 0.42872379308053216,
                "predicted_rp2": 0.5077529466813056,
                "predicted_score": -1.8357210178,
                "team_numbers": ["189", "345", "200"],
            },
            {
                "alliance_num": 10,
                "_auto_amp": 0,
                "_auto_speaker": 0,
                "_num_leave": 0,
                "_num_onstage": 0,
                "_num_park": 0,
                "_num_trap": 0,
                "_tele_amp": 0,
                "_tele_speaker_all": 0,
                "event_key": utils.TBA_EVENT_KEY,
                "picks": ["189", "345", "100"],
                "predicted_rp1": 0.42872379308053216,
                "predicted_rp2": 0.5077529466813056,
                "predicted_score": -1.8357210178,
                "team_numbers": ["189", "345", "100"],
            },
            {
                "alliance_num": 18,
                "_auto_amp": 0,
                "_auto_speaker": 0,
                "_num_leave": 0,
                "_num_onstage": 0,
                "_num_park": 0,
                "_num_trap": 0,
                "_tele_amp": 0,
                "_tele_speaker_all": 0,
                "event_key": utils.TBA_EVENT_KEY,
                "picks": ["189", "200", "100"],
                "predicted_rp1": 0.42872379308053216,
                "predicted_rp2": 0.5077529466813056,
                "predicted_score": -1.8357210178,
                "team_numbers": ["189", "200", "100"],
            },
        ]
        self.expected_results = [
            {
                "alliance_color_is_red": True,
                "match_number": 1,
                "_auto_amp_red": 3,
                "_auto_speaker_red": 5,
                "_num_leave_red": 2.4,
                "_num_onstage_red": 2.4,
                "_num_park_red": 0.33,
                "_num_trap_red": 2.0,
                "_tele_amp_red": 8,
                "_tele_speaker_all_red": 49,
                "actual_foul_points": 2,
                "actual_rp1": 0,
                "actual_rp2": 1,
                "actual_score": 320,
                "actual_score_auto": 12,
                "actual_score_endgame": 10,
                "actual_score_no_foul": 318,
                "actual_score_tele": 244,
                "cooperated": True,
                "event_key": utils.TBA_EVENT_KEY,
                "has_actual_data": True,
                "predicted_rp1": 0.8854458416321949,
                "predicted_rp2": 0.727488403131397,
                "predicted_score": 158.54667309336998,
                "predicted_score_red": 158.54667309336998,
                "predicted_win_chance": 0.40419390147006296,
                "team_numbers": ["1678", "254", "4414"],
                "won_match": True,
            },
            {
                "alliance_color_is_red": False,
                "match_number": 1,
                "_auto_amp_blue": 3,
                "_auto_speaker_blue": 9,
                "_num_leave_blue": 1.4000000000000001,
                "_num_onstage_blue": 2.5,
                "_num_park_blue": 0.33,
                "_num_trap_blue": 0.9,
                "_rel_score_diff": 1.1062357903405726,
                "_tele_amp_blue": 12,
                "_tele_speaker_all_blue": 37,
                "actual_foul_points": 2,
                "actual_rp1": 1,
                "actual_rp2": 1,
                "actual_score": 278,
                "actual_score_auto": 12,
                "actual_score_endgame": 10,
                "actual_score_no_foul": 276,
                "actual_score_tele": 244,
                "cooperated": True,
                "event_key": utils.TBA_EVENT_KEY,
                "has_actual_data": True,
                "predicted_rp1": 0.8854458416321949,
                "predicted_rp2": 0.727488403131397,
                "predicted_score": 158.54667309336998,
                "predicted_score_blue": 143.32086746584,
                "predicted_win_chance": 0.595806098529937,
                "team_numbers": ["125", "1323", "5940"],
                "won_match": False,
            },
            {
                "alliance_color_is_red": True,
                "match_number": 2,
                "_auto_amp_red": 3,
                "_auto_speaker_red": 9,
                "_num_leave_red": 2.2,
                "_num_onstage_red": 2.5,
                "_num_park_red": 0.66,
                "_num_trap_red": 1.9,
                "_tele_amp_red": 12,
                "_tele_speaker_all_red": 44,
                "event_key": utils.TBA_EVENT_KEY,
                "has_actual_data": False,
                "predicted_rp1": 0.921041385963257,
                "predicted_rp2": 0.7177317233522308,
                "predicted_score": 169.04080734664998,
                "predicted_score_red": 169.04080734664998,
                "predicted_win_chance": 0.5560264545383701,
                "team_numbers": ["1678", "1323", "125"],
            },
            {
                "alliance_color_is_red": False,
                "match_number": 2,
                "_auto_amp_blue": 3,
                "_auto_speaker_blue": 5,
                "_num_leave_blue": 1.5999999999999999,
                "_num_onstage_blue": 2.4,
                "_num_park_blue": 0,
                "_num_trap_blue": 1.0,
                "_rel_score_diff": 1.272641457470292,
                "_tele_amp_blue": 8,
                "_tele_speaker_all_blue": 42,
                "event_key": utils.TBA_EVENT_KEY,
                "has_actual_data": False,
                "predicted_rp1": 0.921041385963257,
                "predicted_rp2": 0.7177317233522308,
                "predicted_score": 169.04080734664998,
                "predicted_score_blue": 132.82673321256,
                "predicted_win_chance": 0.4439735454616299,
                "team_numbers": ["254", "4414", "5940"],
            },
            {
                "alliance_color_is_red": True,
                "match_number": 3,
                "_auto_amp_red": 3,
                "_auto_speaker_red": 7,
                "_num_leave_red": 1.7999999999999998,
                "_num_onstage_red": 2.7,
                "_num_park_red": 0.33,
                "_num_trap_red": 1.2,
                "_tele_amp_red": 10,
                "_tele_speaker_all_red": 43,
                "event_key": utils.TBA_EVENT_KEY,
                "has_actual_data": False,
                "predicted_rp1": 0.8935666937803423,
                "predicted_rp2": 0.6618379483839812,
                "predicted_score": 149.24616035142998,
                "predicted_score_red": 149.24616035142998,
                "predicted_win_chance": 0.29715337874545394,
                "team_numbers": ["1678", "5940", "4414"],
            },
            {
                "alliance_color_is_red": False,
                "match_number": 3,
                "_auto_amp_blue": 3,
                "_auto_speaker_blue": 7,
                "_num_leave_blue": 2.0,
                "_num_onstage_blue": 2.2,
                "_num_park_blue": 0.33,
                "_num_trap_blue": 1.7000000000000002,
                "_rel_score_diff": 0.9778850128877424,
                "_tele_amp_blue": 10,
                "_tele_speaker_all_blue": 43,
                "event_key": utils.TBA_EVENT_KEY,
                "has_actual_data": False,
                "predicted_rp1": 0.8935666937803423,
                "predicted_rp2": 0.6618379483839812,
                "predicted_score": 149.24616035142998,
                "predicted_score_blue": 152.62138020778,
                "predicted_win_chance": 0.7028466212545461,
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
                    "const": -1.8357210178,
                    "_auto_speaker": 3.3261972774,
                    "_auto_amp": 1.3510207911,
                    "_num_leave": 5.995113766,
                    "_tele_speaker_all": 1.7574535611,
                    "_tele_amp": 1.7399168516,
                    "_num_onstage": 3.6180720174,
                    "_num_trap": 7.9704662237,
                    "_num_park": 1.973356717,
                },
                "rp1": {
                    "const": -0.287059945,
                    "_auto_speaker": 0.0832153976,
                    "_auto_amp": -0.1055357247,
                    "_tele_speaker_all": 0.0351742679,
                    "_tele_amp": 0.0636368235,
                },
                "rp2": {
                    "const": 0.0310142725,
                    "_num_onstage": 0.0598301184,
                    "_num_trap": 0.4104630143,
                    "_num_park": -0.0412596896,
                },
                "win_chance": {"const": -4.4636124314, "_rel_score_diff": 3.6841981681},
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
                    "const": -1.8357210178,
                    "_auto_speaker": 3.3261972774,
                    "_auto_amp": 1.3510207911,
                    "_num_leave": 5.995113766,
                    "_tele_speaker_all": 1.7574535611,
                    "_tele_amp": 1.7399168516,
                    "_num_onstage": 3.6180720174,
                    "_num_trap": 7.9704662237,
                    "_num_park": 1.973356717,
                },
                "rp1": {
                    "const": -0.287059945,
                    "_auto_speaker": 0.0832153976,
                    "_auto_amp": -0.1055357247,
                    "_tele_speaker_all": 0.0351742679,
                    "_tele_amp": 0.0636368235,
                },
                "rp2": {
                    "const": 0.0310142725,
                    "_num_onstage": 0.0598301184,
                    "_num_trap": 0.4104630143,
                    "_num_park": -0.0412596896,
                },
                "win_chance": {"const": -4.4636124314, "_rel_score_diff": 3.6841981681},
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
                    "const": -1.8357210178,
                    "_auto_speaker": 3.3261972774,
                    "_auto_amp": 1.3510207911,
                    "_num_leave": 5.995113766,
                    "_tele_speaker_all": 1.7574535611,
                    "_tele_amp": 1.7399168516,
                    "_num_onstage": 3.6180720174,
                    "_num_trap": 7.9704662237,
                    "_num_park": 1.973356717,
                },
                "rp1": {
                    "const": -0.287059945,
                    "_auto_speaker": 0.0832153976,
                    "_auto_amp": -0.1055357247,
                    "_tele_speaker_all": 0.0351742679,
                    "_tele_amp": 0.0636368235,
                },
                "rp2": {
                    "const": 0.0310142725,
                    "_num_onstage": 0.0598301184,
                    "_num_trap": 0.4104630143,
                    "_num_park": -0.0412596896,
                },
                "win_chance": {"const": -4.4636124314, "_rel_score_diff": 3.6841981681},
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
