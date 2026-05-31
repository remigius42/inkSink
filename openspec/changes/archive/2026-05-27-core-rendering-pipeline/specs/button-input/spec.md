<!-- spellchecker:ignore mosi pinout raspi sclk -->

## MODIFIED Requirements

### Requirement: Buttons are mapped to generic positional IDs

`input.py` SHALL rename `_DEFAULT_PIN_MAP` to use generic positional IDs
`btn_1`–`btn_8` instead of Anki-specific action names. The `power` entry SHALL
be removed — PiSugar owns hardware power-on/off via its own button. Updated
default mapping (8 buttons, 4×2 grid on bottom edge):

| ID | GPIO | Physical pin |
| --- | --- | --- |
| `btn_1` | 4 | 7 |
| `btn_2` | 12 | 32 |
| `btn_3` | 13 | 33 |
| `btn_4` | 16 | 36 |
| `btn_5` | 19 | 35 |
| `btn_6` | 22 | 15 |
| `btn_7` | 26 | 37 |
| `btn_8` | 27 | 13 |

Pin selection rationale (see <https://pinout.xyz> for the full Pi Zero 2 W
pinout):

- GPIO 17 was originally proposed for btn_5 but conflicts with the Waveshare
  HAT RST line; GPIO 22 (physical pin 15) is a clean general-purpose pin with
  no alt-function conflict on this assembly.
- Waveshare 7.5" V2 HAT occupies: GPIO 8 (CS/CE0), 10 (MOSI), 11 (SCLK),
  17 (RST), 24 (BUSY), 25 (DC).
- PiSugar 3 uses I2C: GPIO 2 (SDA) and GPIO 3 (SCL).
- All eight button pins are free of the above assignments. Verify on first
  assembly with a multimeter or `raspi-gpio get <pin>` before soldering.

The mapping SHALL remain overridable via `config.yml` (`input.pin_map`).

#### Scenario: Default mapping uses generic IDs

- **WHEN** `InputHandler` is instantiated without a custom mapping
- **THEN** GPIO pin 12 maps to the action `btn_2`

#### Scenario: power action is not present in default mapping

- **WHEN** `InputHandler` is instantiated without a custom mapping
- **THEN** `"power"` is not a value in the active pin map

### Requirement: `wait_for_action()` returns a generic button ID

`wait_for_action()` SHALL return one of `btn_1`–`btn_8`. Callers are
responsible for mapping IDs to semantic actions (e.g. Anki App maps `btn_5` to
"Again"). The return value SHALL be the action string value from the active
`_pin_map` (`dict[int, str]`), not the GPIO pin number key.

#### Scenario: Returns generic ID on press

- **WHEN** the button wired to GPIO 19 is pressed cleanly
- **THEN** `wait_for_action()` returns `"btn_5"`
