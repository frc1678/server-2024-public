import tba_comp_export_csv
import warnings
from data_transfer import tba_communicator
from unittest.mock import *
import pyfakefs
from pyfakefs.fake_filesystem_unittest import fake_os
from pyfakefs.fake_filesystem_unittest import Patcher


def mock_tba_request(api_url):
    if api_url == "event/2023cada":
        return {
            "address": "164 Orchard Park Dr, Davis, CA 95616, USA",
            "city": "Davis",
            "country": "USA",
            "district": None,
            "division_keys": [],
            "end_date": "2023-03-26",
            "event_code": "cada",
            "event_type": 0,
            "event_type_string": "Regional",
            "first_event_code": "cada",
            "first_event_id": None,
            "gmaps_place_id": "ChIJ_U9p9QAphYARItEorYXUibY",
            "gmaps_url": "https://maps.google.com/?cid=13153277857313116450",
            "key": "2023cada",
            "lat": 38.54117419999999,
            "lng": -121.7621451,
            "location_name": "The Colleges at La Rue Apartments",
            "name": "Sacramento Regional",
            "parent_event_key": None,
            "playoff_type": 10,
            "playoff_type_string": "Double Elimination Bracket (8 Alliances)",
            "postal_code": "95616",
            "short_name": "Sacramento",
            "start_date": "2023-03-23",
            "state_prov": "CA",
            "timezone": "America/Los_Angeles",
            "webcasts": [
                {"channel": "firstinspires3", "type": "twitch"},
                {"channel": "firstinspires4", "type": "twitch"},
            ],
            "website": "https://cafirst.org/frc/sacramento/",
            "week": 3,
            "year": 2023,
        }
    if api_url == "event/2023cada/alliances":
        return [
            {
                "declines": [],
                "name": "Alliance 1",
                "picks": ["frc254", "frc1678", "frc3189"],
                "status": {
                    "current_level_record": {"losses": 0, "ties": 0, "wins": 2},
                    "double_elim_round": "Finals",
                    "level": "f",
                    "playoff_type": 10,
                    "record": {"losses": 0, "ties": 0, "wins": 5},
                    "status": "won",
                },
            }
        ]
    if api_url == "event/2023cada/insights":
        return {"playoff": {"average_points_auto": 30}, "qual": {"average_points_auto": 25}}
    if api_url == "event/2023cada/oprs":
        return {"ccwms": {"frc1678": 99}, "dprs": {"frc1678": 99}, "oprs": {"frc1678": 99}}
    if api_url == "event/2023cada/predictions":
        return {
            "match_prediction_stats": {
                "playoff": {
                    "brier_scores": {"win_loss": 0.5},
                    "err_mean": 20,
                    "err_var": 200,
                    "wl_accuracy": 50,
                    "wl_accuracy_75": 100.0,
                },
                "qual": {
                    "brier_scores": {"win_loss": 0.5},
                    "err_mean": 20,
                    "err_var": 200,
                    "wl_accuracy": 50,
                    "wl_accuracy_75": 100.0,
                },
            },
            "match_predictions": {
                "playoff": {
                    "2023cadaf1m1": {
                        "blue": {"test_predicted_match_stat": 69},
                        "red": {"test_predicted_match_stat": 42},
                        "winning_alliance": "blue",
                    }
                },
                "qual": {
                    "2023cadaqm1": {
                        "blue": {"test_predicted_match_stat": 69},
                        "red": {"test_predicted_match_stat": 42},
                        "winning_alliance": "blue",
                    }
                },
            },
            "ranking_predictions": [
                ["frc254", [1, 1, 1, 1, 37.0, 37, 37]],
                ["frc1678", [2, 2, 2, 2, 37.0, 37, 37]],
            ],
            "stat_mean_vars": {
                "playoff": {
                    "test_match_stat": {
                        "mean": {"frc254": 6, "frc1678": 9},
                        "var": {"frc254": 42, "frc1678": 42},
                    }
                },
                "qual": {
                    "test_match_stat": {
                        "mean": {"frc254": 6, "frc1678": 9},
                        "var": {"frc254": 42, "frc1678": 42},
                    }
                },
            },
        }
    if api_url == "event/2023cada/rankings":
        return {
            "extra_stats_info": [{"name": "Total Ranking Points", "precision": 0}],
            "rankings": [
                {
                    "dq": 0,
                    "extra_stats": [37],
                    "matches_played": 10,
                    "qual_average": None,
                    "rank": 1,
                    "record": {"losses": 1, "ties": 0, "wins": 9},
                    "sort_orders": [3.7, 129.2, 29.8, 33.6, 0.0, 0.0],
                    "team_key": "frc254",
                },
            ],
            "sort_order_info": [{"name": "Ranking Score", "precision": 2}],
        }
    if api_url == "event/2023cada/district_points":
        return {
            "points": {
                "frc1678": {
                    "alliance_points": 16,
                    "award_points": 5,
                    "elim_points": 30,
                    "qual_points": 21,
                    "total": 72,
                }
            },
            "tiebreakers": {
                "frc1678": {"highest_qual_scores": [159, 149, 145], "qual_wins": 0},
            },
        }
    if api_url == "event/2023cada/teams":
        return [{"key": "frc1678", "team_number": 1678}, {"key": "frc254", "team_number": 254}]
    if api_url == "event/2023cada/matches":
        return [
            {
                "actual_time": 10,
                "alliances": {
                    "blue": {"score": 999, "team_keys": ["frc1678", "frc8761", "frc1687"]},
                    "red": {"score": 998, "team_keys": ["frc254", "frc452", "frc245"]},
                },
                "key": "2023cadaf1m1",
            }
        ]
    if api_url == "event/2023cada/awards":
        return [
            {
                "award_type": 1,
                "event_key": "2023cada",
                "name": "Regional Winners",
                "recipient_list": [
                    {"team_key": "frc254"},
                    {"team_key": "frc1678"},
                    {"team_key": "frc3189"},
                ],
                "year": 2023,
            }
        ]
    return None


