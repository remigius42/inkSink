## Purpose

The Launcher STATUS screen shows live device diagnostics on demand. Reached via
`btn_5` in MENU. Displays 10 fields (time, battery, WiFi, hostname, IP,
Bluetooth, load, memory, storage, version) sourced from `core/state.py`.
All fields degrade gracefully to `"unavailable"` when hardware or tools are absent.

## Requirements

### Requirement: Status screen shows device diagnostics

In MENU state, `btn_5` SHALL be labeled "Status" and SHALL transition to the
STATUS state. The STATUS screen SHALL display the following fields in this
order:

1. System time (current local time)
2. Battery percent (from PiSugar I2C; `-1` shown as "unavailable")
3. WiFi SSID and signal quality (or "Offline" if disconnected)
4. Hostname (`socket.gethostname()`)
5. IP address (outbound interface IP; see notes/pi-ip-lookup.md; shown as
   "unavailable" when lookup fails or returns a loopback address)
6. Bluetooth state — "off" if disabled; "on" with connected device list if
   enabled (friendly name, fallback to MAC address; empty list shown as "no
   devices connected")
7. System load — 1m / 5m / 15m averages (`os.getloadavg()`; shown as
   "unavailable" on non-Linux hosts)
8. Memory — `MemTotal` MB / `MemAvailable` MB (from `/proc/meminfo`; note:
   `MemAvailable` is used for "free", not `MemFree`; shown as "unavailable" if
   either key is absent or the file is unreadable)
9. Storage — total GB / free GB (root `/` via `shutil.disk_usage`)
10. Tag version (`INKSINK_VERSION` env var; fallback `"unknown"`)

`btn_1` SHALL be labeled "Menu" and SHALL return to MENU. All other buttons
are inactive. The STATUS screen does NOT scroll in v1 — all 10 fields are
displayed simultaneously, truncated to fit the content area. Hostname and
Bluetooth device names are truncated to 30 characters; Bluetooth connected
devices shown as a comma-separated list on a single line (e.g. "DevA, DevB")
rather than one-per-row.

Sentinel values (hardware unavailable, subprocess failure) SHALL be displayed
as `"unavailable"` rather than raising an exception.

#### Scenario: Status screen shows battery and WiFi

- **WHEN** `btn_5` is pressed in MENU state
- **THEN** the display shows battery percent and WiFi SSID (or "Offline")

#### Scenario: Status screen shows hostname and IP

- **WHEN** the STATUS screen is shown
- **THEN** hostname and IP address are displayed

#### Scenario: Bluetooth shown as off when disabled

- **WHEN** the STATUS screen is shown and Bluetooth is disabled
- **THEN** the Bluetooth row shows "off"

#### Scenario: Bluetooth shows connected devices

- **WHEN** the STATUS screen is shown and a device is connected via Bluetooth
- **THEN** the Bluetooth row shows the device's friendly name (or MAC if no
  name is available)

#### Scenario: System load is displayed

- **WHEN** the STATUS screen is shown
- **THEN** load averages for 1m, 5m, and 15m are displayed

#### Scenario: Memory and storage are displayed

- **WHEN** the STATUS screen is shown
- **THEN** total and free memory (MB) and total and free storage (GB) are
  displayed

#### Scenario: Tag version is displayed

- **WHEN** the STATUS screen is shown and `INKSINK_VERSION` is set in the
  environment
- **THEN** the version row shows the value of `INKSINK_VERSION`

#### Scenario: Tag version fallback

- **WHEN** the STATUS screen is shown and `INKSINK_VERSION` is not set
- **THEN** the version row shows `"unknown"`

#### Scenario: Menu returns from status

- **WHEN** `btn_1` is pressed in STATUS state
- **THEN** the Launcher returns to MENU state
