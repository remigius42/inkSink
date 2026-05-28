<!-- spellchecker:ignore distrelec eckstein mosi noto opencircuit pisugar -->

<!-- spellchecker:ignore reichelt sclk tindie waveshare -->

# Build Guide

Portable e-ink device for Anki flashcard reviews and reading. Runs on a
Raspberry Pi Zero 2 W with a Waveshare 7.5" display and PiSugar 3 battery.

**Bill of materials:** [hardware/bom.md](../hardware/bom.md) — ~€150 total,
CH/EU sources listed.

______________________________________________________________________

## Physical Design

### Form Factor

_Dimensions are provisional until the case design is finalized._

- **Width:** ~110mm (portrait orientation — long display edge vertical)
- **Height:** ~210mm (display area + bezel + 35mm bottom button section)
- **Depth:** TBD — stack is ~26mm (2mm display + ~2mm air gap + 22mm
  electronics) plus wall thickness (≥1.5mm) and a sunken display recess;
  expect ~28–32mm
- **Weight:** ~140g (estimate)

### Component Stack (front to back)

```text
[FRONT]
1. E-ink display panel (~2mm) — viewing surface
        ║ FPC cable
2. E-ink HAT PCB (~5mm with components)
        ║ 40-pin socket + 11mm standoffs
3. Raspberry Pi Zero 2 W (~5mm with components)
        ○ Pogo pins on underside
4. PiSugar 3 PCB (~4mm with components)
        ~ short cable
5. Battery pack (6mm, beside stack in cavity)
[BACK]
```

### Button Layout (bottom edge, 4×2 grid)

```text
[ btn_1 ] [ btn_2 ] [ btn_3 ] [ btn_4 ]
[ btn_5 ] [ btn_6 ] [ btn_7 ] [ btn_8 ]
```

Labels are rendered on-screen by the software (see [ADR 0007](adr/0007-softkey-button-model.md)). `btn_1` is
reserved as Menu/Back across all apps (see [ADR 0010](adr/0010-launcher-first-architecture.md)).

### 3D-Printed Case

Source files in `hardware/case/` (OpenSCAD, parametric). All dimensions
adjustable via `hardware/case/params.scad`. Snap-fit join; optional M2.5 corner
screws. Display window is an open cutout; button holes sized for 12mm tactile
buttons.

______________________________________________________________________

## Electronics Assembly

### GPIO Pin Usage

| Subsystem | Pins |
| -- | -- |
| E-ink HAT — SPI | GPIO 8, 10, 11 (CE0/CS, MOSI, SCLK) |
| E-ink HAT — control | GPIO 17, 18, 24, 25 (RST, PWR, BUSY, DC) |
| PiSugar 3 — I2C | GPIO 2, 3 (SDA, SCL) |
| PiSugar 3 — power | Pins 2, 4, 6 (5V, 5V, GND via pogo pins) |
| Buttons | GPIO 4, 5, 6, 7, 12, 13, 16, 19 (btn_1–btn_8) |

Pin assignments per the [Waveshare 7.5inch e-Paper HAT
manual](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_Manual) and [PiSugar
3
docs](https://docs.pisugar.com/docs/product-wiki/battery/pisugar3/pisugar-3-series).
PiSugar 3 I2C addresses: `0x57` (battery/power management), `0x68` (RTC).

### Button Mapping

| Button | GPIO |
| -- | -- |
| btn_1 | 4 |
| btn_2 | 5 |
| btn_3 | 6 |
| btn_4 | 7 |
| btn_5 | 12 |
| btn_6 | 13 |
| btn_7 | 16 |
| btn_8 | 19 |

All buttons: common GND, internal pull-up enabled in software.

### Button Wiring

The HAT's female socket sits directly on the GPIO header with only 11mm
clearance — standard Dupont connectors won't fit.

**Technique:** solder 28AWG silicone wire directly to the side of each GPIO
header pin before installing the HAT. Cover each joint with 2mm heat shrink
tubing. Route wires out the side once the HAT is seated on 11mm standoffs.

#### Steps

1. Cut 28AWG wires to ~15cm. Strip 2mm and slide heat shrink onto each.
1. Solder wire to the **side** of the GPIO pin (between plastic base and tip).
1. Slide heat shrink over joint and apply heat.
1. Repeat for all 8 button pins + 1 GND.

### Assembly Order

1. Attach PiSugar 3 to Pi (pogo pins; secure with screws).
1. Solder button wires to GPIO pins (see Button Wiring above).
1. Install 11mm standoffs; plug HAT onto header; route wires out the side; screw down.
1. Plug battery cable into PiSugar 3.
1. Place stack in case; connect free wire ends to tactile buttons; close case.

______________________________________________________________________

## Software Setup

See [setup.md](setup.md) for the full provisioning walkthrough (OS flash,
Ansible vault, deploy + verify playbooks).

**Quick checklist:**

- [ ] Flash Raspberry Pi OS Lite (64-bit) via Raspberry Pi Imager
- [ ] Boot Pi; verify SSH access at `inksink.local`
- [ ] Configure Ansible vault (`ansible/group_vars/all/vault.yml`)
- [ ] Run `ansible-playbook ansible/playbooks/setup.yml`
- [ ] Run `ansible-playbook ansible/playbooks/deploy.yml`
- [ ] Run `ansible-playbook ansible/playbooks/verify.yml`

______________________________________________________________________

> **Archive:** The original Claude-generated build guide (initial project
> sketch, may contain outdated information) is preserved at
> [`docs/archive/anki-eink-device-build-guide.md`](archive/anki-eink-device-build-guide.md).
