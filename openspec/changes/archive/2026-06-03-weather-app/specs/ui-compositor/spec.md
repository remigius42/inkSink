## MODIFIED Requirements

### Requirement: Content zone dimensions are publicly accessible

`Compositor` SHALL expose `content_zone_height() -> int` and
`content_zone_width() -> int` as public methods. These return the pixel
dimensions available to App content after subtracting all visible chrome
elements. Apps SHALL use these methods; they SHALL NOT access private Compositor
internals.

`content_zone_height()` returns the framebuffer height minus the status bar
height (when visible) and minus `BUTTON_BAR_SIZE` when the button bar edge is
`"top"` or `"bottom"`.

`content_zone_width()` returns the framebuffer width minus `BUTTON_BAR_SIZE`
when the button bar edge is `"left"` or `"right"` and buttons are visible. The
status bar does not affect width.

#### Scenario: Portrait — width is full framebuffer width

- **WHEN** orientation is `PORTRAIT` and buttons are visible
- **THEN** `content_zone_width()` returns the full framebuffer width (button bar
  is on the bottom edge, not a side edge)

#### Scenario: Landscape side bar — width is reduced

- **WHEN** orientation is `LANDSCAPE` and `portrait_rotation=90` (button bar on
  right edge) and buttons are visible
- **THEN** `content_zone_width()` returns `framebuffer_width − BUTTON_BAR_SIZE`

#### Scenario: Landscape top/bottom bar — width is not reduced

- **WHEN** orientation is `LANDSCAPE` and `portrait_rotation=0` or `180` (button
  bar on top or bottom edge) and buttons are visible
- **THEN** `content_zone_width()` returns the full framebuffer width

### Requirement: Content zone height is orientation-aware

`content_zone_height()` SHALL compute the available height for App content by
starting from the framebuffer height and subtracting only chrome elements whose
edge is `"top"` or `"bottom"`. The status bar (always top) SHALL be subtracted
when visible. `BUTTON_BAR_SIZE` SHALL be subtracted only when the button bar
edge is `"top"` or `"bottom"`. When the button bar edge is `"left"` or `"right"`
(landscape side bar), it occupies horizontal space and SHALL NOT be subtracted
from the height.

#### Scenario: Portrait subtracts button bar from height

- **WHEN** orientation is `PORTRAIT` and buttons are visible
- **THEN** `content_zone_height()` returns `framebuffer_height −
  STATUS_BAR_HEIGHT − BUTTON_BAR_SIZE`

#### Scenario: Landscape side bar does not reduce content height

- **WHEN** orientation is `LANDSCAPE` and `portrait_rotation=90` (button bar on
  right edge) and buttons are visible
- **THEN** `content_zone_height()` returns `framebuffer_height −
  STATUS_BAR_HEIGHT` (button bar does not reduce height)

#### Scenario: Landscape top/bottom bar still reduces content height

- **WHEN** orientation is `LANDSCAPE` and `portrait_rotation=0` or `180` (button
  bar on top or bottom edge) and buttons are visible
- **THEN** `content_zone_height()` returns `framebuffer_height −
  STATUS_BAR_HEIGHT − BUTTON_BAR_SIZE`
