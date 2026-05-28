<!-- spellchecker:ignore mosi sclk -->

# GPIO Pin Mapping

From the build guide. These are the recommended BCM pin numbers.

## Display HAT (SPI + Control) — pre-assigned, do not use for buttons

| Signal | GPIO (BCM) | Notes |
| -- | -- | -- |
| CE0/CS | 8 | |
| MOSI | 10 | |
| SCLK | 11 | |
| RST | 17 | |
| PWR | 18 | Power enable (GPIO_PWR_PIN in epdconfig.py) |
| BUSY | 24 | |
| DC | 25 | |

## PiSugar 3 (I2C + Power) — pre-assigned

| Signal | GPIO (BCM) |
| -- | -- |
| SDA | 2 |
| SCL | 3 |

I2C address: **0x57**

## Buttons — default mapping

| Action | GPIO (BCM) |
| -- | -- |
| `power` | 4 |
| `show_answer` | 12 |
| `again` | 13 |
| `hard` | 16 |
| `good` | 19 |
| `easy` | 26 |

All button pins: active-low, `GPIO.PUD_UP` (internal pull-up). No external
resistors needed.

## Available pins for future use

GPIO 5, 6, 7, 14, 15, 20, 21, 22, 23, 27 (plus multiple GND pins)
