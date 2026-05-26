<!-- spellchecker:ignore pillarboxed -->

# ADR 0008 — Per-App display orientation; Core rotates image before driver handoff

> **Note**: This is the proposed updated version of ADR 0008, to be applied
> when implementing the `core-rendering-pipeline` change (see task 4.x).
> The committed ADR still reflects the old `width`/`height` decision.

## Status

Accepted

## Context

The Waveshare 7.5" V2 panel is physically 800×480 px (landscape). The
hardware driver (`epd7in5_V2`) always expects an 800×480 buffer.

Anki flashcards and e-book pages are inherently portrait content. A landscape
layout wastes vertical space and produces awkward text columns. Future Apps
(PDF viewer, Launcher menu) may prefer landscape. Orientation therefore needs
to be a per-App (or per-state) concern, not a fixed hardware assumption.

Three approaches were considered:

**Always landscape (800×480).** No rotation logic needed. Portrait content
is pillarboxed or reflowed into a wide-short frame — poor UX for cards and
reading.

**Always portrait (480×800) via software rotation.** Simpler than per-App
switching: one code path, renderer always targets 480×800, Display always
rotates before driver handoff. Breaks any future App that genuinely wants
landscape (e.g. a media viewer or a wide data dashboard).

**Per-App orientation via a named string; rotation at the display boundary.**
The renderer accepts an `orientation` string (`"portrait"` or `"landscape"`)
and resolves pixel dimensions internally. The display has exactly two valid
logical sizes — portrait (480×800) or landscape (800×480) — so raw integer
dimensions at every call site are unnecessary indirection on a fixed-display
device. `Display` detects orientation from image dimensions and rotates before
calling the driver. The driver always sees the correct 800×480 buffer.

The rotation angle is a hardware-assembly concern, not a software design
concern — it depends on which edge of the panel faces up after mounting in the
case. Templates use CSS viewport units (`100vw`/`100vh`) and are
orientation-agnostic; `Display` resolves the physical rotation from Config.

## Decision

Orientation is a per-App concern expressed via `Orientation`, a `StrEnum`
(`class Orientation(enum.StrEnum)`) with `PORTRAIT = "portrait"` and
`LANDSCAPE = "landscape"` defined in `core/renderer.py`. Each App declares
its orientation via `apps.<name>.orientation` in `core/config.py` DEFAULTS
(stored as a plain string; converted at the call site via
`Orientation(settings[...])`). `renderer.render()` accepts
`orientation: Orientation` instead of raw `width`/`height`; Core owns the
mapping derived from `_PANEL_W = 800` and `_PANEL_H = 480` constants:
`{Orientation.PORTRAIT: (_PANEL_H, _PANEL_W), Orientation.LANDSCAPE: (_PANEL_W, _PANEL_H)}`.

Layout templates (`fill_fullscreen`, `fill_default`) use CSS viewport units
and require no orientation argument — they produce correct HTML regardless of
orientation; wkhtmltoimage sizes the viewport from the resolved dimensions.

`Display` reads two config keys at init to determine how to rotate before
driver handoff:

- `display.portrait_rotation` — degrees CCW (PIL `Image.rotate()` convention)
  applied when the image is portrait-sized (height > width). Default: `90`.
- `display.landscape_rotation` — degrees CCW applied when the image is
  landscape-sized (width ≥ height). Default: `0`.

Defaults match the most common mounting orientation and keep a fresh deploy
functional without explicit config. Physical rotation values must be verified
on first assembly or after case reassembly.

Default orientation: `"portrait"` for all current Apps (Launcher, Anki).
The device is a hand-held portrait reading device; no App should require the
user to physically rotate it. Future Apps that genuinely need landscape (e.g.
a wide data dashboard) may override via their own `apps.<name>.orientation`
config key.

## Consequences

- `renderer.render()` signature changes: `orientation: Orientation` replaces the
  implicit 800×480 assumption; existing callers must be updated
- Layout templates use `100vw`/`100vh` viewport units — no pixel variables
  injected; the renderer's internal `_HTML_TEMPLATE` wrapper is removed
- `Display.display_partial()` and `display_full()` gain a rotation step —
  a PIL `Image.rotate(angle, expand=True)` call — using the config-driven
  angle for the detected orientation; `expand=True` ensures the buffer
  dimensions are always correct for the driver
- `core/config.py` gains defaults `display.portrait_rotation: 90`,
  `display.landscape_rotation: 0`, and `apps.<name>.orientation: "portrait"`
  per App; `config.yml` should document rotation values so builders know to
  check on reassembly
- wkhtmltoimage `--width`/`--height` are set from the resolved orientation
  dimensions, no longer hardcoded
- LRU cache key: `(sha256(html), mode, orientation)` — replaces the former
  `(sha256, mode)` to avoid cache collisions across orientations
