# spellchecker:ignore tmpl

"""Jinja2 layout filling for the Anki review template."""

from __future__ import annotations

from pathlib import Path

import jinja2

from inksink.core.ui import BUTTON_BAR_SIZE, STATUS_BAR_HEIGHT

_LAYOUTS_DIR = Path(__file__).parent / "layouts"
_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(_LAYOUTS_DIR)),
    autoescape=jinja2.select_autoescape(["html", "j2"]),
)

PROGRESS_BAR_HEIGHT: int = 20


def fill_review(content: str, progress: str) -> str:
    """Return a complete HTML document for a card review screen.

    Chrome (status bar, button bar) is reserved as blank space for the
    Compositor to draw via Pillow. Only the Anki-specific progress strip
    is rendered in HTML.

    Args:
        content: Card HTML (question or answer).
        progress: Progress string shown in the progress strip, e.g. "3 / 47".

    """
    tmpl = _ENV.get_template("review.html.j2")
    return tmpl.render(
        content=content,
        progress=progress,
        status_bar_height=STATUS_BAR_HEIGHT,
        button_bar_size=BUTTON_BAR_SIZE,
        progress_bar_height=PROGRESS_BAR_HEIGHT,
    )
