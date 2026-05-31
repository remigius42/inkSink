<!-- spellchecker:ignore furigana -->

## Context

The Waveshare EPD 7.5" V2 driver accepts a PIL Image and supports both full
refresh (~3–4 s in 4gray, ~0.4 s in 1-bit) and partial refresh (1-bit only,
sub-second). The current pipeline is write-and-forget: every render shells out
to wkhtmltoimage, producing a fresh PIL Image that is handed to the driver and
discarded. There is no in-memory framebuffer, so partial refresh is
architecturally impossible today.

Interactive UI (button highlight on press, live clock in status bar) requires:

1. A mutable framebuffer persisted across renders
2. A fast path to update a small screen region without re-invoking wkhtmltoimage
3. Chrome (status bar, buttons) rendered separately from content so it can be
   updated independently

## Goals / Non-Goals

**Goals:**

- Enable sub-second button state feedback via partial refresh
- Keep status bar time current via a background refresh timer
- Fix landscape orientation: button bar moves to the physical-button edge; text
  rendered vertically
- Replace `fill_fullscreen` / `fill_default` with a single `fill_content`

**Non-Goals:**

- Partial refresh for the content zone (content rarely changes; wkhtmltoimage
  render + full refresh is acceptable)
- 4gray partial refresh (Waveshare driver does not expose this path)
- Per-pixel diff / dirty-region tracking beyond the fixed chrome regions

## Decisions

### D1 — Two-layer rendering pipeline

wkhtmltoimage renders the content zone; Pillow renders chrome. Templates leave
chrome regions as blank white space (sized by `BUTTON_BAR_SIZE` /
`STATUS_BAR_HEIGHT` constants injected as Jinja2 variables). Pillow composites
chrome onto the content-zone image before any display call.

**Why not Pillow-only:** Rich card content (furigana, images, variable text)
requires HTML layout. Pillow draw-mode layout code would be intractable.

**Why not wkhtmltoimage-only:** wkhtmltoimage spawns a WebKit process (~1–5 s);
button highlights need <100 ms. Chrome must be Pillow.

### D2 — Chrome is always 1-bit

Partial refresh is only available via `display.display_partial()`, which uses
the 1-bit driver path. Chrome is therefore rendered as 1-bit PIL Images regardless
of the App's `display_mode`. The content zone renders in the App's mode (1-bit or
4gray) and is composited onto a 1-bit framebuffer for partial refresh purposes.

**Consequence for disabled buttons:** Gray fill is unavailable in 1-bit. Disabled
state uses a dashed black outline instead — unambiguous at e-ink resolution and
consistent with embedded UI conventions.

### D3 — Compositor as shared stateful object

One `Compositor` instance exists for the process lifetime, instantiated at boot
in `core/startup.py` alongside `Display`. Apps receive it via dependency
injection. This mirrors how `Display` is currently handled.

**Why not per-App compositor:** The physical screen is a singleton. App
transitions naturally reset state via `set_content()`.

### D4 — Button bar edge derived from `display.portrait_rotation`

`portrait_rotation` encodes how the panel is physically mounted (set once at
assembly; never changes during operation). The Compositor derives which screen
edge is adjacent to the physical buttons from this value:

| `portrait_rotation` (CCW) | Logical bottom maps to | Landscape button edge |
| --- | --- | --- |
| 0 | bottom | bottom |
| 90 | right | right |
| 180 | top | top |
| 270 | left | left |

No additional config key is needed; the rotation value is the ground truth.

### D5 — `fill_content(content, has_statusbar, has_buttons)` unifies layouts

`fill_fullscreen()` and `fill_default()` are replaced by a single function.
`has_statusbar=False, has_buttons=False` reproduces fullscreen behavior. The
template reserves chrome regions conditionally; the Compositor always knows
which regions exist from the App's last `fill_content` call (passed through via
`set_content`).

### D6 — Landscape button layout

Portrait 4×2 button grid rotates to 2×4 in landscape. Without doubling: 4×2
layout (4 rows, 2 columns), narrow bar (`BUTTON_BAR_SIZE`). With
`double_vertical_button_size=True`: 4×4 layout (4 rows, 4 columns), wide bar
(2 × `BUTTON_BAR_SIZE`), both physical depth columns labeled. A filled dot
marker (●) in doubled mode indicates each button's y-position to disambiguate
which on-screen slot maps to which physical button.

### D7 — Status bar timer as daemon thread in Compositor

A `threading.Timer`-based loop inside the Compositor refreshes the status bar
region every `display.status_refresh_interval` seconds (default 20 s) via
partial refresh. Lifecycle: `compositor.start()` at boot, `compositor.stop()` in
the SIGTERM handler (alongside `display.sleep()`).

## Risks / Trade-offs

- **1-bit content zone on 4gray Apps** — compositing 4gray content onto a 1-bit
  framebuffer for partial refresh degrades chrome-update visual quality
  slightly. Acceptable: content zone is never partial-refreshed, only chrome is.
- **Status bar timer thread** — adds threading complexity to Compositor.
  Mitigated by using the same `threading.Timer` daemon pattern already in
  `Display`.
- **wkhtmltoimage latency on Pi Zero** — cold renders (new card content) still
  take 1–5 s. LRU cache absorbs repeat renders. This change does not worsen it.
- **Dashed outline in Pillow** — no native primitive; requires manual pixel
  iteration. Acceptable: button area is small, cost is negligible.

## Migration Plan

1. Add `core/ui/` with Compositor and constants
2. Update `fill_content` in `core/layout.py`; update templates
3. Update `core/startup.py` to instantiate Compositor
4. Update `anki/app.py` and `launcher/app.py` to new API
5. Update `core/config.py` with new defaults
6. Update CONTEXT.md and ADRs

No data migration required. No deployed config changes required (new keys have
safe defaults). Breaking API changes are internal — no external callers.

## Open Questions

None. All design decisions resolved in pre-spec grilling session.
