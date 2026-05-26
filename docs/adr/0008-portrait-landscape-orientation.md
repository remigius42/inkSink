<!-- spellchecker:ignore pillarboxed -->

# ADR 0008 — Per-App display orientation; Core rotates image before driver handoff

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

**Per-App orientation; rotation at the display boundary.** The renderer
accepts explicit pixel dimensions (`width`, `height`) and produces an image
of exactly that size. `Display` detects orientation from image dimensions and
rotates before calling the driver. Apps that want landscape pass 800×480; Apps
that want portrait pass 480×800. The driver always sees the correct 800×480
buffer.

The rotation angle is a hardware-assembly concern, not a software design
concern — it depends on which edge of the panel faces up after mounting in the
case. Templates and Apps always work in logical pixels; `Display` resolves the
physical rotation from Config.

## Decision

Orientation is a per-App (or per-render) concern. `renderer.render()` accepts
`width` and `height` parameters instead of hardcoded 800×480 values. Apps
select orientation by choosing the dimensions they pass to the renderer;
templates are designed in logical pixels at those dimensions with no awareness
of physical rotation.

`Display` reads two config keys at init to determine how to rotate before
driver handoff:

- `display.portrait_rotation` — degrees CW applied when the image is
  portrait-sized (height > width). Default: `90`.
- `display.landscape_rotation` — degrees CW applied when the image is
  landscape-sized (width ≥ height). Default: `0`.

Defaults match the most common mounting orientation and keep a fresh deploy
functional without explicit config. Physical rotation values must be verified
on first assembly or after case reassembly.

The default orientation for the Anki App and future reading Apps is portrait
(480×800). The Launcher may use landscape or portrait depending on its layout.

## Consequences

- `renderer.render()` signature changes: `width` and `height` replace the
  implicit 800×480 assumption; existing callers must be updated
- The renderer's HTML template body width must be parameterized; it is
  currently hardcoded to `760px` and must adapt to the caller-specified width
- `Display.display_partial()` and `display_full()` gain a rotation step —
  a PIL `Image.rotate(angle, expand=True)` call — using the config-driven
  angle for the detected orientation; `expand=True` ensures the buffer
  dimensions are always correct for the driver
- `core/config.py` gains defaults `display.portrait_rotation: 90` and
  `display.landscape_rotation: 0`; `config.yml` should document them
  explicitly so builders know to check on reassembly
- wkhtmltoimage is called with the App-specified dimensions; the `--width`
  and `--height` flags are no longer hardcoded
- `renderer.py` must extend the LRU cache key to include dimensions alongside
  the HTML hash and display mode to avoid cache collisions across orientations
