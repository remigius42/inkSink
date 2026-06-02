## Implementation Notes

- [Renderer: exact lines to change](notes/renderer-lines.md)
- [Compositor: current vs new set_content flow](notes/compositor-flow.md)
- [Config: per-app override pattern](notes/config-pattern.md)

## 1. Renderer: drop --height and resize()

- [ ] 1.1 Remove `--height` flag from `_invoke_wkhtmltoimage()` in
  `core/renderer.py`
- [ ] 1.2 Remove the `img.resize((width, height))` call from
  `_render_html_to_image()` in `core/renderer.py`
- [ ] 1.3 Add `max_image_height` truncation to `render()`: crop to
  `renderer.max_image_height` rows and log a warning if exceeded
- [ ] 1.4 Update renderer tests to assert natural-height output (not forced
  panel dimensions) and that truncation + warning fires correctly

## 2. Layout templates: remove chrome reservations

- [ ] 2.1 Remove status-bar blank region from `core/layouts/content.html.j2`
- [ ] 2.2 Remove button-bar blank region from `core/layouts/content.html.j2`
- [ ] 2.3 Remove status-bar blank region from `anki/layouts/review.html.j2`
- [ ] 2.4 Remove button-bar blank region from `anki/layouts/review.html.j2`
- [ ] 2.5 Remove `has_statusbar` and `has_buttons` parameters from
  `fill_content()` in `core/layout.py`
- [ ] 2.6 Update layout tests to assert no blank chrome regions in rendered HTML

## 3. Compositor: PIL Image interface and Content Zone placement

- [ ] 3.1 Change `set_content(html: str)` to `set_content(img: Image)` in
  `core/ui/compositor.py`
- [ ] 3.2 Implement Content Zone height calculation (screen height minus active
  chrome heights)
- [ ] 3.3 Implement content image placement: crop to Content Zone and composite
  at correct y-offset (below status bar)
- [ ] 3.4 Retain full content image as `_content_image` instance variable; reset
  on each `set_content()` call
- [ ] 3.5 Update all `set_content()` callers to call `renderer.render(html)`
  first: `anki/app.py`, `launcher/app.py`

## 4. Compositor: scroll state and scroll methods

- [ ] 4.1 Add `_scroll_offset: int = 0` instance variable to `Compositor`
- [ ] 4.2 Add `_scroll_step` property reading
  `apps.<name>.display.vertical_scroll_step` with fallback to
  `display.vertical_scroll_step`
- [ ] 4.3 Implement `scroll_down() -> tuple[bool, bool]`: clamp offset, re-crop,
  partial refresh, return predicates
- [ ] 4.4 Implement `scroll_up() -> tuple[bool, bool]`: clamp offset, re-crop,
  partial refresh, return predicates
- [ ] 4.5 Ensure no-op when scrolling is not possible (offset already at limit):
  skip display call, return correct predicates
- [ ] 4.6 Write unit tests for scroll clamping, predicate correctness, and no-op
  behavior

## 5. Config: vertical_scroll_step and max_image_height defaults

- [ ] 5.1 Add `display.vertical_scroll_step: 50` to `DEFAULTS` in `core/config.py`
- [ ] 5.2 Add `renderer.max_image_height: 8000` to `DEFAULTS` in
  `core/config.py`
- [ ] 5.3 Update config tests to assert both new defaults are present

## 6. Docs and verification

- [ ] 6.1 Update `ansible/playbooks/verify.yml` if any verified behavior changed
- [ ] 6.2 Run pre-commit hooks and fix any issues
