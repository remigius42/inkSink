<!-- spellchecker:ignore ankiweb boox noto paperwhite pnas wkhtmltoimage wttr -->

# [inkSink](https://github.com/remigius42/inkSink)

Copyright 2026 [Andreas Remigius Schmidt](https://github.com/remigius42)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%20OS%20Trixie-lightgrey.svg)
[![CI](https://github.com/remigius42/inkSink/actions/workflows/ci.yml/badge.svg)](https://github.com/remigius42/inkSink/actions/workflows/ci.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/5b2a8a4a7ced493ba762bfa1955f8a31)](https://app.codacy.com/gh/remigius42/inkSink/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/remigius42/inkSink?utm_source=oss&utm_medium=github&utm_campaign=remigius42%2FinkSink&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)

<img src="docs/logo.svg" alt="inkSink logo" width="300" /> <!-- markdownlint-disable-line MD033 -->

> **Status: Proof of Concept** — Software implemented; hardware not yet assembled.

A portable e-ink display device for spaced repetition learning and personal
dashboards. **ink** = e-ink display; **Sink** = terminal node in graph theory
where information flows to rest.

**Example use cases:**

- **Anki spaced repetition** — Distraction-free flashcard reviews
- **Information dashboard** — Weather and other push-rendered content _(Display
  Server planned)_

**Why inkSink?**

- Distraction-free by design (no notifications, no internet browsing)
- Better for evening use than a phone — no backlight means no blue light, which
  suppresses melatonin and delays sleep
  ([Chang et al., PNAS 2015](https://www.pnas.org/doi/10.1073/pnas.1418490112))
- Multi-day battery life (5-7 hours active, days for typical usage)
- Fast e-ink refresh (0.4s partial refresh)
- Portable and lightweight (170mm × 115mm × 26mm, 140g)

## Alternatives

If building from scratch isn't for you, these off-the-shelf devices support custom software:

| Device | Price | Key advantage | Anki |
| -- | -- | -- | -- |
| [Onyx BOOX](https://www.boox.com/) | $250–820 | Android 15 — install Anki from Play Store directly | Native app |
| [PineNote](https://pine64.org/devices/pinenote/) | $399 | Ships Debian (community image); SSH root access | Custom client |
| [reMarkable Paper](https://remarkable.com/) | €399–649 | SSH root enabled by default; Vellum package manager | Via Vellum |
| [Kobo](https://www.kobo.com/) + [KOReader](https://github.com/koreader/koreader) | $160–260 | No jailbreak needed; cheapest hackable option | Limited |

**Why build inkSink instead?**

- Full Linux control — no Android abstractions, no closed firmware
- Cheaper than most alternatives (parts only; excludes build time)
- Full GPIO access for custom button layout (all commercial devices are sealed)
- Custom 7.5" display size; commercial devices are 6–10" fixed form factors
- Silent network display — any LAN device can push content via HTTP POST
  (planned); no commercial device exposes an open rendering API like this

## Hardware

### Components

- **Raspberry Pi Zero 2 W** — 1GHz quad-core ARM, 512MB RAM, WiFi/BT
- **Waveshare 7.5" E-Ink HAT** — 800×480 display, 0.4s partial refresh
- **PiSugar 3** — 1200mAh battery, RTC, UPS functionality
- **6mm tactile switches** — 6-8 buttons with 3D printed caps
- **3D printed case** — Custom enclosure, 26mm uniform depth

**Total cost:** €120-170

### Physical Design

```text
Device: 170mm × 115mm × 26mm (Kindle-sized, slightly thicker)
Weight: ~140g (lighter than Kindle Paperwhite)

Layout:
┌─────────────────────────────────┐
│ Display (2mm) - front surface   │
├─────────────────────────────────┤
│ Empty space (~2mm air gap)      │
├───────────┬─────────────────────┤
│  Battery  │  Electronics Stack  │
│  (6mm)    │  (22mm)             │
└───────────┴─────────────────────┘
```

Display is ~2mm at the front, electronics stack ~22mm at the back, with a
~2mm air gap in between — 26mm total depth.

## Software

### Architecture

**Console-only system** (no desktop environment):

- Raspberry Pi OS Lite (minimal RAM footprint)
- Custom Python application (auto-starts on boot via systemd)
- Two-layer rendering pipeline: wkhtmltoimage content + Pillow compositor
- Direct SPI display access via Waveshare library

### Launcher

- Boot menu: App selection, device status, settings, log viewer, sleep
- Status screen: time, battery, WiFi, Bluetooth, system load, storage

### Anki reviews

- Full HTML/CSS card rendering via wkhtmltoimage
- Image support (downloads from AnkiWeb)
- Kanji/CJK fonts (Noto Sans CJK)
- AnkiWeb sync at session start (download) and end (upload)
- Partial refresh (0.4s per card) in 1-bit mode
- Full refresh every N cards (configurable; clears ghosting)

### Weather

- wttr.in pre-rendered PNG displayed in landscape orientation
- Fetched on app launch; location configurable

### Display Server _(planned)_

Any device on the LAN can push content to the screen without user interaction:

```sh
curl -X POST http://inksink.local:8080/render \
  --data-binary @image.png -H "Content-Type: image/png"
```

Accepts PNG or HTML. Disabled by default (`apps.display_server.enabled` in
config). HTTP is open (LAN trust); HTTPS is also available and supports an
optional bearer token.

### Maintenance

- Fully automated provisioning via Ansible (SSH, firewall, app deployment)

### RAM Budget

| Component | Usage |
| -- | -- |
| Raspberry Pi OS Lite | ~80 MB |
| Python + `anki` Rust backend | ~120 MB (needs measurement) |
| HTML renderer (active) | ~30 MB |
| Application logic | ~10 MB |
| **Total** | **~240 MB** |
| Available (of 512 MB) | ~270 MB |

## Development

See [docs/development.md](docs/development.md) for local setup, running tests, linting,
and the OpenSpec change workflow. Architectural decisions are recorded in
[docs/adr/](docs/adr/).

## Build Guide

Detailed build instructions: [docs/build_guide.md](docs/build_guide.md)

Full bill of materials: [hardware/bom.md](hardware/bom.md)

**Quick overview:**

1. **Order components** (~€150 total)
1. **3D print case and button caps**
1. **Solder button wires** to GPIO pins (28AWG with heat shrink)
1. **Assemble electronics** (PiSugar → Pi → HAT stack)
1. **Install software** — see [docs/setup.md](docs/setup.md) for full instructions
1. **Configure application** (AnkiWeb credentials, preferences)
1. **Test and iterate**

**Build time:** 1-2 weekends _(estimate; not yet validated on a real device)_

**Difficulty:** Intermediate (basic soldering + Python)
