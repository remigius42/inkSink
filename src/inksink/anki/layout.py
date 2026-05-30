# spellchecker:ignore tmpl

"""Jinja2 layout filling for the Anki review template."""

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


def fill_review(content: str, progress: str, buttons: list[str]) -> str:
    """Return a complete HTML document for a card review screen.

    Args:
        content: Card HTML (question or answer).
        progress: Progress string shown top-right, e.g. "3 / 47".
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
    tmpl = _ENV.get_template("review.html.j2")
    return tmpl.render(
        content=content,
        progress=progress,
        buttons=buttons,
        time=now,
        wifi_connected=wifi.connected,
        ssid=wifi.ssid or "",
        battery=battery,
    )
