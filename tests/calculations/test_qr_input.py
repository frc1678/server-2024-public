import server

from unittest import mock

import pytest

FAKE_SCHEMA = {
    "objective_tim": {"_start_character": "+"},
    "subjective_aim": {"_start_character": "*"},
}


@pytest.mark.clouddb
class TestQRInput:
    def setup(self):
        with mock.patch("server.Server.ask_calc_all_data", return_value=False):
            self.server = server.Server()

    def test_run(self, caplog):
        with mock.patch("utils.read_schema", return_value=FAKE_SCHEMA), mock.patch(
            "builtins.open", mock.mock_open(read_data="1,1,1")
        ), mock.patch("json.load", return_value={}):
            from calculations import qr_input

            self.test_calc = qr_input.QRInput(self.server)
        with mock.patch("data_transfer.adb_communicator.pull_device_data", return_value=[]):

            self.test_calc.run("*test")
            assert (query := self.server.db.find("raw_qr")) != []
            assert "data" in query[0].keys() and query[0]["data"] == "*test"
            assert isinstance(query[0]["ulid"], str)
            assert isinstance(query[0]["readable_time"], str)

            self.test_calc.run("*test\ntest")
            assert [
                "Duplicate QR code not uploaded\t*test",
                'Invalid QR code not uploaded: "test"',
            ] == [rec.message for rec in caplog.records if rec.levelname == "WARNING"]

            self.test_calc.run("*test2\n+test3\n*test4")
            assert (query := self.server.db.find("raw_qr")) != [] and len(query) == 4

            ## Mocks for when qr_input used input() instead of reading directly from stdin

            # with mock.patch("builtins.input", return_value="*test"):
            #     self.test_calc.run()
            #     assert (query := self.server.db.find("raw_qr")) != []
            #     assert "data" in query[0].keys() and query[0]["data"] == "*test"
            #     assert isinstance(query[0]["ulid"], str)
            #     assert isinstance(query[0]["readable_time"], str)
            # with mock.patch("builtins.input", return_value="*test\ttest"):
            #     self.test_calc.run()
            #     reading = capsys.readouterr()
            #     assert "WARNING: duplicate QR code not uploaded" in reading.out
            #     assert "Invalid QR code not uploaded: " in reading.err
            # with mock.patch("builtins.input", return_value="*test2\t+test3\t*test4"):
            #     self.test_calc.run()
            #     assert (query := self.server.db.find("raw_qr")) != [] and len(query) == 4
