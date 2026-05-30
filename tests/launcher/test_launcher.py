"""Tests for Launcher class behaviors."""

import sys
from unittest.mock import MagicMock, patch

import pytest

# Stub waveshare_epd before display import
_epd_stub = MagicMock()
_epd_stub.epd7in5_V2.EPD.side_effect = lambda: MagicMock()
sys.modules.setdefault("waveshare_epd", _epd_stub)
sys.modules.setdefault("waveshare_epd.epd7in5_V2", _epd_stub.epd7in5_V2)

from inksink.launcher.app import Launcher  # noqa: E402


def _settings():
    return {
        "apps": {"launcher": {"orientation": "portrait"}},
        "display": {"idle_timeout": 180},
    }


def _make_display():
    d = MagicMock()
    d.display_full = MagicMock()
    d.sleep = MagicMock()
    d.init = MagicMock()
    return d


def _make_input(actions):
    ih = MagicMock()
    ih.wait_for_action = MagicMock(side_effect=actions)
    return ih


# ---- Task 4.3: sleep ----


def test_btn8_calls_display_sleep_and_run_returns():
    display = _make_display()
    input_handler = _make_input(["btn_8"])

    with patch("inksink.launcher.app.fill_content", return_value="<html/>"):
        Launcher(display, input_handler, _settings(), MagicMock()).run()

    display.sleep.assert_called_once()


def test_btn8_does_not_call_display_init():
    display = _make_display()
    input_handler = _make_input(["btn_8"])

    with patch("inksink.launcher.app.fill_content", return_value="<html/>"):
        Launcher(display, input_handler, _settings(), MagicMock()).run()

    display.init.assert_not_called()


# ---- Task 4.1: settings masking ----


def test_render_settings_masks_password_key():
    display = _make_display()
    launcher = Launcher(display, _make_input([]), _settings(), MagicMock())
    captured_content: list[str] = []

    def capture_fill(content, **_kwargs):
        captured_content.append(content)
        return "<html/>"

    with (
        patch(
            "inksink.launcher.app.load_settings",
            return_value={
                "ankiweb_password": "secret123",
                "display": {"idle_timeout": 180},
            },
        ),
        patch("inksink.launcher.app.fill_content", side_effect=capture_fill),
        patch.object(launcher._input_handler, "wait_for_action", return_value="btn_1"),
    ):
        launcher._render_settings()

    content = " ".join(captured_content)
    assert "secret123" not in content
    assert "***" in content


def test_render_settings_shows_flattened_nested_key():
    display = _make_display()
    launcher = Launcher(display, _make_input([]), _settings(), MagicMock())
    captured_content: list[str] = []

    def capture_fill(content, **_kwargs):
        captured_content.append(content)
        return "<html/>"

    with (
        patch(
            "inksink.launcher.app.load_settings",
            return_value={"display": {"idle_timeout": 180}},
        ),
        patch("inksink.launcher.app.fill_content", side_effect=capture_fill),
        patch.object(launcher._input_handler, "wait_for_action", return_value="btn_1"),
    ):
        launcher._render_settings()

    content = " ".join(captured_content)
    assert "display.idle_timeout" in content


# ---- run() routing ----


def test_run_routes_btn5_to_status():
    display = _make_display()
    input_handler = _make_input(["btn_5"])
    launcher = Launcher(display, input_handler, _settings(), MagicMock())

    with (
        patch("inksink.launcher.app.fill_content", return_value="<html/>"),
        patch.object(launcher, "_render_status") as mock_status,
    ):
        mock_status.side_effect = lambda: None
        launcher.run()

    mock_status.assert_called_once()


def test_run_routes_btn6_to_settings():
    display = _make_display()
    input_handler = _make_input(["btn_6"])
    launcher = Launcher(display, input_handler, _settings(), MagicMock())

    with (
        patch("inksink.launcher.app.fill_content", return_value="<html/>"),
        patch.object(launcher, "_render_settings") as mock_settings,
    ):
        mock_settings.side_effect = lambda: None
        launcher.run()

    mock_settings.assert_called_once()


