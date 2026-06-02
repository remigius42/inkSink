<!-- spellchecker:ignore expressionality -->

## Context

The Compositor today calls `renderer.render(html)` internally inside
`set_content(html)`, and the renderer always calls wkhtmltoimage with both
`--width` and `--height` locked to panel dimensions, followed by a PIL
`resize()` to the same dimensions. This means all content is clipped to
exactly one screen height.

The two-layer pipeline (ADR 0012) already separated chrome from content, but
the Compositor's content interface is still HTML-centric. This design
generalizes it to accept any PIL Image, makes the Compositor own scroll
state, and adjusts the renderer to return natural-height images.

See ADR 0014 for the full trade-off record.

## Goals / Non-Goals

**Goals:**

- Compositor accepts a PIL Image for content (source-agnostic)
- Vertical scroll via Scroll Offset; `scroll_up()` / `scroll_down()` return
  `(can_scroll_up, can_scroll_down)` predicates
- Renderer returns natural-height images (drop `--height` and `resize()`)
- Templates simplified to pure content (no chrome blank reservations)
- `display.vertical_scroll_step` config key with per-App override

**Non-Goals:**

- Horizontal scroll
- Automatic scroll button management (App owns button semantics per ADR 0007)
- Persistent scroll position across App restarts

## Decisions

### Compositor accepts `PIL Image`, not HTML

`set_content(img: Image)` replaces `set_content(html: str)`. Apps that render
HTML call `renderer.render(html)` first, then pass the result in. Apps that
draw with Pillow directly also pass a PIL Image.

*Why*: scroll, cropping, and Content Zone placement are display concerns; the
Compositor should not special-case HTML. Decoupling also makes Pillow-rendered
content (needed for interactive Apps where wkhtmltoimage latency is
unacceptable) a first-class path.

### Compositor retains full content image between scroll events

After `set_content(img)`, the Compositor stores the full (potentially tall)
image. `scroll_up()` / `scroll_down()` shift the Scroll Offset and re-crop
without re-invoking the renderer.

*Why*: re-rendering on each scroll press (even via cache) requires a full
pipeline round-trip. Retaining the image makes scroll a PIL crop + partial
refresh — sub-second.

### Renderer drops `--height` and `resize()`

`renderer.render()` omits `--height` from the wkhtmltoimage invocation and
removes the subsequent `img.resize((width, height))` call. The returned image
is always `panel_width` wide and `natural_content_height` tall.

*Why*: the `resize()` call silently distorts content when natural height
differs from panel height. Dropping `--height` is correct regardless of
scrolling; fixing the distortion is a long-standing correctness issue.

*Cache impact*: cache key `(sha256(html), mode, orientation)` is unchanged —
the same HTML always produces the same natural-height image for a given
orientation.

### Templates render pure content; Compositor places content in Content Zone

Chrome blank reservations are removed from all layout templates. The
Compositor computes the Content Zone (screen height minus visible chrome
heights) and places the cropped content image at the correct y-offset
(below the status bar when shown).

*Why*: blank HTML regions and Pillow chrome regions must stay in sync —
fragile coordination. Moving placement entirely into the Compositor is the
natural completion of the two-layer pipeline. It also makes `has_statusbar` /
`has_buttons` flags on `fill_content()` obsolete (the Compositor already
knows what chrome it is drawing).

### `scroll_up()` / `scroll_down()` return predicates; App manages buttons

Both methods return `(can_scroll_up: bool, can_scroll_down: bool)` after
updating the display. The App uses these to call `set_buttons()` and
enable/disable scroll button slots — or dynamically reassign freed slots.

*Why*: button semantics belong to the App layer (ADR 0007). Returning
predicates avoids the Compositor needing to know which button slots the App
has assigned to scrolling.

### renderer.max_image_height caps rendered height as a memory safety guard

`renderer.render()` truncates images taller than `renderer.max_image_height`
(default 8000px, ~10× portrait screen height) and logs a warning. This
prevents wkhtmltoimage from producing memory-exhausting images for long
content on Pi Zero 2W (512MB). The correct long-term fix — content-side
chunking where the App feeds bounded slices to the Compositor — is out of
scope here.

*Why truncate rather than raise*: a crash is worse than truncated content;
the warning gives the developer signal to implement chunking.

*Why 8000px default*: ~3.5MB RGB PNG, well within Pi Zero memory budget.
Configurable for Apps that know their content is bounded.

## Risks / Trade-offs

**All existing `set_content()` callers break** — they pass HTML strings today.
→ Each caller gains one line: `img = renderer.render(html)` before the call.
Low mechanical risk; no logic changes.

**Templates lose `has_statusbar` / `has_buttons` expressionality** — currently
you swap a template to change chrome presence.
→ The Compositor already tracks what chrome it draws; the flags are moved to
the Compositor's runtime state, not lost. Apps control chrome by whether they
call `set_buttons()` and whether the status bar is active.

**Natural-height renderer changes cache semantics** — existing cached entries
(rendered at panel height) are invalid after this change.
→ Cache is in-memory and process-scoped; it clears on service restart, which
always accompanies a deploy.

## Open Questions

None — all design decisions resolved in grill session (ADR 0014).

## Implementation Notes

- [Renderer: exact lines to change](notes/renderer-lines.md)
- [Compositor: current vs new set_content flow](notes/compositor-flow.md)
- [Config: per-app override pattern](notes/config-pattern.md)
