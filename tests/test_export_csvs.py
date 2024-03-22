from data_transfer import database
import utils
import export_csvs
import json

from unittest import mock
import pytest

import shutil

from server import Server


DATABASE = database.Database()


TEST_TIM_DATA = [
    {
        "confidence_rating": 1,
        "team_number": "2",
        "match_number": 3,
        "auto_cube_low": 8,
        "auto_cube_mid": 3,
        "auto_cube_high": 7,
        "auto_cone_low": 1,
        "auto_cone_mid": 9,
        "auto_cone_high": 8,
        "auto_charge_attempt": 1,
    },
    {
        "confidence_rating": 5,
        "team_number": "1690",
        "match_number": 2,
        "auto_cube_low": 3,
        "auto_cube_mid": 4,
        "auto_cube_high": 3,
        "auto_cone_low": 6,
        "auto_cone_mid": 3,
        "auto_cone_high": 8,
        "auto_charge_attempt": 4,
    },
]

TEST_TBA_DATA = [
    {
        "actual_time": 1678061442,
        "alliances": {
            "blue": {
                "dq_team_keys": [],
                "score": 148,
                "surrogate_team_keys": [],
                "team_keys": ["frc4414", "frc1678", "frc696"],
            },
            "red": {
                "dq_team_keys": [],
                "score": 148,
                "surrogate_team_keys": [],
                "team_keys": ["frc4481", "frc3859", "frc6036"],
            },
        },
        "comp_level": "f",
        "event_key": "2023caph",
        "key": "2023caph_f1m1",
        "match_number": 1,
        "post_result_time": 1678061640,
        "predicted_time": 1678061466,
        "score_breakdown": {
            "blue": {
                "activationBonusAchieved": False,
                "adjustPoints": 0,
                "autoBridgeState": "Level",
                "autoChargeStationPoints": 12,
                "autoChargeStationRobot1": "None",
                "autoChargeStationRobot2": "Docked",
                "autoChargeStationRobot3": "None",
                "autoCommunity": {
                    "B": ["None", "None", "None", "None", "None", "None", "None", "None", "None"],
                    "M": ["None", "None", "None", "None", "None", "None", "None", "None", "None"],
                    "T": ["Cone", "None", "None", "None", "None", "None", "None", "None", "Cone"],
                },
                "autoDocked": True,
                "autoGamePieceCount": 2,
                "autoGamePiecePoints": 12,
                "autoMobilityPoints": 6,
                "autoPoints": 30,
                "coopGamePieceCount": 7,
                "coopertitionCriteriaMet": False,
                "endGameBridgeState": "Level",
                "endGameChargeStationPoints": 20,
                "endGameChargeStationRobot1": "Docked",
                "endGameChargeStationRobot2": "Park",
                "endGameChargeStationRobot3": "Docked",
                "endGameParkPoints": 2,
                "foulCount": 2,
                "foulPoints": 5,
                "linkPoints": 30,
                "links": [
                    {"nodes": [2, 3, 4], "row": "Bottom"},
                    {"nodes": [5, 6, 7], "row": "Bottom"},
                    {"nodes": [5, 6, 7], "row": "Mid"},
                    {"nodes": [0, 1, 2], "row": "Top"},
                    {"nodes": [3, 4, 5], "row": "Top"},
                    {"nodes": [6, 7, 8], "row": "Top"},
                ],
                "mobilityRobot1": "Yes",
                "mobilityRobot2": "Yes",
                "mobilityRobot3": "No",
                "rp": 0,
                "sustainabilityBonusAchieved": False,
                "techFoulCount": 0,
                "teleopCommunity": {
                    "B": ["Cone", "None", "Cube", "Cube", "Cube", "Cone", "Cube", "Cube", "None"],
                    "M": ["None", "None", "None", "None", "None", "Cone", "Cone", "Cube", "Cone"],
                    "T": ["Cone", "Cube", "Cone", "Cone", "Cube", "Cone", "Cone", "Cube", "Cone"],
                },
                "teleopGamePieceCount": 20,
                "teleopGamePiecePoints": 61,
                "teleopPoints": 83,
                "totalChargeStationPoints": 32,
                "totalPoints": 148,
            },
            "red": {
                "activationBonusAchieved": False,
                "adjustPoints": 0,
                "autoBridgeState": "Level",
                "autoChargeStationPoints": 12,
                "autoChargeStationRobot1": "None",
                "autoChargeStationRobot2": "None",
                "autoChargeStationRobot3": "Docked",
                "autoCommunity": {
                    "B": ["None", "None", "None", "Cube", "None", "None", "None", "None", "None"],
                    "M": ["None", "Cube", "None", "None", "None", "None", "None", "None", "None"],
                    "T": ["None", "Cube", "None", "None", "None", "None", "None", "None", "Cone"],
                },
                "autoDocked": True,
                "autoGamePieceCount": 4,
                "autoGamePiecePoints": 19,
                "autoMobilityPoints": 6,
                "autoPoints": 37,
                "coopGamePieceCount": 6,
                "coopertitionCriteriaMet": False,
                "endGameBridgeState": "Level",
                "endGameChargeStationPoints": 30,
                "endGameChargeStationRobot1": "Docked",
                "endGameChargeStationRobot2": "Docked",
                "endGameChargeStationRobot3": "Docked",
                "endGameParkPoints": 0,
                "foulCount": 1,
                "foulPoints": 10,
                "linkPoints": 20,
                "links": [
                    {"nodes": [6, 7, 8], "row": "Mid"},
                    {"nodes": [0, 1, 2], "row": "Top"},
                    {"nodes": [3, 4, 5], "row": "Top"},
                    {"nodes": [6, 7, 8], "row": "Top"},
                ],
                "mobilityRobot1": "Yes",
                "mobilityRobot2": "No",
                "mobilityRobot3": "Yes",
                "rp": 0,
                "sustainabilityBonusAchieved": False,
                "techFoulCount": 0,
                "teleopCommunity": {
                    "B": ["None", "Cube", "None", "Cube", "Cube", "None", "None", "None", "None"],
                    "M": ["None", "Cube", "None", "None", "Cube", "None", "Cone", "Cube", "Cone"],
                    "T": ["Cone", "Cube", "Cone", "Cone", "Cube", "Cone", "Cone", "Cube", "Cone"],
                },
                "teleopGamePieceCount": 17,
                "teleopGamePiecePoints": 51,
                "teleopPoints": 81,
                "totalChargeStationPoints": 42,
                "totalPoints": 148,
            },
        },
        "set_number": 1,
        "time": 1678059480,
        "videos": [{"key": "vtZSDhk9Czs", "type": "youtube"}],
        "winning_alliance": "",
    },
    {
        "actual_time": 1678062765,
        "alliances": {
            "blue": {
                "dq_team_keys": [],
                "score": 129,
                "surrogate_team_keys": [],
                "team_keys": ["frc4414", "frc1678", "frc696"],
            },
            "red": {
                "dq_team_keys": [],
                "score": 145,
                "surrogate_team_keys": [],
                "team_keys": ["frc4481", "frc3859", "frc6036"],
            },
        },
        "comp_level": "f",
        "event_key": "2023caph",
        "key": "2023caph_f1m2",
        "match_number": 2,
        "post_result_time": 1678063010,
        "predicted_time": 1678062792,
        "score_breakdown": {
            "blue": {
                "activationBonusAchieved": False,
                "adjustPoints": 0,
                "autoBridgeState": "Level",
                "autoChargeStationPoints": 12,
                "autoChargeStationRobot1": "None",
                "autoChargeStationRobot2": "Docked",
                "autoChargeStationRobot3": "None",
                "autoCommunity": {
                    "B": ["None", "None", "None", "None", "None", "None", "None", "None", "None"],
                    "M": ["None", "None", "None", "None", "None", "None", "None", "None", "None"],
                    "T": ["Cone", "None", "None", "None", "None", "None", "Cone", "None", "Cone"],
                },
                "autoDocked": True,
                "autoGamePieceCount": 3,
                "autoGamePiecePoints": 18,
                "autoMobilityPoints": 6,
                "autoPoints": 36,
                "coopGamePieceCount": 7,
                "coopertitionCriteriaMet": False,
                "endGameBridgeState": "NotLevel",
                "endGameChargeStationPoints": 12,
                "endGameChargeStationRobot1": "Docked",
                "endGameChargeStationRobot2": "None",
                "endGameChargeStationRobot3": "Docked",
                "endGameParkPoints": 0,
                "foulCount": 2,
                "foulPoints": 0,
                "linkPoints": 30,
                "links": [
                    {"nodes": [0, 1, 2], "row": "Bottom"},
                    {"nodes": [3, 4, 5], "row": "Bottom"},
                    {"nodes": [6, 7, 8], "row": "Bottom"},
                    {"nodes": [0, 1, 2], "row": "Top"},
                    {"nodes": [3, 4, 5], "row": "Top"},
                    {"nodes": [6, 7, 8], "row": "Top"},
                ],
                "mobilityRobot1": "Yes",
                "mobilityRobot2": "Yes",
                "mobilityRobot3": "No",
                "rp": 0,
                "sustainabilityBonusAchieved": False,
                "techFoulCount": 0,
                "teleopCommunity": {
                    "B": ["Cube", "Cone", "Cube", "Cone", "Cube", "Cube", "Cone", "Cube", "Cube"],
                    "M": ["None", "None", "None", "None", "None", "Cone", "None", "None", "None"],
                    "T": ["Cone", "Cube", "Cone", "Cone", "Cube", "Cone", "Cone", "Cube", "Cone"],
                },
                "teleopGamePieceCount": 19,
                "teleopGamePiecePoints": 51,
                "teleopPoints": 63,
                "totalChargeStationPoints": 24,
                "totalPoints": 129,
            },
            "red": {
                "activationBonusAchieved": False,
                "adjustPoints": 0,
                "autoBridgeState": "Level",
                "autoChargeStationPoints": 12,
                "autoChargeStationRobot1": "None",
                "autoChargeStationRobot2": "None",
                "autoChargeStationRobot3": "Docked",
                "autoCommunity": {
                    "B": ["None", "None", "None", "Cube", "None", "None", "None", "None", "None"],
                    "M": ["None", "Cube", "None", "None", "None", "None", "None", "None", "None"],
                    "T": ["None", "Cube", "None", "None", "None", "None", "None", "None", "Cone"],
                },
                "autoDocked": True,
                "autoGamePieceCount": 4,
                "autoGamePiecePoints": 19,
                "autoMobilityPoints": 6,
                "autoPoints": 37,
                "coopGamePieceCount": 5,
                "coopertitionCriteriaMet": False,
                "endGameBridgeState": "Level",
                "endGameChargeStationPoints": 30,
                "endGameChargeStationRobot1": "Docked",
                "endGameChargeStationRobot2": "Docked",
                "endGameChargeStationRobot3": "Docked",
                "endGameParkPoints": 0,
                "foulCount": 0,
                "foulPoints": 10,
                "linkPoints": 20,
                "links": [
                    {"nodes": [0, 1, 2], "row": "Mid"},
                    {"nodes": [0, 1, 2], "row": "Top"},
                    {"nodes": [3, 4, 5], "row": "Top"},
                    {"nodes": [6, 7, 8], "row": "Top"},
                ],
                "mobilityRobot1": "Yes",
                "mobilityRobot2": "No",
                "mobilityRobot3": "Yes",
                "rp": 0,
                "sustainabilityBonusAchieved": False,
                "techFoulCount": 0,
                "teleopCommunity": {
                    "B": ["None", "None", "None", "Cube", "None", "None", "Cone", "Cube", "None"],
                    "M": ["Cone", "Cube", "Cone", "None", "Cube", "None", "None", "None", "None"],
                    "T": ["Cone", "Cube", "Cone", "Cone", "Cube", "Cone", "Cone", "Cube", "Cone"],
                },
                "teleopGamePieceCount": 16,
                "teleopGamePiecePoints": 48,
                "teleopPoints": 78,
                "totalChargeStationPoints": 42,
                "totalPoints": 145,
            },
        },
        "set_number": 1,
        "time": 1678060680,
        "videos": [{"key": "0oWrmK1uUxU", "type": "youtube"}],
        "winning_alliance": "red",
    },
    {
        "actual_time": 1678064347,
        "alliances": {
            "blue": {
                "dq_team_keys": [],
                "score": 157,
                "surrogate_team_keys": [],
                "team_keys": ["frc4414", "frc1678", "frc696"],
            },
            "red": {
                "dq_team_keys": [],
                "score": 126,
                "surrogate_team_keys": [],
                "team_keys": ["frc4481", "frc3859", "frc6036"],
            },
        },
        "comp_level": "f",
        "event_key": "2023caph",
        "key": "2023caph_f1m3",
        "match_number": 3,
        "post_result_time": 1678064524,
        "predicted_time": 1678064351,
        "score_breakdown": {
            "blue": {
                "activationBonusAchieved": False,
                "adjustPoints": 0,
                "autoBridgeState": "Level",
                "autoChargeStationPoints": 12,
                "autoChargeStationRobot1": "None",
                "autoChargeStationRobot2": "Docked",
                "autoChargeStationRobot3": "None",
                "autoCommunity": {
                    "B": ["None", "None", "None", "None", "None", "None", "None", "None", "None"],
                    "M": ["None", "None", "None", "None", "None", "None", "None", "None", "None"],
                    "T": ["Cone", "None", "None", "None", "None", "None", "None", "None", "Cone"],
                },
                "autoDocked": True,
                "autoGamePieceCount": 2,
                "autoGamePiecePoints": 12,
                "autoMobilityPoints": 6,
                "autoPoints": 30,
                "coopGamePieceCount": 7,
                "coopertitionCriteriaMet": False,
                "endGameBridgeState": "Level",
                "endGameChargeStationPoints": 20,
                "endGameChargeStationRobot1": "Docked",
                "endGameChargeStationRobot2": "Park",
                "endGameChargeStationRobot3": "Docked",
                "endGameParkPoints": 2,
                "foulCount": 0,
                "foulPoints": 5,
                "linkPoints": 35,
                "links": [
                    {"nodes": [0, 1, 2], "row": "Bottom"},
                    {"nodes": [3, 4, 5], "row": "Bottom"},
                    {"nodes": [6, 7, 8], "row": "Bottom"},
                    {"nodes": [6, 7, 8], "row": "Mid"},
                    {"nodes": [0, 1, 2], "row": "Top"},
                    {"nodes": [3, 4, 5], "row": "Top"},
                    {"nodes": [6, 7, 8], "row": "Top"},
                ],
                "mobilityRobot1": "Yes",
                "mobilityRobot2": "Yes",
                "mobilityRobot3": "No",
                "rp": 0,
                "sustainabilityBonusAchieved": False,
                "techFoulCount": 0,
                "teleopCommunity": {
                    "B": ["Cone", "Cone", "Cube", "Cube", "Cube", "Cube", "Cube", "Cube", "Cube"],
                    "M": ["None", "None", "None", "None", "Cube", "None", "Cone", "Cube", "Cone"],
                    "T": ["Cone", "Cube", "Cone", "Cone", "Cube", "Cone", "Cone", "Cube", "Cone"],
                },
                "teleopGamePieceCount": 22,
                "teleopGamePiecePoints": 65,
                "teleopPoints": 87,
                "totalChargeStationPoints": 32,
                "totalPoints": 157,
            },
            "red": {
                "activationBonusAchieved": False,
                "adjustPoints": 0,
                "autoBridgeState": "Level",
                "autoChargeStationPoints": 12,
                "autoChargeStationRobot1": "None",
                "autoChargeStationRobot2": "None",
                "autoChargeStationRobot3": "Docked",
                "autoCommunity": {
                    "B": ["None", "None", "None", "Cube", "None", "None", "None", "None", "Cone"],
                    "M": ["None", "Cube", "None", "None", "None", "None", "None", "None", "None"],
                    "T": ["None", "Cube", "None", "None", "None", "None", "None", "None", "None"],
                },
                "autoDocked": True,
                "autoGamePieceCount": 4,
                "autoGamePiecePoints": 16,
                "autoMobilityPoints": 6,
                "autoPoints": 34,
                "coopGamePieceCount": 5,
                "coopertitionCriteriaMet": False,
                "endGameBridgeState": "Level",
                "endGameChargeStationPoints": 30,
                "endGameChargeStationRobot1": "Docked",
                "endGameChargeStationRobot2": "Docked",
                "endGameChargeStationRobot3": "Docked",
                "endGameParkPoints": 0,
                "foulCount": 1,
                "foulPoints": 0,
                "linkPoints": 15,
                "links": [
                    {"nodes": [0, 1, 2], "row": "Top"},
                    {"nodes": [3, 4, 5], "row": "Top"},
                    {"nodes": [6, 7, 8], "row": "Top"},
                ],
                "mobilityRobot1": "Yes",
                "mobilityRobot2": "No",
                "mobilityRobot3": "Yes",
                "rp": 0,
                "sustainabilityBonusAchieved": False,
                "techFoulCount": 0,
                "teleopCommunity": {
                    "B": ["Cone", "Cone", "None", "Cube", "None", "None", "None", "None", "Cone"],
                    "M": ["None", "Cube", "None", "None", "Cube", "None", "None", "None", "None"],
                    "T": ["Cone", "Cube", "Cone", "Cone", "Cube", "Cone", "Cone", "Cube", "Cone"],
                },
                "teleopGamePieceCount": 15,
                "teleopGamePiecePoints": 47,
                "teleopPoints": 77,
                "totalChargeStationPoints": 42,
                "totalPoints": 126,
            },
        },
        "set_number": 1,
        "time": 1678061880,
        "videos": [
            {"key": "Hir_mCID8i0", "type": "youtube"},
            {"key": "wjElPqqg9f4", "type": "youtube"},
        ],
        "winning_alliance": "blue",
    },
]

