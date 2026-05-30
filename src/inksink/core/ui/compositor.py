"""Stateful Compositor: framebuffer + two-layer rendering pipeline."""

# cspell:ignore bboxes

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Sequence

from PIL import Image, ImageDraw

from inksink.core.display import _PANEL_H, _PANEL_W
from inksink.core.ui import ButtonState
from inksink.core.ui.buttons import (
    _button_bar_edge,
    _compute_bounding_boxes,
    _draw_button,
    _resolve_slots,
)
from inksink.core.ui.status import _draw_status_bar

if TYPE_CHECKING:
    pass


class Compositor:
    def __init__(self, display, settings: dict) -> None:
        """Initialize compositor for the given display and runtime settings."""
        self._display = display
        self._settings = settings
        active = settings.get("_active_app", "")
        app_cfg = settings.get("apps", {}).get(active, {})
        self._orientation = app_cfg.get("orientation", "portrait")
        self._display_mode = app_cfg.get("display_mode", "1bit")
        display_sub = app_cfg.get("display", {})
        self._double_vertical = display_sub.get("double_vertical_button_size", False)
        self._portrait_rotation = settings.get("display", {}).get(
            "portrait_rotation", 90
        )
        self._status_interval = settings.get("display", {}).get(
            "status_refresh_interval", 20
        )
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()
        self._labels: list[str | None] = [""] * 8
        self._states: list[ButtonState] = [ButtonState.DEFAULT] * 8
        self._framebuffer = self._make_framebuffer()

    def _make_framebuffer(self) -> Image.Image:
        if self._orientation == "portrait":
            size = (_PANEL_H, _PANEL_W)
        else:
            size = (_PANEL_W, _PANEL_H)
        return Image.new("1", size, color=1)

    def _fb_width(self) -> int:
        return self._framebuffer.size[0]

    def _fb_height(self) -> int:
        return self._framebuffer.size[1]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_content(self, html: str) -> None:
        from inksink.core import renderer

        img = renderer.render(
            html, mode=self._display_mode, orientation=self._orientation
        )
        with self._lock:
            self._framebuffer = img.convert("1")
            self._redraw_chrome()
            if self._display_mode == "4gray":
                self._display.display_4gray(self._framebuffer)
            else:
                self._display.display_full(self._framebuffer)

    def set_buttons(
        self,
        labels: Sequence[str | None],
        states: Sequence[ButtonState],
    ) -> None:
        if len(labels) != 8 or len(states) != 8:
            raise ValueError(
                f"labels and states must each have 8 entries, "
                f"got {len(labels)} and {len(states)}"
            )
        with self._lock:
            self._labels = list(labels)
            self._states = [s for s in states]
            self._redraw_buttons()
        self._display.display_partial(self._framebuffer)

    def set_button_state(self, idx: int, state: ButtonState) -> None:
        with self._lock:
            self._states[idx] = state
            self._redraw_buttons()
        self._display.display_partial(self._framebuffer)

    def start(self) -> None:
        self._schedule_status_tick()

    def stop(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None

    # ------------------------------------------------------------------
    # Internal rendering
    # ------------------------------------------------------------------

    def _redraw_chrome(self) -> None:
        draw = ImageDraw.Draw(self._framebuffer)
        _draw_status_bar(draw, self._fb_width())
        self._redraw_buttons(draw=draw)

    def _redraw_buttons(self, draw: ImageDraw.ImageDraw | None = None) -> None:
        if not any(lbl != "" for lbl in self._labels):
            return
        if draw is None:
            draw = ImageDraw.Draw(self._framebuffer)

        groups = _resolve_slots(self._labels)
        bboxes = _compute_bounding_boxes(
            groups,
            self._orientation,
            self._double_vertical,
            self._portrait_rotation,
        )
        edge = _button_bar_edge(self._portrait_rotation, self._orientation)
        text_vertical = edge in ("left", "right")

        for x, y, w, h in bboxes:
            draw.rectangle([x, y, x + w - 1, y + h - 1], fill=1)

        for group, (x, y, w, h) in zip(groups, bboxes, strict=True):
            state = self._states[group.state_index]
            _draw_button(draw, x, y, w, h, group.label, state, text_vertical)

    def _status_tick(self) -> None:
        with self._lock:
            draw = ImageDraw.Draw(self._framebuffer)
            _draw_status_bar(draw, self._fb_width())
        self._display.display_partial(self._framebuffer)
        with self._lock:
            should_reschedule = self._timer is not None
        if should_reschedule:
            self._schedule_status_tick()

    def _schedule_status_tick(self) -> None:
        with self._lock:
            self._timer = threading.Timer(self._status_interval, self._status_tick)
            self._timer.daemon = True
            self._timer.start()
