<!-- spellchecker:ignore ankiweb noto paperwhite pnas wkhtmltoimage -->

# [inkSink](https://github.com/remigius42/inkSink)

Copyright 2026 [Andreas Remigius Schmidt](https://github.com/remigius42)

A portable e-ink display device for spaced repetition learning, reading, and
personal dashboards. **ink** = e-ink display; **Sink** = terminal node in graph
theory where information flows to rest.

```text
Calendar API ─┐
Weather API  ─┤
AnkiWeb API  ─┼─> inkSink ─> E-ink Display
RSS feeds    ─┘
```

**Primary use cases:**

- **Anki spaced repetition** - Distraction-free flashcard reviews
- **E-reader** - EPUB/PDF reading with e-ink comfort
- **Information dashboard** - Calendar, weather, RSS, todos
- **Text editor** - Neovim via Bluetooth keyboard

**Why inkSink?**

- Distraction-free by design (no notifications, no internet browsing)
- Better for evening use than a phone — no backlight means no blue light,
  which suppresses melatonin and delays sleep
  ([Chang et al., PNAS 2015](https://www.pnas.org/doi/10.1073/pnas.1418490112))
- Multi-day battery life (5-7 hours active, days for typical usage)
- Fast e-ink refresh (0.4s partial refresh)
- Portable and lightweight (170mm × 115mm × 26mm, 140g)

## Hardware

### Components

- **Raspberry Pi Zero 2 W** - 1GHz quad-core ARM, 512MB RAM, WiFi/BT
- **Waveshare 7.5" E-Ink HAT** - 800×480 display, 0.4s partial refresh
- **PiSugar 3** - 1200mAh battery, RTC, UPS functionality
- **6mm tactile switches** - 6-8 buttons with 3D printed caps
- **3D printed case** - Custom enclosure, 26mm uniform depth

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
- Custom Python application (auto-starts on boot)
- Framebuffer rendering (direct display access)
- AnkiWeb API integration (cloud sync)

### Anki reviews

- Full HTML/CSS card rendering via wkhtmltoimage
- Image support (downloads from AnkiWeb)
- Kanji/CJK fonts (Noto Sans CJK)
- Offline review queue with background sync
- Partial refresh (0.4s per card, feels instant)
- Full refresh every 10-20 cards (clears ghosting)

### E-reading

- EPUB/PDF support (same HTML rendering pipeline)
- Page navigation via buttons
- Bookmark support

### Dashboards

- Modular widget system
- API integration (Calendar, Weather, RSS)
- Automatic refresh intervals
- Low-power always-on display

### Maintenance

- SSH over WiFi
- Bluetooth keyboard support
- Neovim for editing
- PiSugar web UI (battery stats, configuration)

### RAM Budget

| Component | Usage |
| -- | -- |
| Raspberry Pi OS Lite | ~80 MB |
| Python + libraries | ~40 MB |
| HTML renderer (active) | ~30 MB |
| Application logic | ~10 MB |
| **Total** | **~160 MB** |
| Available (of 512 MB) | ~350 MB |

## Build Guide

Detailed build instructions: [docs/anki-eink-device-build-guide.md](docs/anki-eink-device-build-guide.md)

**Quick overview:**

1. **Order components** (~€150 total)
1. **3D print case and button caps**
1. **Solder button wires** to GPIO pins (28AWG with heat shrink)
1. **Assemble electronics** (PiSugar → Pi → HAT stack)
1. **Install software** (Raspberry Pi OS Lite + dependencies)
1. **Configure application** (AnkiWeb credentials, preferences)
1. **Test and iterate**

**Build time:** 1-2 weekends

**Difficulty:** Intermediate (basic soldering + Python)
