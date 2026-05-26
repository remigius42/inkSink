## Why

The `repo-scaffold` change establishes stub modules in `src/inksink/core/`. This
change implements them — providing the shared hardware abstraction layer that
all Apps (starting with `anki`) depend on.

## What Changes

- `core/display.py` — Waveshare 7.5" V2 wrapper with partial and full refresh
- `core/input.py` — GPIO button handler with debounce for 6-8 physical buttons
- `core/renderer.py` — HTML → 1-bit 800×480 PNG pipeline via wkhtmltoimage +
  Pillow
- `core/config.py` — `DEFAULTS` dict; `load_settings()` and `save_settings()`
  persisting YAML to `/etc/inksink/config.yml`
- `core/state.py` — `battery_percent()` (PiSugar I2C); `wifi_status()` returning
  a `WifiStatus` dataclass (`connected`, `ssid`, `strength` 0–100) via `nmcli`

## Capabilities

### New Capabilities

- `display-driver`: Waveshare e-ink display abstraction (init, partial refresh,
  full refresh, sleep)
- `button-input`: GPIO button handler with debounce and action mapping
- `card-renderer`: HTML-to-image pipeline producing 1-bit 800×480 images for
  e-ink
- `device-state`: Hardware state reads — battery (PiSugar I2C) and WiFi
  (connected, SSID, signal strength) via `nmcli`
- `config`: Persistent settings — load/save YAML at `/etc/inksink/config.yml`,
  merged over `DEFAULTS`

### Modified Capabilities

## Impact

- Fills in `src/inksink/core/` stub modules from `repo-scaffold`
- Python deps (`Pillow`, `smbus2`) and system deps (`wkhtmltopdf`,
  `python3-rpi.gpio`) already installed by `repo-scaffold`
- Remaining system dep: `fonts-noto-cjk` (needed for CJK rendering)
- No App logic touched — `anki/` remains a stub
