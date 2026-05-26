## MODIFIED Requirements

### Requirement: HTML is rendered to a PIL image in the requested orientation and mode

`renderer.py` SHALL define an `Orientation` enum (extending `str` and
`enum.Enum`, i.e. a `StrEnum`) with members `PORTRAIT = "portrait"` and
`LANDSCAPE = "landscape"`. Because it inherits from `str`, `Orientation`
values compare equal to their string equivalents and can be used as dict keys
interchangeably with plain strings.

`render(html, mode="1bit", orientation=Orientation.PORTRAIT)` SHALL accept a
**complete HTML document** string (not a fragment); `mode` and `orientation`
are optional with the shown defaults. It SHALL resolve orientation to pixel
dimensions internally via `_ORIENTATION_DIMS` and return a `PIL.Image` at
those dimensions. For `"1bit"`, the image mode SHALL be `"1"`. For `"4gray"`,
the mode SHALL be `"L"` quantized to 4 levels (0, 85, 170, 255).

The internal `_HTML_TEMPLATE` wrapper SHALL be removed; `render()` passes the
`html` argument directly to wkhtmltoimage. Callers are responsible for
supplying a complete document — typically via `fill_fullscreen()` or
`fill_default()` from `core/layout.py`.

Apps convert their config string at call time: `Orientation(settings["apps"]["<name>"]["orientation"])`.

#### Scenario: Portrait output dimensions and mode are correct

- **WHEN** `render(html, mode="1bit", orientation=Orientation.PORTRAIT)` is called
- **THEN** the returned image has size `(480, 800)` and mode `"1"`

#### Scenario: Landscape output dimensions and mode are correct

- **WHEN** `render(html, mode="1bit", orientation=Orientation.LANDSCAPE)` is called
- **THEN** the returned image has size `(800, 480)` and mode `"1"`

#### Scenario: 4-gray portrait output is correct

- **WHEN** `render(html, mode="4gray", orientation=Orientation.PORTRAIT)` is called
- **THEN** the returned image has size `(480, 800)`, mode `"L"`, and only the
  pixel values 0, 85, 170, 255

### Requirement: Rendered images are cached by content hash, mode, and orientation

Calling `render(html, mode, orientation)` with identical arguments SHALL
return the cached image without re-invoking `wkhtmltoimage`. The cache key
SHALL be `(sha256(html), mode, orientation)`. The cache SHALL be in-memory,
bounded to `renderer.cache_max_size` entries (default 100), with
least-recently-used eviction. `configure(max_size)` replaces the cache with a
fresh instance of the given size.

#### Scenario: Repeated render skips wkhtmltoimage

- **WHEN** `render(html, mode, orientation)` is called twice with identical arguments
- **THEN** `wkhtmltoimage` is invoked exactly once

#### Scenario: Different orientations bypass cache

- **WHEN** `render(html, "1bit", Orientation.PORTRAIT)` is called followed by
  `render(html, "1bit", Orientation.LANDSCAPE)`
- **THEN** `wkhtmltoimage` is invoked twice and each result has the correct dimensions
