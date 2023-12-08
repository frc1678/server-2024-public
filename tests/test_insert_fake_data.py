# import pytest
# from unittest.mock import patch
# from unittest import mock

# with patch(
#     ".utils.create_file_path('data/tablet_serials.json')", mock.mock_open(read_data="something")
# ):
#     import insert_fake_data

# import server
# from calculations import decompressor

# with patch("server.Server.ask_calc_all_data", return_value=False):
#     DECOMPRESSOR = decompressor.Decompressor(server.Server())


# def test_fake_name():
#     assert isinstance(insert_fake_data.fake_name(), str)


# def test_insert_fake_qr_data():
#     # Use decompressor function to check if qrs match schema
#     formatted_fake_qrs = []
#     for qr in insert_fake_data.insert_fake_qr_data():
#         formatted_fake_qrs.append(
#             {"data": qr, "override": {}, "ulid": "01GWT1FZ20QQ277RAKQK0ND3DM"}
#         )

#     DECOMPRESSOR.decompress_qrs(formatted_fake_qrs)


# def test_insert_fake_non_qr_data():
#     assert len(insert_fake_data.insert_fake_non_qr_data()) == len(insert_fake_data.TEAMS)
#     for obj_data in insert_fake_data.insert_fake_non_qr_data():
#         assert obj_data["team_number"] in insert_fake_data.TEAMS
