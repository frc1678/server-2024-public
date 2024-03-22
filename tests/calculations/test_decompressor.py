import datetime

import pytest
from unittest.mock import patch

import server
from calculations import decompressor


@pytest.mark.clouddb
class TestDecompressor:
    def setup_method(self, method):
        with patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = server.Server()
        self.test_decompressor = decompressor.Decompressor(self.test_server)

    def test___init__(self):
        assert self.test_decompressor.server == self.test_server
        assert self.test_decompressor.watched_collections == ["raw_qr"]

    def test_convert_data_type(self):
        # List of compressed names and decompressed names of enums
        action_type_dict = {
            "score_speaker": "AA",
            "score_amp": "AB",
            "start_incap_time": "AC",
            "end_incap_time": "AD",
            "auto_intake_spike_1": "AE",
            "auto_intake_spike_2": "AF",
            "auto_intake_spike_3": "AG",
            "auto_intake_center_1": "AH",
            "auto_intake_center_2": "AI",
            "auto_intake_center_3": "AJ",
            "auto_intake_center_4": "AK",
            "auto_intake_center_5": "AL",
            "intake_amp": "AM",
            "intake_poach": "AN",
            "intake_center": "AO",
            "intake_far": "AP",
            "score_amplify": "AQ",
            "drop": "AR",
            "ferry": "AS",
            "fail": "AT",
            "to_teleop": "AU",
            "to_endgame": "AV",
        }
        # Test a few values for each type to make sure they make sense
        assert 5 == self.test_decompressor.convert_data_type("5", "int")
        assert 6 == self.test_decompressor.convert_data_type(6.43, "int")
        assert 5.0 == self.test_decompressor.convert_data_type("5", "float")
        assert 6.32 == self.test_decompressor.convert_data_type("6.32", "float")
        assert 3.0 == self.test_decompressor.convert_data_type(3, "float")
        assert self.test_decompressor.convert_data_type("1", "bool")
        assert self.test_decompressor.convert_data_type("T", "bool")
        assert self.test_decompressor.convert_data_type("TRUE", "bool")
        assert not self.test_decompressor.convert_data_type("0", "bool")
        assert not self.test_decompressor.convert_data_type("F", "bool")
        assert not self.test_decompressor.convert_data_type("FALSE", "bool")
        assert "" == self.test_decompressor.convert_data_type("", "str")
        # Test all enums
        for decompressed, compressed in action_type_dict.items():
            assert decompressed == self.test_decompressor.convert_data_type(
                compressed, "Enum", name="action_type"
            )
        # Test error raising
        with pytest.raises(ValueError) as type_error:
            self.test_decompressor.convert_data_type("", "tuple")
        assert "Type tuple not recognized" in str(type_error.value)

    def test_get_decompressed_name(self):
        # Test for the that '$' returns '_separator' in all 3 sections that have it
        sections = ["generic_data", "objective_tim", "subjective_aim"]
        for section in sections:
            assert "_separator" == self.test_decompressor.get_decompressed_name("$", section)
        # Test for a name with a string and a name with a list from each section
        assert "_section_separator" == self.test_decompressor.get_decompressed_name(
            "%", "generic_data"
        )
        assert "timeline" == self.test_decompressor.get_decompressed_name("W", "objective_tim")
        assert "_start_character" == self.test_decompressor.get_decompressed_name(
            "+", "objective_tim"
        )
        assert "time" == self.test_decompressor.get_decompressed_name(3, "timeline")
        assert "_start_character" == self.test_decompressor.get_decompressed_name(
            "*", "subjective_aim"
        )
        assert "_team_separator" == self.test_decompressor.get_decompressed_name(
            "#", "subjective_aim"
        )
        assert "scout_id" == self.test_decompressor.get_decompressed_name("Y", "objective_tim")
        assert "start_position" == self.test_decompressor.get_decompressed_name(
            "X", "objective_tim"
        )
        assert "field_awareness_score" == self.test_decompressor.get_decompressed_name(
            "C", "subjective_aim"
        )
        assert "score_speaker" == self.test_decompressor.get_decompressed_name("AA", "action_type")
        assert "auto_intake_spike_1" == self.test_decompressor.get_decompressed_name(
            "AE", "action_type"
        )
        assert "has_preload" == self.test_decompressor.get_decompressed_name("V", "objective_tim")
        with pytest.raises(ValueError) as excinfo:
            self.test_decompressor.get_decompressed_name("#", "generic_data")
        assert "Retrieving Variable Name # from generic_data failed." in str(excinfo)

    def test_get_decompressed_type(self):
        # Test when there are two values in a list
        assert "int" == self.test_decompressor.get_decompressed_type(
            "schema_version", "generic_data"
        )
        # Test when list has more than two values
        assert ["list", "dict"] == self.test_decompressor.get_decompressed_type(
            "timeline", "objective_tim"
        )

    def test_decompress_data(self):
        # Test generic data
        assert {
            "schema_version": 7,
            "scout_name": "Name",
        } == self.test_decompressor.decompress_data(["A7", "EName"], "generic_data")
        # Test objective tim
        assert {"team_number": "1678"} == self.test_decompressor.decompress_data(
            ["Z1678"], "objective_tim"
        )
        # Test timeline decompression
        assert {
            "timeline": [{"action_type": "score_speaker", "time": 51, "in_teleop": False}]
        } == self.test_decompressor.decompress_data(["W051AA"], "objective_tim")
        # Test using list with internal separators
        assert {
            "quickness_score": 1,
            "field_awareness_score": 3,
        } == self.test_decompressor.decompress_data(["B1", "C3"], "subjective_aim")

    def test_decompress_generic_qr(self):
        # Test if the correct error is raised when the Schema version is incorrect
        with pytest.raises(LookupError) as version_error:
            self.test_decompressor.decompress_generic_qr("A250$")
        assert "does not match Server version" in str(version_error)
        # What decompress_generic_qr() should return
        expected_decompressed_data = {
            "schema_version": decompressor.Decompressor.SCHEMA["schema_file"][
                "version"
            ],  # read the current version of schema file
            "match_number": 34,
            "timestamp": 1230,
            "match_collection_version_number": "v1.3",
            "scout_name": "Name",
        }
        assert expected_decompressed_data == self.test_decompressor.decompress_generic_qr(
            f"A{decompressor.Decompressor.SCHEMA['schema_file']['version']}$B34$C1230$Dv1.3$EName"
        )

    def test_decompress_timeline(self):
        # Function should raise an error if the data isn't the right length
        with pytest.raises(ValueError) as excinfo:
            self.test_decompressor.decompress_timeline(["abcdefg"])
        assert "Invalid timeline -- Timeline length invalid: ['abcdefg']" in str(excinfo)
        # Test timeline decompression
        assert [
            {"time": 59, "action_type": "score_speaker", "in_teleop": False},
            {"time": 60, "action_type": "to_teleop", "in_teleop": True},
            {"time": 61, "action_type": "score_amp", "in_teleop": True},
        ] == self.test_decompressor.decompress_timeline("059AA060AU061AB")
        # Should return empty list if passed an empty string
        assert [] == self.test_decompressor.decompress_timeline("")

    def test_decompress_single_qr(self):
        # Expected decompressed objective qr
        expected_objective = [
            {
                "schema_version": decompressor.Decompressor.SCHEMA["schema_file"]["version"],
                "match_number": 34,
                "override": {},
                "timestamp": 1230,
                "match_collection_version_number": "v1.3",
                "scout_name": "Name",
                "alliance_color_is_red": False,
                "team_number": "1678",
                "scout_id": 14,
                "start_position": "3",
                "timeline": [
                    {"time": 60, "action_type": "score_speaker", "in_teleop": False},
                    {"time": 61, "action_type": "score_amp", "in_teleop": False},
                ],
                "stage_level_left": "O",
                "stage_level_right": "N",
                "stage_level_center": "N",
                "parked": False,
                "has_preload": True,
                "trap": "F",
            },
        ]
        # Expected decompressed subjective qr
        # Only 2 teams should be returned, 254 should be cut due to an invalid quickness score
        expected_subjective = [
            {
                "schema_version": decompressor.Decompressor.SCHEMA["schema_file"]["version"],
                "match_number": 34,
                "match_collection_version_number": "v1.3",
                "scout_name": "Name",
                "alliance_color_is_red": True,
                "team_number": "1678",
                "quickness_score": 1,
                "field_awareness_score": 2,
                "climb_after": True,
                "time_left_to_climb": 13,
                "timestamp": 1230,
            },
            {
                "schema_version": decompressor.Decompressor.SCHEMA["schema_file"]["version"],
                "match_number": 34,
                "match_collection_version_number": "v1.3",
                "scout_name": "Name",
                "alliance_color_is_red": True,
                "team_number": "1323",
                "quickness_score": 3,
                "field_awareness_score": 1,
                "climb_after": True,
                "time_left_to_climb": 13,
                "timestamp": 1230,
            },
        ]
        # Test objective qr decompression
        assert expected_objective == self.test_decompressor.decompress_single_qr(
            f"A{decompressor.Decompressor.SCHEMA['schema_file']['version']}$B34$C1230$Dv1.3$EName$FFALSE%Z1678$Y14$X3$W060AA061AB$VTRUE$UO$TN$SN$RFALSE$QF",
            decompressor.QRType.OBJECTIVE,
            {},
        )
        # Test subjective qr decompression
        assert expected_subjective == self.test_decompressor.decompress_single_qr(
            f"A{decompressor.Decompressor.SCHEMA['schema_file']['version']}$B34$C1230$Dv1.3$EName$FTRUE%A1678$B1$C2$D13$ETRUE#A254$B4$C1$D13$EFALSE#A1323$B3$C1$D13$ETRUE",
            decompressor.QRType.SUBJECTIVE,
            {},
        )
        # Test error raising for objective and subjective using incomplete qrs
        with pytest.raises(ValueError) as excinfo:
            self.test_decompressor.decompress_single_qr(
                f"A{decompressor.Decompressor.SCHEMA['schema_file']['version']}$B34$C1230$Dv1.3$EName$FTRUE%Z1678$Y14$VTRUE$UO",
                decompressor.QRType.OBJECTIVE,
                {},
            )
        assert "QR missing data fields" in str(excinfo)
        with pytest.raises(IndexError) as excinfo:
            self.test_decompressor.decompress_single_qr(
                f"A{decompressor.Decompressor.SCHEMA['schema_file']['version']}$B34$C1230$Dv1.3$EName$FFALSE%A1678$B1$C2$D3$EFALSE$FTRUE",
                decompressor.QRType.SUBJECTIVE,
                {},
            )
        assert "Incorrect number of teams in Subjective QR" in str(excinfo)
        with pytest.raises(ValueError) as excinfo:
            self.test_decompressor.decompress_single_qr(
                f"A{decompressor.Decompressor.SCHEMA['schema_file']['version']}$B34$C1230$Dv1.3$ENameFTRUE%A1678$B1$C2#A254#A1323",
                decompressor.QRType.SUBJECTIVE,
                {},
            )
        assert "QR missing data fields" in str(excinfo)

    def test_decompress_qrs(self):
        # Expected output from a list containing one obj qr and one subj qr
        expected_output = {
            "unconsolidated_obj_tim": [
                {
                    "schema_version": decompressor.Decompressor.SCHEMA["schema_file"]["version"],
                    "match_number": 34,
                    "timestamp": 1230,
                    "match_collection_version_number": "v1.3",
                    "scout_name": "Name",
                    "alliance_color_is_red": True,
                    "team_number": "1678",
                    "scout_id": 14,
                    "override": {},
                    "start_position": "4",
                    "timeline": [
                        {
                            "time": 60,
                            "action_type": "start_incap_time",
                            "in_teleop": False,
                        },
                        {
                            "time": 61,
                            "action_type": "end_incap_time",
                            "in_teleop": False,
                        },
                    ],
                    "stage_level_left": "N",
                    "stage_level_right": "O",
                    "stage_level_center": "N",
                    "has_preload": False,
                    "parked": False,
                    "trap": "F",
                    "ulid": "01GWSXQYKYQQ963QMT77A3NPBZ",
                }
            ],
            "subj_tim": [
                {
                    "schema_version": decompressor.Decompressor.SCHEMA["schema_file"]["version"],
                    "match_number": 34,
                    "timestamp": 1230,
                    "match_collection_version_number": "v1.3",
                    "scout_name": "Name",
                    "alliance_color_is_red": True,
                    "team_number": "1678",
                    "quickness_score": 1,
                    "field_awareness_score": 2,
                    "climb_after": False,
                    "time_left_to_climb": 13,
                    "ulid": "01GWSXSNSF93BQZ2GRG0C4E7AC",
                },
                {
                    "schema_version": decompressor.Decompressor.SCHEMA["schema_file"]["version"],
                    "match_number": 34,
                    "timestamp": 1230,
                    "match_collection_version_number": "v1.3",
                    "scout_name": "Name",
                    "alliance_color_is_red": True,
                    "team_number": "254",
                    "quickness_score": 2,
                    "field_awareness_score": 1,
                    "climb_after": True,
                    "time_left_to_climb": 13,
                    "ulid": "01GWSXSNSF93BQZ2GRG0C4E7AC",
                },
                {
                    "schema_version": decompressor.Decompressor.SCHEMA["schema_file"]["version"],
                    "match_number": 34,
                    "timestamp": 1230,
                    "match_collection_version_number": "v1.3",
                    "scout_name": "Name",
                    "alliance_color_is_red": True,
                    "team_number": "1323",
                    "quickness_score": 3,
                    "field_awareness_score": 1,
                    "climb_after": False,
                    "time_left_to_climb": 13,
                    "ulid": "01GWSXSNSF93BQZ2GRG0C4E7AC",
                },
            ],
        }
        assert expected_output == self.test_decompressor.decompress_qrs(
            [
                {
                    "data": f"+A{decompressor.Decompressor.SCHEMA['schema_file']['version']}$B34$C1230$Dv1.3$EName$FTRUE%Z1678$Y14$X4$W060AC061AD$VFALSE$UN$TO$SN$RFALSE$QF",
                    "ulid": "01GWSXQYKYQQ963QMT77A3NPBZ",
                    "override": {},
                },
                {
                    "data": f"*A{decompressor.Decompressor.SCHEMA['schema_file']['version']}$B34$C1230$Dv1.3$EName$FTRUE%A1678$B1$C2$D13$EFALSE#A254$B2$C1$D13$ETRUE#A1323$B3$C1$D13$EFALSE",
                    "ulid": "01GWSXSNSF93BQZ2GRG0C4E7AC",
                    "override": {},
                },
            ]
        )

    def test_decompress_pit_data(self):
        raw_obj_pit = {
            "team_number": "3448",
            "drivetrain": 3,
            "has_auto_vision": True,
            "has_vision_assisted_shot": True,
            "has_hp_indicator": False,
            "can_climb": True,
            "weight": 1,
        }
        expected_obj_pit = {
            "team_number": "3448",
            "has_auto_vision": True,
            "drivetrain": "swerve",
            "has_vision_assisted_shot": True,
            "has_hp_indicator": False,
            "can_climb": True,
            "weight": 1,
        }
        citrus_seal = {
            "team_number": "3448",
            "drivetrain": 3,
            "has_auto_vision": False,
            "has_vision_assisted_shot": True,
            "has_hp_indicator": False,
            "can_climb": False,
            "weight": 1,
        }
        new_expected_obj_pit = {
            "team_number": "3448",
            "drivetrain": "swerve",
            "has_auto_vision": True,
            "has_vision_assisted_shot": True,
            "has_hp_indicator": False,
            "can_climb": True,
            "weight": 1,
        }
        raw2_obj_pit = {
            "team_number": "1678",
            "drivetrain": 3,
            "has_auto_vision": False,
            "has_vision_assisted_shot": True,
            "has_hp_indicator": False,
            "can_climb": True,
            "weight": 1,
        }
        expected2_obj_pit = {
            "team_number": "1678",
            "drivetrain": "swerve",
            "has_auto_vision": True,
            "has_vision_assisted_shot": True,
            "has_hp_indicator": False,
            "can_climb": True,
            "weight": 1,
        }
        citrus2_seal = {
            "team_number": "1678",
            "drivetrain": 3,
            "has_auto_vision": True,
            "has_vision_assisted_shot": True,
            "has_hp_indicator": False,
            "can_climb": False,
            "weight": 1,
        }
        new2_expected_obj_pit = {
            "team_number": "1678",
            "drivetrain": "swerve",
            "has_auto_vision": True,
            "has_vision_assisted_shot": True,
            "has_hp_indicator": False,
            "can_climb": False,
            "weight": 1,
        }

        assert (
            self.test_decompressor.decompress_pit_data(raw_obj_pit, "raw_obj_pit")
            == expected_obj_pit
        )
        self.test_server.db.insert_documents("raw_obj_pit", expected_obj_pit)
        assert (
            self.test_decompressor.decompress_pit_data(citrus_seal, "raw_obj_pit")
            == new_expected_obj_pit
        )
        assert (
            self.test_decompressor.decompress_pit_data(citrus2_seal, "raw_obj_pit")
            == new2_expected_obj_pit
        )
        self.test_server.db.insert_documents("raw_obj_pit", new2_expected_obj_pit)
        assert (
            self.test_decompressor.decompress_pit_data(raw2_obj_pit, "raw_obj_pit")
            == expected2_obj_pit
        )

    def test_decompress_ss_team(self):
        input_1 = {
            "shoot_specific_area_only": "subwoofer",
            "can_intake_ground": True,
            "can_go_under_stage": False,
        }
        input_2 = {
            "auto_strategies": "goes to center first",
            "can_intake_ground": False,
            "can_go_under_stage": True,
        }
        input_3 = {
            "strengths": "very fast",
            "weaknesses": "tippy",
            "can_intake_ground": False,
            "can_go_under_stage": True,
        }
        input_4 = {
            "strengths": "fast cycles",
            "can_intake_ground": False,
            "can_go_under_stage": True,
        }

        expected_output_1 = {
            "auto_strategies": "",
            "can_go_under_stage": False,
            "can_intake_ground": True,
            "notes": "",
            "shoot_specific_area_only": "subwoofer",
            "strengths": "",
            "weaknesses": "",
        }
        expected_output_2 = {
            "auto_strategies": "goes to center first",
            "can_go_under_stage": True,
            "can_intake_ground": False,
            "notes": "",
            "shoot_specific_area_only": "",
            "strengths": "",
            "weaknesses": "",
        }
        expected_output_3 = {
            "auto_strategies": "",
            "can_go_under_stage": True,
            "can_intake_ground": False,
            "notes": "",
            "shoot_specific_area_only": "",
            "strengths": "very fast",
            "weaknesses": "tippy",
        }
        expected_output_4 = {
            "auto_strategies": "",
            "can_go_under_stage": True,
            "can_intake_ground": False,
            "notes": "",
            "shoot_specific_area_only": "",
            "strengths": "fast cycles",
            "weaknesses": "",
        }

        assert decompressor.Decompressor.decompress_ss_team(input_1) == expected_output_1
        assert decompressor.Decompressor.decompress_ss_team(input_2) == expected_output_2
        assert decompressor.Decompressor.decompress_ss_team(input_3) == expected_output_3
        assert decompressor.Decompressor.decompress_ss_team(input_4) == expected_output_4

    def test_decompress_ss_tim(self):
        # Creates 8 instances and checks them with their expected outputs.
        input_1 = {"coopertition": True, "played_defense": True}
        input_2 = {"coopertition": True, "broken_mechanism": "shooter broke"}
        input_3 = {"coopertition": True, "played_defense": True, "defense_rating": 2}
        input_4 = {"notes": "can shoot from anywhere", "coopertition": True}
        input_5 = {"played_defense": True, "broken_mechanism": "shooter broke"}
        input_6 = {"defense_rating": 3, "broken_mechanism": "shooter broke", "played_defense": True}
        input_7 = {"coopertition": True, "defense_rating": 2}
        input_8 = {"notes": "can shoot from anywhere"}

        excepted_output_1 = {
            "broken_mechanism": False,
            "coopertition": True,
            "defense_rating": 0,
            "notes": "",
            "played_defense": True,
        }
        excepted_output_2 = {
            "broken_mechanism": True,
            "coopertition": True,
            "defense_rating": 0,
            "notes": "",
            "played_defense": False,
        }

        excepted_output_3 = {
            "broken_mechanism": False,
            "coopertition": True,
            "defense_rating": 2,
            "notes": "",
            "played_defense": True,
        }
        excepted_output_4 = {
            "broken_mechanism": False,
            "coopertition": True,
            "defense_rating": 0,
            "notes": "can shoot from anywhere",
            "played_defense": False,
        }
        excepted_output_5 = {
            "broken_mechanism": True,
            "coopertition": False,
            "defense_rating": 0,
            "notes": "",
            "played_defense": True,
        }
        excepted_output_6 = {
            "broken_mechanism": True,
            "coopertition": False,
            "defense_rating": 3,
            "notes": "",
            "played_defense": True,
        }
        excepted_output_7 = {
            "broken_mechanism": False,
            "coopertition": True,
            "defense_rating": 2,
            "notes": "",
            "played_defense": False,
        }
        excepted_output_8 = {
            "broken_mechanism": False,
            "coopertition": False,
            "defense_rating": 0,
            "notes": "can shoot from anywhere",
            "played_defense": False,
        }

        assert decompressor.Decompressor.decompress_ss_tim(input_1) == excepted_output_1
        assert decompressor.Decompressor.decompress_ss_tim(input_2) == excepted_output_2
        assert decompressor.Decompressor.decompress_ss_tim(input_3) == excepted_output_3
        assert decompressor.Decompressor.decompress_ss_tim(input_4) == excepted_output_4
        assert decompressor.Decompressor.decompress_ss_tim(input_5) == excepted_output_5
        assert decompressor.Decompressor.decompress_ss_tim(input_6) == excepted_output_6
        assert decompressor.Decompressor.decompress_ss_tim(input_7) == excepted_output_7
        assert decompressor.Decompressor.decompress_ss_tim(input_8) == excepted_output_8

    def test_run(self):
        expected_obj = {
            "schema_version": decompressor.Decompressor.SCHEMA["schema_file"]["version"],
            "override": {"doesnt_exist": 5, "start_position": "1"},
            "match_number": 51,
            "timestamp": 9321,
            "match_collection_version_number": "v1.3",
            "scout_name": "XvfaPcSrgJw25VKrcsphdbyEVjmHrH1V",
            "alliance_color_is_red": False,
            "team_number": "3603",
            "scout_id": 13,
            "start_position": "1",
            "timeline": [
                {"time": 0, "action_type": "score_speaker", "in_teleop": False},
                {"time": 1, "action_type": "score_amp", "in_teleop": False},
                {"time": 5, "action_type": "to_teleop", "in_teleop": True},
                {"time": 6, "action_type": "score_amp", "in_teleop": True},
                {"time": 7, "action_type": "start_incap_time", "in_teleop": True},
                {"time": 8, "action_type": "end_incap_time", "in_teleop": True},
            ],
            "stage_level_left": "O",
            "stage_level_right": "N",
            "stage_level_center": "N",
            "parked": False,
            "has_preload": True,
            "trap": "F",
            "ulid": "01GWSYJHR5EC6PAKCS79YZAF3Z",
        }
        expected_sbj = [
            {
                "schema_version": decompressor.Decompressor.SCHEMA["schema_file"]["version"],
                "match_number": 34,
                "timestamp": 1230,
                "match_collection_version_number": "v1.3",
                "scout_name": "Name",
                "alliance_color_is_red": False,
                "team_number": "1678",
                "quickness_score": 2,
                "field_awareness_score": 2,
                "was_tippy": False,
                "climb_after": True,
                "did_ferry": False,
                "ulid": "01GWSYMT48K5P3BFF183GXB9C0",
            },
            {
                "schema_version": decompressor.Decompressor.SCHEMA["schema_file"]["version"],
                "match_number": 34,
                "timestamp": 1230,
                "match_collection_version_number": "v1.3",
                "scout_name": "Name",
                "alliance_color_is_red": False,
                "team_number": "254",
                "quickness_score": 2,
                "field_awareness_score": 3,
                "was_tippy": False,
                "climb_after": True,
                "did_ferry": False,
                "ulid": "01GWSYMT48K5P3BFF183GXB9C0",
            },
            {
                "schema_version": decompressor.Decompressor.SCHEMA["schema_file"]["version"],
                "match_number": 34,
                "timestamp": 1230,
                "match_collection_version_number": "v1.3",
                "scout_name": "Name",
                "alliance_color_is_red": False,
                "team_number": "1323",
                "quickness_score": 3,
                "field_awareness_score": 1,
                "was_tippy": False,
                "climb_after": True,
                "did_ferry": False,
                "ulid": "01GWSYMT48K5P3BFF183GXB9C0",
            },
        ]

        self.test_server.db.insert_documents(
            "raw_qr",
            [
                {
                    "data": f"+A{decompressor.Decompressor.SCHEMA['schema_file']['version']}$B51$C9321$Dv1.3$EXvfaPcSrgJw25VKrcsphdbyEVjmHrH1V$FFALSE%Z3603$Y13$X2$W000AA001AB005AU006AB007AC008AD$VTRUE$UO$TN$SN$RFALSE$QF",
                    "blocklisted": False,
                    "override": {"start_position": "1", "doesnt_exist": 5},
                    "ulid": "01GWSYJHR5EC6PAKCS79YZAF3Z",
                    "readable_time": "2023-03-30 19:05:38.821000+00:00",
                },
                {
                    "data": f"+A{decompressor.Decompressor.SCHEMA['schema_file']['version']}$B51$C9321$Dv1.3$EXvfaPcSrgJw25VKrcsphdbyEVjmHrH1V$FFALSE%Z3603$Y13$X2$W000AA001AB002AC005AO006AB007AD008AE$VTRUE$UN$TO$SN$RFALSE$QF",
                    "blocklisted": True,
                    "override": {"start_position": "1", "doesnt_exist": 5},
                    "ulid": "01GWSYKDZDM45M1K4ZBHN6G97H",
                    "readable_time": "2023-03-30 19:06:07.725000+00:00",
                },
                {
                    "data": f"*A{decompressor.Decompressor.SCHEMA['schema_file']['version']}$B34$C1230$Dv1.3$EName%A1678$B2$C2$DFALSE$ETRUE$FFALSE#A254$B2$C3$DFALSE$ETRUE$FFALSE#A1323$B3$C1$DTRUE$ETRUE$FFALSE",
                    "blocklisted": True,
                    "override": {},
                    "ulid": "01GWSYM2JP9JMDFCRVCX49PNY0",
                    "readable_time": "2023-03-30 19:06:28.822000+00:00",
                },
                {
                    "data": f"*A{decompressor.Decompressor.SCHEMA['schema_file']['version']}$B34$C1230$Dv1.3$EName%A1678$B2$C2$DFALSE$ETRUE$FFALSE#A254$B2$C3$DFALSE$ETRUE$FFALSE#A1323$B3$C1$DFALSE$ETRUE$FFALSE",
                    "blocklisted": False,
                    "override": {},
                    "ulid": "01GWSYMT48K5P3BFF183GXB9C0",
                    "readable_time": "2023-03-30 19:06:52.936000+00:00",
                },
            ],
        )
        self.test_decompressor.run()
        result_obj = self.test_server.db.find("unconsolidated_obj_tim")
        result_sbj = self.test_server.db.find("subj_tim")
        assert len(result_obj) == 1
        assert len(result_sbj) == 0
        result_obj = result_obj[0]
        result_obj.pop("_id")
        assert result_obj == expected_obj
        for i, result in enumerate(result_sbj):
            result.pop("_id")
            assert result == expected_sbj[i]

    def test_get_qr_type(self):
        # Test when QRType.OBJECTIVE returns when first character is '+'
        assert decompressor.QRType.OBJECTIVE == self.test_decompressor.get_qr_type("+")
        # Test when QRType.SUBJECTIVE returns when first character is '*'
        assert decompressor.QRType.SUBJECTIVE == self.test_decompressor.get_qr_type("*")

        # Test if correct error runs when neither '+' or '*' is the first character
        with pytest.raises(ValueError) as char_error:
            self.test_decompressor.get_qr_type("a")
        assert "QR type unknown" in str(char_error)
