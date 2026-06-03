# Compositor Landscape Height Bug

## Location

`src/inksink/core/ui/compositor.py`, method `_content_zone_height()` (around
line 143 at time of writing):

```python
def _content_zone_height(self) -> int:
    h = self._fb_height()
    if self._status_bar_visible:
        h -= STATUS_BAR_HEIGHT
    if any(lbl != "" for lbl in self._labels):
        h -= BUTTON_BAR_SIZE   # ← BUG: always subtracts, even for side bars
    return max(h, 0)
```

## The bug

In landscape with `portrait_rotation=90`, `_button_bar_edge()` returns
`"right"`. The button bar occupies the rightmost 80 px of the framebuffer
(horizontal space), not vertical space. Subtracting `BUTTON_BAR_SIZE` (80 px)
from the height incorrectly reduces the content zone height from 456 px to
376 px — 80 px of content is clipped for no reason.

`_compute_bounding_boxes()` in `core/ui/buttons.py` already handles placing
the button bar on the correct edge; `_content_zone_height()` just needs to
stop double-counting it.

## The fix

```python
def _content_zone_height(self) -> int:
    h = self._fb_height()
    if self._status_bar_visible:
        h -= STATUS_BAR_HEIGHT
    edge = _button_bar_edge(self._portrait_rotation, self._orientation)
    if edge in ("top", "bottom") and any(lbl != "" for lbl in self._labels):
        h -= BUTTON_BAR_SIZE
    return max(h, 0)
```

Note: `_button_bar_edge` is already imported in `compositor.py` from
`core/ui/buttons`.

## Impact on content zone dimensions

With the fix, landscape (`portrait_rotation=90`, status bar + side button bar):

| | Before fix | After fix |
| --- | --- | --- |
| Content zone height | 376 px | **456 px** |
| Content zone width | 720 px | 720 px |

The 720 px width is not affected by `_content_zone_height()` — it is handled
by the paste offset in `_compose_and_display()` which uses `_fb_width()`.
