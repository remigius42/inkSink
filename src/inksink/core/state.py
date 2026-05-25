"""On-demand hardware state reads: battery (PiSugar I2C) and WiFi (nmcli).

No session state lives here — session tracking belongs to each App.
Both functions return sentinel values (-1 / False / None) when the
underlying hardware or tool is unavailable, so they are safe to call on
a dev machine.
"""

from __future__ import annotations

import subprocess
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


def wifi_status() -> WifiStatus:
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "active,ssid,signal", "dev", "wifi"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return _WIFI_SENTINEL
        for line in result.stdout.splitlines():
            first = line.index(":") if ":" in line else -1
            last = line.rindex(":") if ":" in line else -1
            if first == -1 or first == last:
                continue
            active = line[:first]
            if active != "yes":
                continue
            raw_ssid = line[first + 1 : last]
            strength = int(line[last + 1 :])
            ssid = raw_ssid.replace("\\:", ":").replace("\\\\", "\\") or None
            return WifiStatus(connected=True, ssid=ssid, strength=strength)
        return _WIFI_SENTINEL
    except (FileNotFoundError, OSError, subprocess.SubprocessError, ValueError):
        return _WIFI_SENTINEL
