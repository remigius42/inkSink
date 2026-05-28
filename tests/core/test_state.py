# spellchecker:ignore delenv memavailable memtotal

from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock, patch

import pytest

from inksink.core.state import (
    BluetoothStatus,
    MemoryInfo,
    StorageInfo,
    WifiStatus,
    battery_percent,
    bluetooth_status,
    hostname,
    ip_address,
    load_averages,
    memory_info,
    storage_info,
    version_info,
    wifi_status,
)


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


# --- ip_address ---


def test_ip_address_returns_string_on_success(mocker):
    mocker.patch("inksink.core.state.socket.socket")
    sock = mocker.MagicMock()
    sock.__enter__ = mocker.MagicMock(return_value=sock)
    sock.__exit__ = mocker.MagicMock(return_value=False)
    sock.getsockname.return_value = ("192.168.1.42", 0)
    mocker.patch("inksink.core.state.socket.socket", return_value=sock)
    assert ip_address() == "192.168.1.42"


def test_ip_address_returns_unavailable_on_oserror(mocker):
    sock = mocker.MagicMock()
    sock.__enter__ = mocker.MagicMock(side_effect=OSError("no network"))
    sock.__exit__ = mocker.MagicMock(return_value=False)
    mocker.patch("inksink.core.state.socket.socket", return_value=sock)
    assert ip_address() == "unavailable"


def test_ip_address_returns_unavailable_on_loopback(mocker):
    sock = mocker.MagicMock()
    sock.__enter__ = mocker.MagicMock(return_value=sock)
    sock.__exit__ = mocker.MagicMock(return_value=False)
    sock.getsockname.return_value = ("127.0.0.1", 0)
    mocker.patch("inksink.core.state.socket.socket", return_value=sock)
    assert ip_address() == "unavailable"


# --- hostname ---


def test_hostname_returns_name(mocker):
    mocker.patch("inksink.core.state.socket.gethostname", return_value="inksink-pi")
    assert hostname() == "inksink-pi"


def test_hostname_returns_unknown_on_error(mocker):
    mocker.patch("inksink.core.state.socket.gethostname", side_effect=OSError)
    assert hostname() == "unknown"


# --- version_info ---


def test_version_info_reads_env(monkeypatch):
    monkeypatch.setenv("INKSINK_VERSION", "v1.2.3")
    assert version_info() == "v1.2.3"


def test_version_info_fallback_when_unset(monkeypatch):
    monkeypatch.delenv("INKSINK_VERSION", raising=False)
    assert version_info() == "unknown"


# --- load_averages ---


def test_load_averages_returns_tuple(mocker):
    mocker.patch("inksink.core.state.os.getloadavg", return_value=(0.5, 1.0, 1.5))
    assert load_averages() == (0.5, 1.0, 1.5)


def test_load_averages_sentinel_on_oserror(mocker):
    mocker.patch("inksink.core.state.os.getloadavg", side_effect=OSError)
    assert load_averages() == (-1.0, -1.0, -1.0)


# --- memory_info ---


def test_memory_info_parses_proc_meminfo(tmp_path, mocker):
    fake = tmp_path / "meminfo"
    fake.write_text("MemTotal:       2048000 kB\nMemAvailable:    512000 kB\n")
    mocker.patch("inksink.core.state._MEMINFO_PATH", str(fake))
    result = memory_info()
    assert result.total_mb == 2000
    assert result.free_mb == 500


def test_memory_info_sentinel_on_missing_file(mocker):
    mocker.patch("inksink.core.state._MEMINFO_PATH", "/nonexistent/proc/meminfo")
    result = memory_info()
    assert result == MemoryInfo(total_mb=-1, free_mb=-1)


def test_memory_info_sentinel_when_memtotal_absent(tmp_path, mocker):
    fake = tmp_path / "meminfo"
    fake.write_text("MemAvailable:    512000 kB\n")
    mocker.patch("inksink.core.state._MEMINFO_PATH", str(fake))
    assert memory_info() == MemoryInfo(total_mb=-1, free_mb=-1)


def test_memory_info_sentinel_when_memavailable_absent(tmp_path, mocker):
    fake = tmp_path / "meminfo"
    fake.write_text("MemTotal:       2048000 kB\n")
    mocker.patch("inksink.core.state._MEMINFO_PATH", str(fake))
    assert memory_info() == MemoryInfo(total_mb=-1, free_mb=-1)


# --- storage_info ---


def test_storage_info_returns_gb(mocker):
    mocker.patch(
        "inksink.core.state.shutil.disk_usage",
        return_value=mocker.MagicMock(total=32 * 1024**3, free=10 * 1024**3),
    )
    result = storage_info()
    assert result.total_gb == pytest.approx(32.0)
    assert result.free_gb == pytest.approx(10.0)


def test_storage_info_sentinel_on_oserror(mocker):
    mocker.patch("inksink.core.state.shutil.disk_usage", side_effect=OSError)
    result = storage_info()
    assert result == StorageInfo(total_gb=-1.0, free_gb=-1.0)


# --- bluetooth_status ---


def test_bluetooth_status_sentinel_when_bluetoothctl_not_found(mocker):
    mocker.patch("inksink.core.state.subprocess.run", side_effect=FileNotFoundError)
    result = bluetooth_status()
    assert result == BluetoothStatus(enabled=False, connected_devices=[])


def test_bluetooth_status_disabled_when_powered_off(mocker):
    mocker.patch(
        "inksink.core.state.subprocess.run",
        return_value=mocker.MagicMock(returncode=0, stdout="Powered: no\n"),
    )
    result = bluetooth_status()
    assert result.enabled is False


def test_bluetooth_status_enabled_with_connected_device(mocker):
    show_result = mocker.MagicMock(returncode=0, stdout="Powered: yes\n")
    devices_result = mocker.MagicMock(
        returncode=0, stdout="Device AA:BB:CC:DD:EE:FF MyHeadset\n"
    )
    mocker.patch(
        "inksink.core.state.subprocess.run",
        side_effect=[show_result, devices_result],
    )
    result = bluetooth_status()
    assert result.enabled is True
    assert "MyHeadset" in result.connected_devices