TEST_TBA_TIM = [
    {
        "match_number": 4,
        "team_number": "1678",
        "mobility": True,
    },
    {"match_number": 3, "team_number": "2", "mobility": False},
    {"match_number": 1, "team_number": "3", "mobility": False},
]

TEST_TBA_TEAM = [
    {"team_number": "78", "team_name": "gibbon ribbon", "foul_cc": 0.4393, "mobility_successes": 4},
    {"team_number": "2", "team_name": "fab nerds", "foul_cc": 3.4462, "mobility_successes": 8},
    {"team_number": "0", "team_name": "linux lovers", "foul_cc": 2.4052, "mobility_successes": 1},
]

TEST_SS_TIM = [
    {
        "team_number": "78",
        "match_number": 1,
        "username": "123",
        "played_defense": True,
        "coopertition": False,
        "defense_rating": 2,
        "notes": "bad",
        "broken_mechanism": True,
    },
    {
        "team_number": "2",
        "match_number": 2,
        "username": "456",
        "played_defense": True,
        "coopertition": True,
        "defense_rating": 2,
        "notes": "good",
        "broken_mechanism": False,
    },
    {
        "team_number": "0",
        "match_number": 2,
        "username": "789",
        "played_defense": False,
        "coopertition": False,
        "defense_rating": 2,
        "notes": "medium",
        "broken_mechanism": False,
    },
]

