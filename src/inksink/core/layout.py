# spellchecker:ignore tmpl

"""
Jinja2-based layout filling for Core display layouts.

Provides fill_content() and fill_error() which return complete HTML documents
ready for renderer.render(). Chrome regions (status bar, button bar) are blank
space — the Compositor renders them via Pillow.
"""

from __future__ import annotations

import html as _html
from pathlib import Path

import jinja2

from inksink.core.ui import BUTTON_BAR_SIZE, STATUS_BAR_HEIGHT

_LAYOUTS_DIR = Path(__file__).parent / "layouts"
_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(_LAYOUTS_DIR)),
    autoescape=jinja2.select_autoescape(["html", "j2"]),
)


def fill_content(
    content: str,
    has_statusbar: bool = True,
    has_buttons: bool = True,
) -> str:
    """
    Return a complete HTML document reserving blank chrome regions.

    Chrome (status bar, button bar) is rendered by the Compositor via Pillow;
    the template only reserves blank space of the correct size.
    """
    tmpl = _ENV.get_template("content.html.j2")
    return tmpl.render(
        content=content,
        has_statusbar=has_statusbar,
        has_buttons=has_buttons,
        status_bar_height=STATUS_BAR_HEIGHT,
        button_bar_size=BUTTON_BAR_SIZE,
    )


def fill_error(message: str) -> str:
    """Return a fullscreen HTML document showing an error message."""
    safe_message = _html.escape(message)
    content = (
        f'<div style="padding:40px;font-family:monospace;font-size:18px;">'
        f"<p>{safe_message}</p>"
        f"<p>Press any button to continue…</p>"
        f"</div>"
    )
    return fill_content(content, has_statusbar=False, has_buttons=False)
