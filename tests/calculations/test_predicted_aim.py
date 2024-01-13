from calculations import predicted_aim
from unittest.mock import patch
import server
import pytest
from utils import near


class TestPredictedAimCalc:
    def setup_method(self, method):
        with patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = server.Server()
        self.test_calc = predicted_aim.PredictedAimCalc(self.test_server)
        self.aims_list = [
            {
                "match_number": 1,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "7229"],
            },
            {
                "match_number": 1,
                "alliance_color": "B",
                "team_list": ["1678", "1533", "2468"],
            },
            {
                "match_number": 2,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "1690"],
            },
            {
                "match_number": 2,
                "alliance_color": "B",
                "team_list": ["254", "1323", "973"],
            },
            {
                "match_number": 3,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "2468"],
            },
            {
                "match_number": 3,
                "alliance_color": "B",
                "team_list": ["1678", "1533", "7229"],
            },
        ]
        self.filtered_aims_list = [
            {
                "match_number": 1,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "7229"],
            },
            {
                "match_number": 1,
                "alliance_color": "B",
                "team_list": ["1678", "1533", "2468"],
            },
            {
                "match_number": 3,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "2468"],
            },
            {
                "match_number": 3,
                "alliance_color": "B",
                "team_list": ["1678", "1533", "7229"],
            },
        ]
        self.expected_updates = [
            {
                "match_number": 1,
                "alliance_color_is_red": True,
                "has_actual_data": True,
                "actual_score": 320,
                "actual_rp1": 0.0,
                "actual_rp2": 1.0,
                "won_match": True,
                "predicted_score": 206.4,
                "team_numbers": ["1678", "1533", "7229"],
            },
            {
                "match_number": 1,
                "alliance_color_is_red": False,
                "has_actual_data": True,
                "actual_score": 278,
                "actual_rp1": 1.0,
                "actual_rp2": 1.0,
                "won_match": False,
                "predicted_score": 223.4,
                "team_numbers": ["1678", "1533", "2468"],
            },
            {
                "match_number": 3,
                "alliance_color_is_red": True,
                "has_actual_data": False,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "predicted_score": 223.4,
                "team_numbers": ["1678", "1533", "2468"],
            },
            {
                "match_number": 3,
                "alliance_color_is_red": False,
                "has_actual_data": False,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "predicted_score": 206.4,
                "team_numbers": ["1678", "1533", "7229"],
            },
        ]
        self.expected_playoffs_updates = [
            {
                "alliance_num": 1,
                "picks": ["1678", "1533", "7229"],
                "predicted_score": 206.4,
                "predicted_auto_score": 59.8,
                "predicted_tele_score": 146.6,
                "predicted_stage_score": None,
            },
            {
                "alliance_num": 9,
                "picks": ["1678", "1533", "7229"],
                "predicted_score": 206.4,
                "predicted_auto_score": 59.8,
                "predicted_tele_score": 146.6,
                "predicted_stage_score": None,
            },
            {
                "alliance_num": 17,
                "picks": ["1678", "1533", "7229"],
                "predicted_score": 206.4,
                "predicted_auto_score": 59.8,
                "predicted_tele_score": 146.6,
                "predicted_stage_score": None,
            },
        ]
        self.expected_results = [
            {
                "match_number": 1,
                "alliance_color_is_red": True,
                "has_actual_data": True,
                "actual_score": 320,
                "actual_rp1": 0.0,
                "actual_rp2": 1.0,
                "won_match": True,
                "predicted_score": 206.4,
                "win_chance": 0.99966,
                "team_numbers": ["1678", "1533", "7229"],
            },
            {
                "match_number": 1,
                "alliance_color_is_red": False,
                "has_actual_data": True,
                "actual_score": 278,
                "actual_rp1": 1.0,
                "actual_rp2": 1.0,
                "won_match": False,
                "predicted_score": 223.4,
                "win_chance": 0.00034,
                "team_numbers": ["1678", "1533", "2468"],
            },
            {
                "match_number": 3,
                "alliance_color_is_red": True,
                "has_actual_data": False,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "predicted_score": 223.4,
                "win_chance": 0.00034,
                "team_numbers": ["1678", "1533", "2468"],
            },
            {
                "match_number": 3,
                "alliance_color_is_red": False,
                "has_actual_data": False,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "predicted_score": 206.4,
                "win_chance": 0.99966,
                "team_numbers": ["1678", "1533", "7229"],
            },
        ]
        self.expected_playoffs_alliances = [
            {"alliance_num": 1, "picks": ["1678", "1533", "7229"]},
            {"alliance_num": 9, "picks": ["1678", "1533", "7229"]},
            {"alliance_num": 17, "picks": ["1678", "1533", "7229"]},
        ]
        self.full_predicted_values = predicted_aim.PredictedAimScores(
            tele_park_successes=1.5,
            tele_onstage_successes=0.5,
        )
        self.blank_predicted_values = predicted_aim.PredictedAimScores()
        self.obj_team = [
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
            {
                "team_number": "2468",
                "matches_played": 5,
                "auto_avg_speaker": 3.6,
                "auto_avg_amp": 1.4,
                "tele_avg_speaker": 2.4,
                "tele_avg_speaker_amped": 8.6,
                "tele_avg_amp": 2.2,
                "avg_trap": 0.6,
            },
            {
                "team_number": "1000",
                "matches_played": 5,
                "auto_avg_speaker": 0.0,
                "auto_avg_amp": 0.0,
                "tele_avg_speaker": 0.0,
                "tele_avg_speaker_amped": 0.0,
                "tele_avg_amp": 0.0,
                "avg_trap": 0.0,
            },
        ]
        self.tba_team = [
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
            {
                "team_number": "2468",
                "leave_successes": 2,
            },
            {
                "team_number": "1000",
                "leave_successes": 1,
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
                "picks": ["frc1678", "frc1533", "frc7229"],
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

    def test_calculate_predicted_stage_success_rate(self):
        pass

    def test_calculate_predicted_alliance_score(self):
        """Test the total predicted_score is correct"""
        assert near(
            self.test_calc.calculate_predicted_alliance_score(
                self.blank_predicted_values,
                self.obj_team,
                self.tba_team,
                ["1678", "1533", "7229"],
            ),
            206.40000,
        )
        # Make sure there are no errors with no data
        try:
            self.test_calc.calculate_predicted_alliance_score(
                self.blank_predicted_values,
                self.obj_team,
                self.tba_team,
                ["1000", "1000", "1000"],
            )
        except ZeroDivisionError as exc:
            assert False, f"calculate_predicted_alliance_score has a {exc}"

    def test_get_playoffs_alliances(self):
        with patch(
            "data_transfer.tba_communicator.tba_request", return_value=self.tba_playoffs_data
        ):
            assert self.test_calc.get_playoffs_alliances() == self.expected_playoffs_alliances

    def test_calculate_predicted_ensemble_rp(self):
        pass

    def test_calculate_predicted_melody_rp(self):
        pass

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
            playoff_update = self.test_calc.update_playoffs_alliances()
        assert playoff_update == self.expected_playoffs_updates
        # Make sure auto score + tele score = total score
        assert near(
            playoff_update[0]["predicted_auto_score"] + playoff_update[0]["predicted_tele_score"],
            playoff_update[0]["predicted_score"],
        )

    def test_calculate_predicted_win_chance(self):
        with patch("data_transfer.database.Database.find", return_value=self.expected_updates):
            assert self.test_calc.calculate_predicted_win_chance() == self.expected_results

    def test_get_predicted_win_chance(self):
        """Check that the function generated by the logistic regression makes sense"""
        match_list = list(range(1, 6))
        aims = [
            {
                "match_number": 1,
                "predicted_score": 10,
                "has_actual_data": True,
                "won_match": False,
            },
            {
                "match_number": 1,
                "predicted_score": 20,
                "has_actual_data": True,
                "won_match": True,
            },
            {
                "match_number": 2,
                "predicted_score": 14,
                "has_actual_data": True,
                "won_match": True,
            },
            {
                "match_number": 2,
                "predicted_score": 16,
                "has_actual_data": True,
                "won_match": False,
            },
            {
                "match_number": 3,
                "predicted_score": 13,
                "has_actual_data": True,
                "won_match": False,
            },
            {
                "match_number": 3,
                "predicted_score": 18,
                "has_actual_data": True,
                "won_match": True,
            },
            {
                "match_number": 4,
                "predicted_score": 12,
                "has_actual_data": True,
                "won_match": True,
            },
            {
                "match_number": 4,
                "predicted_score": 11,
                "has_actual_data": True,
                "won_match": False,
            },
            {
                "match_number": 5,
                "predicted_score": 1000,
                "has_actual_data": False,
            },
            {
                "match_number": 5,
                "predicted_score": 0,
                "has_actual_data": False,
            },
        ]
        predicted_win_chance = self.test_calc.get_predicted_win_chance(match_list, aims)
        # Bigger point difference => larger chance of winning
        assert predicted_win_chance(0) == 0.4634287128417273
        assert predicted_win_chance(3) == 0.7405684767137776
        assert predicted_win_chance(10) == 0.978924852564896

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
        assert len(result) == 4
        for document in result:
            del document["_id"]
            assert document in self.expected_results
            # Removes the matching expected result to protect against duplicates from the calculation
            self.expected_results.remove(document)
        result2 = self.test_server.db.find("predicted_alliances")
        assert len(result2) == 3
        for document in result2:
            del document["_id"]
            assert document in self.expected_playoffs_updates
            self.expected_playoffs_updates.remove(document)
