## ADDED Requirements

### Requirement: display.vertical_scroll_step configures scroll step size

`DEFAULTS` in `core/config.py` SHALL include `display.vertical_scroll_step`
with a default value of 50 (pixels). Apps MAY override this via
`apps.<name>.display.vertical_scroll_step`. The Compositor SHALL read the
per-App override first and fall back to the global default.

#### Scenario: Default scroll step is used when not configured

- **WHEN** neither `display.vertical_scroll_step` nor a per-App override is set
- **THEN** the Compositor uses a step of 50 pixels per scroll action

#### Scenario: Per-App override takes precedence over global default

- **WHEN** `apps.ebooks.display.vertical_scroll_step` is set to 100 and
  `display.vertical_scroll_step` is 50
- **THEN** the Compositor uses 100 px per scroll action when the ebooks App
  is active

### Requirement: renderer.max_image_height caps rendered image height

`DEFAULTS` in `core/config.py` SHALL include `renderer.max_image_height`
with a default value of 8000 (pixels, approximately 10× portrait screen
height). `renderer.render()` SHALL truncate any image taller than this value
to `max_image_height` rows and emit a warning. This is a memory-safety
stopgap for Pi Zero; content-side chunking is the long-term solution for
ebook-length content.

#### Scenario: Image within cap is returned unchanged

- **WHEN** `renderer.render()` produces an image of height ≤ `max_image_height`
- **THEN** the full image is returned with no truncation

#### Scenario: Image exceeding cap is truncated with a warning

- **WHEN** `renderer.render()` produces an image taller than `max_image_height`
- **THEN** the returned image is cropped to `max_image_height` rows and a
  warning is logged identifying the content hash and actual vs cap height

#### Scenario: Cap is configurable

- **WHEN** `renderer.max_image_height` is set to 4000 in config
- **THEN** `renderer.render()` uses 4000 as the truncation threshold
