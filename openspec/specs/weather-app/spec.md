<!-- spellchecker:ignore Effretikon pressable -->

## Purpose

Display wttr.in forecast PNGs in landscape orientation with multi-location
auto-cycling, manual navigation, and location label/coordinate overlays.

## Requirements

### Requirement: Weather App displays wttr.in forecast PNG in landscape

The Weather App SHALL run in landscape orientation and display a wttr.in
pre-rendered PNG forecast for the current location. The PNG SHALL be fetched via
HTTPS from `https://wttr.in/{location}.png?2nTFQ`, inverted with
`PIL.ImageOps.invert()`, and passed to `Compositor.set_content()`. The App SHALL
NOT use wkhtmltoimage for content rendering.

#### Scenario: Forecast PNG is displayed on launch

- **WHEN** the Weather App is launched with at least one configured location
- **THEN** the display shows the inverted wttr.in PNG for the first location in
  the landscape content zone

#### Scenario: Both hosts unreachable shows informative error

- **WHEN** the HTTPS fetch for the PNG fails on both `https://wttr.in` and
  `https://wttr.is`
- **THEN** the display shows a message indicating that both weather hosts are
  unreachable, and the app remains interactive (buttons still respond)

### Requirement: Location label and coordinates rendered as Pillow overlays

The Compositor content image SHALL have a location label rendered at the top and
coordinates rendered at the bottom using `PIL.ImageFont.truetype` with DejaVu
Sans Mono at 13pt. The label SHALL be the configured `label` value if present,
otherwise `nearest_area[0].areaName[0].value` from the JSON response. The
coordinates SHALL be `"{latitude}, {longitude}"` from the JSON response.

#### Scenario: Configured label overrides resolved name

- **WHEN** a location entry has `label: "Home"` and the JSON resolves the area
  as "Effretikon"
- **THEN** the overlay displays "Home" as the top label

#### Scenario: Resolved name used when label absent

- **WHEN** a location entry has no `label` field
- **THEN** the overlay displays the `areaName` value from the JSON response

#### Scenario: Coordinates always shown in footer

- **WHEN** any location is displayed
- **THEN** the bottom overlay shows `"{latitude}, {longitude}"` from the JSON
  response regardless of whether a label was configured

### Requirement: JSON metadata fetched once per location at startup

On app launch, the Weather App SHALL fetch `wttr.in/{location}?format=j1` for
each configured location exactly once. The response SHALL be cached in memory
for the process lifetime. The cached data SHALL provide the label fallback and
coordinate footer for all subsequent renders of that location.

#### Scenario: JSON fetched once, not on every cycle

- **WHEN** the Weather App cycles through a location multiple times
- **THEN** only one JSON HTTP request is made for that location (at startup)

#### Scenario: JSON fetch failure falls back to location string

- **WHEN** the JSON fetch for a location fails at startup
- **THEN** the configured `location` string is used as the label fallback and
  coordinates are omitted from the footer

### Requirement: Auto-cycling advances locations on a configurable timer

The Weather App SHALL cycle through configured locations automatically using a
`threading.Timer` with interval `apps.weather.cycle_speed_seconds` (default:
30). Cycling SHALL be enabled on launch. The timer SHALL be reset after each
location transition (including manual navigation). The cycling state SHALL be
toggled by `btn_3`.

#### Scenario: Auto-advance after cycle interval

- **WHEN** `cycle_speed_seconds` elapses with cycling enabled
- **THEN** the display advances to the next location (wrapping from last to
  first)

#### Scenario: btn_3 pauses cycling

- **WHEN** cycling is active and `btn_3` is pressed
- **THEN** cycling stops, the timer is cancelled, and `btn_3` label changes to
  indicate "resume"

#### Scenario: btn_3 resumes cycling

- **WHEN** cycling is paused and `btn_3` is pressed
- **THEN** cycling resumes from the current location and `btn_3` label reverts
  to indicate "pause"

### Requirement: Manual navigation with btn_2 and btn_4

`btn_2` SHALL navigate to the previous location (wrapping); `btn_4` SHALL
navigate to the next location (wrapping). Manual navigation SHALL reset the
cycle timer without disabling auto-cycling.

#### Scenario: Next location wraps around

- **WHEN** `btn_4` is pressed while the last location is displayed
- **THEN** the display shows the first location

#### Scenario: Manual navigation resets cycle timer

- **WHEN** `btn_4` is pressed while cycling is active
- **THEN** the cycle timer resets; the next auto-advance occurs
  `cycle_speed_seconds` after the manual press

### Requirement: Direct location shortcuts on btn_5–btn_8

`btn_5`–`btn_8` SHALL be mapped to locations by index according to
`apps.weather.location_shortcuts` (default: `[0, 1, 2, 3]`). Each button SHALL
display the label of the mapped location (truncated to fit the slot). If an
index exceeds the number of configured locations, the button SHALL be rendered
with a `None` label (invisible). Pressing a shortcut button SHALL navigate
directly to that location and reset the cycle timer.

#### Scenario: Shortcut navigates directly to location

- **WHEN** `btn_5` is pressed and `location_shortcuts[0]` is `2`
- **THEN** the display shows location at index 2

#### Scenario: Out-of-range shortcut renders as invisible

- **WHEN** `location_shortcuts` maps a button to an index beyond the configured
  location list
- **THEN** that button renders as `None` (invisible, not pressable)

### Requirement: Weather App config schema

`apps.weather` in Config SHALL support:

- `locations`: list of objects with required `location: str` and optional
  `label: str`
- `cycle_speed_seconds`: int, default `30`
- `location_shortcuts`: list of up to 4 location indices, default `[0, 1, 2, 3]`

#### Scenario: Minimal config with one location — cycling acts as periodic refresh

- **WHEN** config contains only `apps.weather.locations: [{location: "Zürich"}]`
- **THEN** the app launches, shows Zürich, and the cycle timer fires every
  `cycle_speed_seconds` to re-fetch and re-render the same location (periodic
  refresh). Prev (btn_2) and Next (btn_4) are rendered as `None` (invisible).
  Pause/Resume (btn_3) remains functional.

#### Scenario: Single location hides Prev and Next buttons

- **WHEN** exactly one location is configured
- **THEN** btn_2 (Prev) and btn_4 (Next) are `None`; btn_3 (Pause/Resume) is
  visible

#### Scenario: No locations configured shows informative message

- **WHEN** `apps.weather.locations` is empty or absent
- **THEN** the display shows "No weather locations configured." and only btn_1
  (Menu) is visible; pressing any button returns to the Launcher

#### Scenario: Custom shortcuts respected

- **WHEN** `location_shortcuts: [0, 2]` is configured with 3 locations
- **THEN** btn_5 → location 0, btn_6 → location 2, btn_7 and btn_8 invisible
