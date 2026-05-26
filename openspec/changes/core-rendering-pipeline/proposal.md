## Why

`core/renderer.py` and `core/display.py` were built for a single fixed
orientation (landscape 800×480) with no layout abstraction. Supporting
portrait-first Apps, per-App orientations, and on-screen button labels
requires an orientation-aware renderer and a Jinja2 layout system — both
Core changes that every future App depends on.

## What Changes

- `core/renderer.py` — **BREAKING**: `render()` gains `orientation` parameter
  (`"portrait"` | `"landscape"`) replacing raw `width`/`height`; Core owns
  the `{"portrait": (480, 800), "landscape": (800, 480)}` mapping; LRU cache
  key updated to `(sha256, mode, orientation)`; `_HTML_TEMPLATE` removed —
  callers must pass a complete HTML document
- `core/display.py` — `display_partial()` and `display_full()` rotate the
  image before driver handoff using config-driven angles
  (`display.portrait_rotation`, `display.landscape_rotation`)
- `core/config.py` — add `display.portrait_rotation: 90` and
  `display.landscape_rotation: 0` to `DEFAULTS`
- `core/layout.py` — new module: named filling functions over Jinja2
  templates; auto-injects status bar (time, WiFi, battery) in `default`
  layout
- `core/layouts/fullscreen.html.j2` — new: single content slot, full
  portrait screen
- `core/layouts/default.html.j2` — new: content slot + 8-button label bar
  (btn_1–btn_8) + status bar auto-populated by Core
- `jinja2` added to `pyproject.toml` `[project.dependencies]`
- `core/input.py` — **BREAKING**: `_DEFAULT_PIN_MAP` renamed from
  Anki-specific action names (`power`, `show_answer`, `again`, `hard`,
  `good`, `easy`) to generic positional IDs (`btn_1`–`btn_8`); `power`
  entry removed (PiSugar owns hardware power)

## Capabilities

### New Capabilities

- `layout-system`: Jinja2 layout templates with dedicated slots; Core
  auto-injects status bar; Apps fill content and button labels only

### Modified Capabilities

- `card-renderer`: `render()` now accepts `orientation` (`"portrait"` | `"landscape"`);
  Core owns the dimension mapping; cache key is `(sha256, mode, orientation)`
- `display-driver`: rotation applied at display boundary before driver
  handoff; rotation angles configurable via Config
- `button-input`: default mapping changes from 6 Anki-specific names to
  8 generic `btn_1`–`btn_8` IDs; `power` entry removed (ADR 0007)

## Impact

- **Breaking**: all `renderer.render()` call sites must pass `orientation`;
  currently only stub callers exist so blast radius is contained
- **Breaking**: all `InputHandler` callers that match on action names
  (`"show_answer"`, `"again"`, etc.) must update to `"btn_2"`, `"btn_5"`,
  etc.; only stub callers exist today
- `core/config.py` DEFAULTS gains two new keys under `display`
- `core/display.py` gains a PIL rotation step — no API change for callers
- New runtime dependency: `jinja2` (pure Python, `py3-none-any`, ARM-safe)
- Launcher and Anki App are blocked on this change
