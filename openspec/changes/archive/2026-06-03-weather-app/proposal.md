<!-- spellchecker:ignore glanceable launchable -->

## Why

The Device has no way to display weather information. A dedicated Weather App
adds passive glanceable forecast display, making the Device useful between Anki
sessions without requiring any interaction.

## What Changes

- New `weather` App (`src/inksink/weather/`) added to the Launcher menu
- Weather content fetched from wttr.in as a pre-rendered PNG — no custom
  renderer required (see ADR 0015)
- Location label and coordinates rendered as Pillow overlays using DejaVu Sans
  Mono to match the wttr.in PNG font
- Multiple locations supported with auto-cycling and manual navigation
- `fonts-dejavu-core` Debian package added to the Ansible base role
- **Bundled fix**: Compositor `_content_zone_height()` incorrectly subtracts
  `BUTTON_BAR_SIZE` from the framebuffer height in landscape orientation even
  when the button bar is on a side edge (not top/bottom)

## Capabilities

### New Capabilities

- `weather-app`: Landscape App that fetches, inverts, and displays wttr.in PNG
  forecasts with Pillow-rendered location label and coordinates overlays;
  supports multiple configured locations with auto-cycling and direct shortcuts

### Modified Capabilities

- `ui-compositor`: Fix landscape content zone height calculation; expose
  `content_zone_height()` and `content_zone_width()` as the public API for Apps
  to size their content — only the height subtracts `BUTTON_BAR_SIZE` for
  `top`/`bottom` edges; only the width subtracts it for `left`/`right` edges
- `ansible-provisioning`: Add `fonts-dejavu-core` to the base role package list
- `launcher-menu`: Register the Weather App as a launchable content App

## Impact

- New `src/inksink/weather/` subpackage
- `src/inksink/core/ui/compositor.py`: landscape height bug fix; new public
  `content_zone_height()` / `content_zone_width()` methods
- `ansible/roles/base/`: add `fonts-dejavu-core` package
- `src/inksink/launcher/app.py`: register Weather App
- New runtime dependency: `requests` (if not already present) for HTTP fetches
- New system dependency: `fonts-dejavu-core` on the Device
- Network connectivity required at runtime; no offline fallback
