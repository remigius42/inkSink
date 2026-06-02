## MODIFIED Requirements

### Requirement: set_content triggers full refresh and resets framebuffer

`Compositor.set_content(img: Image)` SHALL accept a PIL Image, reset the
Scroll Offset to 0, retain the full image for scroll operations, crop the
Content Zone region (rows 0 through `content_zone_height − 1`) from the
image, composite it into the framebuffer at the correct y-offset (below the
status bar when shown), draw chrome, and call `display.display_full()` or
`display.display_4gray()` according to the App's display mode. This is the
natural App transition point; all previous framebuffer state is discarded.

#### Scenario: New content replaces previous framebuffer state

- **WHEN** `set_content(img)` is called after a prior screen state
- **THEN** the framebuffer is fully redrawn from the new image and current
  chrome state

#### Scenario: set_content with 4gray mode calls display_4gray

- **WHEN** the App's display mode is `"4gray"` and `set_content(img)` is called
- **THEN** `display.display_4gray()` is used for the full refresh
