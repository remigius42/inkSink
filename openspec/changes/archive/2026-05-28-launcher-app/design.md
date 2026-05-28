<!-- spellchecker:ignore gethostbyname -->

## Notes

- [notes/button-state-reference.md](notes/button-state-reference.md) —
  full button label grid per Launcher state; App slot assignment convention;
  btn_1 contract for content Apps
- [notes/pi-ip-lookup.md](notes/pi-ip-lookup.md) —
  two approaches for getting device IP on Pi OS; `gethostbyname` pitfall
- [notes/state-functions-reference.md](notes/state-functions-reference.md) —
  dataclass definitions and function signatures for all `core/state.py` reads
- [ADR 0010](../../../docs/adr/0010-launcher-first-architecture.md) —
  Launcher-first architecture; `btn_1` reserved as Menu across all Apps
- [ADR 0007](../../../docs/adr/0007-softkey-button-model.md) —
  softkey button model; `btn_1`–`btn_8` generic IDs
- [ADR 0009](../../../docs/adr/0009-jinja2-layout-templates.md) —
  Jinja2 layout templates; `fill_default()` / `fill_fullscreen()`

## Context

The Launcher is the first App that runs on boot (via `__main__.py` →
systemd). `__main__.py` owns the top-level lifecycle loop; `Launcher.run()`
is single-pass — it renders MENU, handles one selection, and returns.
Content Apps (Anki, future ebooks/pdf) are called as functions and return
control to `__main__.py`, which restarts the Launcher.

The Launcher uses `fill_default()` for all screens (MENU, STATUS, SETTINGS)
with the status bar auto-populated by Core.

Settings in v1 are read-only: show current config values without editing.
Editing requires SSH access; the device is not a general settings terminal.

## Goals / Non-Goals

**Goals:**

- Boot into a usable menu in under 3 seconds from `__main__.py` start
- Allow launching Anki (and future Apps) via button press
- Show device status on demand: time, battery, WiFi SSID + signal, hostname,
  IP, Bluetooth state + connected devices, system load (1m/5m/15m), memory
  (total/free MB), storage (total/free GB), tag version
- Show current config values (read-only) on demand
- Return to menu automatically when any App exits

**Non-Goals:**

- In-device config editing — SSH + deploy covers this
- WiFi credential entry on device — no text input mechanism exists
- App management (install, remove, update) — handled by Ansible Deploy
- Multi-level menus — flat list of Apps is sufficient for v1

## Decisions

### Lifecycle: `__main__.py` owns the loop; Launcher is a single-pass App

`__main__.py` holds the infinite loop, display init, and exception handling.
`Launcher.run()` is a single-pass: renders MENU, handles one user selection
(App launch, Status, Settings, or Sleep), then returns. `display.init()` is
called once before the loop; `Display._wake_if_sleeping()` handles auto-wake
after sleep (called internally by `display_full()` et al.).

```python
# __main__.py
display.init()  # once — _wake_if_sleeping() handles post-sleep wake
while True:
    try:
        Launcher(display, input_handler, settings).run()
    except KeyboardInterrupt:
        display.sleep(); break
    except Exception as e:
        fill_error(str(e))  # core/layout.py — returns HTML; rendered via display_full()
        input_handler.wait_for_action()
```

### State machine: MENU → one action → return

```text
MENU ──btn_2──→ ANKI (blocks until Anki returns) → Launcher returns
     ──btn_5──→ STATUS (shows status screen; btn_1 returns) → Launcher returns
     ──btn_6──→ SETTINGS (shows settings screen; btn_1 returns) → Launcher returns
     ──btn_7──→ LOGS (shows journal log screen; btn_1 returns) → Launcher returns
     ──btn_8──→ SLEEP (calls display.sleep()) → Launcher returns
```

`btn_8` in MENU calls `display.sleep()` and returns immediately. The next
`display_full()` call in the restarted Launcher triggers `_wake_if_sleeping()`
automatically. PiSugar button handles power-off separately.

### Apps registered as a static list in `launcher/app.py`

