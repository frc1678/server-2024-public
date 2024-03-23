from calculations import predicted_team
import server

from unittest import mock


class TestPredictedTeamCalc:
    def setup_method(self, method):
        with mock.patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = server.Server()
        self.test_calc = predicted_team.PredictedTeamCalc(self.test_server)
        self.predicted_aim = [
            {
                "match_number": 1,
                "alliance_color_is_red": True,
                "predicted_rp1": 1.0,
                "predicted_rp2": 1.0,
                "predicted_score_constant": 60.4,
                "actual_score": 54,
                "actual_rp1": 1.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "has_actual_data": True,
            },
            {
                "match_number": 1,
                "alliance_color_is_red": False,
                "predicted_rp1": 0.0,
                "predicted_rp2": 0.0,
                "predicted_score_constant": 56.8,
                "actual_score": 59,
                "actual_rp1": 1.0,
                "actual_rp2": 1.0,
                "won_match": True,
                "has_actual_data": True,
            },
            {
                "match_number": 2,
                "alliance_color_is_red": True,
                "predicted_rp1": 0.0,
                "predicted_rp2": 1.0,
                "predicted_score_constant": 162.3,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "has_actual_data": False,
            },
            {
                "match_number": 2,
                "alliance_color_is_red": False,
                "predicted_rp1": 1.0,
                "predicted_rp2": 0.0,
                "predicted_score_constant": 100.2,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "has_actual_data": False,
            },
            {
                "match_number": 3,
                "alliance_color_is_red": True,
                "predicted_rp1": 1.0,
                "predicted_rp2": 1.0,
                "predicted_score_constant": 82.0,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "has_actual_data": False,
            },
            {
                "match_number": 3,
                "alliance_color_is_red": False,
                "predicted_rp1": 1.0,
                "predicted_rp2": 0.0,
                "predicted_score_constant": 90.5,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "has_actual_data": False,
            },
            {
                "match_number": 4,
                "alliance_color_is_red": False,
                "predicted_rp1": 1.0,
                "predicted_rp2": 0.0,
                "predicted_score_constant": 90.5,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "has_actual_data": False,
            },
        ]
        self.aim_list = [
            {
                "match_number": 1,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "7229"],
            },
            {
                "match_number": 1,
                "alliance_color": "B",
                "team_list": ["254", "971", "1323"],
            },
            {
                "match_number": 2,
                "alliance_color": "R",
                "team_list": ["2056", "1114", "7179"],
            },
            {
                "match_number": 2,
                "alliance_color": "B",
                "team_list": ["1678", "971", "7229"],
            },
            {
                "match_number": 3,
                "alliance_color": "R",
                "team_list": ["2056", "254", "1323"],
            },
            {
                "match_number": 3,
                "alliance_color": "B",
                "team_list": ["1533", "1114", "7179"],
            },
            {
                "match_number": 4,
                "alliance_color": "R",
                "team_list": ["4414", "1690", "973"],
            },
        ]
        self.ranking_data = {
            "rankings": [
                {
                    "extra_stats": [26],
                    "matches_played": 11,
                    "rank": 1,
                    "team_key": "frc1678",
                },
                {
                    "extra_stats": [25],
                    "matches_played": 11,
                    "rank": 2,
                    "team_key": "frc1533",
                },
                {
                    "extra_stats": [24],
                    "matches_played": 11,
                    "rank": 3,
                    "team_key": "frc7229",
                },
                {
                    "extra_stats": [23],
                    "matches_played": 11,
                    "rank": 4,
                    "team_key": "frc254",
                },
                {
                    "extra_stats": [22],
                    "matches_played": 11,
                    "rank": 5,
                    "team_key": "frc971",
                },
                {
                    "extra_stats": [21],
                    "matches_played": 11,
                    "rank": 6,
                    "team_key": "frc1323",
                },
                {
                    "extra_stats": [20],
                    "matches_played": 11,
                    "rank": 7,
                    "team_key": "frc2056",
                },
                {
                    "extra_stats": [19],
                    "matches_played": 11,
                    "rank": 8,
                    "team_key": "frc1114",
                },
                {
                    "extra_stats": [18],
                    "matches_played": 11,
                    "rank": 9,
                    "team_key": "frc7179",
                },
            ]
        }
        self.predicted_alliance_rps = {
            1: {"R": 1, "B": 4},
            2: {"R": 3, "B": 1},
            3: {"R": 2, "B": 3},
        }
        self.updates = [
            {"team_number": "1678", "predicted_rps": 2},
            {"team_number": "1533", "predicted_rps": 4},
            {"team_number": "7229", "predicted_rps": 2},
            {"team_number": "254", "predicted_rps": 6},
            {"team_number": "971", "predicted_rps": 5},
            {"team_number": "1323", "predicted_rps": 6},
            {"team_number": "2056", "predicted_rps": 5},
            {"team_number": "1114", "predicted_rps": 6},
            {"team_number": "7179", "predicted_rps": 6},
        ]
        self.expected_results = [
            {
                "team_number": "1678",
                "predicted_rps": 2.0,
                "matches_played": 11,
                "predicted_rank": 8,
                "current_rank": 1,
                "current_rps": 26,
                "current_avg_rps": 26 / 11,
            },
            {
                "team_number": "1533",
                "predicted_rps": 4.0,
                "matches_played": 11,
                "predicted_rank": 7,
                "current_rank": 2,
                "current_rps": 25,
                "current_avg_rps": 25 / 11,
            },
            {
                "team_number": "7229",
                "predicted_rps": 2.0,
                "matches_played": 11,
                "predicted_rank": 9,
                "current_rank": 3,
                "current_rps": 24,
                "current_avg_rps": 24 / 11,
            },
            {
                "team_number": "254",
                "predicted_rps": 6.0,
                "matches_played": 11,
                "predicted_rank": 1,
                "current_rank": 4,
                "current_rps": 23,
                "current_avg_rps": 23 / 11,
            },
            {
                "team_number": "971",
                "predicted_rps": 5.0,
                "matches_played": 11,
                "predicted_rank": 5,
                "current_rank": 5,
                "current_rps": 22,
                "current_avg_rps": 22 / 11,
            },
            {
                "team_number": "1323",
                "predicted_rps": 6.0,
                "matches_played": 11,
                "predicted_rank": 2,
                "current_rank": 6,
                "current_rps": 21,
                "current_avg_rps": 21 / 11,
            },
            {
                "team_number": "2056",
                "predicted_rps": 5.0,
                "matches_played": 11,
                "predicted_rank": 6,
                "current_rank": 7,
                "current_rps": 20,
                "current_avg_rps": 20 / 11,
            },
            {
                "team_number": "1114",
                "predicted_rps": 6.0,
                "matches_played": 11,
                "predicted_rank": 3,
                "current_rank": 8,
                "current_rps": 19,
                "current_avg_rps": 19 / 11,
            },
            {
                "team_number": "7179",
                "predicted_rps": 6.0,
                "matches_played": 11,
                "predicted_rank": 4,
                "current_rank": 9,
                "current_rps": 18,
                "current_avg_rps": 18 / 11,
            },
        ]
        self.teams = [
            "1678",
            "1533",
            "7229",
            "254",
            "971",
            "1323",
            "2056",
            "1114",
            "7179",
        ]

    def test_calculate_current_values(self):
        current_values = self.test_calc.calculate_current_values(
            self.ranking_data["rankings"], "1678"
        )
        assert current_values["current_rank"] == 1
        assert current_values["current_rps"] == 26
        assert current_values["current_avg_rps"] == 26 / 11

    def test_calculate_predicted_alliance_rps(self, caplog):
        predicted_alliance_rps = self.test_calc.calculate_predicted_alliance_rps(self.predicted_aim)

        assert ["Incomplete AIM data for Match 4"] == [
            rec.message for rec in caplog.records if rec.levelname == "WARNING"
        ]

        assert predicted_alliance_rps[1]["R"] == 1
        assert predicted_alliance_rps[1]["B"] == 4
        assert predicted_alliance_rps[2]["R"] == 3
        assert predicted_alliance_rps[2]["B"] == 1
        assert predicted_alliance_rps[3]["R"] == 2
        assert predicted_alliance_rps[3]["B"] == 3

    def test_predicted_team_rps(self, caplog):
        assert (
            self.test_calc.calculate_predicted_team_rps(
                "1678", self.aim_list, self.predicted_alliance_rps
            )
            == 2
        )
        assert (
            self.test_calc.calculate_predicted_team_rps(
                "1533", self.aim_list, self.predicted_alliance_rps
            )
            == 4
        )
        assert (
            self.test_calc.calculate_predicted_team_rps(
                "7229", self.aim_list, self.predicted_alliance_rps
            )
            == 2
        )
        assert (
            self.test_calc.calculate_predicted_team_rps(
                "254", self.aim_list, self.predicted_alliance_rps
            )
            == 6
        )
        assert (
            self.test_calc.calculate_predicted_team_rps(
                "971", self.aim_list, self.predicted_alliance_rps
            )
            == 5
        )
        assert (
            self.test_calc.calculate_predicted_team_rps(
                "1323", self.aim_list, self.predicted_alliance_rps
            )
            == 6
        )
        assert (
            self.test_calc.calculate_predicted_team_rps(
                "2056", self.aim_list, self.predicted_alliance_rps
            )
            == 5
        )
        assert (
            self.test_calc.calculate_predicted_team_rps(
                "1114", self.aim_list, self.predicted_alliance_rps
            )
            == 6
        )
        assert (
            self.test_calc.calculate_predicted_team_rps(
                "7179", self.aim_list, self.predicted_alliance_rps
            )
            == 6
        )
        # to test for catching errors and correct logging
        self.test_calc.calculate_predicted_team_rps(
            "4414", self.aim_list, self.predicted_alliance_rps
        )
        assert ["Missing predicted RPs for Match 4"] == [
            rec.message for rec in caplog.records if rec.levelname == "WARNING"
        ]

    def test_calculate_predicted_ranks(self):
        updates = self.test_calc.calculate_predicted_ranks(
            self.updates, self.aim_list, self.ranking_data["rankings"]
        )
        for update in updates:
            for result in self.expected_results:
                if update["team_number"] == result["team_number"]:
                    assert update["predicted_rank"] == result["predicted_rank"]

    def test_update_predicted_team(self):
        with mock.patch(
            "data_transfer.tba_communicator.tba_request", return_value=self.ranking_data
        ), mock.patch(
            "calculations.predicted_team.PredictedTeamCalc.get_aim_list",
            return_value=self.aim_list,
        ), mock.patch(
            "calculations.predicted_team.PredictedTeamCalc.get_teams_list",
            return_value=self.teams,
        ):
            assert self.test_calc.update_predicted_team(self.predicted_aim) == self.expected_results

    def test_run(self):
        self.test_server.db.insert_documents("predicted_aim", self.predicted_aim)
        with mock.patch(
            "data_transfer.tba_communicator.tba_request", return_value=self.ranking_data
        ), mock.patch(
            "calculations.predicted_team.PredictedTeamCalc.get_aim_list",
            return_value=self.aim_list,
        ), mock.patch(
            "calculations.predicted_team.PredictedTeamCalc.get_teams_list",
            return_value=self.teams,
        ):
            self.test_calc.run()
        result = self.test_server.db.find("predicted_team")
        assert len(result) == 9
        for document in result:
            del document["_id"]
            assert document in self.expected_results
            # Removes the matching expected result to protect against duplicates from the calculation
            self.expected_results.remove(document)
