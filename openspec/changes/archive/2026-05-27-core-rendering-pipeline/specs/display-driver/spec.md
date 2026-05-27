## ADDED Requirements

### Requirement: Display rotates images before driver handoff

`Display` SHALL rotate PIL images to match the physical driver buffer
(800×480) before calling the Waveshare driver. The rotation angle SHALL be
read from Config at `Display.__init__` time:

- `display.portrait_rotation` (default `90`) — degrees CCW (PIL convention)
  applied when `image.height > image.width`
- `display.landscape_rotation` (default `0`) — degrees CCW (PIL convention)
  applied when `image.width >= image.height`

The rotation SHALL use `Image.rotate(angle, expand=True)`, where `angle` is
the config value directly. PIL treats positive angles as counterclockwise; the
config values use the same convention. After rotation the image passed to the
driver SHALL always be exactly 800×480 pixels.

#### Scenario: Portrait image is rotated before driver handoff

- **WHEN** `display_partial(image)` is called with a 480×800 image and
  `display.portrait_rotation` is `90`
- **THEN** the Waveshare driver receives an 800×480 image (rotated 90° CCW)

#### Scenario: Landscape image passes through without rotation

- **WHEN** `display_partial(image)` is called with an 800×480 image and
  `display.landscape_rotation` is `0`
- **THEN** the Waveshare driver receives the image unchanged

#### Scenario: Non-zero landscape rotation is applied

- **WHEN** `display_full(image)` is called with an 800×480 image and
  `display.landscape_rotation` is `180`
- **THEN** the Waveshare driver receives the image rotated 180°

### Requirement: Rotation config values are validated to cardinal angles

`Display.__init__` SHALL raise `ValueError` if `display.portrait_rotation` or
`display.landscape_rotation` is not one of `{0, 90, 180, 270}`. This ensures
`Image.rotate(angle, expand=True)` always produces an exactly 800×480 buffer
after rotation — non-cardinal angles produce non-integer intermediate dimensions
that would corrupt the driver buffer.

#### Scenario: Invalid rotation angle raises ValueError

- **WHEN** `Display` is initialized with `display.portrait_rotation: 45`
- **THEN** `ValueError` is raised at init time, before any image is rendered

### Requirement: Rotation config keys have safe defaults

`core/config.py` DEFAULTS SHALL include `display.portrait_rotation: 90` and
`display.landscape_rotation: 0`. A fresh deploy with no `config.yml` SHALL
produce correct rotation for the standard case assembly without requiring
explicit config.

#### Scenario: Missing config uses defaults

- **WHEN** `load_settings()` is called with no `config.yml` present
- **THEN** `settings["display"]["portrait_rotation"]` is `90` and
  `settings["display"]["landscape_rotation"]` is `0`
