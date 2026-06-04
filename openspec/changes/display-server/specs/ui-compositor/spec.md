## MODIFIED Requirements

### Requirement: set_content triggers full refresh and resets framebuffer

`Compositor.set_content(img: Image, mode: str | None = None)` SHALL accept a
PIL Image and an optional display mode (`"1bit"` or `"4gray"`). When `mode` is
provided it overrides `self._display_mode` for this call only; when omitted,
`self._display_mode` is used. The method SHALL reset the Scroll Offset to 0,
retain the full image for scroll operations, crop the Content Zone region (rows
0 through `content_zone_height − 1`) from the image, composite it into the
framebuffer at the correct y-offset (below the status bar when shown), draw
chrome, and call `display.display_full()` or `display.display_4gray()`
accordingly. This is the natural App transition point; all previous framebuffer
state is discarded.

#### Scenario: New content replaces previous framebuffer state

- **WHEN** `set_content(img)` is called after a prior screen state
- **THEN** the framebuffer is fully redrawn from the new image and current
  chrome state

#### Scenario: set_content with 4gray mode calls display_4gray

- **WHEN** `set_content(img, mode="4gray")` is called
- **THEN** `display.display_4gray()` is used for the full refresh

#### Scenario: set_content with no mode argument uses the App's configured display_mode

- **WHEN** `set_content(img)` is called with no mode argument
- **AND** `self._display_mode` is `"1bit"`
- **THEN** `display.display_full()` is used for the full refresh

#### Scenario: Existing App with display_mode=4gray is unaffected

- **WHEN** `set_content(img)` is called with no mode argument
- **AND** `self._display_mode` is `"4gray"`
- **THEN** `display.display_4gray()` is used for the full refresh
