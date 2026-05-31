"""Launcher App — single-pass menu that lets users select and launch content Apps.

__main__.py owns the infinite loop; Launcher.run() is single-pass:
renders MENU, handles one selection (App / Status / Settings / Logs / Sleep),
then returns. App exceptions propagate to __main__.py — no try/except here.
"""

from __future__ import annotations

import html
import subprocess
from typing import Callable

import inksink.anki.app as _anki_app
from inksink.core.config import load_settings
from inksink.core.layout import fill_content
from inksink.core.state import (
    battery_percent,
    bluetooth_status,
    hostname,
    ip_address,
    load_averages,
    memory_info,
    storage_info,
    version_info,
    wifi_status,
)
from inksink.core.ui import ButtonState

_VISIBLE_LINES = 34
_LINE_HEIGHT_PX = 20


# pylint: disable=unnecessary-lambda
APPS: list[tuple[str, Callable]] = [
    # lambda defers run_anki lookup so patch("inksink.anki.app.run_anki") works in tests
    ("Anki", lambda d, i, s, c: _anki_app.run_anki(d, i, s, c)),  # noqa: E731
]
# pylint: enable=unnecessary-lambda


def _flatten(obj: object, prefix: str = "") -> list[tuple[str, object]]:
    """Recursively flatten nested dicts/lists to dot/bracket-notation pairs."""
    items: list[tuple[str, object]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            full_key = f"{prefix}.{k}" if prefix else k
            items.extend(_flatten(v, full_key))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            full_key = f"{prefix}[{i}]"
            items.extend(_flatten(v, full_key))
    else:
        items.append((prefix, obj))
    return sorted(items, key=lambda t: t[0])


def _mask_credentials(key: str, value: object) -> str:
    lower = key.lower()
    if "password" in lower or "secret" in lower:
        return "***"
    return str(value)


def _scroll_content_html(lines: list[str], offset: int) -> str:
    total = len(lines)
    top_px = offset * _LINE_HEIGHT_PX
    show_down = offset + _VISIBLE_LINES < total
    show_up = offset > 0

    _abs = "position:absolute;left:0;right:0;text-align:center;"
    indicators = ""
    if show_up:
        indicators += f'<div style="{_abs}top:0;">↑ more</div>'
    if show_down:
        indicators += f'<div style="{_abs}bottom:0;">↓ more</div>'

    body = html.escape("\n".join(lines))
    pre_style = f"margin-top:-{top_px}px;font-size:{_LINE_HEIGHT_PX}px;"
    return (
        '<div style="position:relative;overflow:hidden;">'
        f"{indicators}"
        f'<pre style="{pre_style}">{body}</pre>'
        "</div>"
    )


class Launcher:
    def __init__(self, display, input_handler, settings: dict, compositor) -> None:
        """Initialize launcher with hardware handles and runtime settings."""
        self._display = display
        self._input_handler = input_handler
        self._orientation = settings["apps"]["launcher"]["orientation"]
        self._compositor = compositor

    def _render_and_display(self, html_doc: str) -> None:
        self._compositor.set_content(html_doc)

    def _set_buttons(self, labels: list[str | None]) -> None:
        converted = [lbl if lbl != "" else None for lbl in labels]
        states = [ButtonState.DEFAULT] * 8
        self._compositor.set_buttons(converted, states)

    def _render_menu(self) -> None:
        app_labels = [app[0] for app in APPS]
        btn2 = app_labels[0] if len(app_labels) > 0 else ""
        btn3 = app_labels[1] if len(app_labels) > 1 else ""
        btn4 = app_labels[2] if len(app_labels) > 2 else ""

        items_html = "".join(
            f'<div style="font-size:24px;margin:8px 0;">{html.escape(label)}</div>'
            for label in app_labels
        )
        content = f'<div style="padding:20px;">{items_html}</div>'
        buttons: list[str | None] = [
            "",
            btn2,
            btn3,
            btn4,
            "Status",
            "Settings",
            "Logs",
            "Sleep",
        ]
        html_doc = fill_content(content)
        self._set_buttons(buttons)
        self._render_and_display(html_doc)

    def _render_status(self) -> None:
        from datetime import datetime

        now = datetime.now().strftime("%H:%M:%S")
        battery = battery_percent()
        wifi = wifi_status()
        host = hostname()
        ip = ip_address()
        bt = bluetooth_status()
        load = load_averages()
        mem = memory_info()
        stor = storage_info()
        ver = version_info()

        battery_str = "unavailable" if battery == -1 else f"{battery}%"
        wifi_str = f"{wifi.ssid} ({wifi.strength}%)" if wifi.connected else "Offline"
        host_str = host[:30]
        ip_str = ip
        bt_enabled = "on" if bt.enabled else "off"
        bt_devices = (
            ", ".join(d[:30] for d in bt.connected_devices)
            if bt.connected_devices
            else "no devices connected"
        )
        bt_str = f"{bt_enabled}" + (f" — {bt_devices}" if bt.enabled else "")
        load_str = (
            "unavailable"
            if load[0] == -1.0
            else f"{load[0]:.2f} / {load[1]:.2f} / {load[2]:.2f}"
        )
        mem_str = (
            "unavailable"
            if mem.total_mb == -1
            else f"{mem.total_mb} MB total / {mem.free_mb} MB free"
        )
        stor_str = (
            "unavailable"
            if stor.total_gb == -1.0
            else f"{stor.total_gb:.1f} GB total / {stor.free_gb:.1f} GB free"
        )

        rows = [
            ("Time", now),
            ("Battery", battery_str),
            ("WiFi", wifi_str),
            ("Hostname", host_str),
            ("IP", ip_str),
            ("Bluetooth", bt_str),
            ("Load", load_str),
            ("Memory", mem_str),
            ("Storage", stor_str),
            ("Version", ver),
        ]
        rows_html = "".join(
            f"<tr><td><b>{html.escape(k)}</b></td><td>{html.escape(str(v))}</td></tr>"
            for k, v in rows
        )
        tbl_style = "font-size:18px;padding:10px;width:100%;"
        content = f'<table style="{tbl_style}">{rows_html}</table>'
        self._set_buttons(["Menu", "", "", "", "", "", "", ""])
        html_doc = fill_content(content)
        self._render_and_display(html_doc)

        while True:
            action = self._input_handler.wait_for_action()
            if action == "btn_1":
                return

    def _render_settings(self) -> None:
        settings = load_settings()
        pairs = _flatten(settings)
        lines = [f"{key}: {_mask_credentials(key, val)}" for key, val in pairs]
        total_lines = len(lines)
        max_offset = max(0, total_lines - _VISIBLE_LINES)
        offset = 0
        needs_render = True

        while True:
            if needs_render:
                content = _scroll_content_html(lines, offset)
                self._set_buttons(["Menu", "", "", "", "", "↓", "↑", ""])
                html_doc = fill_content(content)
                self._render_and_display(html_doc)
            action = self._input_handler.wait_for_action()
            if action == "btn_1":
                return
            elif action == "btn_6":
                new_offset = min(offset + 5, max_offset)
                needs_render = new_offset != offset
                offset = new_offset
            elif action == "btn_7":
                new_offset = max(0, offset - 5)
                needs_render = new_offset != offset
                offset = new_offset
            else:
                needs_render = False

    def _render_logs(self) -> None:
        try:
            result = subprocess.run(
                [
                    "/usr/bin/journalctl",
                    "-u",
                    "inksink",
                    "-n",
                    "100",
                    "--no-pager",
                    "--output=short",
                ],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode != 0:
                lines = ["unavailable"]
            else:
                lines = result.stdout.splitlines() or ["unavailable"]
        except (FileNotFoundError, OSError, subprocess.SubprocessError):
            lines = ["unavailable"]

        total_lines = len(lines)
        max_offset = max(0, total_lines - _VISIBLE_LINES)
        offset = max_offset
        needs_render = True

        while True:
            if needs_render:
                content = _scroll_content_html(lines, offset)
                self._set_buttons(["Menu", "", "", "", "", "↓", "↑", ""])
                html_doc = fill_content(content)
                self._render_and_display(html_doc)
            action = self._input_handler.wait_for_action()
            if action == "btn_1":
                return
            elif action == "btn_6":
                new_offset = min(offset + 5, max_offset)
                needs_render = new_offset != offset
                offset = new_offset
            elif action == "btn_7":
                new_offset = max(0, offset - 5)
                needs_render = new_offset != offset
                offset = new_offset
            else:
                needs_render = False

    def _render_sleep(self) -> None:
        self._display.sleep()

    def run(self) -> None:
        self._render_menu()
        action = self._input_handler.wait_for_action()

        settings = load_settings()
        if action == "btn_2" and len(APPS) > 0:
            APPS[0][1](self._display, self._input_handler, settings, self._compositor)
        elif action == "btn_3" and len(APPS) > 1:
            APPS[1][1](self._display, self._input_handler, settings, self._compositor)
        elif action == "btn_4" and len(APPS) > 2:
            APPS[2][1](self._display, self._input_handler, settings, self._compositor)
        elif action == "btn_5":
            self._render_status()
        elif action == "btn_6":
            self._render_settings()
        elif action == "btn_7":
            self._render_logs()
        elif action == "btn_8":
            self._render_sleep()
        # btn_1 / unknown: return (go back to __main__ loop → restart Launcher)
