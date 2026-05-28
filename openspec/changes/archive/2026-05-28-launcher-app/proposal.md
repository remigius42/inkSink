## Why

`__main__.py` currently launches the Anki App directly — viable for a
single-purpose device but unworkable as more Apps are added. A dedicated
Launcher App runs on boot, lets the user select an App, shows device status,
and provides basic settings access. It is the prerequisite for every content
App, including `anki-app`.

## What Changes

- `src/inksink/launcher/` — new App subpackage: `app.py` and `__init__.py`
- `src/inksink/__main__.py` — updated to wire up `Display`, `InputHandler`,
  and `Launcher`; owns the infinite loop, `display.init()`, and exception
  handling; restarts Launcher on each iteration
- `src/inksink/launcher/app.py` — `Launcher` class: single-pass — renders
  MENU, handles one selection (App / Status / Settings / Sleep), returns;
  uses `core/layout.py` and `core/renderer.py`; orientation configurable via
  `settings["apps"]["launcher"]["orientation"]`

## Capabilities

### New Capabilities

- `launcher-menu`: App selection screen — lists available Apps, launches
  selected App on button press, returns here when App exits via `btn_1`
- `launcher-status`: Status screen — shows battery percent, WiFi SSID,
  system time, and IP address
- `launcher-settings`: Settings screen — read-only display of current
  config values (credentials shown as `***`); scrollable; no editing in v1
- `launcher-logs`: Logs screen — last 100 lines of the `inksink` systemd
  journal; scrollable; starts at bottom (most recent first)

### Modified Capabilities

- `python-package`: `__main__.py` entry point now runs the lifecycle loop
  (init, restart Launcher, handle exceptions), not a stub; the module is no
  longer a placeholder

## Impact

- `src/inksink/__main__.py` changes from a stub `print()` to a real entry point
- All content Apps (`anki`, future `ebooks`) become callable functions
  invoked by Launcher; exceptions propagate to `__main__.py` for handling
- `btn_1` ("Menu") is reserved in all App layouts — enforced by convention,
  documented in ADR 0007 and CONTEXT.md
- Depends on `core-rendering-pipeline` (Jinja2 layouts, orientation-aware
  renderer, `btn_1`–`btn_8` GPIO map)
- Requires `ansible-roles` change: add `Environment=INKSINK_VERSION=...` to the
  systemd service template so the STATUS screen can display the deployed tag;
  without this the version row falls back to `"unknown"`
