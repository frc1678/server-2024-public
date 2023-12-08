import pytest
from unittest.mock import patch
import server
from calculations import decompressor

# import generate_test_qrs
import utils

SCHEMA = utils.read_schema("schema/match_collection_qr_schema.yml")
with patch("server.Server.ask_calc_all_data", return_value=False):
    DECOMPRESSOR = decompressor.Decompressor(server.Server())


def test_gen_timeline():
    pass


def test_gen_generic_data():
    pass


def test_gen_obj_tim():
    pass


# Does not exist in generate_test_qrs yet
def test_gen_subj_aim():
    pass
