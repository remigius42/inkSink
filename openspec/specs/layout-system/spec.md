## Purpose

Jinja2-based layout system for Core. Provides `fill_content()` helper that
produces complete HTML documents ready for `renderer.render()`. Apps may define
their own layouts independently.

## Requirements

### Requirement: Core provides a unified fill_content layout function

`core/layout.py` SHALL provide `fill_content(content: str) -> str` that fills
`core/layouts/content.html.j2` with the given HTML content and returns a
complete HTML document ready for `renderer.render()`. The template SHALL
render pure content at full panel width with no reserved blank regions for
chrome. Chrome placement is the sole responsibility of the Compositor.

#### Scenario: fill_content returns a complete HTML document

- **WHEN** `fill_content("<p>Card</p>")` is called
- **THEN** the returned string is a complete HTML document containing the
  content with no blank chrome reservation regions

#### Scenario: Rendered output has no chrome blank regions

- **WHEN** the returned HTML is rendered by `renderer.render()`
- **THEN** the resulting image has no top or bottom blank reserved strips

### Requirement: Apps may define their own layouts

Core SHALL NOT restrict where App-specific Jinja2 templates are placed. An App
that needs a custom layout MAY place templates in `<app>/layouts/` and fill
them directly using `jinja2.Environment`. Built-in Core layouts SHALL reside in
`core/layouts/`.

#### Scenario: App-specific layout is independent of Core layouts

- **WHEN** an App renders using its own `<app>/layouts/custom.html.j2`
- **THEN** the output is not affected by changes to Core layout templates
