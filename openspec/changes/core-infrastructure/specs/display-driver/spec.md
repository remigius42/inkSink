## ADDED Requirements

### Requirement: Display initializes before use

`display.py` SHALL provide an `init()` call that initializes the Waveshare
7.5" V2 HAT via SPI before any image is written. Calling `display()` or
`display_partial()` without prior `init()` SHALL raise `RuntimeError`.

#### Scenario: Init required before display

- **WHEN** `display_partial(image)` is called without a prior `init()`
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

### Requirement: Full refresh to clear ghosting

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
