# ADR 0012 — Two-layer rendering pipeline: wkhtmltoimage content + Pillow chrome

## Status

Accepted

## Context

Every App state requires a full-screen image combining content (card HTML,
menu items, status output) and chrome (status bar, button bar). The existing
pipeline routes everything through wkhtmltoimage, making sub-second updates
impossible: a full 1–5 s render is required for any visual change including
button highlights and clock ticks.

Partial refresh — the only path to sub-second screen updates on the Waveshare
7.5" V2 — requires a mutable in-memory framebuffer and the ability to update
small regions without re-invoking wkhtmltoimage.

## Decision

Separate the pipeline into two layers:

1. **Content layer** — wkhtmltoimage renders App-provided HTML to a PIL Image.
   The HTML template reserves blank white regions where chrome will be placed
   (`BUTTON_BAR_SIZE`, `STATUS_BAR_HEIGHT` constants). Content renders in the
   App's display mode (1-bit or 4gray) via the existing `renderer.render()`
   call.

1. **Chrome layer** — the Compositor renders status bar and button bar directly
   onto the framebuffer using Pillow 1-bit primitives. Chrome is always 1-bit
   (see ADR 0013).

The Compositor owns a persistent 1-bit PIL Image (framebuffer) at the current
orientation dimensions. `set_content(html)` composites a new content render onto
the framebuffer and triggers a full refresh. `set_buttons()` and
`set_button_state()` redraw only the button bar region and trigger a partial
refresh.

## Consequences

- Button state feedback is sub-second (Pillow redraw + `display_partial()`)
- Status bar time stays current via a background timer thread (ADR 0013 scope)
- wkhtmltoimage latency (~1–5 s on Pi Zero) is unchanged for content updates;
  this change does not worsen it
- The LRU render cache continues to absorb repeat content renders
- Chrome is always 1-bit regardless of App display mode; content zone
  quality is unaffected (content renders in the App's mode before compositing)
