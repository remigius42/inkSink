## ADDED Requirements

### Requirement: Logs screen shows recent systemd journal entries

In MENU state, `btn_7` SHALL be labeled "Logs" and SHALL transition to the
LOGS state. The LOGS screen SHALL display the last 100 lines of the systemd
journal for the `inksink` unit (`journalctl -u inksink -n 100 --no-pager
--output=short`). `btn_1` SHALL be labeled "Menu" and SHALL return to MENU.

If `journalctl` is unavailable or returns a non-zero exit code, the screen
SHALL show "unavailable" rather than raising an exception.

#### Scenario: Logs screen shows journal entries

- **WHEN** `btn_7` is pressed in MENU state
- **THEN** the display shows the most recent `inksink` journal entries

#### Scenario: Journal unavailable

- **WHEN** the LOGS screen is shown and `journalctl` is not found
- **THEN** the screen shows "unavailable"

### Requirement: Logs screen is scrollable

The LOGS screen SHALL support vertical scrolling via `btn_6` (scroll down,
label "↓") and `btn_7` (scroll up, label "↑") using the same mechanism as
the SETTINGS screen: 5-line increments, clamped at top and bottom, with
"↓ more" / "↑ more" indicators. The initial offset SHALL be at the bottom
(most recent entries visible first).

#### Scenario: Scrolling reveals older entries

- **WHEN** `btn_7` (scroll up) is pressed in LOGS state
- **THEN** the display re-renders with content shifted up by 5 lines

#### Scenario: Offset clamps at top

- **WHEN** the user presses `btn_7` (scroll up) and the top of the log is
  already visible
- **THEN** the offset does not change and no re-render occurs

#### Scenario: Menu returns from logs

- **WHEN** `btn_1` is pressed in LOGS state
- **THEN** the Launcher returns to MENU state
