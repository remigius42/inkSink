"""Tests for weather overlay rendering."""

from __future__ import annotations

from PIL import Image

from inksink.weather.overlay import render_content


def _white_png(width: int = 200, height: int = 100) -> Image.Image:
    return Image.new("1", (width, height), color=1)


_CONTENT_SIZE = (600, 300)  # (width, height) — PIL convention


# ---------------------------------------------------------------------------
# render_content returns a PIL Image of correct size
# ---------------------------------------------------------------------------


def test_render_content_size_is_width_height():
    """content_zone_size is (width, height); result.size must equal it directly."""
    w, h = _CONTENT_SIZE
    result = render_content(_white_png(), "Home", "47.4, 8.7", _CONTENT_SIZE)
    assert result.size == (w, h)


def test_render_content_returns_image_of_content_zone_size():
    result = render_content(_white_png(), "Home", "47.4, 8.7", _CONTENT_SIZE)
    assert isinstance(result, Image.Image)
    w, h = _CONTENT_SIZE
    assert result.size == (w, h)


# ---------------------------------------------------------------------------
# PNG is pasted into result (not just blank)
# ---------------------------------------------------------------------------


def test_render_content_pastes_png_onto_canvas():
    black_png = Image.new("1", (200, 100), color=0)
    result = render_content(black_png, "Home", "47.4, 8.7", _CONTENT_SIZE)
    # The PNG should be pasted somewhere — result must not be all-white
    pixels = list(result.get_flattened_data())
    assert any(p == 0 for p in pixels), "PNG was not pasted onto canvas"


# ---------------------------------------------------------------------------
# Label present — some black pixels in upper portion (label drawn)
# ---------------------------------------------------------------------------


def test_render_content_draws_label_at_top():
    white_png = _white_png()
    result = render_content(white_png, "MyCity", None, _CONTENT_SIZE)
    # Sample top 20 rows for any black pixel (label text)
    top_strip = result.crop((0, 0, _CONTENT_SIZE[0], 20))
    pixels = list(top_strip.get_flattened_data())
    assert any(p == 0 for p in pixels), "No label text found in top strip"


# ---------------------------------------------------------------------------
# Coords present — some black pixels in lower portion
# ---------------------------------------------------------------------------


def test_render_content_draws_coords_at_bottom():
    white_png = _white_png()
    result = render_content(white_png, "MyCity", "47.4, 8.7", _CONTENT_SIZE)
    w, h = _CONTENT_SIZE
    bottom_strip = result.crop((0, h - 20, w, h))
    pixels = list(bottom_strip.get_flattened_data())
    assert any(p == 0 for p in pixels), "No coords text found in bottom strip"


# ---------------------------------------------------------------------------
# Coords absent — no error, result still valid
# ---------------------------------------------------------------------------


def test_render_content_no_coords_does_not_raise():
    result = render_content(_white_png(), "Home", None, _CONTENT_SIZE)
    assert isinstance(result, Image.Image)


# ---------------------------------------------------------------------------
# Label absent — no error
# ---------------------------------------------------------------------------


def test_render_content_empty_label_does_not_raise():
    result = render_content(_white_png(), "", "47.4, 8.7", _CONTENT_SIZE)
    assert isinstance(result, Image.Image)
