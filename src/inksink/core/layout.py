# spellchecker:ignore tmpl

"""Jinja2-based layout filling functions for Core display layouts.

Provides fill_fullscreen() and fill_default() which return complete HTML
documents ready for renderer.render(). Core automatically injects status bar
data (time, WiFi, battery) — callers do not provide these.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import jinja2

from inksink.core.state import battery_percent, wifi_status

_LAYOUTS_DIR = Path(__file__).parent / "layouts"
_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(_LAYOUTS_DIR)),
    autoescape=jinja2.select_autoescape(["html", "j2"]),
)


def fill_fullscreen(content: str) -> str:
    """Return a complete HTML document with content filling the full viewport."""
    tmpl = _ENV.get_template("fullscreen.html.j2")
    return tmpl.render(content=content)


def fill_default(content: str, buttons: list[str]) -> str:
    """Return a complete HTML document with status bar, content area, and button bar.

    Args:
        content: HTML content for the main area.
        buttons: Exactly 8 label strings (btn_1-btn_8); empty string = inactive.

    Raises:
        ValueError: If buttons length is not 8.
    """
    if len(buttons) != 8:
        raise ValueError(
            f"buttons must have exactly 8 entries (one per btn_1-btn_8), "
            f"got {len(buttons)}"
        )
    wifi = wifi_status()
    battery = battery_percent()
    now = datetime.now().strftime("%H:%M")
    tmpl = _ENV.get_template("default.html.j2")
    return tmpl.render(
        content=content,
        buttons=buttons,
        time=now,
        wifi_connected=wifi.connected,
        ssid=wifi.ssid or "",
        battery=battery,
    )
