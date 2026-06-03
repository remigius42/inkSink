# Renderer: exact lines to change

File: `src/inksink/core/renderer.py`

## 1. Drop `--height` from wkhtmltoimage invocation

In `_invoke_wkhtmltoimage()`, remove the two lines:

```python
"--height",
str(height),
```

The `height` parameter can stay in the function signature for now (it's derived
from orientation dims); only the CLI flags are removed.

## 2. Drop `resize()` from `_render_html_to_image()`

The current line is:

```python
img = raw.convert("RGB").resize((width, height))
```

Change to:

```python
img = raw.convert("RGB")
```

The `.resize()` was silently distorting content whenever the natural content
height differed from panel height. Removing it is a correctness fix independent
of scrolling.

## 3. Cache key is unchanged

Cache key is `(sha256(html), mode, str(orientation))`. Since we always drop
`--height`, the same HTML + orientation always produces the same natural-height
image. No key change needed.

## 4. Add max_image_height truncation after wkhtmltoimage returns

In `_render_html_to_image()`, after converting but before returning, add:

```python
max_h = settings.get("renderer", {}).get("max_image_height", 8000)
if converted.height > max_h:
    import warnings
    warnings.warn(f"Rendered image height {converted.height}px exceeds max_image_height {max_h}px (content hash: {cache_key}); truncating.")
    converted = converted.crop((0, 0, converted.width, max_h))
```

`cache_key` (the `sha256(html)` value) is already computed earlier in `_render_html_to_image()` — use it directly.

The renderer doesn't currently receive `settings` — the simplest path is to
read it from the module-level configured state (similar to how `_cache` is
module-level) or pass it in. Follow the existing `configure_from_settings()`
pattern: add a module-level `_max_image_height` variable set by
`configure_from_settings()`.

## 5. `_ORIENTATION_DIMS` is still used

`width` is still needed for `--width`. `height` is no longer passed to
wkhtmltoimage but is still used by callers that expected a fixed-size image —
verify no callers use the returned image's `.height` assuming it equals panel
height.
