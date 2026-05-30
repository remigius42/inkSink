"""Application startup sequence.

Call startup(settings, display) once at boot to apply config-driven defaults
and instantiate core subsystems. Returns a Compositor.
"""

from __future__ import annotations

from inksink.core import renderer


def startup(settings: dict, display=None, active_app: str = ""):
    """Apply settings to Core subsystems; return a Compositor if display given."""
    renderer.configure_from_settings(settings)
    if display is None:
        return None
    from inksink.core.ui.compositor import Compositor

    patched = dict(settings)
    if active_app:
        patched["_active_app"] = active_app
    compositor = Compositor(display, patched)
    return compositor
