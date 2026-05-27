"""Application startup sequence.

Call startup(settings) once at boot (after load_settings()) to apply
config-driven defaults to Core subsystems.
"""

from inksink.core import renderer


def startup(settings: dict) -> None:
    """Apply settings to Core subsystems. Must be called after load_settings()."""
    renderer.configure_from_settings(settings)