def test_pull_comp_data():
    expected_output = {
        "event_info": {
            "address": "164 Orchard Park Dr, Davis, CA 95616, USA",
            "city": "Davis",
            "country": "USA",
            "district": None,
            "division_keys": [],
            "end_date": "2023-03-26",
            "event_code": "cada",
            "event_type": 0,
            "event_type_string": "Regional",
            "first_event_code": "cada",
            "first_event_id": None,
            "gmaps_place_id": "ChIJ_U9p9QAphYARItEorYXUibY",
            "gmaps_url": "https://maps.google.com/?cid=13153277857313116450",
            "key": "2023cada",
            "lat": 38.54117419999999,
            "lng": -121.7621451,
            "location_name": "The Colleges at La Rue Apartments",
            "name": "Sacramento Regional",
            "parent_event_key": None,
            "playoff_type": 10,
            "playoff_type_string": "Double Elimination Bracket (8 Alliances)",
            "postal_code": "95616",
            "short_name": "Sacramento",
            "start_date": "2023-03-23",
            "state_prov": "CA",
            "timezone": "America/Los_Angeles",
            "webcasts": [
                {"channel": "firstinspires3", "type": "twitch"},
                {"channel": "firstinspires4", "type": "twitch"},
            ],
            "website": "https://cafirst.org/frc/sacramento/",
            "week": 3,
            "year": 2023,
        },
        "alliances": [
            {
                "declines": [],
                "name": "Alliance 1",
                "picks": ["frc254", "frc1678", "frc3189"],
                "status.current_level_record.losses": 0,
                "status.current_level_record.ties": 0,
                "status.current_level_record.wins": 2,
                "status.double_elim_round": "Finals",
                "status.level": "f",
                "status.playoff_type": 10,
                "status.record.losses": 0,
                "status.record.ties": 0,
                "status.record.wins": 5,
                "status.status": "won",
            }
        ],
        "insights": {"playoff": {"average_points_auto": 30}, "qual": {"average_points_auto": 25}},
        "oprs": {"ccwms": {"frc1678": 99}, "dprs": {"frc1678": 99}, "oprs": {"frc1678": 99}},
        "predictions.match_prediction_stats": {
            "playoff": {
                "brier_scores": {"win_loss": 0.5},
                "err_mean": 20,
                "err_var": 200,
                "wl_accuracy": 50,
                "wl_accuracy_75": 100.0,
            },
            "qual": {
                "brier_scores": {"win_loss": 0.5},
                "err_mean": 20,
                "err_var": 200,
                "wl_accuracy": 50,
                "wl_accuracy_75": 100.0,
            },
        },
        "predictions.match_predictions.playoff": {
            "2023cadaf1m1": {
                "blue": {"test_predicted_match_stat": 69},
                "red": {"test_predicted_match_stat": 42},
                "winning_alliance": "blue",
            }
        },
        "predictions.match_predictions.qual": {
            "2023cadaqm1": {
                "blue": {"test_predicted_match_stat": 69},
                "red": {"test_predicted_match_stat": 42},
                "winning_alliance": "blue",
            }
        },
        "predictions.stat_mean_vars.playoff": {
            "test_match_stat": {"frc254": {"mean": 6, "var": 42}, "frc1678": {"mean": 9, "var": 42}}
        },
        "predictions.stat_mean_vars.qual": {
            "test_match_stat": {"frc254": {"mean": 6, "var": 42}, "frc1678": {"mean": 9, "var": 42}}
        },
        "predictions.ranking_predictions": [
            {"team_key": "frc254", "predictions": [1, 1, 1, 1, 37.0, 37, 37]},
            {"team_key": "frc1678", "predictions": [2, 2, 2, 2, 37.0, 37, 37]},
        ],
        "rankings.extra_stats_info": [{"name": "Total Ranking Points", "precision": 0}],
        "rankings.rankings": [
            {
                "dq": 0,
                "extra_stats": [37],
                "matches_played": 10,
                "qual_average": None,
                "rank": 1,
                "record.losses": 1,
                "record.ties": 0,
                "record.wins": 9,
                "sort_orders": [3.7, 129.2, 29.8, 33.6, 0.0, 0.0],
                "team_key": "frc254",
            },
        ],
        "rankings.sort_order_info": [{"name": "Ranking Score", "precision": 2}],
        "district_points.points": {
            "frc1678": {
                "alliance_points": 16,
                "award_points": 5,
                "elim_points": 30,
                "qual_points": 21,
                "total": 72,
            }
        },
        "district_points.tiebreakers": {
            "frc1678": {"highest_qual_scores": [159, 149, 145], "qual_wins": 0},
        },
        "teams": [{"key": "frc1678", "team_number": 1678}, {"key": "frc254", "team_number": 254}],
        "matches": [
            {
                "actual_time": 10,
                "alliances.blue.score": 999,
                "alliances.blue.team_keys": ["frc1678", "frc8761", "frc1687"],
                "alliances.red.score": 998,
                "alliances.red.team_keys": ["frc254", "frc452", "frc245"],
                "key": "2023cadaf1m1",
            }
        ],
        "awards": [
            {
                "award_type": 1,
                "event_key": "2023cada",
                "name": "Regional Winners",
                "recipient_list": ["frc254", "frc1678", "frc3189"],
                "year": 2023,
            }
        ],
    }
    real_tba_request = tba_communicator.tba_request
    tba_communicator.tba_request = MagicMock(side_effect=mock_tba_request)
    assert tba_comp_export_csv.pull_comp_data("2023cada") == expected_output
    tba_communicator.tba_request = real_tba_request


