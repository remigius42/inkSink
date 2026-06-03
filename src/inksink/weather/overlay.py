"""Compose a wttr.in PNG with location label and coordinates overlays."""

from __future__ import annotations

from PIL import Image, ImageDraw, ImageFont

_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
_FONT_SIZE = 13


def _load_font() -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(_FONT_PATH, _FONT_SIZE)
    except OSError:
        return ImageFont.load_default()


def render_content(
    png: Image.Image,
    label: str,
    coords: str | None,
    content_zone_size: tuple[int, int],
) -> Image.Image:
    """Paste *png* centered in content zone and draw label/coords overlays.

    Args:
        png: The wttr.in forecast image (already inverted).
        label: Location label drawn at the top.
        coords: Coordinate string drawn at the bottom; omitted if None.
        content_zone_size: (width, height) of the content zone — PIL convention.

    Returns:
        New "1"-mode image sized to the content zone.

    """
    zone_w, zone_h = content_zone_size
    canvas = Image.new("1", (zone_w, zone_h), color=1)
    draw = ImageDraw.Draw(canvas)
    font = _load_font()

    # Paste PNG centered
    src = png.convert("1")
    paste_x = max(0, (zone_w - src.width) // 2)
    paste_y = max(0, (zone_h - src.height) // 2)
    canvas.paste(src, (paste_x, paste_y))

    # Label at top
    if label:
        draw.text((2, 2), label, font=font, fill=0)

    # Coordinates at bottom
    if coords:
        draw.text((2, zone_h - _FONT_SIZE - 2), coords, font=font, fill=0)

    return canvas
