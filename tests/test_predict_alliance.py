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
            "tele_avg_speaker_amped": 11.2,
            "tele_avg_amp": 2.0,
            "avg_trap": 1.0,
        },
        {
            "team_number": "1533",
            "matches_played": 5,
            "auto_avg_speaker": 2.6,
            "auto_avg_amp": 0.8,
            "tele_avg_speaker": 0.5,
            "tele_avg_speaker_amped": 8.2,
            "tele_avg_amp": 3.6,
            "avg_trap": 0.2,
        },
        {
            "team_number": "7229",
            "matches_played": 5,
            "auto_avg_speaker": 3.4,
            "auto_avg_amp": 1.2,
            "tele_avg_speaker": 4.4,
            "tele_avg_speaker_amped": 4.4,
            "tele_avg_amp": 3.2,
            "avg_trap": 0.6,
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
        "predicted_score": 206.4,
        "predicted_auto_score": 59.8,
        "predicted_stage_score": None,
        "predicted_tele_score": 146.6,
    }
    assert (
        predict_alliance(
            "1678", "1533", "7229", test_server, fake_obj_team_data, fake_tba_team_data
        )
        == expected_return
    )
