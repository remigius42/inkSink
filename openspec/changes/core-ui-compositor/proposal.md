## Why

The current rendering pipeline routes everything through wkhtmltoimage, making
interactive UI feedback (button highlights, live status bar) impossible without
a full 1–5s re-render. Partial refresh — the only path to sub-second screen
updates — requires a mutable in-memory framebuffer and Pillow-based chrome
rendering, neither of which exist today.

## What Changes

- **NEW** `core/ui/` subpackage with a stateful `Compositor` class owning the
  framebuffer
- **NEW** Two-layer rendering pipeline: wkhtmltoimage for the content zone;
  Pillow for chrome (status bar, button bar)
- **NEW** Button tristate rendering (default / active / disabled) via Pillow in
  1-bit
- **NEW** Orientation-aware button bar: moves to the physical-button edge in
  landscape; text rendered vertically
- **NEW** Landscape double-column button layout
  (`apps.<name>.display.double_vertical_button_size`)
- **NEW** Status bar auto-refresh timer (`display.status_refresh_interval`,
  default 20 s)
- **BREAKING** `fill_fullscreen()` and `fill_default()` replaced by
  `fill_content(content, has_statusbar=True, has_buttons=True)`
- **BREAKING** Apps must call `compositor.set_buttons()` instead of passing
  button labels to the layout fill function

## Capabilities

### New Capabilities

- `ui-compositor`: Stateful Compositor owning the framebuffer; orchestrates
  two-layer rendering, partial refresh, and the status bar timer

### Modified Capabilities

- `layout-system`: `fill_content()` replaces `fill_fullscreen()` /
  `fill_default()`; templates now reserve blank chrome regions instead of
  rendering them

## Impact

- `core/layout.py` — `fill_fullscreen` / `fill_default` removed; `fill_content`
  added
- `core/layouts/` — templates updated to leave chrome regions as blank space
- `core/ui/compositor.py` — new file
- `core/ui/` — new subpackage with `BUTTON_BAR_SIZE`, `STATUS_BAR_HEIGHT`
  constants
- `core/startup.py` — Compositor instantiated alongside Display at boot
- `anki/app.py`, `launcher/app.py` — callers updated to new layout and
  compositor API
- `core/config.py` — new defaults: `display.status_refresh_interval`,
  `apps.<name>.display.double_vertical_button_size`
- `docs/adr/` — two new ADRs; ADR 0009 updated
- `CONTEXT.md` — Compositor term added; Layout and Core definitions updated
