from calculations.qr_state import QRState


class TestQRState:
    def setup_method(self):
        self.test_qrstate = QRState()

    def test_get_data_fields(self):
        # Set of what the data fields should be
        expected_data_fields = {
            "schema_version",
            "match_number",
            "timestamp",
            "match_collection_version_number",
            "scout_name",
            "alliance_color_is_red",
        }
        # Test that it returns the correct data type
        assert isinstance(self.test_qrstate._get_data_fields("generic_data"), set)
        # Test that the returned fields match what is expected
        assert expected_data_fields == QRState._get_data_fields("generic_data")

    def test_get_timeline_info(self):
        # What get_timeline_info() should return
        expected_timeline_info = [
            {"name": "time", "length": 3, "type": "int", "position": 0},
            {"name": "action_type", "length": 2, "type": "Enum[str]", "position": 1},
        ]
        assert expected_timeline_info == QRState.get_timeline_info()
