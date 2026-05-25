"""HTML-to-image renderer for e-ink display.

Shells out to wkhtmltoimage to render Anki card HTML to an 800x480 PNG,
then converts via Pillow to the requested bit depth. Results are cached
in-memory by (sha256(html), mode) to avoid re-rendering unchanged cards.
Intermediate files are written to /tmp/ and cleaned up in a finally block.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from collections import OrderedDict
from pathlib import Path

from PIL import Image

_DEFAULT_CACHE_MAX_SIZE = 100


class _LRUCache:
    def __init__(self, max_size: int) -> None:
        self._store: OrderedDict[tuple[str, str], Image.Image] = OrderedDict()
        self._max_size = max_size

    def get(self, key: tuple[str, str]) -> Image.Image | None:
        if key not in self._store:
            return None
        self._store.move_to_end(key)
        return self._store[key]

    def put(self, key: tuple[str, str], value: Image.Image) -> None:
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = value
        if len(self._store) > self._max_size:
            self._store.popitem(last=False)

    def clear(self) -> None:
        self._store.clear()


_cache = _LRUCache(_DEFAULT_CACHE_MAX_SIZE)


def configure(max_size: int = _DEFAULT_CACHE_MAX_SIZE) -> None:
    """Replace the renderer cache with a fresh LRU instance of the given size."""
    global _cache
    _cache = _LRUCache(max_size)


_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{
      font-family: 'Noto Sans CJK JP', 'Noto Sans', sans-serif;
      font-size: 24px;
      padding: 20px;
      width: 760px;  /* 800px viewport minus 2x20px padding */
      margin: 0;
    }}
  </style>
</head>
<body>{content}</body>
</html>
"""

_4GRAY_LEVELS = [0, 85, 170, 255]


def render(html: str, mode: str = "1bit") -> Image.Image:
    """Render HTML to an 800x480 PIL image in the requested mode.

    Args:
        html: Card HTML fragment (not a full document).
        mode: ``"1bit"`` for PIL mode ``"1"`` (fast partial refresh),
              ``"4gray"`` for PIL mode ``"L"`` quantized to 4 levels.

    Returns:
        800x480 PIL Image ready for the display driver.
    """
    if mode not in ("1bit", "4gray"):
        raise ValueError(f"Unknown render mode: {mode!r}; expected '1bit' or '4gray'")

    key = (hashlib.sha256(html.encode()).hexdigest(), mode)
    cached = _cache.get(key)
    if cached is not None:
        return cached.copy()

    binary = shutil.which("wkhtmltoimage")
    if binary is None:
        raise RuntimeError("wkhtmltoimage not found on PATH")

    tmp = tempfile.gettempdir()
    html_path: Path | None = None
    png_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".html", dir=tmp, delete=False) as f:
            html_path = Path(f.name)
            f.write((_HTML_TEMPLATE.format(content=html)).encode("utf-8"))

        with tempfile.NamedTemporaryFile(suffix=".png", dir=tmp, delete=False) as f:
            png_path = Path(f.name)

        subprocess.run(
            [
                binary,
                "--enable-local-file-access",
                "--allow",
                tmp,
                "--width",
                "800",
                "--height",
                "480",
                "--encoding",
                "utf-8",
                str(html_path),
                str(png_path),
            ],
            check=True,
            capture_output=True,
            timeout=30,
        )

        with Image.open(png_path) as raw:
            img = raw.convert("RGB").resize((800, 480))
        converted = _convert(img, mode)
        _cache.put(key, converted.copy())
        return converted
    finally:
        if html_path and html_path.exists():
            html_path.unlink()
        if png_path and png_path.exists():
            png_path.unlink()


def _convert(img: Image.Image, mode: str) -> Image.Image:
    if mode == "1bit":
        return img.convert("1")
    if mode == "4gray":
        gray = img.convert("L")
        pixels = gray.load()
        assert pixels is not None
        w, h = gray.size
        for y in range(h):
            for x in range(w):
                v = int(pixels[x, y])  # type: ignore[arg-type]  # mode "L" pixels are int
                pixels[x, y] = min(_4GRAY_LEVELS, key=lambda lv, _v=v: abs(lv - _v))
        return gray
    raise ValueError(f"Unknown render mode: {mode!r}")
