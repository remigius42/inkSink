## Purpose

Vertical scroll capability for the Compositor. Allows Apps to present content
taller than the Content Zone and navigate it via scroll actions, using partial
refresh for low-latency updates.

## Requirements

### Requirement: Compositor accepts PIL Image as content

`Compositor.set_content(img: Image)` SHALL accept a PIL Image, reset the
Scroll Offset to 0, crop the Content Zone region starting at offset 0 (i.e.
the top of the image), composite it into the framebuffer, draw chrome, and
trigger a full refresh. The full image SHALL be retained internally for
subsequent scroll operations.

#### Scenario: set_content resets scroll to top

- **WHEN** `set_content(img)` is called after a prior scroll action
- **THEN** the Scroll Offset is 0 and the top of the content image is displayed

#### Scenario: Content taller than Content Zone is cropped to viewport

- **WHEN** `set_content(img)` is called with an image taller than the Content
  Zone
- **THEN** only the first `content_zone_height` rows of the image are composited
  into the framebuffer

#### Scenario: Content shorter than or equal to Content Zone is placed as-is

- **WHEN** `set_content(img)` is called with an image whose height ≤ Content
  Zone height
- **THEN** the entire image is composited (no cropping) and scrolling is not
  possible

### Requirement: scroll_up and scroll_down shift the Scroll Offset

`Compositor.scroll_up()` and `Compositor.scroll_down()` SHALL shift the
Scroll Offset by `display.vertical_scroll_step` pixels (or the per-App override)
in the respective direction, re-crop the retained content image, redraw the
framebuffer, and call `display.display_partial()`. Both methods SHALL return
`(can_scroll_up: bool, can_scroll_down: bool)` reflecting whether further
scrolling is possible in each direction after the operation.

Scroll Offset SHALL be clamped: minimum 0, maximum
`content_image_height − content_zone_height`.

#### Scenario: scroll_down shifts content up by one step

- **WHEN** `scroll_down()` is called with Scroll Offset 0 and content image
  height > content zone height
- **THEN** Scroll Offset increases by `vertical_scroll_step`, the framebuffer
  shows content starting at that offset, and `display.display_partial()` is
  called

#### Scenario: scroll_up at top is a no-op

- **WHEN** `scroll_up()` is called with Scroll Offset 0
- **THEN** Scroll Offset remains 0, no display call is made, and
  `can_scroll_up` is `False`

#### Scenario: scroll_down at bottom is a no-op

- **WHEN** `scroll_down()` is called with Scroll Offset already at maximum
- **THEN** Scroll Offset is unchanged, no display call is made, and
  `can_scroll_down` is `False`

#### Scenario: can_scroll_up is False at top

- **WHEN** Scroll Offset is 0
- **THEN** both `scroll_up()` and `scroll_down()` return `can_scroll_up=False`

#### Scenario: can_scroll_down is False at bottom

- **WHEN** Scroll Offset equals `content_image_height − content_zone_height`
- **THEN** both `scroll_up()` and `scroll_down()` return `can_scroll_down=False`

#### Scenario: Scroll Offset is clamped at bottom

- **WHEN** `scroll_down()` would push Scroll Offset beyond the maximum
- **THEN** Scroll Offset is set to `content_image_height − content_zone_height`
  (not beyond) and `can_scroll_down` is `False`

### Requirement: Content Zone height accounts for visible chrome

The Compositor SHALL compute Content Zone height as screen height minus the
height of each chrome element that is currently being drawn (status bar,
button bar). When no chrome is drawn, Content Zone height equals screen height.

#### Scenario: Content Zone excludes status bar and button bar when both visible

- **WHEN** both status bar and button bar are active
- **THEN** content zone height equals screen height minus `STATUS_BAR_HEIGHT`
  minus `BUTTON_BAR_SIZE`

#### Scenario: Content Zone equals screen height when no chrome is drawn

- **WHEN** no buttons are set and no status bar is drawn
- **THEN** content zone height equals screen height
