# ADR 0014 — Vertical scroll: Compositor-owned state, PIL Image content interface

Scrolling content that overflows the Content Zone is a display concern, not
App logic — so the Compositor owns the Scroll Offset, retains the full
content image, and handles cropping on each scroll action.

## Decision

- **Vertical only.** HTML reflows to natural height when `--height` is
  omitted from the wkhtmltoimage call; horizontal overflow has no equivalent
  natural path and requires four buttons instead of two.
- **Compositor accepts `PIL Image`, not HTML.** `set_content(img)` takes a
  pre-rendered image. Apps that render HTML call `renderer.render()` first;
  Apps that use Pillow directly pass their image in. Scroll is therefore
  content-source-agnostic.
- **Compositor-owned scroll state.** `scroll_up()` and `scroll_down()` shift
  the Scroll Offset by the configured Scroll Step, re-crop the retained
  content image into the Content Zone, and trigger a partial refresh.
- **Predicates returned to App.** Both scroll methods return
  `(can_scroll_up: bool, can_scroll_down: bool)`. The App uses these to
  enable or disable scroll buttons via the existing `set_buttons()` API,
  preserving ADR 0007's rule that button semantics belong to the App layer.
  This also lets Apps dynamically reassign freed button slots when one scroll
  direction is exhausted.
- **Scroll Step config.** `display.vertical_scroll_step` (global default) with
  per-App override at `apps.<name>.display.vertical_scroll_step`, following the
  pattern established in ADR 0006.

## Considered options

**App-owned scroll state** was rejected: the App would need to reason about
pixel offsets and content image dimensions — display concerns that belong in
the Compositor.

**Hybrid template model** (chrome reservations in HTML for non-scrollable
content, content-only HTML for scrollable) was rejected in favour of a
unified model where templates render pure content and the Compositor always
owns chrome placement. This also makes Pillow-rendered content a first-class
path without requiring Apps to manually reserve chrome regions.
