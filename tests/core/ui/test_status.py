"""Tests for core/ui/status.py — status bar rendering."""

# spellchecker:ignore langinfo

from __future__ import annotations

import locale
from datetime import datetime
from unittest.mock import patch

from PIL import Image, ImageDraw

from inksink.core.ui.status import _draw_status_bar


def _make_draw(w: int = 480, h: int = 24):
    img = Image.new("1", (w, h), color=1)
    return img, ImageDraw.Draw(img)


def test_status_bar_time_uses_locale_format():
    """Time string must use locale.nl_langinfo(T_FMT), not a hardcoded format."""
    _, draw = _make_draw()
    fixed_time = datetime(2024, 1, 15, 14, 30, 0)

    with (
        patch("inksink.core.ui.status.datetime") as mock_dt,
        patch("locale.nl_langinfo", return_value="%I:%M %p") as mock_locale,
        patch("inksink.core.ui.status.wifi_status") as mock_wifi,
        patch("inksink.core.ui.status.battery_percent", return_value=80),
    ):
        mock_dt.now.return_value = fixed_time
        mock_wifi.return_value.connected = False
        _draw_status_bar(draw, 480)

    mock_locale.assert_called_once_with(locale.T_FMT)