TEST_SS_TEAM = [
    {
        "team_number": "78",
        "username": 123,
        "auto_strategies": "nothing",
        "strengths": "nothing",
        "weaknesses": "everything",
        "can_go_under_stage": True,
        "can_intake_ground": False,
        "shoot_specific_area_only": "speaker",
        "avg_defense_rating": 3,
    },
    {
        "team_number": "2",
        "username": 456,
        "auto_strategies": "score in amp",
        "strengths": "trap",
        "weaknesses": "slow",
        "can_go_under_stage": True,
        "can_intake_ground": True,
        "shoot_specific_area_only": "all",
        "avg_defense_rating": 5,
    },
    {
        "team_number": "0",
        "username": 789,
        "auto_strategies": "ferry notes",
        "strengths": "fast",
        "weaknesses": "bad at shooting",
        "can_go_under_stage": False,
        "can_intake_ground": True,
        "shoot_specific_area_only": "amp",
        "avg_defense_rating": 4,
    },
]

TEST_RAW_OBJ_PIT = [
    {
        "team_number": "254",
        "drivetrain": "2",
        "drivetrain_motors": 1,
        "drivetrain_motor_type": "0",
        "has_vision": True,
        "has_communication_device": True,
        "weight": 5.8153,
        "length": 4.0599,
        "width": 3.7634,
    },
    {
        "team_number": "0",
        "drivetrain": "0",
        "drivetrain_motors": 8,
        "drivetrain_motor_type": "2",
        "has_vision": True,
        "has_communication_device": True,
        "weight": 0.6261,
        "length": 2.8623,
        "width": 1.0344,
    },
    {
        "team_number": "1",
        "drivetrain": "1",
        "drivetrain_motors": 3,
        "drivetrain_motor_type": "2",
        "has_vision": True,
        "has_communication_device": False,
        "weight": 5.1894,
        "length": 0.5501,
        "width": 6.5503,
    },
]

