## Purpose

Thin wrapper around the Waveshare 7.5" V2 e-ink HAT driver. Manages
init/sleep lifecycle, partial vs full refresh, auto-sleep idle timer, and
the partial-refresh counter that triggers a full clear to prevent ghosting.

## Requirements

### Requirement: Display initializes before use

`display.py` SHALL provide an `init()` call that initializes the Waveshare
7.5" V2 HAT via SPI before any image is written. Calling `display_partial()`,
`display_full()`, or `display_4gray()` without prior `init()` SHALL raise
`RuntimeError`.

#### Scenario: Init required before display

- **WHEN** `display_partial(image)`, `display_full(image)`, or `display_4gray(image)`
  is called without a prior `init()`
- **THEN** `RuntimeError` is raised with a message indicating init is required

### Requirement: Partial refresh for card transitions

The display SHALL support partial refresh (`display_partial(image)`) for
card-to-card transitions. Partial refresh SHALL complete in under 1 second
on the Waveshare 7.5" V2 hardware.

#### Scenario: Partial refresh updates the screen

- **WHEN** `display_partial(image)` is called with a valid 800×480 1-bit PIL image
- **THEN** the display updates within 1 second without a full clear cycle

### Requirement: 4-gray refresh for image-quality-sensitive Apps

The display SHALL support 4-gray full refresh (`display_4gray(image)`)
accepting a PIL image in mode `"L"` quantized to 4 levels (0, 85, 170, 255).
Only available on screens sold after Oct 2023.

#### Scenario: 4-gray refresh renders grayscale content

- **WHEN** `display_4gray(image)` is called with a valid 800×480 PIL `"L"` image
- **THEN** the display performs a full refresh cycle rendering four gray levels

#### Scenario: 4-gray refresh does not affect the partial-refresh counter

- **WHEN** `display_4gray(image)` is called with a non-zero partial-refresh count
- **THEN** `_partial_count` is unchanged

### Requirement: Full refresh to clear ghosting

The partial-refresh counter SHALL only be incremented by `display_partial()`
calls. `display_4gray()` SHALL leave the counter unchanged because every
4-gray call is already a full refresh — the counter is meaningless in that
mode.

The display SHALL support full refresh (`display_full(image)`) that performs
a complete clear-and-draw cycle. Full refresh SHALL be called automatically
after every 20 partial refreshes unless overridden by config.

#### Scenario: Auto full refresh after threshold

- **WHEN** `display_partial()` has been called 20 times since the last full refresh
- **THEN** the next call triggers a full refresh instead of a partial refresh

### Requirement: Display sleeps when idle

`sleep()` SHALL put the e-ink controller into low-power mode. `init()` SHALL
be called again before the next display update after `sleep()`.

#### Scenario: Sleep reduces power consumption

- **WHEN** `sleep()` is called after displaying a card
- **THEN** the display enters low-power mode and no further SPI activity occurs
  until the next `init()`

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
