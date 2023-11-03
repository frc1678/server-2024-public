from calculations import compression
import pytest
from utils import read_schema


def test_compress_timeline():
    timeline_data = [
        {"time": 51, "action_type": "start_incap"},
        {"time": 32, "action_type": "end_incap"},
    ]
    assert compression.compress_timeline(timeline_data) == "051AL032AM"
    timeline_data[1]["action_type"] = "score_cone_high"
    assert compression.compress_timeline(timeline_data) == "051AL032AA"


def test_compress_section_generic_data():
    # Make sure it adds schema version
    assert (
        compression.compress_section({}, "generic_data")
        == f'A{read_schema("schema/match_collection_qr_schema.yml")["schema_file"]["version"]}'
    )
    # Check generic data compression
    schema_data = {"schema_version": 5}
    compressed_schema = "A5"
    assert compression.compress_section(schema_data, "generic_data") == compressed_schema


def test_compress_section_obj():
    # Without timeline
    schema_data = {"team_number": "1678", "scout_id": 18}
    compressed_schema = "Z1678$Y18"
    assert compression.compress_section(schema_data, "objective_tim") == compressed_schema
    # With timeline
    schema_data["timeline"] = [{"time": 51, "action_type": "start_incap", "in_teleop": False}]
    compressed_schema += "$W051AL"
    assert compression.compress_section(schema_data, "objective_tim") == compressed_schema


def test_compress_section_subj():
    data = {
        "team_number": "1678",
        "quickness_score": 2,
        "field_awareness_score": 1,
        "played_defense": False,
    }
    compressed_data = "A1678$B2$C1$FFALSE"
    assert compression.compress_section(data, "subjective_aim") == compressed_data


def test_compress_obj_tim():
    data = {
        "schema_version": 1,
        "match_number": 1,
        "timestamp": 1582994470,
        "match_collection_version_number": "1.0.2",
        "team_number": "9999",
        "scout_name": "KEI R",
        "scout_id": 2,
        "start_position": "FOUR",
        "timeline": [
            {"time": 45, "action_type": "start_incap"},
            {"time": 7, "action_type": "end_incap"},
        ],
        "auto_charge_level": "N",
    }
    compressed_data = "+A1$B1$C1582994470$D1.0.2$EKEI R%Z9999$Y2$XFOUR$W045AL007AM$VN"
    assert compression.compress_obj_tim(data) == compressed_data


def test_compress_subj_aim():
    data = [
        {
            "schema_version": 1,
            "match_number": 1,
            "timestamp": 1582994470,
            "match_collection_version_number": "1.0.2",
            "scout_name": "YOUYOU X",
            "team_number": "3128",
            "quickness_score": 1,
            "field_awareness_score": 2,
            "played_defense": False,
        },
        {
            "schema_version": 1,
            "match_number": 1,
            "timestamp": 1582994470,
            "match_collection_version_number": "1.0.2",
            "scout_name": "YOUYOU X",
            "team_number": "1678",
            "quickness_score": 2,
            "field_awareness_score": 1,
            "played_defense": False,
        },
        {
            "schema_version": 1,
            "match_number": 1,
            "timestamp": 1582994470,
            "match_collection_version_number": "1.0.2",
            "scout_name": "YOUYOU X",
            "team_number": "972",
            "quickness_score": 3,
            "field_awareness_score": 3,
            "played_defense": True,
        },
    ]
    compressed_data = (
        "*A1$B1$C1582994470$D1.0.2$EYOUYOU X%A3128$B1$C2$FFALSE#A1678$B2$C1$FFALSE#A972$B3$C3$FTRUE"
    )
    assert compression.compress_subj_aim(data) == compressed_data
    error_data = [
        {
            "schema_version": 1,
            "match_number": 1,
            "timestamp": 1582994470,
            "match_collection_version_number": "1.0.2",
            "scout_name": "KINA L",
            "team_number": "3128",
            "quickness_score": 1,
            "field_awareness_score": 2,
            "played_defense": False,
        },
        {
            "schema_version": 1,
            "match_number": 1,
            "timestamp": 1582994470,
            "match_collection_version_number": "1.0.2",
            "scout_name": "YOUYOU X",
            "team_number": "1678",
            "quickness_score": 2,
            "field_awareness_score": 1,
            "played_defense": True,
        },
        {
            "schema_version": 1,
            "match_number": 1,
            "timestamp": 1582994470,
            "match_collection_version_number": "1.0.2",
            "scout_name": "YOUYOU X",
            "team_number": "972",
            "quickness_score": 3,
            "field_awareness_score": 3,
            "played_defense": False,
        },
    ]
    with pytest.raises(ValueError) as error:
        compression.compress_subj_aim(error_data)
    assert "Different generic data between documents in the same subj QR" in str(error)
