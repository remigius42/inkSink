"""GPIO button input handler with debounce.

Uses a polling loop (10ms interval, 50ms debounce) rather than GPIO
interrupts to avoid callback-threading complexity. RPi.GPIO is imported
lazily so the module is safe to import on non-Pi dev machines.
"""

from __future__ import annotations

import time
from typing import Any

_DEFAULT_PIN_MAP: dict[int, str] = {
    4: "btn_1",
    12: "btn_2",
    13: "btn_3",
    16: "btn_4",
    19: "btn_5",
    22: "btn_6",
    26: "btn_7",
    27: "btn_8",
}

_DEBOUNCE_S = 0.05
_POLL_S = 0.01


class HardwareNotAvailable(Exception):
    """Raised when RPi.GPIO cannot be imported on a non-Pi host."""


class InputHandler:
    """Maps GPIO pins to named actions and blocks until a button is pressed.

    The App layer is responsible for passing the mapping from config, e.g.:
        InputHandler(load_settings()["apps"]["anki"].get("button_map"))
    If pin_map is None the default mapping from the build guide is used.
    """

    def __init__(self, pin_map: dict[int, str] | None = None) -> None:
        resolved = dict(pin_map) if pin_map is not None else dict(_DEFAULT_PIN_MAP)
        if not resolved:
            raise ValueError(
                "pin_map must not be empty; wait_for_action() would never return"
            )
        self._pin_map = resolved
        self._gpio: Any = self._import_gpio()
        self._setup_done = False

    def _import_gpio(self) -> Any:
        try:
            import RPi.GPIO as GPIO  # type: ignore[reportMissingModuleSource]

            return GPIO
        except ImportError:
            return None

    def setup(self) -> None:
        """Configure all button pins as input with internal pull-ups."""
        if self._gpio is None:
            raise HardwareNotAvailable("RPi.GPIO not available")
        self._gpio.setmode(self._gpio.BCM)
        for pin in self._pin_map:
            self._gpio.setup(pin, self._gpio.IN, pull_up_down=self._gpio.PUD_UP)
        self._setup_done = True

    def wait_for_action(self) -> str:
        """Block until a button is cleanly pressed; return the action name."""
        if self._gpio is None:
            raise HardwareNotAvailable("RPi.GPIO not available")
        if not self._setup_done:
            raise RuntimeError(
                "InputHandler.setup() must be called before wait_for_action()"
            )
        while True:
            for pin, action in self._pin_map.items():
                if self._gpio.input(pin) == 0:  # active-low
                    time.sleep(_DEBOUNCE_S)
                    if self._gpio.input(pin) == 0:
                        return action
            time.sleep(_POLL_S)