def test_export_csv():
    real_tba_request = tba_communicator.tba_request
    tba_communicator.tba_request = MagicMock(side_effect=mock_tba_request)
    expected_csv = ""
    expected_csv += "EVENT INFO\naddress,city,country,district,division_keys,end_date,event_code,event_type,event_type_string,first_event_code,first_event_id,gmaps_place_id,gmaps_url,key,lat,lng,location_name,name,parent_event_key,playoff_type,playoff_type_string,postal_code,short_name,start_date,state_prov,timezone,webcasts,website,week,year\n\"164 Orchard Park Dr, Davis, CA 95616, USA\",Davis,USA,,[],2023-03-26,cada,0,Regional,cada,,ChIJ_U9p9QAphYARItEorYXUibY,https://maps.google.com/?cid=13153277857313116450,2023cada,38.54117419999999,-121.7621451,The Colleges at La Rue Apartments,Sacramento Regional,,10,Double Elimination Bracket (8 Alliances),95616,Sacramento,2023-03-23,CA,America/Los_Angeles,\"[{'channel': 'firstinspires3', 'type': 'twitch'}, {'channel': 'firstinspires4', 'type': 'twitch'}]\",https://cafirst.org/frc/sacramento/,3,2023"
    expected_csv += "\nALLIANCES\nname,declines,picks,status.current_level_record.losses,status.current_level_record.ties,status.current_level_record.wins,status.double_elim_round,status.level,status.playoff_type,status.record.losses,status.record.ties,status.record.wins,status.status\nAlliance 1,[],\"['frc254', 'frc1678', 'frc3189']\",0,0,2,Finals,f,10,0,0,5,won"
    expected_csv += "\nINSIGHTS\n,average_points_auto\nplayoff,30\nqual,25"
    expected_csv += "\nOPRs\n,ccwms,dprs,oprs\nfrc1678,99,99,99"
    expected_csv += "\nMATCH PREDICTION STATS\n,brier_scores,err_mean,err_var,wl_accuracy,wl_accuracy_75\nplayoff,{'win_loss': 0.5},20,200,50,100.0\nqual,{'win_loss': 0.5},20,200,50,100.0"
    expected_csv += "\nMATCH PREDICTIONS (PLAYOFF)\n,blue,red,winning_alliance\n2023cadaf1m1,{'test_predicted_match_stat': 69},{'test_predicted_match_stat': 42},blue"
    expected_csv += "\nMATCH PREDICTIONS (QUAL)\n,blue,red,winning_alliance\n2023cadaqm1,{'test_predicted_match_stat': 69},{'test_predicted_match_stat': 42},blue"
    expected_csv += "\nPREDICTED STAT MEANS, VARS (PLAYOFF)\n,test_match_stat\nfrc254,\"{'mean': 6, 'var': 42}\"\nfrc1678,\"{'mean': 9, 'var': 42}\""
    expected_csv += "\nPREDICTED STAT MEANS, VARS (QUAL)\n,test_match_stat\nfrc254,\"{'mean': 6, 'var': 42}\"\nfrc1678,\"{'mean': 9, 'var': 42}\""
    expected_csv += '\nPREDICTED RANKINGS\nteam_key,predictions\nfrc254,"[1, 1, 1, 1, 37.0, 37, 37]"\nfrc1678,"[2, 2, 2, 2, 37.0, 37, 37]"'
    expected_csv += "\nRANKING EXTRA STATS INFO\nname,precision\nTotal Ranking Points,0"
    expected_csv += '\nFINAL/CURRENT RANKINGS\nrank,dq,extra_stats,matches_played,qual_average,sort_orders,team_key,record.losses,record.ties,record.wins\n1,0,[37],10,,"[3.7, 129.2, 29.8, 33.6, 0.0, 0.0]",frc254,1,0,9'
    expected_csv += "\nRANKING SORT ORDER INFO\nname,precision\nRanking Score,2"
    expected_csv += "\nDISTRICT POINTS (POINTS)\n,alliance_points,award_points,elim_points,qual_points,total\nfrc1678,16,5,30,21,72"
    expected_csv += '\nDISTRICT POINTS (TIEBREAKERS)\n,highest_qual_scores,qual_wins\nfrc1678,"[159, 149, 145]",0'
    expected_csv += "\nTEAMS\nteam_number,key\n1678,frc1678\n254,frc254"
    expected_csv += "\nMATCHES\nkey,actual_time,alliances.blue.score,alliances.blue.team_keys,alliances.red.score,alliances.red.team_keys\n2023cadaf1m1,10,999,\"['frc1678', 'frc8761', 'frc1687']\",998,\"['frc254', 'frc452', 'frc245']\""
    expected_csv += "\nAWARDS\nname,award_type,event_key,recipient_list,year\nRegional Winners,1,2023cada,\"['frc254', 'frc1678', 'frc3189']\",2023\n"
    with Patcher() as patcher:
        tba_comp_export_csv.export_csv("2023cada", "tba_data_2023cada.csv")
        with open("tba_data_2023cada.csv", "r") as test_output:
            assert test_output.read() == expected_csv
    tba_communicator.tba_request = real_tba_request
