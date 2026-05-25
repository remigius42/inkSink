## ADDED Requirements

### Requirement: HTML is rendered to an 800×480 PIL image in the requested mode

`renderer.py` SHALL accept an HTML string and a `mode` argument (`"1bit"` or
`"4gray"`) and return a `PIL.Image` at exactly 800×480 pixels. For `"1bit"`,
the image mode SHALL be `"1"` (1-bit black and white), suitable for
`display_partial()`. For `"4gray"`, the mode SHALL be `"L"` quantized to 4
levels (0, 85, 170, 255), suitable for `display_4gray()`. Default: `"1bit"`.

#### Scenario: 1-bit output dimensions and mode are correct

- **WHEN** `render(html, mode="1bit")` is called
- **THEN** the returned image has size `(800, 480)` and mode `"1"`

#### Scenario: 4-gray output dimensions and mode are correct

- **WHEN** `render(html, mode="4gray")` is called
- **THEN** the returned image has size `(800, 480)`, mode `"L"`, and only the
  pixel values 0, 85, 170, 255

### Requirement: CJK characters render correctly

The renderer SHALL use `fonts-noto-cjk` so that Japanese and Chinese
characters in Anki card HTML display without tofu (missing glyph boxes).

#### Scenario: Kanji renders without tofu

- **WHEN** `render("<p>日本語</p>")` is called
- **THEN** the output image contains non-blank pixels in the character regions

### Requirement: Rendered images are cached by content hash and mode

Calling `render(html, mode)` with identical HTML and mode SHALL return the
cached image without re-invoking `wkhtmltoimage`. The cache key SHALL be
`(sha256(html), mode)`. The cache SHALL be in-memory (not persisted to disk).

#### Scenario: Repeated render skips wkhtmltoimage

- **WHEN** `render(html, mode)` is called twice with the same HTML and mode
- **THEN** `wkhtmltoimage` is invoked exactly once

#### Scenario: Different mode bypasses cache

- **WHEN** `render(html, "1bit")` is called followed by `render(html, "4gray")`
- **THEN** `wkhtmltoimage` is invoked twice and each call returns the correct mode

### Requirement: Intermediate files are written to `/tmp/`

The renderer SHALL write the temporary HTML and PNG files to `/tmp/` and
clean them up after each render. Files SHALL NOT be left on disk between
renders.

#### Scenario: No leftover files after render

- **WHEN** `render(html)` completes successfully
- **THEN** no `.html` or `.png` files from the render remain in `/tmp/`

#### Scenario: Cleanup on render failure

- **WHEN** `render(html)` fails due to `wkhtmltoimage` error or image loading error
- **THEN** no `.html` or `.png` files from the failed render remain in `/tmp/`