TEST_OBJ_TEAM = [
    {
        "team_number": "3947",
        "auto_avg_cone_high": 1.659,
        "auto_avg_cone_mid": 4.1833,
        "auto_avg_cone_low": 5.3567,
        "auto_avg_cone_total": 3.7173,
    },
    {
        "team_number": "1",
        "auto_avg_cone_high": 3.758,
        "auto_avg_cone_mid": 2.978,
        "auto_avg_cone_low": 6.1984,
        "auto_avg_cone_total": 0.6452,
    },
]

TEST_SUBJ_TEAM = [
    {
        "team_number": "0",
        "driver_field_awareness": 4.7762,
        "driver_quickness": 2.7329,
        "driver_ability": 1.5561,
        "test_driver_ability": 2.2446,
        "unadjusted_field_awareness": 6.8875,
        "unadjusted_quickness": 5.1464,
        "auto_pieces_start_position": [0, 0, 1, 2],
    },
    {
        "team_number": "3",
        "driver_field_awareness": 1.3817,
        "driver_quickness": 5.7287,
        "driver_ability": 4.6641,
        "test_driver_ability": 5.7414,
        "unadjusted_field_awareness": 6.0605,
        "unadjusted_quickness": 1.5379,
        "auto_pieces_start_position": [2, 2, 2, 2],
    },
    {
        "team_number": "4",
        "driver_field_awareness": 0.4113,
        "driver_quickness": 3.1528,
        "driver_ability": 2.9349,
        "test_driver_ability": 4.374,
        "unadjusted_field_awareness": 2.1501,
        "unadjusted_quickness": 4.6836,
        "auto_pieces_start_position": [1, 2, 0, 0],
    },
    {
        "team_number": "45",
        "driver_field_awareness": 3.5576,
        "driver_quickness": 4.7751,
        "driver_ability": 2.5079,
        "test_driver_ability": 6.9134,
        "unadjusted_field_awareness": 4.1487,
        "unadjusted_quickness": 6.9111,
        "auto_pieces_start_position": [0, 0, 0, 1],
    },
]

