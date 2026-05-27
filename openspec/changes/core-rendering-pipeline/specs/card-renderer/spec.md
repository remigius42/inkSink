## MODIFIED Requirements

### Requirement: HTML is rendered to a PIL image in the requested orientation and mode

`renderer.py` SHALL define `class Orientation(enum.StrEnum)` with members
`PORTRAIT = "portrait"` and `LANDSCAPE = "landscape"`. Because it inherits
from `str`, `Orientation` values compare equal to their string equivalents and
can be used as dict keys interchangeably with plain strings.

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

### Requirement: Renderer cache size is configurable from settings

`core/renderer.py` SHALL expose `configure_from_settings(settings: dict) -> None`
that reads `settings["renderer"]["cache_max_size"]` and calls
`configure(max_size=...)`. This is the canonical entry point for startup code to
apply the config value; it MUST be called after `load_settings()` at application
boot. Until called, the renderer uses its hardcoded default of 100.

#### Scenario: configure_from_settings applies cache size from settings

- **WHEN** `configure_from_settings({"renderer": {"cache_max_size": 5}})` is called
- **THEN** the renderer cache behaves as if `configure(max_size=5)` was called —
  the 6th unique render evicts the oldest cached entry
