"""Weather App — displays wttr.in forecast PNGs in landscape orientation."""

from __future__ import annotations

import signal
import threading
from dataclasses import dataclass

from inksink.core.ui import ButtonState
from inksink.weather.client import (
    LocationMeta,
    WeatherFetchError,
    fetch_metadata,
    fetch_png,
)
from inksink.weather.overlay import render_content


@dataclass
class _LocationMeta:
    location: str
    label: str
    latitude: str
    longitude: str


def _build_meta(entry: dict) -> _LocationMeta:
    location = entry["location"]
    try:
        meta: LocationMeta = fetch_metadata(location)
        label = entry.get("label") or meta.label
        return _LocationMeta(
            location=location,
            label=label,
            latitude=meta.latitude,
            longitude=meta.longitude,
        )
    except WeatherFetchError:
        return _LocationMeta(
            location=location,
            label=entry.get("label") or location,
            latitude="",
            longitude="",
        )


class WeatherApp:
    def __init__(self, display, input_handler, settings: dict, compositor) -> None:
        """Initialize with hardware handles and runtime settings."""
        self._display = display
        self._input_handler = input_handler
        self._compositor = compositor
        cfg = settings.get("apps", {}).get("weather", {})
        self._cycle_speed: int = cfg.get("cycle_speed_seconds", 30)
        self._shortcuts: list[int] = cfg.get("location_shortcuts", [0, 1, 2, 3])
        location_entries: list[dict] = cfg.get("locations", [])
        self._locations: list[_LocationMeta] = [
            _build_meta(e) for e in location_entries
        ]
        self._index: int = 0
        self._cycling: bool = True
        self._timer: threading.Timer | None = None
        self._lock = threading.Lock()

    def _show_location(self, idx: int) -> None:
        if not self._locations:
            return
        meta = self._locations[idx]
        coords = (
            f"{meta.latitude}, {meta.longitude}"
            if meta.latitude and meta.longitude
            else None
        )
        content_size = (
            self._compositor.content_zone_width(),
            self._compositor.content_zone_height(),
        )
        try:
            png = fetch_png(meta.location)
            img = render_content(png, meta.label, coords, content_size)
        except WeatherFetchError:
            from PIL import Image, ImageDraw

            w, h = content_size[0], content_size[1]
            img = Image.new("1", (w, h), color=1)
            draw = ImageDraw.Draw(img)
            draw.text(
                (10, h // 2 - 10), "Both wttr.in and wttr.is are unreachable", fill=0
            )
        self._compositor.set_content(img)

    def _advance(self) -> None:
        with self._lock:
            if not self._locations:
                return
            self._index = (self._index + 1) % len(self._locations)
            idx = self._index
        self._show_location(idx)
        if self._cycling:
            self._restart_timer()

    def _restart_timer(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self._cycle_speed, self._advance)
            self._timer.daemon = True
            self._timer.start()

    def _stop_timer(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None

    def _update_buttons(self) -> None:
        pause_label = "Pause" if self._cycling else "Resume"
        shortcut_labels: list[str | None] = []
        for idx in self._shortcuts[:4]:
            if idx < len(self._locations):
                label = self._locations[idx].label
                shortcut_labels.append(label[:8])
            else:
                shortcut_labels.append(None)
        while len(shortcut_labels) < 4:
            shortcut_labels.append(None)

        single = len(self._locations) <= 1
        labels: list[str | None] = [
            "Menu",
            None if single else "Prev",
            pause_label,
            None if single else "Next",
            shortcut_labels[0],
            shortcut_labels[1],
            shortcut_labels[2],
            shortcut_labels[3],
        ]
        self._compositor.set_buttons(labels, [ButtonState.DEFAULT] * 8)

    def _handle_no_locations(self) -> None:
        from PIL import Image, ImageDraw

        w, h = (
            self._compositor.content_zone_width(),
            self._compositor.content_zone_height(),
        )
        img = Image.new("1", (w, h), color=1)
        draw = ImageDraw.Draw(img)
        draw.text((10, h // 2 - 10), "No weather locations configured.", fill=0)
        self._compositor.set_content(img)
        self._compositor.set_buttons(
            ["Menu", None, None, None, None, None, None, None],
            [ButtonState.DEFAULT] * 8,
        )
        self._input_handler.wait_for_action()

    def _handle_menu_button(self) -> None:
        self._stop_timer()

    def _handle_prev_button(self) -> None:
        if self._locations:
            with self._lock:
                self._index = (self._index - 1) % len(self._locations)
                idx = self._index
            self._show_location(idx)
            if self._cycling:
                self._restart_timer()

    def _handle_pause_resume_button(self) -> None:
        self._cycling = not self._cycling
        if self._cycling:
            self._restart_timer()
        else:
            self._stop_timer()
        self._update_buttons()

    def _handle_next_button(self) -> None:
        if self._locations:
            with self._lock:
                self._index = (self._index + 1) % len(self._locations)
                idx = self._index
            self._show_location(idx)
            if self._cycling:
                self._restart_timer()

    def _handle_shortcut_button(self, action: str) -> None:
        btn_map = {f"btn_{5 + i}": i for i in range(4)}
        if action in btn_map:
            slot = btn_map[action]
            if slot < len(self._shortcuts):
                target = self._shortcuts[slot]
                if target < len(self._locations):
                    with self._lock:
                        self._index = target
                        idx = self._index
                    self._show_location(idx)
                    if self._cycling:
                        self._restart_timer()

    def _run_action_loop(self) -> None:
        while True:
            action = self._input_handler.wait_for_action()

            if action == "btn_1":
                self._handle_menu_button()
                return
            elif action == "btn_2":
                self._handle_prev_button()
            elif action == "btn_3":
                self._handle_pause_resume_button()
            elif action == "btn_4":
                self._handle_next_button()
            else:
                self._handle_shortcut_button(action)

    def run(self) -> None:
        if not self._locations:
            self._handle_no_locations()
            return

        def _sigterm(_sig, _frame):  # noqa: ANN001
            self._stop_timer()
            self._display.sleep()

        signal.signal(signal.SIGTERM, _sigterm)

        with self._lock:
            idx = self._index
        self._update_buttons()
        self._show_location(idx)
        if self._cycling and self._locations:
            self._restart_timer()

        self._run_action_loop()


def run(display, input_handler, settings: dict, compositor) -> None:
    WeatherApp(display, input_handler, settings, compositor).run()