TEST_PICKABILITY = [
    {
        "team_number": "3",
        "first_pickability": 4.1853,
        "offensive_second_pickability": 5.4094,
        "defensive_second_pickability": 2.6118,
        "overall_second_pickability": 4.7381,
    },
    {
        "team_number": "1",
        "first_pickability": 2.9372,
        "offensive_second_pickability": 5.4891,
        "defensive_second_pickability": 6.2833,
        "overall_second_pickability": 2.0437,
    },
    {
        "team_number": "4",
        "first_pickability": 6.6783,
        "offensive_second_pickability": 4.9784,
        "defensive_second_pickability": 3.4455,
        "overall_second_pickability": 5.719,
    },
]


@pytest.fixture(autouse=True, scope="function")
def mock_team_list():
    with mock.patch.object(
        export_csvs.BaseExport, "get_teams_list", return_value=["0", "1", "2", "3"]
    ) as teams_list_mock:
        yield teams_list_mock


class TestBaseExport:
    def setup_method(self):
        self.base_class = export_csvs.BaseExport()
        self.collections = self.base_class.collections
        self.teams_list = self.base_class.teams_list

    def test_load_single_collection(self):
        for collection in ["obj_tim", "subj_pit"]:
            result = self.base_class.load_single_collection(collection)
            assert isinstance(result, list)
            if len(result) > 0:
                assert isinstance(result[0], dict)

    def test_get_data(self):
        cols = ["obj_tim", "subj_pit"]
        result = self.base_class.get_data(cols)
        assert isinstance(result, dict)
        for key in ["obj_tim", "subj_pit"]:
            assert key in result

    def test_create_name(self):
        for name in ["endow", "tba_export"]:
            result_name = self.base_class.create_name(name)
            assert isinstance(result_name, str)

    def test_get_teams_list(self):
        result = self.base_class.get_teams_list()
        assert isinstance(result, list)
        assert result == self.teams_list


