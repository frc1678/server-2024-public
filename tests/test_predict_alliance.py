from predict_alliance import predict_alliance
from unittest.mock import patch
import server
import pytest


def test_predict_alliance():
    with patch("server.Server.ask_calc_all_data", return_value=False):
        test_server = server.Server()
    fake_obj_team_data = [
        {
            "team_number": "1678",
            "matches_played": 5,
            "auto_avg_speaker": 4.0,
            "auto_avg_amp": 0.5,
            "tele_avg_speaker": 0.0,
            "tele_avg_amplified": 11.2,
            "tele_avg_amp": 2.0,
            "avg_trap": 1.0,
            "avg_cycle_time": 20.0,
            "trap_successes": 1,
            "trap_fails": 3,
            "trap_percent_success": 100,
            "parks": 0,
            "parked_percent": 0,
            "onstage_successes": 5,
            "onstage_attempts": 5,
            "stage_percent_success_all": 100,
            "climb_after_percent_success": 0,
        },
        {
            "team_number": "1533",
            "matches_played": 5,
            "auto_avg_speaker": 2.6,
            "auto_avg_amp": 0.8,
            "tele_avg_speaker": 0.5,
            "tele_avg_amplified": 8.2,
            "tele_avg_amp": 3.6,
            "avg_trap": 0.2,
            "avg_cycle_time": 25.0,
            "trap_successes": 2,
            "trap_fails": 1,
            "trap_percent_success": 50,
            "parks": 2,
            "parked_percent": 40,
            "onstage_successes": 1,
            "onstage_attempts": 2,
            "stage_percent_success_all": 20,
            "climb_after_percent_success": 100,
        },
        {
            "team_number": "7229",
            "matches_played": 5,
            "auto_avg_speaker": 3.4,
            "auto_avg_amp": 1.2,
            "tele_avg_speaker": 4.4,
            "tele_avg_amplified": 4.4,
            "tele_avg_amp": 3.2,
            "avg_trap": 0.6,
            "avg_cycle_time": 30.0,
            "trap_successes": 0,
            "trap_fails": 3,
            "trap_percent_success": 0,
            "parks": 1,
            "parked_percent": 80,
            "onstage_successes": 3,
            "onstage_attempts": 4,
            "stage_percent_success_all": 60,
            "climb_after_percent_success": 0,
        },
    ]
    fake_tba_team_data = [
        {
            "team_number": "1678",
            "leave_successes": 5,
        },
        {
            "team_number": "1533",
            "leave_successes": 4,
        },
        {
            "team_number": "7229",
            "leave_successes": 3,
        },
    ]
    expected_return = {
        "predicted_score": 113.51599999999999,
        "predicted_auto_score": 4.8,
        "predicted_stage_score": 14,
        "predicted_tele_score": 94.716,
    }
    assert (
        predict_alliance(
            "1678", "1533", "7229", test_server, fake_obj_team_data, fake_tba_team_data
        )
        == expected_return
    )
