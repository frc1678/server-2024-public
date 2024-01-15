import pytest
import unittest
import unittest
from unittest.mock import *
from calculations import decompressor
import os
import utils
import logging
import json
import re
import qr_code_uploader
import pyfakefs
from pyfakefs.fake_filesystem_unittest import fake_os
from pyfakefs.fake_filesystem_unittest import Patcher

with Patcher() as patcher:
    with patch("calculations.decompressor.Decompressor"):
        with patch("json.load", return_value={"A1B2C3D4": "Test Lenovo Tab 1"}):
            patcher.fs.create_file(utils.create_file_path("data/tablet_serials.json"))
            from data_transfer import adb_communicator


def return_input(val):
    # used to make qr_code_uploader.upload_qr_codes do nothing
    return val


def test_delete_tablet_downloads():
    real_get_attached_devices = adb_communicator.get_attached_devices
    real_run_command = utils.run_command

    fake_serials = ["A1B2C3D4", "E5F6G7H8", "I9J1K2L3"]
    adb_communicator.get_attached_devices = MagicMock(return_value=fake_serials)
    utils.run_command = MagicMock()
    adb_communicator.DEVICE_SERIAL_NUMBERS = {
        "A1B2C3D4": "Fake Lenovo Tab 1",
        "E5F6G7H8": "Fake Lenovo Tab 2",
        "I9J1K2L3": "Fake Lenovo Tab 3",
    }
    adb_communicator.delete_tablet_downloads()
    for i in fake_serials:
        utils.run_command.assert_any_call(f"adb -s {i} shell rm -r /storage/emulated/0/Download")

    adb_communicator.get_attached_devices = real_get_attached_devices
    utils.run_command = real_run_command


def test_get_attached_devices():
    fake_attached_devices = (
        "List of devices attached\nA1B2C3D4\tdevice\nE5F6G7H8\tdevice\nI9J1K2L3\tdevice"
    )
    expected_output = ["A1B2C3D4", "E5F6G7H8", "I9J1K2L3"]

    with patch("utils.run_command", return_value=fake_attached_devices):
        assert adb_communicator.get_attached_devices() == expected_output


def test_push_file():
    real_run_command = utils.run_command

    with Patcher() as patcher:
        fake_serial = "A1B2C3D4"
        fake_local_path = "fakepath/path"
        patcher.fs.create_file(fake_local_path)
        fake_tablet_path = "fakedata/fakefile"
        expected_push_command = "adb -s A1B2C3D4 push fakepath/path fakedata/fakefile"
        utils.run_command = MagicMock()

        adb_communicator.push_file(fake_serial, fake_local_path, fake_tablet_path)
        utils.run_command.assert_called_once_with(expected_push_command)

    utils.run_command = real_run_command


def test_uninstall_app():
    real_run_command = utils.run_command

    with Patcher() as patcher:
        # returns app name so that the app to uninstall is in installed_apps
        utils.run_command = MagicMock(return_value="com.frc1678.match_collection")
        fake_serial = "A1B2C3D4"

        adb_communicator.uninstall_app(fake_serial)
        utils.run_command.assert_any_call(
            "adb -s A1B2C3D4 shell pm list packages -3", return_output=True
        )
        utils.run_command.assert_any_call("adb -s A1B2C3D4 uninstall com.frc1678.match_collection")

    utils.run_command = real_run_command


def test_pull_device_files():
    real_get_attached_devices = adb_communicator.get_attached_devices
    real_run_command = utils.run_command

    with Patcher() as patcher:
        fake_serials = ["A1B2C3D4", "E5F6G7H8", "I9J1K2L3"]
        adb_communicator.get_attached_devices = MagicMock(return_value=fake_serials)
        utils.run_command = MagicMock()
        fake_tablet_path = "fakedata/fakefile"
        fake_local_path = "fakepath/path"
        patcher.fs.create_dir(fake_local_path)

        adb_communicator.pull_device_files(fake_local_path, fake_tablet_path)
        for i in fake_serials:
            utils.run_command.assert_any_call(
                f"adb -s {i} pull fakedata/fakefile fakepath/path/{i}"
            )

    adb_communicator.get_attached_devices = real_get_attached_devices
    utils.run_command = real_run_command


def test_adb_remove_files():
    real_get_attached_devices = adb_communicator.get_attached_devices
    real_run_command = utils.run_command

    fake_serials = ["A1B2C3D4", "E5F6G7H8", "I9J1K2L3"]
    adb_communicator.get_attached_devices = MagicMock(return_value=fake_serials)
    utils.run_command = MagicMock()
    fake_tablet_path = "fakedata/fakefile"

    adb_communicator.adb_remove_files(fake_tablet_path)
    for i in fake_serials:
        utils.run_command.assert_any_call(f"adb -s {i} shell rm -r fakedata/fakefile")

    adb_communicator.get_attached_devices = real_get_attached_devices
    utils.run_command = real_run_command


