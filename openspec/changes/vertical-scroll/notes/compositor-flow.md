# Compositor: current vs new set_content flow

File: `src/inksink/core/ui/compositor.py`

## Current flow (set_content takes html: str)

```python
def set_content(self, html: str) -> None:
    img = renderer.render(html, mode=..., orientation=...)
    with self._lock:
        self._framebuffer = img.convert("1")   # replaces entire framebuffer
        self._redraw_chrome()                   # draws chrome on top
        self._display.display_full(...)
```

The framebuffer IS the content image — chrome is drawn directly onto it.

## New flow (set_content takes img: Image)

The framebuffer is no longer the content image. Flow becomes:

1. Start from a fresh white framebuffer (`_make_framebuffer()`)
2. Compute `content_zone_height` = fb height − STATUS_BAR_HEIGHT − button bar
   height (each term only when that chrome is active)
3. Crop content image: `img.crop((0, scroll_offset, fb_width, scroll_offset +
   content_zone_height))`
4. Paste cropped content into framebuffer at `(0, STATUS_BAR_HEIGHT)` (or `(0,
   0)` if no status bar)
5. Call `_redraw_chrome()` to draw status bar and button bar on top
6. Call `display.display_full()` / `display.display_4gray()`

Store `self._content_image = img` (full image, unconverted) for scroll reuse.
Reset `self._scroll_offset = 0`.

## scroll_up / scroll_down

Same as steps 1–5 above, but:

- Adjust `_scroll_offset` first (clamped to `[0, content_image_height −
  content_zone_height]`)
- Skip if already at limit (no display call, return predicates)
- Call `display.display_partial()` instead of `display_full()`

## Chrome presence heuristic

The Compositor currently has no explicit "is status bar active" flag — it always
draws the status bar. For Content Zone height calculation, use:

- Status bar: always active (existing behavior)
- Button bar: active when `any(lbl != "" for lbl in self._labels)` — this check
  already exists in `_redraw_buttons()`

## Content image mode

`_content_image` should be stored as received from the caller. Convert to `"1"`
only when pasting into the framebuffer (or derive from display mode as the
existing code does).
