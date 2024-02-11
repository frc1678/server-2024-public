# Copyright (c) 2023 FRC Team 1678: Citrus Circuits

from unittest import mock

from calculations import base_calculations
from calculations import auto_paths
from server import Server
import pytest


class TestAutoPathCalc:

    obj_teams = [{"team_number": "254"}, {"team_number": "4414"}, {"team_number": "1678"}]

    expected_obj_teams = [
        {"team_number": "254"},
        {"team_number": "4414"},
        {"team_number": "1678"},
    ]

    auto_pims = [
        {
            # 254, 1
            "match_number": 42,
            "team_number": "254",
            "start_position": "1",
            "has_preload": True,
            "score_1": "speaker",
            "intake_position_1": "spike_1",
            "score_2": "amp",
            "intake_position_2": "spike_2",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "leave": True,
            "auto_timeline": [
                {"in_teleop": False, "time": 146, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 147, "action_type": "auto_intake_spike_2"},
                {"in_teleop": False, "time": 148, "action_type": "score_amp"},
                {"in_teleop": False, "time": 149, "action_type": "auto_intake_spike_1"},
                {"in_teleop": False, "time": 150, "action_type": "score_speaker"},
            ][::-1],
            "match_numbers_played": [],
            "path_number": 0,
            "num_matches_ran": 0,
        },
        {
            # 1678, 1
            "match_number": 43,
            "team_number": "1678",
            "start_position": "2",
            "has_preload": True,
            "score_1": "speaker",
            "intake_position_1": "spike_1",
            "score_2": "amp",
            "intake_position_2": "spike_2",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "leave": True,
            "auto_timeline": [
                {"in_teleop": False, "time": 146, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 147, "action_type": "auto_intake_spike_2"},
                {"in_teleop": False, "time": 148, "action_type": "score_amp"},
                {"in_teleop": False, "time": 149, "action_type": "auto_intake_spike_1"},
                {"in_teleop": False, "time": 150, "action_type": "score_speaker"},
            ][::-1],
            "match_numbers_played": [],
            "path_number": 0,
            "num_matches_ran": 0,
        },
        {
            # 4414, 1
            "match_number": 44,
            "team_number": "4414",
            "start_position": "3",
            "has_preload": True,
            "score_1": "speaker",
            "intake_position_1": "spike_1",
            "score_2": "speaker",
            "intake_position_2": "spike_2",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "leave": True,
            "auto_timeline": [
                {"in_teleop": False, "time": 146, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 147, "action_type": "auto_intake_spike_2"},
                {"in_teleop": False, "time": 148, "action_type": "score_amp"},
                {"in_teleop": False, "time": 149, "action_type": "auto_intake_spike_1"},
                {"in_teleop": False, "time": 150, "action_type": "score_speaker"},
            ][::-1],
            "match_numbers_played": [],
            "path_number": 0,
            "num_matches_ran": 0,
        },
        {
            # 254, 2
            "match_number": 45,
            "team_number": "254",
            "start_position": "1",
            "has_preload": True,
            "score_1": "speaker",
            "intake_position_1": "spike_1",
            "score_2": "amp",
            "intake_position_2": "spike_2",
            "score_3": "fail",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "leave": True,
            "auto_timeline": [
                {"in_teleop": False, "time": 146, "action_type": "score_fail"},
                {"in_teleop": False, "time": 147, "action_type": "auto_intake_spike_2"},
                {"in_teleop": False, "time": 148, "action_type": "score_amp"},
                {"in_teleop": False, "time": 149, "action_type": "auto_intake_spike_1"},
                {"in_teleop": False, "time": 150, "action_type": "score_speaker"},
            ][::-1],
            "match_numbers_played": [],
            "path_number": 0,
            "num_matches_ran": 0,
        },
        {
            # 1678, 2
            "match_number": 46,
            "team_number": "1678",
            "start_position": "2",
            "has_preload": True,
            "score_1": "fail",
            "intake_position_1": "spike_1",
            "score_2": "amp",
            "intake_position_2": "spike_2",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "leave": True,
            "auto_timeline": [
                {"in_teleop": False, "time": 146, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 147, "action_type": "auto_intake_spike_2"},
                {"in_teleop": False, "time": 148, "action_type": "score_amp"},
                {"in_teleop": False, "time": 149, "action_type": "auto_intake_spike_1"},
                {"in_teleop": False, "time": 150, "action_type": "score_fail"},
            ][::-1],
            "match_numbers_played": [],
            "path_number": 0,
            "num_matches_ran": 0,
        },
    ]

    expected_auto_pims = [
        {
            # 254, 1
            "match_number": 42,
            "team_number": "254",
            "start_position": "1",
            "has_preload": True,
            "score_1": "speaker",
            "intake_position_1": "spike_1",
            "score_2": "amp",
            "intake_position_2": "spike_2",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "leave": True,
            "auto_timeline": [
                {"in_teleop": False, "time": 146, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 147, "action_type": "auto_intake_spike_2"},
                {"in_teleop": False, "time": 148, "action_type": "score_amp"},
                {"in_teleop": False, "time": 149, "action_type": "auto_intake_spike_1"},
                {"in_teleop": False, "time": 150, "action_type": "score_speaker"},
            ][::-1],
            "match_numbers_played": [],
            "path_number": 2,
            "num_matches_ran": 2,
        },
        {
            # 1678, 1
            "match_number": 43,
            "team_number": "1678",
            "start_position": "2",
            "has_preload": True,
            "score_1": "speaker",
            "intake_position_1": "spike_1",
            "score_2": "amp",
            "intake_position_2": "spike_2",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "leave": True,
            "auto_timeline": [
                {"in_teleop": False, "time": 146, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 147, "action_type": "auto_intake_spike_2"},
                {"in_teleop": False, "time": 148, "action_type": "score_amp"},
                {"in_teleop": False, "time": 149, "action_type": "auto_intake_spike_1"},
                {"in_teleop": False, "time": 150, "action_type": "score_speaker"},
            ][::-1],
            "match_numbers_played": [],
            "path_number": 2,
            "num_matches_ran": 2,
        },
        {
            # 4414, 1
            "match_number": 44,
            "team_number": "4414",
            "start_position": "3",
            "has_preload": True,
            "score_1": "speaker",
            "intake_position_1": "spike_1",
            "score_2": "speaker",
            "intake_position_2": "spike_2",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "leave": True,
            "auto_timeline": [
                {"in_teleop": False, "time": 146, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 147, "action_type": "auto_intake_spike_2"},
                {"in_teleop": False, "time": 148, "action_type": "score_amp"},
                {"in_teleop": False, "time": 149, "action_type": "auto_intake_spike_1"},
                {"in_teleop": False, "time": 150, "action_type": "score_speaker"},
            ][::-1],
            "match_numbers_played": [],
            "path_number": 1,
            "num_matches_ran": 1,
        },
        {
            # 254, 2
            "match_number": 45,
            "team_number": "254",
            "start_position": "1",
            "has_preload": True,
            "score_1": "speaker",
            "intake_position_1": "spike_1",
            "score_2": "amp",
            "intake_position_2": "spike_2",
            "score_3": "fail",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "leave": True,
            "auto_timeline": [
                {"in_teleop": False, "time": 146, "action_type": "score_fail"},
                {"in_teleop": False, "time": 147, "action_type": "auto_intake_spike_2"},
                {"in_teleop": False, "time": 148, "action_type": "score_amp"},
                {"in_teleop": False, "time": 149, "action_type": "auto_intake_spike_1"},
                {"in_teleop": False, "time": 150, "action_type": "score_speaker"},
            ][::-1],
            "match_numbers_played": [],
            "path_number": 2,
            "num_matches_ran": 2,
        },
        {
            # 1678, 2
            "match_number": 46,
            "team_number": "1678",
            "start_position": "2",
            "has_preload": True,
            "score_1": "fail",
            "intake_position_1": "spike_1",
            "score_2": "amp",
            "intake_position_2": "spike_2",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "leave": True,
            "auto_timeline": [
                {"in_teleop": False, "time": 146, "action_type": "score_speaker"},
                {"in_teleop": False, "time": 147, "action_type": "auto_intake_spike_2"},
                {"in_teleop": False, "time": 148, "action_type": "score_amp"},
                {"in_teleop": False, "time": 149, "action_type": "auto_intake_spike_1"},
                {"in_teleop": False, "time": 150, "action_type": "score_fail"},
            ][::-1],
            "match_numbers_played": [],
            "path_number": 2,
            "num_matches_ran": 2,
        },
    ]

    expected_group_auto_paths = [
        {
            # 254, 1
            "path_number": 1,
            "match_numbers_played": [42],
            "num_matches_ran": 1,
            "team_number": "254",
            "start_position": "1",
            "has_preload": True,
            "leave": True,
            "intake_position_1": "spike_1",
            "intake_position_2": "spike_2",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "score_1": "speaker",
            "score_2": "amp",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "score_1_successes": 1,
            "score_2_successes": 1,
            "score_3_successes": 1,
            "score_4_successes": 0,
            "score_5_successes": 0,
            "score_6_successes": 0,
            "score_7_successes": 0,
            "score_8_successes": 0,
            "score_9_successes": 0,
        },
        {
            # 1678, 1
            "path_number": 1,
            "match_numbers_played": [43],
            "num_matches_ran": 1,
            "team_number": "1678",
            "start_position": "2",
            "has_preload": True,
            "leave": True,
            "intake_position_1": "spike_1",
            "intake_position_2": "spike_2",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "score_1": "speaker",
            "score_2": "amp",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "score_1_successes": 1,
            "score_2_successes": 1,
            "score_3_successes": 1,
            "score_4_successes": 0,
            "score_5_successes": 0,
            "score_6_successes": 0,
            "score_7_successes": 0,
            "score_8_successes": 0,
            "score_9_successes": 0,
        },
        {
            # 4414, 1
            "path_number": 1,
            "match_numbers_played": [44],
            "num_matches_ran": 1,
            "team_number": "4414",
            "start_position": "3",
            "has_preload": True,
            "leave": True,
            "intake_position_1": "spike_1",
            "intake_position_2": "spike_2",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "score_1": "speaker",
            "score_2": "speaker",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "score_1_successes": 1,
            "score_2_successes": 1,
            "score_3_successes": 1,
            "score_4_successes": 0,
            "score_5_successes": 0,
            "score_6_successes": 0,
            "score_7_successes": 0,
            "score_8_successes": 0,
            "score_9_successes": 0,
        },
        {
            # 254, 2
            "path_number": 2,
            "match_numbers_played": [45, 42],
            "num_matches_ran": 2,
            "team_number": "254",
            "start_position": "1",
            "has_preload": True,
            "leave": True,
            "intake_position_1": "spike_1",
            "intake_position_2": "spike_2",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "score_1": "speaker",
            "score_2": "amp",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "score_1_successes": 2,
            "score_2_successes": 2,
            "score_3_successes": 1,
            "score_4_successes": 0,
            "score_5_successes": 0,
            "score_6_successes": 0,
            "score_7_successes": 0,
            "score_8_successes": 0,
            "score_9_successes": 0,
        },
        {
            # 1678, 2
            "path_number": 2,
            "match_numbers_played": [46, 43],
            "num_matches_ran": 2,
            "team_number": "1678",
            "start_position": "2",
            "has_preload": True,
            "leave": True,
            "intake_position_1": "spike_1",
            "intake_position_2": "spike_2",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "score_1": "speaker",
            "score_2": "amp",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "score_1_successes": 1,
            "score_2_successes": 2,
            "score_3_successes": 2,
            "score_4_successes": 0,
            "score_5_successes": 0,
            "score_6_successes": 0,
            "score_7_successes": 0,
            "score_8_successes": 0,
            "score_9_successes": 0,
        },
    ]

    expected_auto_paths = [
        {
            # 4414, 1
            "path_number": 1,
            "match_numbers_played": [44],
            "num_matches_ran": 1,
            "team_number": "4414",
            "start_position": "3",
            "has_preload": True,
            "leave": True,
            "intake_position_1": "spike_1",
            "intake_position_2": "spike_2",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "score_1": "speaker",
            "score_2": "speaker",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "score_1_successes": 1,
            "score_2_successes": 1,
            "score_3_successes": 1,
            "score_4_successes": 0,
            "score_5_successes": 0,
            "score_6_successes": 0,
            "score_7_successes": 0,
            "score_8_successes": 0,
            "score_9_successes": 0,
        },
        {
            # 254, 2
            "path_number": 2,
            "match_numbers_played": [45, 42],
            "num_matches_ran": 2,
            "team_number": "254",
            "start_position": "1",
            "has_preload": True,
            "leave": True,
            "intake_position_1": "spike_1",
            "intake_position_2": "spike_2",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "score_1": "speaker",
            "score_2": "amp",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "score_1_successes": 2,
            "score_2_successes": 2,
            "score_3_successes": 1,
            "score_4_successes": 0,
            "score_5_successes": 0,
            "score_6_successes": 0,
            "score_7_successes": 0,
            "score_8_successes": 0,
            "score_9_successes": 0,
        },
        {
            # 1678, 2
            "path_number": 2,
            "match_numbers_played": [46, 43],
            "num_matches_ran": 2,
            "team_number": "1678",
            "start_position": "2",
            "has_preload": True,
            "leave": True,
            "intake_position_1": "spike_1",
            "intake_position_2": "spike_2",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "score_1": "speaker",
            "score_2": "amp",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "score_1_successes": 1,
            "score_2_successes": 2,
            "score_3_successes": 2,
            "score_4_successes": 0,
            "score_5_successes": 0,
            "score_6_successes": 0,
            "score_7_successes": 0,
            "score_8_successes": 0,
            "score_9_successes": 0,
        },
    ]

    expected_auto_path = [
        {
            "path_number": 1,
            "match_numbers_played": [42],
            "num_matches_ran": 1,
            "team_number": "254",
            "start_position": "1",
            "has_preload": True,
            "leave": True,
            "intake_position_1": "spike_1",
            "intake_position_2": "spike_2",
            "intake_position_3": "spike_3",
            "intake_position_4": "none",
            "intake_position_5": "none",
            "intake_position_6": "none",
            "intake_position_7": "none",
            "intake_position_8": "none",
            "score_1": "speaker",
            "score_2": "amp",
            "score_3": "speaker",
            "score_4": "none",
            "score_5": "none",
            "score_6": "none",
            "score_7": "none",
            "score_8": "none",
            "score_9": "none",
            "score_1_successes": 1,
            "score_2_successes": 1,
            "score_3_successes": 1,
            "score_4_successes": 0,
            "score_5_successes": 0,
            "score_6_successes": 0,
            "score_7_successes": 0,
            "score_8_successes": 0,
            "score_9_successes": 0,
        }
    ]

    @mock.patch.object(
        base_calculations.BaseCalculations, "get_teams_list", return_value=["1678", "4414", "254"]
    )
    def setup_method(self, method, get_teams_list_dummy):
        with mock.patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = Server()
        self.test_calculator = auto_paths.AutoPathCalc(self.test_server)
        # Insert test data into database for testing
        self.test_server.db.insert_documents("auto_pim", self.auto_pims)
        self.test_server.db.insert_documents("obj_team", self.obj_teams)

    def test___init__(self):
        assert self.test_calculator.server == self.test_server
        assert self.test_calculator.watched_collections == [
            "auto_pim",
        ]

    def test_group_auto_paths(self):
        # self.test_server.db.delete_data("auto_paths")
        # 254, 1
        assert (
            self.test_calculator.group_auto_paths(self.auto_pims[0], [])
            == self.expected_group_auto_paths[0]
        )
        self.test_server.db.insert_documents("auto_paths", self.expected_group_auto_paths[0])

        # 1678, 1
        assert (
            self.test_calculator.group_auto_paths(self.auto_pims[1], [])
            == self.expected_group_auto_paths[1]
        )
        self.test_server.db.insert_documents("auto_paths", self.expected_group_auto_paths[1])

        # 4414, 1
        assert (
            self.test_calculator.group_auto_paths(self.auto_pims[2], [])
            == self.expected_group_auto_paths[2]
        )
        self.test_server.db.insert_documents("auto_paths", self.expected_group_auto_paths[2])

        # 254, 2
        assert (
            self.test_calculator.group_auto_paths(self.auto_pims[3], [])
            == self.expected_group_auto_paths[3]
        )
        self.test_server.db.delete_data("auto_paths", {"team_number": "254"})
        self.test_server.db.insert_documents("auto_paths", self.expected_group_auto_paths[3])

        # 1678, 2
        assert (
            self.test_calculator.group_auto_paths(self.auto_pims[4], [])
            == self.expected_group_auto_paths[4]
        )
        self.test_server.db.delete_data("auto_paths", {"team_number": "1678"})
        self.test_server.db.insert_documents("auto_paths", self.expected_group_auto_paths[4])

    def test_calculate_auto_paths(self):
        calculated_auto_paths = self.test_calculator.calculate_auto_paths(
            [{"match_number": 42, "team_number": "254"}]
        )
        assert len(calculated_auto_paths) == 1
        assert len(self.expected_auto_path) == 1
        assert calculated_auto_paths[0] == self.expected_auto_path[0]

    def test_run(self):
        # Delete any data that is already in the database collections
        self.test_server.db.delete_data("auto_paths")
        self.test_server.db.delete_data("auto_pim")
        self.test_server.db.delete_data("obj_team")
        # Insert test data for the run function
        self.test_server.db.insert_documents("auto_pim", self.auto_pims)
        self.test_server.db.insert_documents("obj_team", self.obj_teams)

        self.test_calculator.run()
        result = self.test_server.db.find("auto_paths")

        for document in result:
            del document["_id"]

        assert result == self.expected_auto_paths

        obj_teams_result = self.test_server.db.find("obj_team")

        for obj_team_document in obj_teams_result:
            del obj_team_document["_id"]

        assert obj_teams_result == self.expected_obj_teams

        pim_result = self.test_server.db.find("auto_pim")

        for pim_document in pim_result:
            del pim_document["_id"]

        assert pim_result == self.expected_auto_pims
