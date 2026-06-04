"""Integration tests for __main__ lifecycle loop."""

# spellchecker:ignore capsys

import sys
from unittest.mock import MagicMock, patch

import pytest

# Stub waveshare_epd before any display import
_epd_stub = MagicMock()
_epd_stub.epd7in5_V2.EPD.side_effect = MagicMock
sys.modules.setdefault("waveshare_epd", _epd_stub)
sys.modules.setdefault("waveshare_epd.epd7in5_V2", _epd_stub.epd7in5_V2)

from inksink.__main__ import _handle_app_exception, main  # noqa: E402

_SETTINGS = {
    "display": {
        "idle_timeout": 180,
        "portrait_rotation": 90,
        "landscape_rotation": 0,
        "full_refresh_interval": 20,
    },
    "apps": {
        "launcher": {"orientation": "portrait"},
        "display_server": {
            "enabled": False,
            "http_port": 0,
            "https_port": 0,
            "token": "",
            "orientation": "portrait",
        },
    },
    "renderer": {"cache_max_size": 100},
}


def test_handle_app_exception_stops_compositor_renders_error_and_restarts():
    compositor = MagicMock()
    display = MagicMock()
    input_handler = MagicMock()
    fake_image = MagicMock()

    with (
        patch("inksink.__main__.fill_error", return_value="<err>") as mock_fill,
        patch("inksink.__main__.render", return_value=fake_image),
        patch("inksink.__main__.Orientation"),
    ):
        _handle_app_exception(
            RuntimeError("oops"), compositor, display, input_handler, _SETTINGS
        )

    compositor.stop.assert_called_once()
    mock_fill.assert_called_once_with("oops")
    display.display_full.assert_called_once_with(fake_image)
    input_handler.wait_for_action.assert_called_once()
    compositor.start.assert_called_once()


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
        patch("inksink.__main__.DisplayServer"),
        patch("inksink.__main__.fill_error"),
        patch("inksink.__main__.render"),
        patch("inksink.__main__.Orientation"),
    ):
        main()

    fake_display.sleep.assert_called_once()


def test_display_server_not_started_when_disabled():
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
        patch("inksink.__main__.DisplayServer") as mock_ds_cls,
        patch("inksink.__main__.fill_error"),
        patch("inksink.__main__.render"),
        patch("inksink.__main__.Orientation"),
    ):
        main()

    mock_ds_cls.assert_not_called()


def test_display_server_start_failure_cleans_up():
    fake_display = MagicMock()
    fake_compositor = MagicMock()
    fake_input = MagicMock()
    _enabled_settings = {
        **_SETTINGS,
        "apps": {
            **_SETTINGS["apps"],
            "display_server": {**_SETTINGS["apps"]["display_server"], "enabled": True},
        },
    }
    mock_ds_instance = MagicMock()
    mock_ds_instance.start.side_effect = Exception("port in use")

    with (
        patch("inksink.__main__.load_settings", return_value=_enabled_settings),
        patch("inksink.__main__.startup", return_value=fake_compositor),
        patch("inksink.__main__.Display", return_value=fake_display),
        patch("inksink.__main__.InputHandler", return_value=fake_input),
        patch("inksink.__main__.DisplayServer", return_value=mock_ds_instance),
        patch("inksink.__main__.Launcher"),
        patch("inksink.__main__.fill_error"),
        patch("inksink.__main__.render"),
        patch("inksink.__main__.Orientation"),
    ):
        with pytest.raises(Exception, match="port in use"):
            main()

    fake_display.sleep.assert_called_once()
    fake_compositor.stop.assert_called_once()


_ENABLED_SETTINGS = {
    **_SETTINGS,
    "apps": {
        **_SETTINGS["apps"],
        "display_server": {**_SETTINGS["apps"]["display_server"], "enabled": True},
    },
}


def _make_main_mocks(*, take_side_effect, run_side_effect, wait_side_effect=()):
    fake_display = MagicMock()
    fake_compositor = MagicMock()
    fake_input = MagicMock()
    fake_input.wait_for_action.side_effect = list(wait_side_effect)
    launcher_instance = MagicMock()
    launcher_instance.run.side_effect = list(run_side_effect)
    mock_ds_instance = MagicMock()
    mock_ds_instance.take.side_effect = list(take_side_effect)
    return (
        fake_display,
        fake_compositor,
        fake_input,
        launcher_instance,
        mock_ds_instance,
    )


def _run_main_with_mocks(
    fake_display, fake_compositor, fake_input, launcher_instance, mock_ds_instance
):
    with (
        patch("inksink.__main__.load_settings", return_value=_ENABLED_SETTINGS),
        patch("inksink.__main__.startup", return_value=fake_compositor),
        patch("inksink.__main__.Display", return_value=fake_display),
        patch("inksink.__main__.InputHandler", return_value=fake_input),
        patch("inksink.__main__.Launcher", return_value=launcher_instance),
        patch("inksink.__main__.DisplayServer", return_value=mock_ds_instance),
        patch("inksink.__main__.fill_error"),
        patch("inksink.__main__.render"),
        patch("inksink.__main__.Orientation"),
    ):
        main()


# ---------------------------------------------------------------------------
# Display server loop scenarios
# ---------------------------------------------------------------------------


def test_scenario_1_launcher_interrupted_by_image_then_shown_then_launcher():
    """Launcher interrupted by image → shown until button → back to launcher."""
    fake_img = MagicMock()
    fake_display, fake_compositor, fake_input, launcher_instance, mock_ds_instance = (
        _make_main_mocks(
            take_side_effect=[None, (fake_img, "1bit")],
            run_side_effect=[None, KeyboardInterrupt],
            wait_side_effect=["btn_1"],
        )
    )

    _run_main_with_mocks(
        fake_display, fake_compositor, fake_input, launcher_instance, mock_ds_instance
    )

    fake_compositor.set_content.assert_called_once_with(fake_img, mode="1bit")
    assert launcher_instance.run.call_count == 2


def test_scenario_2_new_image_replaces_shown_image_without_launcher():
    """New image arrives while showing → shown directly, no launcher in between."""
    img1, img2 = MagicMock(), MagicMock()
    fake_display, fake_compositor, fake_input, launcher_instance, mock_ds_instance = (
        _make_main_mocks(
            take_side_effect=[(img1, "1bit"), (img2, "1bit")],
            run_side_effect=[KeyboardInterrupt],
            wait_side_effect=["", "btn_1"],
        )
    )

    _run_main_with_mocks(
        fake_display, fake_compositor, fake_input, launcher_instance, mock_ds_instance
    )

    assert fake_compositor.set_content.call_count == 2
    assert launcher_instance.run.call_count == 1


def test_scenario_3_launcher_image_button_launcher_image_shown():
    """Launcher → image → button → launcher → image → shown."""
    img1, img2 = MagicMock(), MagicMock()
    fake_display, fake_compositor, fake_input, launcher_instance, mock_ds_instance = (
        _make_main_mocks(
            take_side_effect=[None, (img1, "1bit"), (img2, "1bit")],
            run_side_effect=[None, None, KeyboardInterrupt],
            wait_side_effect=["btn_1", "btn_1"],
        )
    )

    _run_main_with_mocks(
        fake_display, fake_compositor, fake_input, launcher_instance, mock_ds_instance
    )

    assert fake_compositor.set_content.call_count == 2
    assert launcher_instance.run.call_count == 3


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
