## ADDED Requirements

### Requirement: Battery level is read from PiSugar via I2C

`state.py` SHALL provide a `battery_percent() -> int` function that reads
the current battery level from the PiSugar 3 over I2C (address 0x57) and
returns a value in the range 0–100.

#### Scenario: Returns integer in valid range

- **WHEN** `battery_percent()` is called on a device with PiSugar 3 attached
- **THEN** an integer between 0 and 100 is returned

#### Scenario: Returns -1 when I2C is unavailable

- **WHEN** `battery_percent()` is called on a machine without PiSugar (dev machine)
- **THEN** `-1` is returned without raising an exception

### Requirement: WiFi status is read via nmcli

`state.py` SHALL provide `wifi_status() -> WifiStatus` where `WifiStatus` is a
dataclass with `connected: bool`, `ssid: str | None`, and `strength: int`
(0–100). `strength` and `ssid` SHALL be `-1` / `None` when not connected or
when `nmcli` is unavailable.

#### Scenario: Connected — returns SSID and strength

- **WHEN** `wifi_status()` is called and the device is connected to WiFi
- **THEN** `connected` is `True`, `ssid` is the network name, and `strength`
  is an integer between 0 and 100

#### Scenario: Disconnected — returns sentinel values

- **WHEN** `wifi_status()` is called and no WiFi connection is active
- **THEN** `connected` is `False`, `ssid` is `None`, and `strength` is `-1`

#### Scenario: nmcli unavailable — returns sentinel values without raising

- **WHEN** `wifi_status()` is called on a machine without `nmcli`
- **THEN** `connected` is `False`, `ssid` is `None`, `strength` is `-1`, and
  no exception is raised

#### Scenario: SSID containing a colon is returned correctly

- **WHEN** `wifi_status()` is called and the active SSID contains a literal `:`
  (escaped as `\:` in nmcli terse output)
- **THEN** `ssid` contains the unescaped network name with the colon intact
