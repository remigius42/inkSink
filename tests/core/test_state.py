from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock, patch

import pytest

from inksink.core.state import WifiStatus, battery_percent, wifi_status


def test_battery_returns_minus_one_when_i2c_unavailable():
    with patch("smbus2.SMBus", side_effect=OSError("no i2c")):
        assert battery_percent() == -1


def test_battery_closes_smbus_on_success(mocker):
    bus_mock = MagicMock()
    bus_mock.__enter__ = MagicMock(return_value=bus_mock)
    bus_mock.__exit__ = MagicMock(return_value=False)
    bus_mock.read_byte_data.return_value = 75
    mocker.patch("smbus2.SMBus", return_value=bus_mock)
    result = battery_percent()
    assert result == 75
    bus_mock.__exit__.assert_called_once()  # context manager was exited (bus closed)


def test_wifi_status_sentinel_is_immutable():
    with patch("inksink.core.state.subprocess.run", side_effect=FileNotFoundError):
        result = wifi_status()
    with pytest.raises(FrozenInstanceError):
        result.connected = True  # type: ignore[misc]


def test_wifi_sentinel_when_nmcli_raises():
    with patch("inksink.core.state.subprocess.run", side_effect=FileNotFoundError):
        result = wifi_status()
    assert result == WifiStatus(connected=False, ssid=None, strength=-1)


def test_wifi_connected_parses_nmcli_output(mocker):
    mocker.patch(
        "inksink.core.state.subprocess.run",
        return_value=mocker.Mock(returncode=0, stdout="yes:HomeNet:72\nno:Other:40\n"),
    )
    result = wifi_status()
    assert result == WifiStatus(connected=True, ssid="HomeNet", strength=72)


def test_wifi_disconnected_when_no_active_row(mocker):
    mocker.patch(
        "inksink.core.state.subprocess.run",
        return_value=mocker.Mock(returncode=0, stdout="no:HomeNet:72\n"),
    )
    result = wifi_status()
    assert result == WifiStatus(connected=False, ssid=None, strength=-1)


def test_wifi_ssid_with_colon(mocker):
    # nmcli terse mode escapes ':' in SSID values as '\:'
    mocker.patch(
        "inksink.core.state.subprocess.run",
        return_value=mocker.Mock(returncode=0, stdout=r"yes:My\:Network:55" + "\n"),
    )
    result = wifi_status()
    assert result == WifiStatus(connected=True, ssid="My:Network", strength=55)


def test_wifi_ssid_with_backslash(mocker):
    mocker.patch(
        "inksink.core.state.subprocess.run",
        return_value=mocker.Mock(returncode=0, stdout=r"yes:Back\\slash:60" + "\n"),
    )
    result = wifi_status()
    assert result == WifiStatus(connected=True, ssid=r"Back\slash", strength=60)
