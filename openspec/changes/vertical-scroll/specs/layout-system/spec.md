## MODIFIED Requirements

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
