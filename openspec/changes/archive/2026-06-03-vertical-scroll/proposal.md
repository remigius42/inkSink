## Why

Apps whose content exceeds the screen height have no way to surface the overflow
— content is silently clipped. Vertical scroll support lets any App expose
scrollable content without bespoke rendering logic.

## What Changes

- **BREAKING** `Compositor.set_content()` changes signature from `(html: str)`
  to `(img: Image)` — callers are responsible for rendering HTML before passing
  it in.
- `Compositor` retains the full content image and owns the Scroll Offset; new
  methods `scroll_up()` / `scroll_down()` return `(can_scroll_up: bool,
  can_scroll_down: bool)`.
- `renderer.render()` drops the `--height` wkhtmltoimage flag and the subsequent
  PIL `resize()` call; the renderer returns the image at its natural content
  height.
- Layout templates are simplified: chrome reservations (blank status-bar and
  button-bar regions) are removed. The Compositor places content inside the
  Content Zone and draws chrome above/below it.
- New config key `display.vertical_scroll_step` (global default, per-App override
  at `apps.<name>.display.vertical_scroll_step`).
- New config key `renderer.max_image_height` caps the height of images returned
  by `renderer.render()`; content beyond the cap is silently truncated with a
  warning. Stopgap until content-side chunking exists.

## Capabilities

### New Capabilities

- `vertical-scroll`: Compositor-owned vertical scroll — Scroll Offset state,
  `scroll_up` / `scroll_down` methods with predicate return values, Content Zone
  placement.

### Modified Capabilities

- `ui-compositor`: `set_content()` signature changes; Compositor now places
  content in the Content Zone rather than relying on template-reserved blank
  regions.
- `layout-system`: Chrome reservations removed from templates; templates render
  pure content only.
- `config`: New `display.vertical_scroll_step` key with per-App override; new
  `renderer.max_image_height` cap.

## Impact

- `src/inksink/core/ui/compositor.py` — primary change surface
- `src/inksink/core/renderer.py` — drop `--height` and `resize()`
- `src/inksink/core/layouts/` and all `<app>/layouts/` templates — remove chrome
  blank regions
- All App callers of `compositor.set_content()` — must call `renderer.render()`
  themselves first
- `src/inksink/core/config.py` — add `vertical_scroll_step` and `max_image_height`
  defaults
