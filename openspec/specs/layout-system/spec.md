## Purpose

Jinja2-based layout system for Core. Provides `fill_content()` helper that
produces complete HTML documents ready for `renderer.render()`. Apps may define
their own layouts independently.

## Requirements

### Requirement: Core provides a unified fill_content layout function

`core/layout.py` SHALL provide `fill_content(content: str, has_statusbar: bool = True, has_buttons: bool = True) -> str`
that fills a single `core/layouts/content.html.j2` template with the given
HTML content and returns a complete HTML document ready for `renderer.render()`.
When `has_statusbar=True`, the template SHALL reserve a blank region of
`STATUS_BAR_HEIGHT` pixels at the top. When `has_buttons=True`, the template
SHALL reserve a blank region of `BUTTON_BAR_SIZE` pixels at the button-bar
edge. Both `STATUS_BAR_HEIGHT` and `BUTTON_BAR_SIZE` SHALL be injected as
Jinja2 template variables from `core/ui/` constants.

#### Scenario: fill_content with defaults reserves both chrome regions

- **WHEN** `fill_content("<p>Card</p>")` is called
- **THEN** the returned HTML document has a blank top region of `STATUS_BAR_HEIGHT` px
  and a blank region of `BUTTON_BAR_SIZE` px at the button-bar edge (derived
  from orientation and `portrait_rotation`), and no button labels or status bar
  content

#### Scenario: fill_content with has_statusbar=False omits status bar region

- **WHEN** `fill_content(content, has_statusbar=False)` is called
- **THEN** the returned HTML has no reserved top region

#### Scenario: fill_content with both False reproduces fullscreen behavior

- **WHEN** `fill_content(content, has_statusbar=False, has_buttons=False)` is called
- **THEN** the returned HTML occupies the full logical pixel area with no reserved regions

### Requirement: Apps may define their own layouts

Core SHALL NOT restrict where App-specific Jinja2 templates are placed. An App
that needs a custom layout MAY place templates in `<app>/layouts/` and fill
them directly using `jinja2.Environment`. Built-in Core layouts SHALL reside in
`core/layouts/`.

#### Scenario: App-specific layout is independent of Core layouts

- **WHEN** an App renders using its own `<app>/layouts/custom.html.j2`
- **THEN** the output is not affected by changes to Core layout templates
