## ADDED Requirements

### Requirement: Settings screen shows current config read-only

In MENU state, `btn_6` SHALL be labeled "Settings" and SHALL transition to
the SETTINGS state. The SETTINGS screen SHALL display all keys from
`load_settings()` as a flat list of `key: value` pairs using the following
canonical flattening:

- Nested dicts produce dot-separated keys (e.g. `parent.child.key`).
- Lists produce zero-based bracket-indexed keys (e.g. `parent.list[0].item`).
- The final flattened keys SHALL be sorted lexicographically (Unicode code point
  order) before rendering.
- Scalar values are preserved as-is, except that any key whose name contains
  `password` or `secret` (case-insensitive) SHALL have its value replaced with
  `***` in the output.

Credential values (keys containing `password` or `secret`, case-insensitive)
SHALL be masked as `***`. `btn_1` SHALL be labeled "Menu" and SHALL return to
MENU. No editing is possible in v1.

#### Scenario: Settings screen shows config keys

- **WHEN** `btn_6` is pressed in MENU state
- **THEN** the display shows a list of config key/value pairs from `load_settings()`

#### Scenario: Credential values are masked

- **WHEN** the settings screen is shown and config contains `ankiweb_password`
- **THEN** the displayed value is `***`

### Requirement: Settings screen is scrollable

The SETTINGS screen SHALL support vertical scrolling via `btn_6` (scroll down,
label "↓") and `btn_7` (scroll up, label "↑"). Each press scrolls by 5 lines
(~100px at 20px/line). The offset SHALL clamp at 0 (top) and at
`max(0, total_lines − visible_lines)` (bottom) — it SHALL NOT wrap.

When content extends below the visible area, a "↓ more" indicator SHALL be
shown at the bottom of the content area. When the offset is greater than 0, a
"↑ more" indicator SHALL be shown at the top. Both indicators are hidden when
the content fits on one screen.

#### Scenario: Scrolling down reveals more keys

- **WHEN** the settings list is longer than the visible area and `btn_6` is
  pressed in SETTINGS state
- **THEN** the display re-renders with the content shifted down by 5 lines

#### Scenario: Offset clamps at bottom

- **WHEN** the user presses `btn_6` (scroll down) and the bottom of the list
  is already visible
- **THEN** the offset does not change and no re-render occurs

#### Scenario: Scroll indicators shown

- **WHEN** content extends below the visible area
- **THEN** a "↓ more" indicator is visible at the bottom of the content area

#### Scenario: Menu returns from settings

- **WHEN** `btn_1` is pressed in SETTINGS state
- **THEN** the Launcher returns to MENU state
