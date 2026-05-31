"""On-demand hardware state reads: battery, WiFi, and system info.

Reads from PiSugar I2C (battery), nmcli (WiFi), socket, os, /proc/meminfo,
shutil, and bluetoothctl. No session state lives here — session tracking
belongs to each App. All functions return sentinel values when the underlying
hardware or tool is unavailable, so they are safe to call on a dev machine.
"""

# spellchecker:ignore dgram

from __future__ import annotations

import os
import shutil
import socket
import subprocess  # noqa: S404  # nosec B404 — subprocess is intentional; all calls use hardcoded system binaries
from dataclasses import dataclass


def battery_percent() -> int:
    try:
        import smbus2

        with smbus2.SMBus(1) as bus:
            raw = bus.read_byte_data(0x57, 0x2A)
        return min(100, max(0, raw))
    except (ImportError, OSError):
        return -1


@dataclass(frozen=True)
class WifiStatus:
    connected: bool
    ssid: str | None
    strength: int


_WIFI_SENTINEL = WifiStatus(connected=False, ssid=None, strength=-1)


def _parse_wifi_line(line: str) -> WifiStatus | None:
    """Parse one nmcli terse line (active:ssid:signal). Returns None if not active."""
    first = line.index(":") if ":" in line else -1
    last = line.rindex(":") if ":" in line else -1
    if first == -1 or first == last:
        return None
    if line[:first] != "yes":
        return None
    raw_ssid = line[first + 1 : last]
    ssid = raw_ssid.replace("\\:", ":").replace("\\\\", "\\") or None
    try:
        strength = int(line[last + 1 :])
    except ValueError:
        return None
    return WifiStatus(connected=True, ssid=ssid, strength=strength)


def wifi_status() -> WifiStatus:
    try:
        result = subprocess.run(  # noqa: S603  # nosec B603 — hardcoded absolute path, no user input
            ["/usr/bin/nmcli", "-t", "-f", "active,ssid,signal", "dev", "wifi"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return _WIFI_SENTINEL
        for line in result.stdout.splitlines():
            parsed = _parse_wifi_line(line)
            if parsed is not None:
                return parsed
        return _WIFI_SENTINEL
    except (FileNotFoundError, OSError, subprocess.SubprocessError, ValueError):
        return _WIFI_SENTINEL


def ip_address() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            addr = s.getsockname()[0]
        if addr.startswith("127."):
            return "unavailable"
        return addr
    except OSError:
        return "unavailable"


def hostname() -> str:
    try:
        return socket.gethostname()
    except OSError:
        return "unknown"


def version_info() -> str:
    return os.environ.get("INKSINK_VERSION", "unknown")


def load_averages() -> tuple[float, float, float]:
    try:
        one, five, fifteen = os.getloadavg()
        return (one, five, fifteen)
    except OSError:
        return (-1.0, -1.0, -1.0)


@dataclass(frozen=True)
class MemoryInfo:
    total_mb: int
    free_mb: int


_MEMINFO_PATH = "/proc/meminfo"
_MEMORY_SENTINEL = MemoryInfo(total_mb=-1, free_mb=-1)


def memory_info() -> MemoryInfo:
    try:
        total_kb: int | None = None
        free_kb: int | None = None
        with open(_MEMINFO_PATH, encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    total_kb = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    free_kb = int(line.split()[1])
        if total_kb is None or free_kb is None:
            return _MEMORY_SENTINEL
        return MemoryInfo(total_mb=total_kb // 1024, free_mb=free_kb // 1024)
    except (OSError, ValueError, IndexError):
        return _MEMORY_SENTINEL


@dataclass(frozen=True)
class StorageInfo:
    total_gb: float
    free_gb: float


_STORAGE_SENTINEL = StorageInfo(total_gb=-1.0, free_gb=-1.0)


def storage_info() -> StorageInfo:
    try:
        usage = shutil.disk_usage("/")
        return StorageInfo(
            total_gb=usage.total / 1024**3,
            free_gb=usage.free / 1024**3,
        )
    except OSError:
        return _STORAGE_SENTINEL


@dataclass
class BluetoothStatus:
    enabled: bool
    connected_devices: list[str]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BluetoothStatus):
            return NotImplemented
        return (
            self.enabled == other.enabled
            and self.connected_devices == other.connected_devices
        )


def bluetooth_status() -> BluetoothStatus:
    try:
        show = subprocess.run(  # noqa: S603  # nosec B603 — hardcoded absolute path, no user input
            ["/usr/bin/bluetoothctl", "show"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        powered = False
        for line in show.stdout.splitlines():
            if "Powered:" in line:
                powered = "yes" in line.lower()
                break
        if not powered:
            return BluetoothStatus(enabled=False, connected_devices=[])

        devices_result = subprocess.run(  # noqa: S603  # nosec B603 — hardcoded absolute path, no user input
            ["/usr/bin/bluetoothctl", "devices", "Connected"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        devices: list[str] = []
        for line in devices_result.stdout.splitlines():
            # Format: "Device AA:BB:CC:DD:EE:FF FriendlyName"
            parts = line.strip().split(" ", 2)
            if len(parts) >= 3:
                devices.append(parts[2])
            elif len(parts) == 2:
                devices.append(parts[1])  # fallback: MAC only
        return BluetoothStatus(enabled=True, connected_devices=devices)
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return BluetoothStatus(enabled=False, connected_devices=[])
