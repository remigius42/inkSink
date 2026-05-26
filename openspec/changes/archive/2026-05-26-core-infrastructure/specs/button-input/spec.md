## ADDED Requirements

### Requirement: Buttons are mapped to named actions

`input.py` SHALL define a mapping from GPIO BCM pin numbers to action names.
Default mapping (from build guide):

| Action        | GPIO |
| ------------- | ---- |
| `power`       | 4    |
| `show_answer` | 12   |
| `again`       | 13   |
| `hard`        | 16   |
| `good`        | 19   |
| `easy`        | 26   |

The mapping SHALL be overridable via `config.yml`.

#### Scenario: Default mapping is applied

- **WHEN** `InputHandler` is instantiated without a custom mapping
- **THEN** GPIO pin 12 maps to the action `show_answer`

### Requirement: Button presses are debounced

A button press SHALL only be registered if the pin reads LOW for at least
50ms continuously. Bounces shorter than 50ms SHALL be ignored.

#### Scenario: Bounce is ignored

- **WHEN** a GPIO pin reads LOW for 20ms then returns HIGH
- **THEN** no action is registered

#### Scenario: Clean press is registered

- **WHEN** a GPIO pin reads LOW for 60ms
- **THEN** exactly one action event is registered

### Requirement: `wait_for_action()` blocks until a button is pressed

`input.py` SHALL provide a `wait_for_action()` function that blocks and
returns the action name of the first button press detected. `setup()` MUST
be called before `wait_for_action()`; calling `wait_for_action()` without
a prior `setup()` SHALL raise `RuntimeError`.

#### Scenario: Returns action name on press

- **WHEN** the `good` button (GPIO 19) is pressed cleanly
- **THEN** `wait_for_action()` returns `"good"`

#### Scenario: Raises if setup not called

- **WHEN** `wait_for_action()` is called without a prior `setup()`
- **THEN** `RuntimeError` is raised

### Requirement: GPIO uses internal pull-ups

All button pins SHALL be configured with `GPIO.PUD_UP` (active-low). No
external resistors are required.

#### Scenario: Pin configured with pull-up

- **WHEN** `InputHandler` is initialized
- **THEN** each button pin is set to `GPIO.IN` with `GPIO.PUD_UP`
