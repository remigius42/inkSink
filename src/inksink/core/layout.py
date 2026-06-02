# spellchecker:ignore tmpl

"""Jinja2-based layout filling for Core display layouts.

Provides fill_content() and fill_error() which return complete HTML documents
ready for renderer.render(). Templates render pure content; chrome placement
is the Compositor's responsibility.
"""

from __future__ import annotations

import html as _html
from pathlib import Path

import jinja2

_LAYOUTS_DIR = Path(__file__).parent / "layouts"
_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(_LAYOUTS_DIR)),
    autoescape=jinja2.select_autoescape(["html", "j2"]),
)


def fill_content(content: str) -> str:
    """Return a complete HTML document with pure content at full panel width.

    Chrome (status bar, button bar) is placed by the Compositor via Pillow.
    """
    tmpl = _ENV.get_template("content.html.j2")
    return tmpl.render(content=content)


def fill_error(message: str) -> str:
    """Return a fullscreen HTML document showing an error message."""
    safe_message = _html.escape(message)
    content = (
        f'<div style="padding:40px;font-family:monospace;font-size:18px;">'
        f"<p>{safe_message}</p>"
        f"<p>Press any button to continue…</p>"
        f"</div>"
    )
    return fill_content(content)
