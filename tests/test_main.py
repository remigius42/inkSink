"""Integration tests for __main__ lifecycle loop."""

# spellchecker:ignore capsys

import sys
from unittest.mock import MagicMock, patch

# Stub waveshare_epd before any display import
_epd_stub = MagicMock()
_epd_stub.epd7in5_V2.EPD.side_effect = lambda: MagicMock()
sys.modules.setdefault("waveshare_epd", _epd_stub)
sys.modules.setdefault("waveshare_epd.epd7in5_V2", _epd_stub.epd7in5_V2)

from inksink.__main__ import main  # noqa: E402

_SETTINGS = {
    "display": {
        "idle_timeout": 180,
        "portrait_rotation": 90,
        "landscape_rotation": 0,
        "full_refresh_interval": 20,
    },
    "apps": {"launcher": {"orientation": "portrait"}},
    "renderer": {"cache_max_size": 100},
}


def test_app_exception_shows_error_screen_then_restarts():
    fake_display = MagicMock()
    fake_input = MagicMock()
    fake_image = MagicMock()
    launcher_instance = MagicMock()
    launcher_instance.run.side_effect = [RuntimeError("boom"), KeyboardInterrupt]

    with (
        patch("inksink.__main__.load_settings", return_value=_SETTINGS),
        patch("inksink.__main__.startup"),
        patch("inksink.__main__.Display", return_value=fake_display),
        patch("inksink.__main__.InputHandler", return_value=fake_input),
        patch("inksink.__main__.Launcher", return_value=launcher_instance),
        patch(
            "inksink.__main__.fill_error", return_value="<error_html>"
        ) as mock_fill_error,
        patch("inksink.__main__.render", return_value=fake_image),
        patch("inksink.__main__.Orientation"),
    ):
        main()

    mock_fill_error.assert_called_once_with("boom")
    fake_display.display_full.assert_called_with(fake_image)
    fake_input.wait_for_action.assert_called()


def test_keyboard_interrupt_sleeps_display_and_exits():
    fake_display = MagicMock()
    fake_input = MagicMock()
    launcher_instance = MagicMock()
    launcher_instance.run.side_effect = KeyboardInterrupt

    with (
        patch("inksink.__main__.load_settings", return_value=_SETTINGS),
        patch("inksink.__main__.startup"),
        patch("inksink.__main__.Display", return_value=fake_display),
        patch("inksink.__main__.InputHandler", return_value=fake_input),
        patch("inksink.__main__.Launcher", return_value=launcher_instance),
        patch("inksink.__main__.fill_error"),
        patch("inksink.__main__.render"),
        patch("inksink.__main__.Orientation"),
    ):
        main()

    fake_display.sleep.assert_called_once()


def test_hardware_not_available_exits_cleanly(capsys):
    from inksink.core.input import HardwareNotAvailable

    fake_input = MagicMock()
    fake_input.setup.side_effect = HardwareNotAvailable("no GPIO")

    with (
        patch("inksink.__main__.load_settings", return_value=_SETTINGS),
        patch("inksink.__main__.startup"),
        patch("inksink.__main__.Display"),
        patch("inksink.__main__.InputHandler", return_value=fake_input),
        patch("inksink.__main__.Launcher") as mock_launcher,
    ):
        main()

    mock_launcher.assert_not_called()
    assert "Hardware not available" in capsys.readouterr().out
