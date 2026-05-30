"""UI constants and types shared across the compositor layer."""

from __future__ import annotations

from enum import Enum

BUTTON_BAR_SIZE: int = 80
STATUS_BAR_HEIGHT: int = 24


class ButtonState(Enum):
    DEFAULT = "default"
    ACTIVE = "active"
    DISABLED = "disabled"
