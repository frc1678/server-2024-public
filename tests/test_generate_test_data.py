import sys
import utils
import pytest

import generate_test_data
from generate_test_data import DataGenerator, parse_args

CORRECT_SCHEMA_DATAPOINT_COLLECTIONS = [
    # Auto Paths
    {
        "team_number": "6604",
        "auto_charge_level_max": "D",
        "score_position_1_max": None,
        "score_position_2_max": None,
        "score_position_3_max": None,
        "score_piece_1_max": None,
        "score_piece_2_max": None,
        "score_piece_3_max": None,
        "auto_charge_successes": 49,
        "score_1_max_successes": 49,
        "score_1_successes": 49,
        "score_2_max_successes": 49,
        "score_2_successes": 49,
        "score_3_max_successes": 49,
        "score_3_successes": 49,
    },
    # Auto PIM
    {
        "team_number": "6604",
        "match_number": 49,
        "obj_tim.start_position": ["3", "0"],  # TODO: Should be str
        "obj_tim.preloaded_gamepiece": "O",
        "obj_tim.auto_charge_level": "D",
        "tba_tim.mobility": True,
        "subj_tim.auto_pieces_start_position": [1, 1, 0, 1],
        "intake_piece_1": "yyyyyyyyyyy",
        "intake_piece_2": "yyyyyyyyyyy",
        "intake_piece_3": "yyyyyyyyyyy",
        "intake_piece_4": "yyyyyyyyyyy",
        "intake_position_1": "yyyyyyyyyyy",
        "intake_position_2": "yyyyyyyyyyy",
        "intake_position_3": "yyyyyyyyyyy",
        "intake_position_4": "yyyyyyyyyyy",
        "score_piece_1": "yyyyyyyyyyy",
        "score_piece_2": "yyyyyyyyyyy",
        "score_piece_3": "yyyyyyyyyyy",
        "score_piece_4": "yyyyyyyyyyy",
        "score_piece_5": "yyyyyyyyyyy",
        "score_position_1": "yyyyyyyyyyy",
        "score_position_2": "yyyyyyyyyyy",
        "score_position_3": "yyyyyyyyyyy",
        "score_position_4": "yyyyyyyyyyy",
        "score_position_5": "yyyyyyyyyyy",
    },
    # Obj Team
    {
        "team_number": "6604",
        "avg_intakes_double": 84.4422,
        "avg_intakes_single": 84.4422,
        "lfm_avg_intakes_double": 84.4422,
        "lfm_avg_intakes_single": 84.4422,
        "auto_avg_charge_points": 84.4422,
        "lfm_auto_avg_charge_points": 84.4422,
        "auto_avg_cone_high": 84.4422,
        "auto_avg_cone_mid": 84.4422,
        "auto_avg_cone_low": 84.4422,
        "auto_avg_cone_total": 84.4422,
        "auto_avg_cube_high": 84.4422,
        "auto_avg_cube_mid": 84.4422,
        "auto_avg_cube_low": 84.4422,
        "auto_avg_cube_total": 84.4422,
        "auto_avg_gamepieces": 84.4422,
        "tele_avg_charge_points": 84.4422,
        "lfm_tele_avg_charge_points": 84.4422,
        "tele_avg_cone_high": 84.4422,
        "tele_avg_cone_mid": 84.4422,
        "tele_avg_cone_low": 84.4422,
        "tele_avg_cone_total": 84.4422,
        "tele_avg_cube_high": 84.4422,
        "tele_avg_cube_mid": 84.4422,
        "tele_avg_cube_low": 84.4422,
        "tele_avg_cube_total": 84.4422,
        "tele_avg_gamepieces": 84.4422,
        "tele_avg_gamepieces_low": 84.4422,
        "auto_max_cone_high": 49,
        "auto_max_cone_low": 49,
        "auto_max_cone_mid": 49,
        "auto_max_cones": 49,
        "auto_max_cube_high": 49,
        "auto_max_cube_low": 49,
        "auto_max_cube_mid": 49,
        "auto_max_cubes": 49,
        "auto_max_gamepieces": 49,
        "avg_incap_time": 84.4422,
        "avg_intakes_ground": 84.4422,
        "avg_intakes_low_row": 84.4422,
        "avg_intakes_mid_row": 84.4422,
        "avg_intakes_high_row": 84.4422,
        "auto_avg_charge_points": 84.4422,
        "tele_avg_charge_points": 84.4422,
        "avg_total_intakes": 84.4422,
        "avg_total_points": 84.4422,
        "lfm_auto_avg_cone_high": 84.4422,
        "lfm_auto_avg_cone_mid": 84.4422,
        "lfm_auto_avg_cone_low": 84.4422,
        "lfm_auto_avg_cone_total": 84.4422,
        "lfm_auto_avg_cube_high": 84.4422,
        "lfm_auto_avg_cube_mid": 84.4422,
        "lfm_auto_avg_cube_low": 84.4422,
        "lfm_auto_avg_cube_total": 84.4422,
        "lfm_auto_avg_gamepieces": 84.4422,
        "lfm_auto_avg_gamepieces_low": 84.4422,
        "lfm_tele_avg_cone_high": 84.4422,
        "lfm_tele_avg_cone_mid": 84.4422,
        "lfm_tele_avg_cone_low": 84.4422,
        "lfm_tele_avg_cone_total": 84.4422,
        "lfm_tele_avg_cube_high": 84.4422,
        "lfm_tele_avg_cube_mid": 84.4422,
        "lfm_tele_avg_cube_low": 84.4422,
        "lfm_tele_avg_cube_total": 84.4422,
        "lfm_tele_avg_gamepieces": 84.4422,
        "lfm_tele_avg_gamepieces_low": 84.4422,
        "lfm_auto_max_cone_high": 49,
        "lfm_auto_max_cone_low": 49,
        "lfm_auto_max_cone_mid": 49,
        "lfm_auto_max_cones": 49,
        "lfm_auto_max_cube_high": 49,
        "lfm_auto_max_cube_low": 49,
        "lfm_auto_max_cube_mid": 49,
        "lfm_auto_max_cubes": 49,
        "lfm_auto_max_gamepieces": 49,
        "lfm_avg_failed_scores": 84.4422,
        "lfm_avg_incap_time": 84.4422,
        "lfm_avg_intakes_ground": 84.4422,
        "lfm_avg_total_intakes": 84.4422,
        "lfm_avg_intakes_low_row": 84.4422,
        "lfm_avg_intakes_mid_row": 84.4422,
        "lfm_avg_intakes_high_row": 84.4422,
        "charge_percent_success": 84.4422,
        "lfm_charge_percent_success": 84.4422,
        "lfm_auto_dock_percent_success": 84.4422,
        "lfm_auto_engage_percent_success": 84.4422,
        "auto_sd_cone_high": 84.4422,
        "auto_sd_cone_mid": 84.4422,
        "auto_sd_cone_low": 84.4422,
        "auto_sd_cone_total": 84.4422,
        "auto_sd_cube_high": 84.4422,
        "auto_sd_cube_mid": 84.4422,
        "auto_sd_cube_low": 84.4422,
        "auto_sd_cube_total": 84.4422,
        "auto_sd_gamepieces": 84.4422,
        "lfm_auto_sd_gamepieces": 84.4422,
        "avg_failed_scores": 84.4422,
        "tele_sd_cone_high": 84.4422,
        "tele_sd_cone_mid": 84.4422,
        "tele_sd_cone_low": 84.4422,
        "tele_sd_cone_total": 84.4422,
        "tele_sd_cube_high": 84.4422,
        "tele_sd_cube_mid": 84.4422,
        "tele_sd_cube_low": 84.4422,
        "tele_sd_cube_total": 84.4422,
        "tele_sd_gamepieces": 84.4422,
        "lfm_tele_sd_gamepieces": 84.4422,
        "auto_avg_gamepieces_low": 84.4422,
        "auto_avg_total_points": 84.4422,
        "tele_avg_total_points": 84.4422,
        "auto_charge_attempts": 49,
        "auto_dock_only_percent_success": 84.4422,
        "auto_dock_only_successes": 49,
        "auto_dock_successes": 49,
        "auto_dock_percent_success": 84.4422,
        "auto_engage_successes": 49,
        "auto_engage_percent_success": 84.4422,
        "tele_charge_attempts": 49,
        "tele_dock_only_percent_success": 84.4422,
        "tele_dock_only_successes": 49,
        "tele_dock_successes": 49,
        "tele_engage_percent_success": 84.4422,
        "lfm_tele_park_percent_success": 84.4422,
        "tele_park_percent_success": 84.4422,
        "tele_engage_successes": 49,
        "tele_park_successes": 49,
        "matches_incap": 49,
        "matches_played": 49,
        "position_zero_starts": 49,
        "position_one_starts": 49,
        "position_two_starts": 49,
        "position_three_starts": 49,
        "lfm_auto_charge_attempts": 49,
        "lfm_auto_dock_only_percent_success": 84.4422,
        "lfm_auto_dock_only_successes": 49,
        "lfm_auto_dock_successes": 49,
        "lfm_auto_engage_successes": 49,
        "lfm_tele_charge_attempts": 49,
        "lfm_tele_dock_percent_success": 84.4422,
        "lfm_tele_dock_only_percent_success": 84.4422,
        "lfm_tele_dock_only_successes": 49,
        "lfm_tele_dock_successes": 49,
        "lfm_tele_engage_percent_success": 84.4422,
        "lfm_tele_engage_successes": 49,
        "lfm_tele_park_successes": 49,
        "lfm_matches_incap": 49,
        "mode_start_position": ["3", "0"],
        "lfm_mode_start_position": ["3", "0"],
        "mode_auto_charge_level": ["D", "P"],
        "lfm_mode_auto_charge_level": ["D", "P"],
        "mode_tele_charge_level": ["D", "P"],
        "lfm_mode_tele_charge_level": ["D", "P"],
        "lfm_position_four_starts": 49,
        "lfm_position_three_starts": 49,
        "lfm_position_two_starts": 49,
        "lfm_position_one_starts": 49,
        "lfm_position_zero_starts": 49,
        "max_tele_charge_level": "D",
        "max_incap": 49,
        "max_auto_charge_level": "D",
        "lfm_max_auto_charge_level": "D",
        "lfm_max_incap": 49,
        "median_nonzero_incap": 84.4422,
        "lfm_max_tele_charge_level": "D",
        "lfm_median_nonzero_incap": 84.4422,
        "tele_dock_percent_success": 84.4422,
        "tele_max_cone_high": 49,
        "tele_max_cone_low": 49,
        "tele_max_cone_mid": 49,
        "tele_max_cones": 49,
        "tele_max_cube_high": 49,
        "tele_max_cube_low": 49,
        "tele_max_cube_mid": 49,
        "tele_max_cubes": 49,
        "tele_max_gamepieces": 49,
        "lfm_tele_max_cone_high": 49,
        "lfm_tele_max_cone_low": 49,
        "lfm_tele_max_cone_mid": 49,
        "lfm_tele_max_cones": 49,
        "lfm_tele_max_cube_high": 49,
        "lfm_tele_max_cube_low": 49,
        "lfm_tele_max_cube_mid": 49,
        "lfm_tele_max_cubes": 49,
        "lfm_tele_max_gamepieces": 49,
        "position_four_starts": 49,
        "mode_preloaded_gamepiece": ["O", "U"],
        "matches_tippy": 49,
        "lfm_matches_tippy": 49,
        "matches_played_defense": 49,
        "lfm_matches_played_defense": 49,
        "total_incap": 49,
        "lfm_total_incap": 49,
    },
    # Obj TIM
    {
        "confidence_rating": 49,
        "match_number": 49,
        "team_number": "6604",
        "auto_cube_low": 49,
        "auto_cube_mid": 49,
        "auto_cube_high": 49,
        "auto_cone_low": 49,
        "auto_cone_mid": 49,
        "auto_cone_high": 49,
        "tele_cube_low": 49,
        "tele_cube_mid": 49,
        "tele_cube_high": 49,
        "tele_cone_low": 49,
        "tele_cone_mid": 49,
        "tele_cone_high": 49,
        "intakes_ground": 49,
        "intakes_low_row": 49,
        "intakes_mid_row": 49,
        "intakes_high_row": 49,
        "intakes_single": 49,
        "intakes_double": 49,
        "median_cycle_time": 49,
        "auto_total_cubes": 49,
        "auto_total_cones": 49,
        "auto_total_gamepieces_low": 49,
        "auto_total_gamepieces": 49,
        "tele_total_cubes": 49,
        "tele_total_cones": 49,
        "tele_total_gamepieces": 49,
        "tele_total_gamepieces_low": 49,
        "failed_scores": 49,
        "incap": 49,
        "median_cycle_time": 49,
        "auto_charge_level": "D",
        "auto_charge_attempt": 49,
        "tele_charge_level": "D",
        "tele_charge_attempt": 49,
        "total_charge_attempts": 49,
        "total_intakes": 49,
        "start_position": ["3", "0"],
        "preloaded_gamepiece": "O",
    },
    # Pickability
    {
        "first_pickability": 84.4422,
        "second_pickability": 84.4422,
        "test_second_pickability": 84.4422,
        "team_number": "6604",
    },
    # Predicted AIM
    {
        "alliance_color_is_red": True,
        "match_number": 49,
        "has_actual_data": True,
        "actual_score": 49,
        "actual_rp1": 84.4422,
        "actual_rp2": 84.4422,
        "final_predicted_score": 84.4422,
        "final_predicted_rp1": 84.4422,
        "final_predicted_rp2": 84.4422,
        "predicted_rp1": 84.4422,
        "predicted_rp2": 84.4422,
        "predicted_score": 84.4422,
        "win_chance": 84.4422,
        "won_match": True,
    },
    # Predicted Team
    {
        "current_avg_rps": 84.4422,
        "current_rank": 49,
        "current_rps": 49,
        "predicted_rank": 49,
        "predicted_rps": 84.4422,
        "team_number": "6604",
    },
    # Scout Precision
    {
        "scout_name": "yyyyyyyyyyy",
        "scout_precision": 84.4422,
    },
    # SIM Precision
    {
        "scout_name": "yyyyyyyyyyy",
        "sim_precision": 84.4422,
        "auto_cone_low_precision": 84.4422,
        "tele_cone_low_precision": 84.4422,
        "auto_cone_mid_precision": 84.4422,
        "tele_cone_mid_precision": 84.4422,
        "auto_cone_high_precision": 84.4422,
        "tele_cone_high_precision": 84.4422,
        "auto_cube_low_precision": 84.4422,
        "tele_cube_low_precision": 84.4422,
        "auto_cube_mid_precision": 84.4422,
        "tele_cube_mid_precision": 84.4422,
        "auto_cube_high_precision": 84.4422,
        "tele_cube_high_precision": 84.4422,
        "team_number": "6604",
        "match_number": 49,
        "alliance_color_is_red": True,
    },
    # Subj Team
    {
        "driver_ability": 84.4422,
        "driver_field_awareness": 84.4422,
        "driver_quickness": 84.4422,
        "team_number": "6604",
        "test_driver_ability": 84.4422,
        "unadjusted_field_awareness": 84.4422,
        "unadjusted_quickness": 84.4422,
        "auto_pieces_start_position": [1, 1, 0, 1],
    },
    # TBA Team
    {
        "team_name": "yyyyyyyyyyy",
        "mobility_successes": 49,
        "lfm_mobility_successes": 49,
        "team_number": "6604",
        "foul_cc": 84.4422,
        "link_cc": 84.4422,
    },
    # TBA TIM
    {
        "mobility": True,
        "match_number": 49,
        "team_number": "6604",
    },
    # Obj Pit
    {
        "team_number": "6604",
        "drivetrain": 1,
        "drivetrain_motor_type": 1,
        "drivetrain_motors": 49,
        "has_vision": True,
        "has_communication_device": True,
        "has_ground_intake": True,
        "is_forkable": True,
        "weight": 84.4422,
        "length": 84.4422,
        "width": 84.4422,
    },
]


