<!-- cspell:ignore updateable -->

# ADR 0013 — Chrome (status bar, button bar) is always rendered in 1-bit

## Status

Accepted

## Context

The Waveshare 7.5" V2 driver exposes three refresh modes: full 1-bit, full
4gray, and partial 1-bit. Partial refresh is only available via the 1-bit path
(`display_partial()`). Apps may choose `display_mode: "4gray"` for richer
content rendering.

Chrome regions (status bar, button bar) must be updateable via partial refresh
— button highlights need \<100 ms feedback, and the status bar clock must tick
without re-rendering content.

Gray fill is unavailable in 1-bit. The disabled button state cannot use a gray
background.

## Decision

Chrome (status bar and button bar) is always rendered as 1-bit Pillow
primitives, regardless of the App's `display_mode` setting.

For disabled buttons: a dashed black outline replaces the unavailable gray
fill. This is unambiguous at e-ink resolution and consistent with embedded UI
conventions.

The Compositor maintains a 1-bit framebuffer. When `display_mode: "4gray"`,
the content zone is rendered in 4gray and composited onto the 1-bit framebuffer
for partial refresh purposes. Full content refreshes call `display_4gray()`;
chrome-only updates always call `display_partial()` (1-bit).

## Consequences

- Partial refresh is available for all chrome updates on all Apps
- Disabled button state uses a dashed outline instead of gray fill
- 4gray content composited onto a 1-bit framebuffer loses grayscale fidelity
  for partial-refresh purposes; this is acceptable because content is never
  partial-refreshed (only chrome is)
- No conditional rendering logic based on display mode in chrome code