@pytest.fixture(autouse=True, scope="function")
def mock_tba_data():
    with mock.patch.object(
        export_csvs.ExportTBA, "get_tba_data", return_value=TEST_TBA_DATA
    ) as tba_data_mock:
        yield tba_data_mock


class TestExportTBA:
    def setup_method(self):
        self.export_tba = export_csvs.ExportTBA()

    def test_get_tba_data(self):
        result = self.export_tba.get_tba_data()
        assert isinstance(result, list)
        for single in result:
            assert isinstance(single["alliances"], dict)
            assert "red" in single["alliances"]
            assert "blue" in single["alliances"]
            assert isinstance(single["alliances"]["red"]["team_keys"], list)
            assert len(single["alliances"]["red"]["team_keys"]) == 3
            assert isinstance(single["event_key"], str)

    def test_build_data(self):
        result = self.export_tba.build_data()
        assert isinstance(result, list)


class TestExportTIM:
    def setup_method(self):
        with mock.patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = Server()
        self.test_server.db.insert_documents("obj_tim", TEST_TIM_DATA)
        self.test_server.db.insert_documents("tba_tim", TEST_TBA_TIM)
        self.test_server.db.insert_documents("ss_tim", TEST_SS_TIM)
        self.export_tim = export_csvs.ExportTIM()

    def test_build_data(self):
        result = self.export_tim.build_data()
        assert (
            result
            == (  # List of headers, plus data for teams in matches. Team data not for teams 0, 1, 2, or 3 should be filtered out
                [
                    "team_number",
                    "match_number",
                    "auto_charge_attempt",
                    "auto_cone_high",
                    "auto_cone_low",
                    "auto_cone_mid",
                    "auto_cube_high",
                    "auto_cube_low",
                    "auto_cube_mid",
                    "broken_mechanism",
                    "confidence_rating",
                    "coopertition",
                    "defense_rating",
                    "mobility",
                    "notes",
                    "played_defense",
                    "username",
                ],
                {
                    ("0", 2): {
                        "broken_mechanism": False,
                        "coopertition": False,
                        "defense_rating": 2,
                        "match_number": 2,
                        "notes": "medium",
                        "played_defense": False,
                        "team_number": "0",
                        "username": "789",
                    },
                    ("2", 2): {
                        "broken_mechanism": False,
                        "coopertition": True,
                        "defense_rating": 2,
                        "match_number": 2,
                        "notes": "good",
                        "played_defense": True,
                        "team_number": "2",
                        "username": "456",
                    },
                    ("2", 3): {
                        "confidence_rating": 1,
                        "team_number": "2",
                        "match_number": 3,
                        "auto_cube_low": 8,
                        "auto_cube_mid": 3,
                        "auto_cube_high": 7,
                        "auto_cone_low": 1,
                        "auto_cone_mid": 9,
                        "auto_cone_high": 8,
                        "auto_charge_attempt": 1,
                        "mobility": False,
                    },
                    ("3", 1): {"match_number": 1, "team_number": "3", "mobility": False},
                },
            )
        )