A simple `APPS` list of `(label, callable)` tuples. The Launcher renders the
list as button labels and calls the selected App's `run()` function. No plugin
system, no dynamic discovery — adding an App means editing one list.

Alternative: dynamic discovery via entry points or a config key. Rejected —
over-engineered for a device that will have 2-3 Apps; adds complexity with
no runtime benefit.

### Launcher uses `fill_default()` for all screens

All three Launcher screens (MENU, STATUS, SETTINGS) call
`fill_default(content, buttons)` from `core/layout.py`. The `content`
argument carries screen-specific HTML (App list, status table, config list);
the `buttons` list carries fixed label assignments per screen (see
notes/button-state-reference.md). No custom Jinja2 templates — the default
layout handles status bar, button bar, and content slot automatically.

Alternative: custom per-screen templates in `launcher/layouts/`. Rejected —
`fill_default()` already provides the full layout; a custom Jinja2 environment
adds boilerplate with no visual benefit for v1.

### Logs and Settings screens share the same scroll sub-loop

Both LOGS and SETTINGS use the same pattern: render at offset, wait for btn,
clamp-scroll on btn_6 (↓) / btn_7 (↑), return on btn_1. LOGS starts with
offset at the bottom (most recent entries visible). SETTINGS starts at the top.

LOGS source: `journalctl -u inksink -n 100 --no-pager --output=short` with
a 2 s timeout; "unavailable" on error.

### Settings screen scrolls in 5-line increments via btn_6/btn_7

Config keys may exceed the visible content area (~34 lines at 20px/line in
portrait). `_render_settings()` runs a sub-loop: renders at current offset,
waits for btn press, increments/decrements by 5 lines, clamps between 0 and
`max(0, total_lines − visible_lines)`, re-renders. btn_1 exits.

Scrolling is line-based (offset in lines × 20px) rather than pixel-based for
predictability. "↓ more" / "↑ more" indicators in the content area signal
remaining content; hidden when the list fits on one screen.

btn_6 (↓) and btn_7 (↑) mirror the Vim j/k navigation convention on the
lower button row. btn_5 and btn_8 are inactive in SETTINGS.

### Settings screen shows masked credentials

`ankiweb_password` and similar credential keys are displayed as `***`.
All other config values shown as-is. No editing — the screen is diagnostic,
not administrative.

### Version display uses `INKSINK_VERSION` environment variable

`version_info()` reads `os.environ.get("INKSINK_VERSION", "unknown")`.
Ansible sets this at deploy time in the systemd unit:
`Environment=INKSINK_VERSION={{ lookup('pipe', 'git describe --tags') }}`.

Rationale: the device runs code via Ansible deploy, not `pip install`. An env
var captures the exact deployed git tag. `importlib.metadata` would return the
static `pyproject.toml` version ("0.1.0"), not the tag — misleading after
subsequent deploys without a version bump.

Dependency: the `ansible-roles` change must add the `Environment=` line to
the systemd service template.

## Risks / Trade-offs

- **App crashes propagate to `__main__.py`**: if an App raises an unhandled
  exception, it propagates through `Launcher.run()` to `__main__.py`, which
  logs it, calls `fill_error(message)` from `core/layout.py` to get error
  HTML, renders it, blocks until a button press, then restarts Launcher.
  → Mitigation: `try/except Exception` in `__main__.py`'s loop;
  `fill_error()` added to `core/layout.py` alongside `fill_default()`.

- **`core/layout.py` default-template contract coupling**: if `fill_default()`
  changes its slot interface, Launcher screens may break silently.
  → Mitigation: integration test renders the launcher menu screen end-to-end
  against the `core/layout.py` default template contract.

- **Bluetooth subprocess latency**: `bluetoothctl` calls may take up to 2 s
  each; two calls = up to 4 s blocking the STATUS render.
  → Mitigation: cap each subprocess call at 2 s timeout; show "unavailable"
  on timeout rather than stalling.

## Open Questions

**Resolved**: The status bar auto-populated by `fill_default()` is sufficient
for MENU. No battery/WiFi indicator in the MENU content area.
