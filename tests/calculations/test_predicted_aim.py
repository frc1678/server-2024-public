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
                "predicted_score": 280.83333,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
            },
            {
                "match_number": 1,
                "alliance_color_is_red": False,
                "has_actual_data": True,
                "actual_score": 278,
                "actual_rp1": 1.0,
                "actual_rp2": 1.0,
                "won_match": False,
                "predicted_score": 279.33333,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
            },
            {
                "match_number": 3,
                "alliance_color_is_red": True,
                "has_actual_data": False,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "predicted_score": 279.33333,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
            },
            {
                "match_number": 3,
                "alliance_color_is_red": False,
                "has_actual_data": False,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "predicted_score": 280.83333,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
            },
        ]
        self.expected_playoffs_updates = [
            {
                "alliance_num": 1,
                "picks": ["1678", "1533", "7229"],
                "predicted_score": 280.83333,
                "predicted_auto_score": 61.2,
                "predicted_tele_score": 219.63333,
                "predicted_grid_score": 250.3,
                "predicted_charge_score": 22.0,
            },
            {
                "alliance_num": 9,
                "picks": ["1678", "1533", "7229"],
                "predicted_score": 280.83333,
                "predicted_auto_score": 61.2,
                "predicted_tele_score": 219.63333,
                "predicted_grid_score": 250.3,
                "predicted_charge_score": 22.0,
            },
            {
                "alliance_num": 17,
                "picks": ["1678", "1533", "7229"],
                "predicted_score": 280.83333,
                "predicted_auto_score": 61.2,
                "predicted_tele_score": 219.63333,
                "predicted_grid_score": 250.3,
                "predicted_charge_score": 22.0,
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
                "predicted_score": 280.83333,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
                "win_chance": 0.96789,
            },
            {
                "match_number": 1,
                "alliance_color_is_red": False,
                "has_actual_data": True,
                "actual_score": 278,
                "actual_rp1": 1.0,
                "actual_rp2": 1.0,
                "won_match": False,
                "predicted_score": 279.33333,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
                "win_chance": 1 - 0.96789,
            },
            {
                "match_number": 3,
                "alliance_color_is_red": True,
                "has_actual_data": False,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "predicted_score": 279.33333,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
                "win_chance": 1 - 0.96789,
            },
            {
                "match_number": 3,
                "alliance_color_is_red": False,
                "has_actual_data": False,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "predicted_score": 280.83333,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
                "win_chance": 0.96789,
            },
        ]
        self.expected_playoffs_alliances = [
            {"alliance_num": 1, "picks": ["1678", "1533", "7229"]},
            {"alliance_num": 9, "picks": ["1678", "1533", "7229"]},
            {"alliance_num": 17, "picks": ["1678", "1533", "7229"]},
        ]
        self.full_predicted_values = predicted_aim.PredictedAimScores(
            auto_dock_successes=0.5,
            auto_engage_successes=0.5,
            tele_engage_successes=1.5,
            tele_dock_successes=0.5,
            link=5,
        )
        self.blank_predicted_values = predicted_aim.PredictedAimScores()
        self.obj_team = [
            {
                "team_number": "1678",
                "matches_played": 5,
                "auto_avg_cube_low": 1.0,
                "auto_avg_cone_low": 2.5,
                "auto_avg_cube_mid": 4.5,
                "auto_avg_cone_mid": 3.5,
                "auto_avg_cube_high": 7.5,
                "auto_avg_cone_high": 6.0,
                "auto_avg_cube_total": 13.0,
                "auto_avg_cone_total": 12.0,
                "tele_avg_cube_low": 3.3,
                "tele_avg_cone_low": 2.3,
                "tele_avg_cube_mid": 3.5,
                "tele_avg_cone_mid": 2.5,
                "tele_avg_cube_high": 2.2,
                "tele_avg_cone_high": 4.3,
                "tele_avg_cube_total": 9.0,
                "tele_avg_cone_total": 8.1,
                "auto_charge_attempts": 1,
                "auto_dock_successes": 1,
                "auto_dock_percent_success": 1.0,
                "auto_dock_only_percent_success": 1.0,
                "auto_engage_successes": 0,
                "auto_engage_percent_success": 0.0,
                "tele_charge_attempts": 2,
                "tele_dock_successes": 1,
                "tele_dock_percent_success": 0.5,
                "tele_dock_only_percent_success": 0.5,
                "tele_engage_successes": 1,
                "tele_engage_percent_success": 0.5,
                "tele_park_successes": 0,
                "tele_park_percent_success": 0.0,
            },
            {
                "team_number": "1533",
                "matches_played": 5,
                "auto_avg_cube_low": 1.1,
                "auto_avg_cone_low": 2.6,
                "auto_avg_cube_mid": 4.6,
                "auto_avg_cone_mid": 3.6,
                "auto_avg_cube_high": 7.6,
                "auto_avg_cone_high": 6.1,
                "auto_avg_cube_total": 13.3,
                "auto_avg_cone_total": 12.3,
                "tele_avg_cube_low": 3.4,
                "tele_avg_cone_low": 2.4,
                "tele_avg_cube_mid": 3.6,
                "tele_avg_cone_mid": 2.6,
                "tele_avg_cube_high": 2.3,
                "tele_avg_cone_high": 4.4,
                "tele_avg_cube_total": 9.3,
                "tele_avg_cone_total": 8.4,
                "auto_charge_attempts": 1,
                "auto_dock_successes": 0,
                "auto_dock_percent_success": 0.0,
                "auto_dock_only_percent_success": 0.0,
                "auto_engage_successes": 1,
                "auto_engage_percent_success": 1.0,
                "tele_charge_attempts": 2,
                "tele_dock_successes": 0,
                "tele_dock_percent_success": 0.0,
                "tele_dock_only_percent_success": 0.0,
                "tele_engage_successes": 1,
                "tele_engage_percent_success": 0.5,
                "tele_park_successes": 1,
                "tele_park_percent_success": 0.5,
            },
            {
                "team_number": "7229",
                "matches_played": 5,
                "auto_avg_cube_low": 1.2,
                "auto_avg_cone_low": 2.7,
                "auto_avg_cube_mid": 4.7,
                "auto_avg_cone_mid": 3.7,
                "auto_avg_cube_high": 7.7,
                "auto_avg_cone_high": 6.2,
                "auto_avg_cube_total": 13.6,
                "auto_avg_cone_total": 12.6,
                "tele_avg_cube_low": 3.5,
                "tele_avg_cone_low": 2.5,
                "tele_avg_cube_mid": 3.7,
                "tele_avg_cone_mid": 2.7,
                "tele_avg_cube_high": 2.4,
                "tele_avg_cone_high": 4.5,
                "tele_avg_cube_total": 9.6,
                "tele_avg_cone_total": 8.7,
                "auto_charge_attempts": 2,
                "auto_dock_successes": 1,
                "auto_dock_percent_success": 0.5,
                "auto_dock_only_percent_success": 0.5,
                "auto_engage_successes": 1,
                "auto_engage_percent_success": 0.5,
                "tele_charge_attempts": 2,
                "tele_dock_successes": 1,
                "tele_dock_percent_success": 0.5,
                "tele_dock_only_percent_success": 0.5,
                "tele_engage_successes": 0,
                "tele_engage_percent_success": 0.0,
                "tele_park_successes": 1,
                "tele_park_percent_success": 0.5,
            },
            {
                "team_number": "2468",
                "matches_played": 5,
                "auto_avg_cube_low": 1.1,
                "auto_avg_cone_low": 2.7,
                "auto_avg_cube_mid": 4.6,
                "auto_avg_cone_mid": 3.7,
                "auto_avg_cube_high": 7.6,
                "auto_avg_cone_high": 6.2,
                "auto_avg_cube_total": 13.3,
                "auto_avg_cone_total": 12.6,
                "tele_avg_cube_low": 3.4,
                "tele_avg_cone_low": 2.5,
                "tele_avg_cube_mid": 3.6,
                "tele_avg_cone_mid": 2.7,
                "tele_avg_cube_high": 2.3,
                "tele_avg_cone_high": 4.5,
                "tele_avg_cube_total": 9.3,
                "tele_avg_cone_total": 8.7,
                "auto_charge_attempts": 1,
                "auto_dock_successes": 0,
                "auto_dock_percent_success": 0.0,
                "auto_dock_only_percent_success": 0.0,
                "auto_engage_successes": 0,
                "auto_engage_percent_success": 0.0,
                "tele_charge_attempts": 2,
                "tele_dock_successes": 0,
                "tele_dock_percent_success": 0.0,
                "tele_dock_only_percent_success": 0.0,
                "tele_engage_successes": 0,
                "tele_engage_percent_success": 0.0,
                "tele_park_successes": 1,
                "tele_park_percent_success": 0.5,
            },
            {
                "team_number": "1000",
                "matches_played": 5,
                "auto_avg_cube_low": 0.0,
                "auto_avg_cone_low": 0.0,
                "auto_avg_cube_mid": 0.0,
                "auto_avg_cone_mid": 0.0,
                "auto_avg_cube_high": 0.0,
                "auto_avg_cone_high": 0.0,
                "auto_avg_cube_total": 0.0,
                "auto_avg_cone_total": 0.0,
                "tele_avg_cube_low": 0.0,
                "tele_avg_cone_low": 0.0,
                "tele_avg_cube_mid": 0.0,
                "tele_avg_cone_mid": 0.0,
                "tele_avg_cube_high": 0.0,
                "tele_avg_cone_high": 0.0,
                "tele_avg_cube_total": 0.0,
                "tele_avg_cone_total": 0.0,
                "auto_charge_attempts": 0,
                "auto_dock_successes": 0,
                "auto_dock_percent_success": 0.0,
                "auto_dock_only_percent_success": 0.0,
                "auto_engage_successes": 0,
                "auto_engage_percent_success": 0.0,
                "tele_charge_attempts": 0,
                "tele_dock_successes": 0,
                "tele_dock_percent_success": 0.0,
                "tele_dock_only_percent_success": 0.0,
                "tele_engage_successes": 0,
                "tele_engage_percent_success": 0.0,
                "tele_park_successes": 0,
                "tele_park_percent_success": 0.0,
            },
        ]
        self.tba_team = [
            {
                "team_number": "1678",
                "mobility_successes": 5,
            },
            {
                "team_number": "1533",
                "mobility_successes": 4,
            },
            {
                "team_number": "7229",
                "mobility_successes": 3,
            },
            {
                "team_number": "2468",
                "mobility_successes": 2,
            },
            {
                "team_number": "1000",
                "mobility_successes": 1,
            },
        ]
        self.tba_match_data = [
            {
                "match_number": 1,
                "comp_level": "qm",
                "score_breakdown": {
                    "blue": {
                        "activationBonusAchieved": True,
                        "sustainabilityBonusAchieved": True,
                        "totalPoints": 278,
                    },
                    "red": {
                        "activationBonusAchieved": False,
                        "sustainabilityBonusAchieved": True,
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
                        "activationBonusAchieved": True,
                        "sustainabilityBonusAchieved": True,
                        "totalPoints": 300,
                    },
                    "red": {
                        "activationBonusAchieved": True,
                        "sustainabilityBonusAchieved": True,
                        "totalPoints": 400,
                    },
                },
                "post_result_time": 182,
                "winning_alliance": "red",
            },
            {
                "match_number": 3,
                "comp_level": "qm",
                "score_breakdown": {},
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

    def test_calculate_predicted_link_score(self):
        """Test if the number of links is calculated correctly"""
        self.test_calc.calculate_predicted_grid_score(self.blank_predicted_values, self.obj_team[4])
        self.test_calc.calculate_predicted_link_score(self.blank_predicted_values, self.obj_team)
        assert near(self.blank_predicted_values.link, 0)

        self.test_calc.calculate_predicted_grid_score(self.blank_predicted_values, self.obj_team[1])
        self.test_calc.calculate_predicted_grid_score(self.blank_predicted_values, self.obj_team[2])
        self.test_calc.calculate_predicted_link_score(self.blank_predicted_values, self.obj_team)
        assert near(self.blank_predicted_values.link, 9)

    def test_calculate_predicted_grid_score(self):
        """Test if the grid obj_team values are added to the total predicted_values correctly"""
        self.test_calc.calculate_predicted_grid_score(self.blank_predicted_values, self.obj_team[0])
        assert near(self.blank_predicted_values.auto_gamepieces_low, 3.5)
        assert near(self.blank_predicted_values.auto_cube_mid, 4.5)
        assert near(self.blank_predicted_values.auto_cone_mid, 3.5)
        assert near(self.blank_predicted_values.auto_cube_high, 7.5)
        assert near(self.blank_predicted_values.auto_cone_high, 6.0)
        assert near(self.blank_predicted_values.tele_gamepieces_low, 5.6)
        assert near(self.blank_predicted_values.tele_cube_mid, 3.5)
        assert near(self.blank_predicted_values.tele_cone_mid, 2.5)
        assert near(self.blank_predicted_values.tele_cube_high, 2.2)
        assert near(self.blank_predicted_values.tele_cone_high, 4.3)

        self.test_calc.calculate_predicted_grid_score(self.blank_predicted_values, self.obj_team[1])
        assert near(self.blank_predicted_values.auto_gamepieces_low, 7.2)
        assert near(self.blank_predicted_values.auto_cube_mid, 9.1)
        assert near(self.blank_predicted_values.auto_cone_mid, 7.1)
        assert near(self.blank_predicted_values.auto_cube_high, 15.1)
        assert near(self.blank_predicted_values.auto_cone_high, 12.1)
        assert near(self.blank_predicted_values.tele_gamepieces_low, 11.4)
        assert near(self.blank_predicted_values.tele_cube_mid, 7.1)
        assert near(self.blank_predicted_values.tele_cone_mid, 5.1)
        assert near(self.blank_predicted_values.tele_cube_high, 4.5)
        assert near(self.blank_predicted_values.tele_cone_high, 8.7)

        self.test_calc.calculate_predicted_grid_score(self.blank_predicted_values, self.obj_team[2])
        assert near(self.blank_predicted_values.auto_gamepieces_low, 11.1)
        assert near(self.blank_predicted_values.auto_cube_mid, 13.8)
        assert near(self.blank_predicted_values.auto_cone_mid, 10.8)
        assert near(self.blank_predicted_values.auto_cube_high, 22.8)
        assert near(self.blank_predicted_values.auto_cone_high, 18.3)
        assert near(self.blank_predicted_values.tele_gamepieces_low, 17.4)
        assert near(self.blank_predicted_values.tele_cube_mid, 10.8)
        assert near(self.blank_predicted_values.tele_cone_mid, 7.8)
        assert near(self.blank_predicted_values.tele_cube_high, 6.9)
        assert near(self.blank_predicted_values.tele_cone_high, 13.2)

    def test_calculate_predicted_alliance_grid(self):
        """Check that the final predicted grid is made possible (i.e. no more than 6 high cones)"""
        for team in self.obj_team[:3]:
            self.test_calc.calculate_predicted_grid_score(self.blank_predicted_values, team)
        self.test_calc.calculate_predicted_alliance_grid(self.blank_predicted_values)
        assert near(self.blank_predicted_values.auto_cone_high, 6)
        assert near(self.blank_predicted_values.auto_cone_mid, 0)
        assert near(self.blank_predicted_values.auto_cube_high, 1)
        assert near(self.blank_predicted_values.auto_cube_mid, 0)
        assert near(self.blank_predicted_values.auto_gamepieces_low, 0)
        assert near(self.blank_predicted_values.tele_cone_high, 0)
        assert near(self.blank_predicted_values.tele_cone_mid, 6)
        assert near(self.blank_predicted_values.tele_cube_high, 2)
        assert near(self.blank_predicted_values.tele_cube_mid, 3)
        assert near(self.blank_predicted_values.tele_gamepieces_low, 9)
        assert near(self.blank_predicted_values.supercharge, 36.1)

    def test_calculate_predicted_charge_success_rate(self):
        """Test that the predicted charge success rates are calculated correctly each time a team is added"""
        self.test_calc.calculate_predicted_charge_success_rate(
            self.blank_predicted_values, self.obj_team[0]
        )
        assert near(self.blank_predicted_values.auto_dock_successes, 1)
        assert near(self.blank_predicted_values.auto_engage_successes, 0)
        assert near(self.blank_predicted_values.tele_dock_successes, 0.5)
        assert near(self.blank_predicted_values.tele_engage_successes, 0.5)
        assert near(self.blank_predicted_values.tele_park_successes, 0)

        self.test_calc.calculate_predicted_charge_success_rate(
            self.blank_predicted_values, self.obj_team[1]
        )
        assert near(self.blank_predicted_values.auto_dock_successes, 0)
        assert near(self.blank_predicted_values.auto_engage_successes, 1)
        assert near(self.blank_predicted_values.tele_dock_successes, 0.5)
        assert near(self.blank_predicted_values.tele_engage_successes, 1)
        assert near(self.blank_predicted_values.tele_park_successes, 0.5)

        self.test_calc.calculate_predicted_charge_success_rate(
            self.blank_predicted_values, self.obj_team[2]
        )
        assert near(self.blank_predicted_values.auto_dock_successes, 0)
        assert near(self.blank_predicted_values.auto_engage_successes, 1)
        assert near(self.blank_predicted_values.tele_dock_successes, 1)
        assert near(self.blank_predicted_values.tele_engage_successes, 1)
        assert near(self.blank_predicted_values.tele_park_successes, 1)

    def test_calculate_predicted_alliance_score(self):
        """Test the total predicted_score is correct"""
        assert near(
            self.test_calc.calculate_predicted_alliance_score(
                self.blank_predicted_values,
                self.obj_team,
                self.tba_team,
                ["1678", "1533", "7229"],
            ),
            280.83333,
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

    def test_calculate_predicted_link_rp(self):
        """Test that the chance of getting the link rp is calculated correctly"""
        assert self.test_calc.calculate_predicted_link_rp(self.blank_predicted_values) == 0
        assert self.test_calc.calculate_predicted_link_rp(self.full_predicted_values) == 0.75

    def test_calculate_predicted_charge_rp(self):
        """Thest that the chance of getting the charge rp is calculated correctly"""
        assert (
            self.test_calc.calculate_predicted_charge_rp(
                self.blank_predicted_values, self.obj_team, ["1000", "1000", "1000"]
            )
            == 0
        )
        assert (
            self.test_calc.calculate_predicted_charge_rp(
                self.full_predicted_values, self.obj_team, ["1678", "1533", "7229"]
            )
            == 0.25
        )

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