class TestExportTeam:
    def setup_method(self):
        with mock.patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = Server()
        self.test_server.db.insert_documents("raw_obj_pit", TEST_RAW_OBJ_PIT)
        self.test_server.db.insert_documents("obj_team", TEST_OBJ_TEAM)
        self.test_server.db.insert_documents("subj_team", TEST_SUBJ_TEAM)
        self.test_server.db.insert_documents("tba_team", TEST_TBA_TEAM)
        self.test_server.db.insert_documents("pickability", TEST_PICKABILITY)
        self.test_server.db.insert_documents("pickability", TEST_SS_TEAM)
        self.export_team = export_csvs.ExportTeam()

    def test_build_data(self):
        result = self.export_team.build_data()
        assert result == (
            [
                "team_number",
                "auto_avg_cone_high",
                "auto_avg_cone_low",
                "auto_avg_cone_mid",
                "auto_avg_cone_total",
                "auto_pieces_start_position",
                "auto_strategies",
                "avg_defense_rating",
                "can_go_under_stage",
                "can_intake_ground",
                "defensive_second_pickability",
                "driver_ability",
                "driver_field_awareness",
                "driver_quickness",
                "drivetrain",
                "drivetrain_motor_type",
                "drivetrain_motors",
                "first_pickability",
                "foul_cc",
                "has_communication_device",
                "has_vision",
                "length",
                "mobility_successes",
                "offensive_second_pickability",
                "overall_second_pickability",
                "shoot_specific_area_only",
                "strengths",
                "team_name",
                "unadjusted_field_awareness",
                "unadjusted_quickness",
                "username",
                "weaknesses",
                "weight",
                "width",
            ],
            {
                "0": {
                    "team_number": "0",
                    "drivetrain": "0",
                    "drivetrain_motors": 8,
                    "drivetrain_motor_type": "2",
                    "has_vision": True,
                    "has_communication_device": True,
                    "weight": 0.6261,
                    "length": 2.8623,
                    "width": 1.0344,
                    "driver_field_awareness": 4.7762,
                    "driver_quickness": 2.7329,
                    "driver_ability": 1.5561,
                    "unadjusted_field_awareness": 6.8875,
                    "unadjusted_quickness": 5.1464,
                    "auto_pieces_start_position": [0, 0, 1, 2],
                    "auto_strategies": "ferry notes",
                    "avg_defense_rating": 4,
                    "can_go_under_stage": False,
                    "can_intake_ground": True,
                    "team_name": "linux lovers",
                    "foul_cc": 2.4052,
                    "mobility_successes": 1,
                    "shoot_specific_area_only": "amp",
                    "strengths": "fast",
                    "username": 789,
                    "weaknesses": "bad at shooting",
                },
                "1": {
                    "team_number": "1",
                    "drivetrain": "1",
                    "drivetrain_motors": 3,
                    "drivetrain_motor_type": "2",
                    "has_vision": True,
                    "has_communication_device": False,
                    "weight": 5.1894,
                    "length": 0.5501,
                    "width": 6.5503,
                    "auto_avg_cone_high": 3.758,
                    "auto_avg_cone_mid": 2.978,
                    "auto_avg_cone_low": 6.1984,
                    "auto_avg_cone_total": 0.6452,
                    "first_pickability": 2.9372,
                    "offensive_second_pickability": 5.4891,
                    "defensive_second_pickability": 6.2833,
                    "overall_second_pickability": 2.0437,
                },
                "3": {
                    "team_number": "3",
                    "driver_field_awareness": 1.3817,
                    "driver_quickness": 5.7287,
                    "driver_ability": 4.6641,
                    "unadjusted_field_awareness": 6.0605,
                    "unadjusted_quickness": 1.5379,
                    "auto_pieces_start_position": [2, 2, 2, 2],
                    "first_pickability": 4.1853,
                    "offensive_second_pickability": 5.4094,
                    "defensive_second_pickability": 2.6118,
                    "overall_second_pickability": 4.7381,
                },
                "2": {
                    "team_number": "2",
                    "team_name": "fab nerds",
                    "foul_cc": 3.4462,
                    "mobility_successes": 8,
                    "auto_strategies": "score in amp",
                    "avg_defense_rating": 5,
                    "can_go_under_stage": True,
                    "can_intake_ground": True,
                    "shoot_specific_area_only": "all",
                    "strengths": "trap",
                    "username": 456,
                    "weaknesses": "slow",
                },
            },
        )


class TestExportImagePaths:
    def setup_method(self):
        self.export_image_paths = export_csvs.ExportImagePaths()

    def test_get_dict_for_teams(self):
        result = self.export_image_paths.get_dict_for_teams()
        assert isinstance(result, dict)

    def test_get_image_paths(self):
        result = self.export_image_paths.get_image_paths()
        assert isinstance(result, dict)
