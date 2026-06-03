## MODIFIED Requirements

### Requirement: Content zone height is orientation-aware

`_content_zone_height()` SHALL compute the available height for App content by
starting from the framebuffer height and subtracting only chrome elements whose
edge is `"top"` or `"bottom"`. The status bar (always top) SHALL be subtracted
when visible. `BUTTON_BAR_SIZE` SHALL be subtracted only when
`_button_bar_edge()` returns `"top"` or `"bottom"`. When the button bar edge is
`"left"` or `"right"` (landscape side bar), it occupies horizontal space and
SHALL NOT be subtracted from the height.

#### Scenario: Portrait subtracts button bar from height

- **WHEN** orientation is `PORTRAIT` and buttons are visible
- **THEN** `_content_zone_height()` returns `framebuffer_height −
  STATUS_BAR_HEIGHT − BUTTON_BAR_SIZE`

#### Scenario: Landscape side bar does not reduce content height

- **WHEN** orientation is `LANDSCAPE` and `portrait_rotation=90` (button bar on
  right edge) and buttons are visible
- **THEN** `_content_zone_height()` returns `framebuffer_height −
  STATUS_BAR_HEIGHT` (button bar does not reduce height)

#### Scenario: Landscape top/bottom bar still reduces content height

- **WHEN** orientation is `LANDSCAPE` and `portrait_rotation=0` or `180` (button
  bar on top or bottom edge) and buttons are visible
- **THEN** `_content_zone_height()` returns `framebuffer_height −
  STATUS_BAR_HEIGHT − BUTTON_BAR_SIZE`