def test_run_routes_btn7_to_logs():
    display = _make_display()
    input_handler = _make_input(["btn_7"])
    launcher = Launcher(display, input_handler, _settings(), MagicMock())

    with (
        patch("inksink.launcher.app.fill_content", return_value="<html/>"),
        patch.object(launcher, "_render_logs") as mock_logs,
    ):
        mock_logs.side_effect = lambda: None
        launcher.run()

    mock_logs.assert_called_once()


# ---- Scroll clamp: no re-render when offset unchanged ----


def test_settings_no_rerender_when_btn6_clamped_at_bottom():
    """btn_6 at max offset must not trigger a second render."""
    display = _make_display()
    compositor = MagicMock()
    # 1 key → fits on screen → max_offset = 0, already at bottom
    launcher = Launcher(display, _make_input([]), _settings(), compositor)

    with (
        patch(
            "inksink.launcher.app.load_settings",
            return_value={"key": "val"},
        ),
        patch("inksink.launcher.app.fill_content", return_value="<html/>"),
        patch.object(
            launcher._input_handler,
            "wait_for_action",
            side_effect=["btn_6", "btn_1"],
        ),
    ):
        launcher._render_settings()

    assert compositor.set_content.call_count == 1


def test_settings_no_rerender_when_btn7_clamped_at_top():
    """btn_7 at offset 0 must not trigger a second render."""
    display = _make_display()
    compositor = MagicMock()
    launcher = Launcher(display, _make_input([]), _settings(), compositor)

    with (
        patch("inksink.launcher.app.load_settings", return_value={"key": "val"}),
        patch("inksink.launcher.app.fill_content", return_value="<html/>"),
        patch.object(
            launcher._input_handler,
            "wait_for_action",
            side_effect=["btn_7", "btn_1"],
        ),
    ):
        launcher._render_settings()

    assert compositor.set_content.call_count == 1


def test_settings_rerenders_when_scroll_changes_offset():
    """btn_6 with scrollable content produces a second render."""
    display = _make_display()
    compositor = MagicMock()
    launcher = Launcher(display, _make_input([]), _settings(), compositor)
    # 40 keys → total_lines=40 > _VISIBLE_LINES=34, so max_offset=6
    many_keys = {f"key{i}": i for i in range(40)}

    with (
        patch("inksink.launcher.app.load_settings", return_value=many_keys),
        patch("inksink.launcher.app.fill_content", return_value="<html/>"),
        patch.object(
            launcher._input_handler,
            "wait_for_action",
            side_effect=["btn_6", "btn_1"],
        ),
    ):
        launcher._render_settings()

    assert compositor.set_content.call_count == 2


def test_logs_no_rerender_when_btn6_clamped_at_bottom():
    """btn_6 at max offset (few log lines, already at bottom) must not re-render."""
    display = _make_display()
    compositor = MagicMock()
    launcher = Launcher(display, _make_input([]), _settings(), compositor)
    few_lines = "\n".join(f"line{i}" for i in range(5))

    with (
        patch(
            "inksink.launcher.app.subprocess.run",
            return_value=MagicMock(returncode=0, stdout=few_lines),
        ),
        patch("inksink.launcher.app.fill_content", return_value="<html/>"),
        patch.object(
            launcher._input_handler,
            "wait_for_action",
            side_effect=["btn_6", "btn_1"],
        ),
    ):
        launcher._render_logs()

    assert compositor.set_content.call_count == 1


def test_logs_no_rerender_when_btn7_clamped_at_top():
    """btn_7 when already at offset 0 (few log lines) must not re-render."""
    display = _make_display()
    compositor = MagicMock()
    launcher = Launcher(display, _make_input([]), _settings(), compositor)
    few_lines = "\n".join(f"line{i}" for i in range(5))

    with (
        patch(
            "inksink.launcher.app.subprocess.run",
            return_value=MagicMock(returncode=0, stdout=few_lines),
        ),
        patch("inksink.launcher.app.fill_content", return_value="<html/>"),
        patch.object(
            launcher._input_handler,
            "wait_for_action",
            side_effect=["btn_7", "btn_1"],
        ),
    ):
        launcher._render_logs()

    assert compositor.set_content.call_count == 1


# ---- Status screen: inactive buttons are silent no-ops ----


