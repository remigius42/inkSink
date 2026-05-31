"""HTML-to-image renderer for e-ink display.

Shells out to wkhtmltoimage to render a complete HTML document to a PIL Image
in the requested orientation and bit depth. Results are cached in-memory by
(sha256(html), mode, orientation) with LRU eviction.

Callers are responsible for supplying a complete HTML document — typically via
fill_fullscreen() or fill_default() from core/layout.py.
"""

from __future__ import annotations

import enum
import hashlib
import shutil
import subprocess  # noqa: S404  # nosec B404 — subprocess is intentional; all calls use hardcoded system binaries
import tempfile
from collections import OrderedDict
from pathlib import Path
from typing import cast

from PIL import Image

from inksink.core.display import _PANEL_H, _PANEL_W

_DEFAULT_CACHE_MAX_SIZE = 100


class Orientation(enum.StrEnum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


_ORIENTATION_DIMS: dict[Orientation, tuple[int, int]] = {
    Orientation.PORTRAIT: (_PANEL_H, _PANEL_W),
    Orientation.LANDSCAPE: (_PANEL_W, _PANEL_H),
}


class _LRUCache:
    def __init__(self, max_size: int) -> None:
        self._store: OrderedDict[tuple[str, str, str], Image.Image] = OrderedDict()
        self._max_size = max_size

    def get(self, key: tuple[str, str, str]) -> Image.Image | None:
        if key not in self._store:
            return None
        self._store.move_to_end(key)
        return self._store[key]

    def put(self, key: tuple[str, str, str], value: Image.Image) -> None:
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


def configure_from_settings(settings: dict) -> None:
    """Apply renderer config from a settings dict (as returned by load_settings())."""
    configure(max_size=settings["renderer"]["cache_max_size"])


_4GRAY_LEVELS = [0, 85, 170, 255]


def render(
    html: str,
    mode: str = "1bit",
    orientation: Orientation = Orientation.PORTRAIT,
) -> Image.Image:
    """Render a complete HTML document to a PIL image.

    Args:
        html: Complete HTML document string.
        mode: ``"1bit"`` for PIL mode ``"1"``; ``"4gray"`` for 4-level grayscale.
        orientation: ``Orientation.PORTRAIT`` (480x800) or ``Orientation.LANDSCAPE``
            (800x480).

    Returns:
        PIL Image at the requested orientation dimensions.

    """
    if mode not in ("1bit", "4gray"):
        raise ValueError(f"Unknown render mode: {mode!r}; expected '1bit' or '4gray'")

    orientation = Orientation(orientation)
    width, height = _ORIENTATION_DIMS[orientation]

    key = (hashlib.sha256(html.encode()).hexdigest(), mode, str(orientation))
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
            f.write(html.encode("utf-8"))

        with tempfile.NamedTemporaryFile(suffix=".png", dir=tmp, delete=False) as f:
            png_path = Path(f.name)

        subprocess.run(  # nosec B603 — all args are hardcoded or internal; no user input  # noqa: S603
            [
                binary,
                "--enable-local-file-access",
                "--allow",
                tmp,
                "--width",
                str(width),
                "--height",
                str(height),
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
            img = raw.convert("RGB").resize((width, height))
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
        w, h = gray.size
        for y in range(h):
            for x in range(w):
                v = cast(int, pixels[x, y])  # type: ignore[union-attr]
                pixels[x, y] = min(_4GRAY_LEVELS, key=lambda lv, _v=v: abs(lv - _v))  # type: ignore[union-attr]
        return gray
    raise ValueError(f"Unknown render mode: {mode!r}")
