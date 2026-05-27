## ADDED Requirements

### Requirement: Core provides a fullscreen layout

`core/layout.py` SHALL provide `fill_fullscreen(content: str) -> str` that
fills `core/layouts/fullscreen.html.j2` with the given HTML content and
returns a complete HTML document ready for `renderer.render()`. The template
SHALL occupy the full logical pixel area with no reserved regions.

#### Scenario: Fullscreen fill returns complete HTML

- **WHEN** `fill_fullscreen("<p>Hello</p>")` is called
- **THEN** the returned string is a complete HTML document containing the
  content and no button bar or status bar elements

### Requirement: Core provides a default layout with button bar and status bar

`core/layout.py` SHALL provide `fill_default(content: str, buttons: list[str]) -> str`
that fills `core/layouts/default.html.j2`. The `buttons` list SHALL contain
exactly 8 strings (one per `btn_1`–`btn_8`); an empty string means that
button is inactive. The status bar (current time, WiFi connected state, SSID, and
battery percent) SHALL be populated automatically by Core via `status.time`,
`status.wifi`, `status.ssid`, and `status.battery` — it is not the
caller's responsibility.

#### Scenario: Default fill injects content and button labels

- **WHEN** `fill_default("<p>Card</p>", ["Menu", "Show Answer", "", "", "", "", "", ""])` is called
- **THEN** the returned HTML contains the content, "Menu" in the btn_1 slot,
  "Show Answer" in the btn_2 slot, and empty strings in the remaining slots

#### Scenario: Wrong button count raises ValueError

- **WHEN** `fill_default(content, buttons)` is called with a list of length ≠ 8
- **THEN** `ValueError` is raised identifying the wrong count

#### Scenario: Status bar is auto-populated

- **WHEN** `fill_default(content, buttons)` is called
- **THEN** the returned HTML contains the current time, WiFi status, and
  battery percent without the caller supplying them

### Requirement: Apps may define their own layouts

Core SHALL NOT restrict where App-specific Jinja2 templates are placed. An App
that needs a custom layout MAY place templates in `<app>/layouts/` and fill
them directly using `jinja2.Environment`. Built-in Core layouts SHALL reside in
`core/layouts/`.

#### Scenario: App-specific layout is independent of Core layouts

- **WHEN** an App renders using its own `<app>/layouts/custom.html.j2`
- **THEN** the output is not affected by changes to Core layout templates
