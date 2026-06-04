"""Stateful Compositor: framebuffer + two-layer rendering pipeline."""

# cspell:ignore bboxes

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Sequence

from PIL import Image, ImageDraw

from inksink.core.display import _PANEL_H, _PANEL_W
from inksink.core.ui import BUTTON_BAR_SIZE, STATUS_BAR_HEIGHT, ButtonState
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
        global_step = settings.get("display", {}).get("vertical_scroll_step", 50)
        self._scroll_step: int = display_sub.get("vertical_scroll_step", global_step)
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()
        self._labels: list[str | None] = [None] * 8
        self._states: list[ButtonState] = [ButtonState.DEFAULT] * 8
        self._buttons_set: bool = False
        self._framebuffer = self._make_framebuffer()
        self._content_image: Image.Image | None = None
        self._scroll_offset: int = 0
        self._status_bar_visible: bool = True

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

    def content_zone_height(self) -> int:
        """Return the pixel height available to App content."""
        return self._content_zone_height()

    def content_zone_width(self) -> int:
        """Return the pixel width available to App content."""
        w = self._fb_width()
        edge = _button_bar_edge(self._portrait_rotation, self._orientation)
        if edge in ("left", "right") and self._buttons_set:
            w -= BUTTON_BAR_SIZE
        return max(w, 0)

    def set_status_bar_visible(self, visible: bool) -> None:
        """Set whether the status bar is drawn. Does not trigger a display refresh.

        The caller must follow this with set_content() to make the change visible.
        This keeps the contract simple: chrome state changes take effect on the next
        full content render, not as an independent display event.
        """
        with self._lock:
            self._status_bar_visible = visible

    def set_content(self, img: Image.Image, mode: str | None = None) -> None:
        with self._lock:
            self._content_image = img
            self._scroll_offset = 0
            self._compose_and_display(full_refresh=True, mode=mode)

    def scroll_down(self) -> tuple[bool, bool]:
        with self._lock:
            return self._scroll(+self._scroll_step)

    def scroll_up(self) -> tuple[bool, bool]:
        with self._lock:
            return self._scroll(-self._scroll_step)

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
            self._buttons_set = True
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

    def _scroll(self, delta: int) -> tuple[bool, bool]:
        """Shift scroll offset by delta; re-compose if changed. Call under lock."""
        if self._content_image is None:
            return False, False
        cz_h = self._content_zone_height()
        max_offset = max(0, self._content_image.height - cz_h)
        new_offset = max(0, min(self._scroll_offset + delta, max_offset))
        if new_offset == self._scroll_offset:
            return (self._scroll_offset > 0), (self._scroll_offset < max_offset)
        self._scroll_offset = new_offset
        self._compose_and_display(full_refresh=False)
        return (self._scroll_offset > 0), (self._scroll_offset < max_offset)

    def _content_zone_height(self) -> int:
        h = self._fb_height()
        if self._status_bar_visible:
            h -= STATUS_BAR_HEIGHT
        edge = _button_bar_edge(self._portrait_rotation, self._orientation)
        if edge in ("top", "bottom") and self._buttons_set:
            h -= BUTTON_BAR_SIZE
        return max(h, 0)

    def _compose_and_display(self, full_refresh: bool, mode: str | None = None) -> None:
        """Crop content image into framebuffer and refresh. Call under lock."""
        self._framebuffer = self._make_framebuffer()
        if self._content_image is not None:
            cz_h = self._content_zone_height()
            src = self._content_image
            crop_bottom = min(self._scroll_offset + cz_h, src.height)
            cropped = src.crop((0, self._scroll_offset, src.width, crop_bottom))
            converted = cropped.convert("1")
            content_y = STATUS_BAR_HEIGHT if self._status_bar_visible else 0
            self._framebuffer.paste(converted, (0, content_y))
        self._redraw_chrome()
        if full_refresh:
            effective_mode = mode if mode is not None else self._display_mode
            if effective_mode == "4gray":
                self._display.display_4gray(self._framebuffer)
            elif effective_mode == "1bit":
                self._display.display_full(self._framebuffer)
            else:
                raise ValueError(f"unknown display mode: {effective_mode!r}")
        else:
            self._display.display_partial(self._framebuffer)

    def _redraw_chrome(self) -> None:
        draw = ImageDraw.Draw(self._framebuffer)
        if self._status_bar_visible:
            _draw_status_bar(draw, self._fb_width())
        self._redraw_buttons(draw=draw)

    def _redraw_buttons(self, draw: ImageDraw.ImageDraw | None = None) -> None:
        if not self._buttons_set:
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