def test_pull_device_data():
    real_pull_device_files = adb_communicator.pull_device_files
    real_upload_qr_codes = qr_code_uploader.upload_qr_codes
    real_get_attached_devices = adb_communicator.get_attached_devices

    with Patcher() as patcher:
        adb_communicator.pull_device_files = Mock()
        fake_serials = ["A1B2C3D4", "E5F6G7H8", "I9J1K2L3"]
        fake_qr_data = [
            "+A1$B66$C4711453624$D8.1.10$ETom$FFALSE%UTrue$VPARKED$W151AA135AU098AO088AN066AN048AP047AO039AO033AO031AO028AQ$X1$Y21$Z766",
            "+A1$B44$C7978641999$D3.6.7$EAnn$FFALSE%UFalse$VNONE$W135AU126BE103AN090AO077AO076AQ060AO051AO046AP045AO033AN028AP$X1$Y29$Z253",
            "+A1$B59$C6574274972$D10.6.6$ESusan$FFALSE%UTrue$VPARKED$W144BD143AJ135AU134AP129AO094AP093AP092AQ086AO084AP076AP070AQ067AN066AN058AO050AP043AQ042AN035AO034AN028AO017AN$X4$Y11$Z5419insertqr3here",
        ]
        qr_code_uploader.upload_qr_codes = MagicMock(side_effect=return_input)
        fake_dir_path = utils.create_file_path("data/devices")
        adb_communicator.DEVICE_SERIAL_NUMBERS = {
            "A1B2C3D4": "Fake Lenovo Tab 1",
            "E5F6G7H8": "Fake Lenovo Tab 2",
            "I9J1K2L3": "Fake Lenovo Tab 3",
        }
        adb_communicator.get_attached_devices = Mock(return_value=fake_serials)
        for i in range(3):
            fake_tablet_dir = utils.create_file_path(f"data/devices/{fake_serials[i]}")
            patcher.fs.create_file(f"{fake_tablet_dir}/qrdatathing.txt", contents=fake_qr_data[i])
        # this stuff is for fixing a bug with pyfakefs breaking os.listdir
        def listdirfix(path):
            if path == fake_dir_path:
                return fake_serials
            else:
                return ["qrdatathing.txt"]

        with patch(
            "pyfakefs.fake_filesystem_unittest.fake_os.FakeOsModule.listdir", side_effect=listdirfix
        ):
            with patch("re.fullmatch", return_value=True):
                test_data = adb_communicator.pull_device_data()

        assert test_data == {"qr": fake_qr_data, "raw_obj_pit": []}

    adb_communicator.pull_device_files = real_pull_device_files
    qr_code_uploader.upload_qr_codes = real_upload_qr_codes
    adb_communicator.get_attached_devices = real_get_attached_devices


def test_validate_apk():
    real_run_command = utils.run_command

    utils.run_command = MagicMock()
    fake_serial = "A1B2C3D4"
    fake_local_path = "fakedir/fakeapk.apk"
    adb_communicator.validate_apk(fake_serial, fake_local_path)
    utils.run_command.assert_any_call(
        "adb -s A1B2C3D4 install -r fakedir/fakeapk.apk", return_output=True
    )

    utils.run_command = real_run_command


def test_adb_font_size_enforcer():
    real_get_attached_devices = adb_communicator.get_attached_devices
    real_run_command = utils.run_command

    fake_serials = ["A1B2C3D4", "E5F6G7H8", "I9J1K2L3"]
    adb_communicator.get_attached_devices = MagicMock(return_value=fake_serials)
    utils.run_command = MagicMock()

    adb_communicator.adb_font_size_enforcer()
    for i in fake_serials:
        utils.run_command.assert_any_call(
            f"adb -s {i} shell settings put system font_scale 1.30", return_output=False
        )

    adb_communicator.get_attached_devices = real_get_attached_devices
    utils.run_command = real_run_command


def test_get_tablet_file_path_hash():
    real_run_command = utils.run_command

    with Patcher() as patcher:
        utils.run_command = MagicMock(return_value="mocked!")
        fake_serial = "A1B2C3D4"
        fake_tablet_path = "fakedir/fakefile"

        assert (
            adb_communicator.get_tablet_file_path_hash(fake_serial, fake_tablet_path) == "mocked!"
        )
        utils.run_command.assert_called_once_with(
            f"adb -s A1B2C3D4 shell sha256sum -b fakedir/fakefile", return_output=True
        )

    utils.run_command = real_run_command