class TestDataGenerator:
    def setup_method(self):
        self.input_filename = "schema/calc_obj_tim_schema.yml"
        self.generate_test_data = DataGenerator(self.input_filename)

        filenames = utils.get_schema_filenames()
        self.schema_files = []
        [self.schema_files.append(file) for file in filenames if file not in self.schema_files]
        self.schema_files.sort()

    def test_open_schema_file(self):
        schema = self.generate_test_data.open_schema_file(self.input_filename)
        assert utils.read_schema(self.input_filename) == schema

    def test_get_datapoint_collections_generation(self):
        for schema_file in self.schema_files:
            generate_test_data = DataGenerator(f"schema/{schema_file}", seed=0)
            datapoint_collections = generate_test_data.get_datapoint_collections_generation()
            assert "schema_file" not in datapoint_collections

    def test_generate_for_each_datapoint_collection(self):
        for num, schema_file in enumerate(self.schema_files):
            generate_test_data = DataGenerator(f"schema/{schema_file}", seed=0)
            generated_structure = generate_test_data.generate_for_each_datapoint_collection()
            assert generated_structure == CORRECT_SCHEMA_DATAPOINT_COLLECTIONS[num]

    def test_format_raw_data(self):
        for schema_file in self.schema_files:
            generate_test_data = DataGenerator(f"schema/{schema_file}", seed=0)
            formated_raw_data = generate_test_data.format_raw_data()
            assert isinstance(formated_raw_data, dict)
            assert "schema_file" not in formated_raw_data
            assert "data" not in formated_raw_data

    def test_request_single_data_struct(self):
        for schema_file in self.schema_files:
            generate_test_data = DataGenerator(f"schema/{schema_file}", seed=0)
            single_raw_data = generate_test_data.request_single_data_struct()
            assert isinstance(single_raw_data, dict)
            assert "schema_file" not in single_raw_data
            assert "data" not in single_raw_data

    def test_get_data(self):
        for schema_file in self.schema_files:
            generate_test_data = DataGenerator(f"schema/{schema_file}", seed=0)
            for num in range(5):
                list_of_raw_data_structures = generate_test_data.get_data(num)
                assert isinstance(list_of_raw_data_structures, list)
                assert len(list_of_raw_data_structures) == num


def test_name_sample_data():
    schema_files = utils.get_schema_filenames()
    schema_files = list(schema_files)
    schema_files.sort()

    for schema in schema_files:
        data = generate_test_data.name_sample_data(f"schema/{schema}", 1)
        assert isinstance(data, dict)
        assert isinstance(data[f"schema/{schema}"], dict)


def test_parse_args():
    sys.argv = [
        "generate_test_data.py",
        "-i",
        "schema/calc_predicted_aim_schema.yml",
        "-n",
        "2",
    ]
    parsed = parse_args()
    assert parsed.infile == sys.argv[2]
    assert parsed.number == sys.argv[4]
