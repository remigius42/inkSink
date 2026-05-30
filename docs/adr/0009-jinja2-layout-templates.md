<!-- spellchecker:ignore htpy unsanitized -->

# ADR 0009 — Jinja2 HTML layout templates with dedicated slots

## Status

Accepted

## Context

Every App state needs to produce a full-screen image: card content, button
labels, and (in most states) a status bar showing time, WiFi, and battery.
Composing these regions requires a templating strategy.

The renderer is a pure HTML→image function (wkhtmltoimage + Pillow). Keeping
it pure means layout composition must happen before the render call.

Four approaches were considered:

**PIL compositing.** Render regions separately; paste them together with
Pillow. Works, but requires pixel-level layout arithmetic in Python, is hard
to style or iterate on, and mixes layout concerns into the App layer.

**Python markup libraries (htpy, dominate).** Generate HTML from Python
objects. Type-safe and no separate template files. Awkward for the content
slot, which contains arbitrary card HTML fragments that must be injected
unsanitized — `raw()` helpers exist but are not idiomatic. Layouts are Python
functions, not readable documents.

**f-strings or `str.format()`.** Zero dependencies. Brittle for non-trivial
HTML; no escaping; hard to maintain as layouts grow.

**Jinja2 templates.** Layout files are readable HTML with `{{ slot }}`
markers. Card HTML is injected with `| safe`. CSS and sizing can be iterated
by editing the `.html.j2` file and previewing with placeholder content in a
browser — important when tuning e-ink font sizes and refresh regions.

## Decision

Layouts are Jinja2 `.html.j2` files living in `core/layouts/` (built-in) or
`<app>/layouts/` (App-specific). A `core/layout.py` module provides named
filling functions rather than a generic `fill(template, context)` interface —
named parameters make slot mismatches a TypeError at the call site, not a
silent missing-key at render time.

One built-in layout (`fill_content` consolidation, superseding `fullscreen`
and `default`):

- **`content`** — reserves blank white regions at the status bar edge and
  button bar edge when `has_statusbar=True` / `has_buttons=True`. Chrome is
  rendered by the Compositor via Pillow, not by the template. Passing both as
  `False` reproduces fullscreen behavior.

Apps that need custom regions (e.g. Anki's progress indicator "3 / 47") define
their own layout template and a corresponding filling function.

Jinja2 is added to `pyproject.toml` `[project.dependencies]`.

## Consequences

- Chrome (status bar, button labels) is no longer rendered by the template —
  the Compositor owns it via Pillow (see ADR 0012 and ADR 0013)
- Layout files can be opened in a browser with placeholder content for visual
  iteration without running the full app
- The renderer cache key is unaffected — layouts are resolved before the
  render call; the renderer sees only the filled HTML string
- `fill_fullscreen` and `fill_default` are removed; callers use `fill_content`