def test_status_non_btn1_buttons_are_ignored_until_btn1():
    """Non-btn_1 presses in STATUS state must not exit; only btn_1 returns."""
    from contextlib import ExitStack

    display = _make_display()
    launcher = Launcher(display, _make_input([]), _settings(), MagicMock())

    with ExitStack() as stack:
        stack.enter_context(
            patch("inksink.launcher.app.fill_content", return_value="<html/>")
        )
        stack.enter_context(
            patch("inksink.launcher.app.battery_percent", return_value=-1)
        )
        stack.enter_context(
            patch(
                "inksink.launcher.app.wifi_status",
                return_value=MagicMock(connected=False),
            )
        )
        stack.enter_context(patch("inksink.launcher.app.hostname", return_value="host"))
        stack.enter_context(
            patch("inksink.launcher.app.ip_address", return_value="unavailable")
        )
        stack.enter_context(
            patch(
                "inksink.launcher.app.bluetooth_status",
                return_value=MagicMock(enabled=False, connected_devices=[]),
            )
        )
        stack.enter_context(
            patch(
                "inksink.launcher.app.load_averages",
                return_value=(-1.0, -1.0, -1.0),
            )
        )
        stack.enter_context(
            patch(
                "inksink.launcher.app.memory_info",
                return_value=MagicMock(total_mb=-1),
            )
        )
        stack.enter_context(
            patch(
                "inksink.launcher.app.storage_info",
                return_value=MagicMock(total_gb=-1.0),
            )
        )
        stack.enter_context(
            patch("inksink.launcher.app.version_info", return_value="unknown")
        )
        wait_mock = stack.enter_context(
            patch.object(
                launcher._input_handler,
                "wait_for_action",
                side_effect=["btn_5", "btn_6", "btn_7", "btn_8", "btn_1"],
            )
        )

        launcher._render_status()

        assert wait_mock.call_count == 5


# ---- Logs screen: journal output appears in rendered content ----


def test_logs_content_shows_journalctl_output():
    """When journalctl succeeds, its output lines appear in the rendered content."""
    display = _make_display()
    launcher = Launcher(display, _make_input([]), _settings(), MagicMock())
    captured_content: list[str] = []

    def capture_fill(content, **_kwargs):
        captured_content.append(content)
        return "<html/>"

    with (
        patch(
            "inksink.launcher.app.subprocess.run",
            return_value=MagicMock(returncode=0, stdout="line1\nline2"),
        ),
        patch("inksink.launcher.app.fill_content", side_effect=capture_fill),
        patch.object(launcher._input_handler, "wait_for_action", return_value="btn_1"),
    ):
        launcher._render_logs()

    content = " ".join(captured_content)
    assert "line1" in content
    assert "line2" in content


def test_apps_list_contains_anki_label():
    from inksink.launcher.app import APPS

    labels = [label for label, _ in APPS]
    assert "Anki" in labels


def test_btn2_calls_run_anki_with_display_input_settings():
    """Launcher passes (display, input_handler, settings) to the app callable.

    Does NOT patch APPS — verifies the real APPS→run_anki binding is called
    with the right arguments by patching run_anki at its source module.
    """
    display = _make_display()
    input_handler = _make_input(["btn_2"])
    settings = _settings()
    received: list = []

    def capture(*args, **kwargs):
        received.append((args, kwargs))

    with (
        patch("inksink.launcher.app.fill_content", return_value="<html/>"),
        patch("inksink.launcher.app.load_settings", return_value=settings),
        patch("inksink.anki.app.run_anki", capture),
    ):
        Launcher(display, input_handler, settings, MagicMock()).run()

    assert len(received) == 1
    args, _ = received[0]
    assert args[0] is display
    assert args[1] is input_handler
    assert args[2] is settings


def test_run_app_exception_propagates():
    display = _make_display()
    input_handler = _make_input(["btn_2"])
    launcher = Launcher(display, input_handler, _settings(), MagicMock())

    with (
        patch("inksink.launcher.app.fill_content", return_value="<html/>"),
        patch(
            "inksink.launcher.app.APPS",
            [("Anki", MagicMock(side_effect=RuntimeError("crash")))],
        ),
    ):
        with pytest.raises(RuntimeError, match="crash"):
            launcher.run()
