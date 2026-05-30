"""Pillow status bar renderer."""

# spellchecker:ignore langinfo

from __future__ import annotations

import locale
from datetime import datetime
from typing import TYPE_CHECKING

from PIL import ImageFont

if TYPE_CHECKING:
    from PIL import ImageDraw

from inksink.core.state import battery_percent, wifi_status


def _draw_status_bar(
    draw: ImageDraw.ImageDraw,
    w: int,
) -> None:
    """Draw time, WiFi, battery onto draw at y=0..STATUS_BAR_HEIGHT."""
    now = datetime.now().strftime(locale.nl_langinfo(locale.T_FMT))
    wifi = wifi_status()
    battery = battery_percent()

    wifi_str = wifi.ssid if wifi.connected else "No WiFi"
    batt_str = f"{battery}%" if battery >= 0 else "?"

    font = ImageFont.load_default()
    y = 2
    draw.text((4, y), now, fill=0, font=font)
    if wifi_str:
        draw.text((w // 2 - 30, y), wifi_str, fill=0, font=font)
    draw.text((w - 40, y), batt_str, fill=0, font=font)
