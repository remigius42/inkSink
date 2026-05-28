"""Waveshare 7.5" V2 e-ink display driver wrapper.

Manages init/sleep lifecycle, partial vs full refresh, auto-sleep via an
idle timer, and the partial-refresh counter that triggers a full clear at
every full_refresh_interval calls to prevent ghosting. Rotates images before
driver handoff using config-driven angles.
"""

# spellchecker:ignore getbuffer

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image

_PANEL_W: int = 800
_PANEL_H: int = 480

_VALID_ROTATIONS: frozenset[int] = frozenset({0, 90, 180, 270})


class Display:
    def __init__(
        self,
        idle_timeout: int = 180,
        full_refresh_interval: int = 20,
        portrait_rotation: int = 90,
        landscape_rotation: int = 0,
    ) -> None:
        """Initialise the display wrapper.

        portrait_rotation and landscape_rotation are degrees CCW (PIL convention)
        applied before driver handoff when the image is portrait- or
        landscape-sized respectively. Only cardinal angles {0, 90, 180, 270} are
        accepted — non-cardinal values with expand=True produce non-integer
        intermediate dimensions that corrupt the 800x480 driver buffer.
        """
        if idle_timeout <= 0:
            raise ValueError(f"idle_timeout must be positive, got {idle_timeout}")
        if full_refresh_interval <= 0:
            raise ValueError(
                f"full_refresh_interval must be positive, got {full_refresh_interval}"
            )
        if portrait_rotation not in _VALID_ROTATIONS:
            raise ValueError(
                f"portrait_rotation must be one of {sorted(_VALID_ROTATIONS)}, "
                f"got {portrait_rotation}"
            )
        if landscape_rotation not in _VALID_ROTATIONS:
            raise ValueError(
                f"landscape_rotation must be one of {sorted(_VALID_ROTATIONS)}, "
                f"got {landscape_rotation}"
            )
        self._idle_timeout = idle_timeout
        self._full_refresh_interval = full_refresh_interval
        self._portrait_rotation = portrait_rotation
        self._landscape_rotation = landscape_rotation
        self._initialized = False
        self._sleeping = False
        self._partial_count = 0
        self._timer: threading.Timer | None = None
        self._lock = threading.RLock()
        self._epd = self._make_epd()

    def _make_epd(self):
        from waveshare_epd import epd7in5_V2  # type: ignore[import-untyped]

        return epd7in5_V2.EPD()

    def _require_init(self) -> None:
        if not self._initialized:
            raise RuntimeError("Display.init() must be called before displaying images")

    def _reset_timer(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self._idle_timeout, self._on_idle)
            self._timer.daemon = True
            self._timer.start()

    def _on_idle(self) -> None:
        self.sleep()

    def _wake_if_sleeping(self) -> None:
        with self._lock:
            if self._sleeping:
                self.init()

    def _rotate(self, image: Image.Image) -> Image.Image:
        """Rotate image to match the 800x480 driver buffer.

        expand=True is required: without it PIL keeps the canvas at the original
        dimensions after rotation, silently producing a wrong-sized buffer.
        """
        angle = (
            self._portrait_rotation
            if image.height > image.width
            else self._landscape_rotation
        )
        if angle == 0:
            return image
        return image.rotate(angle, expand=True)

    def init(self) -> None:
        with self._lock:
            self._epd.init()
            self._initialized = True
            self._sleeping = False
            self._reset_timer()

    def display_partial(self, image: Image.Image) -> None:
        with self._lock:
            self._wake_if_sleeping()
            self._require_init()
            image = self._rotate(image)
            self._partial_count += 1
            if self._partial_count >= self._full_refresh_interval:
                self._partial_count = 0
                self._epd.display(self._epd.getbuffer(image))
            else:
                self._epd.display_Partial(self._epd.getbuffer(image))
            self._reset_timer()

    def display_full(self, image: Image.Image) -> None:
        with self._lock:
            self._wake_if_sleeping()
            self._require_init()
            image = self._rotate(image)
            self._partial_count = 0
            self._epd.display(self._epd.getbuffer(image))
            self._reset_timer()

    def display_4gray(self, image: Image.Image) -> None:
        with self._lock:
            self._wake_if_sleeping()
            self._require_init()
            image = self._rotate(image)
            self._epd.display_4Gray(self._epd.getbuffer_4Gray(image))
            self._reset_timer()

    def set_full_refresh_interval(self, n: int) -> None:
        if n <= 0:
            raise ValueError(f"full_refresh_interval must be positive, got {n}")
        self._full_refresh_interval = n

    def sleep(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            self._epd.sleep()
            self._sleeping = True
            self._initialized = False
