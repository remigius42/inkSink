"""Tests for WeatherApp behavior (button state, cycling, empty locations)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from inksink.weather.app import WeatherApp


def _make_compositor():
    c = MagicMock()
    c.content_zone_height.return_value = 400
    c.content_zone_width.return_value = 800
    return c


def _make_input(actions: list[str]):
    ih = MagicMock()
    ih.wait_for_action.side_effect = actions
    return ih


def _settings(locations: list[dict] | None = None) -> dict:
    return {
        "apps": {
            "weather": {
                "locations": locations if locations is not None else [],
                "cycle_speed_seconds": 30,
                "location_shortcuts": [0, 1, 2, 3],
            }
        }
    }


def _fake_meta(location: str = "Home"):
    from inksink.weather.client import LocationMeta

    return LocationMeta(label=location, latitude="47.4", longitude="8.7")


def test_advance_is_noop_when_no_locations():
    app = WeatherApp(MagicMock(), MagicMock(), _settings(), _make_compositor())
    app._advance()  # must not raise or mutate index


def test_fetch_metadata_called_once_per_location_not_on_advance():
    """JSON metadata fetched once at init per location; _advance() must not re-fetch."""
    with patch(
        "inksink.weather.app.fetch_metadata", return_value=_fake_meta()
    ) as mock_meta:
        app = WeatherApp(
            MagicMock(),
            MagicMock(),
            _settings([{"location": "A"}, {"location": "B"}]),
            _make_compositor(),
        )
        assert mock_meta.call_count == 2

        with (
            patch("inksink.weather.app.fetch_png", return_value=MagicMock()),
            patch("inksink.weather.app.render_content", return_value=MagicMock()),
        ):
            app._advance()
            app._advance()

    assert mock_meta.call_count == 2, "fetch_metadata must not be called after init"


def test_single_location_hides_prev_and_next_buttons():
    """Prev and Next are invisible with one location; Pause/Resume stays visible."""
    comp = _make_compositor()
    with (
        patch("inksink.weather.app.fetch_metadata", return_value=_fake_meta()),
        patch("inksink.weather.app.fetch_png", return_value=MagicMock()),
        patch("inksink.weather.app.render_content", return_value=MagicMock()),
    ):
        app = WeatherApp(
            MagicMock(), _make_input(["btn_1"]), _settings([{"location": "Home"}]), comp
        )
        app.run()

    labels = comp.set_buttons.call_args_list[0][0][0]
    assert labels[1] is None, "btn_2 (Prev) should be None"
    assert labels[3] is None, "btn_4 (Next) should be None"
    assert labels[2] is not None, "btn_3 (Pause/Resume) should be visible"


def test_single_location_starts_cycle_timer():
    """Cycle timer starts even with one location so it acts as a periodic refresh."""
    comp = _make_compositor()
    with (
        patch("inksink.weather.app.fetch_metadata", return_value=_fake_meta()),
        patch("inksink.weather.app.fetch_png", return_value=MagicMock()),
        patch("inksink.weather.app.render_content", return_value=MagicMock()),
    ):
        app = WeatherApp(
            MagicMock(), _make_input(["btn_1"]), _settings([{"location": "Home"}]), comp
        )
        with patch.object(app, "_restart_timer", wraps=app._restart_timer) as spy:
            app.run()
    spy.assert_called()


def test_buttons_set_before_first_content_render():
    """set_buttons must precede set_content so content_zone dimensions are accurate."""
    call_order: list[str] = []
    comp = _make_compositor()
    comp.set_buttons.side_effect = lambda *_: call_order.append("set_buttons")
    comp.set_content.side_effect = lambda *_: call_order.append("set_content")

    with (
        patch("inksink.weather.app.fetch_metadata", return_value=_fake_meta()),
        patch("inksink.weather.app.fetch_png", return_value=MagicMock()),
        patch("inksink.weather.app.render_content", return_value=MagicMock()),
    ):
        app = WeatherApp(
            MagicMock(), _make_input(["btn_1"]), _settings([{"location": "Home"}]), comp
        )
        app.run()

    first_content = call_order.index("set_content")
    first_buttons = call_order.index("set_buttons")
    assert (
        first_buttons < first_content
    ), f"set_buttons must be called before set_content; got order {call_order}"


def _make_app(locations: list[dict], input_actions: list[str] | None = None):
    comp = _make_compositor()
    ih = _make_input(input_actions or [])
    with patch("inksink.weather.app.fetch_metadata", return_value=_fake_meta()):
        app = WeatherApp(MagicMock(), ih, _settings(locations), comp)
    return app, comp


def test_build_meta_falls_back_when_fetch_metadata_raises():
    from inksink.weather.client import WeatherFetchError

    with patch(
        "inksink.weather.app.fetch_metadata", side_effect=WeatherFetchError("x")
    ):
        app = WeatherApp(
            MagicMock(),
            MagicMock(),
            _settings([{"location": "Paris", "label": "My Paris"}]),
            _make_compositor(),
        )
    assert app._locations[0].label == "My Paris"
    assert app._locations[0].latitude == ""
    assert app._locations[0].longitude == ""


def test_show_location_is_noop_with_no_locations():
    app, comp = _make_app([])
    app._show_location(0)
    comp.set_content.assert_not_called()


def test_show_location_renders_error_image_on_fetch_png_failure():
    from inksink.weather.client import WeatherFetchError

    app, comp = _make_app([{"location": "A"}])
    with patch("inksink.weather.app.fetch_png", side_effect=WeatherFetchError("x")):
        app._show_location(0)
    comp.set_content.assert_called_once()


def test_update_buttons_pads_shortcut_slots_with_none_for_one_location():
    app, comp = _make_app([{"location": "Home"}])
    app._update_buttons()
    labels = comp.set_buttons.call_args[0][0]
    assert labels[4] == "Home"[:8]
    assert labels[5] is None
    assert labels[6] is None
    assert labels[7] is None


def test_update_buttons_pads_when_fewer_than_four_shortcuts_configured():
    """while-loop pad (line 126) only fires when _shortcuts has < 4 entries."""
    comp = _make_compositor()
    settings = {
        "apps": {
            "weather": {
                "locations": [{"location": "Home"}],
                "cycle_speed_seconds": 30,
                "location_shortcuts": [0],
            }
        }
    }
    with patch("inksink.weather.app.fetch_metadata", return_value=_fake_meta("Home")):
        app = WeatherApp(MagicMock(), MagicMock(), settings, comp)
    app._update_buttons()
    labels = comp.set_buttons.call_args[0][0]
    assert labels[4] == "Home"[:8]
    assert labels[5] is None
    assert labels[6] is None
    assert labels[7] is None


def test_pause_resume_toggles_cycling_and_timer():
    app, _ = _make_app([{"location": "A"}])
    assert app._cycling is True

    with (
        patch.object(app, "_stop_timer") as stop,
        patch.object(app, "_restart_timer") as restart,
    ):
        app._handle_pause_resume_button()
        assert app._cycling is False
        stop.assert_called_once()
        restart.assert_not_called()

        app._handle_pause_resume_button()
        assert app._cycling is True
        restart.assert_called_once()


def test_handle_next_button_wraps_from_last_to_first():
    app, _ = _make_app([{"location": "A"}, {"location": "B"}])
    app._index = 1
    with (
        patch("inksink.weather.app.fetch_png", return_value=MagicMock()),
        patch("inksink.weather.app.render_content", return_value=MagicMock()),
        patch.object(app, "_restart_timer"),
    ):
        app._handle_next_button()
    assert app._index == 0


def test_handle_shortcut_button_jumps_to_target_location():
    app, _ = _make_app([{"location": "A"}, {"location": "B"}])
    app._index = 0
    with (
        patch("inksink.weather.app.fetch_png", return_value=MagicMock()),
        patch("inksink.weather.app.render_content", return_value=MagicMock()),
        patch.object(app, "_restart_timer"),
    ):
        app._handle_shortcut_button("btn_6")  # slot 1 → shortcuts[1]=1 → location B
    assert app._index == 1


def test_handle_prev_button_wraps_from_first_to_last():
    app, _ = _make_app([{"location": "A"}, {"location": "B"}])
    app._index = 0
    with (
        patch("inksink.weather.app.fetch_png", return_value=MagicMock()),
        patch("inksink.weather.app.render_content", return_value=MagicMock()),
        patch.object(app, "_restart_timer"),
    ):
        app._handle_prev_button()
    assert app._index == 1


def _run_loop_with(app, actions: list[str]) -> None:
    """Drive _run_action_loop with a fixed sequence, ending with btn_1 to exit."""
    app._input_handler.wait_for_action.side_effect = actions
    app._run_action_loop()


def test_action_loop_btn1_calls_menu_handler():
    app, _ = _make_app([{"location": "A"}])
    with patch.object(app, "_handle_menu_button") as h:
        _run_loop_with(app, ["btn_1"])
    h.assert_called_once()


def test_action_loop_btn2_calls_prev_handler():
    app, _ = _make_app([{"location": "A"}])
    with patch.object(app, "_handle_prev_button") as h:
        _run_loop_with(app, ["btn_2", "btn_1"])
    h.assert_called_once()


def test_action_loop_btn3_calls_pause_resume_handler():
    app, _ = _make_app([{"location": "A"}])
    with patch.object(app, "_handle_pause_resume_button") as h:
        _run_loop_with(app, ["btn_3", "btn_1"])
    h.assert_called_once()


def test_action_loop_btn4_calls_next_handler():
    app, _ = _make_app([{"location": "A"}])
    with patch.object(app, "_handle_next_button") as h:
        _run_loop_with(app, ["btn_4", "btn_1"])
    h.assert_called_once()


def test_action_loop_unknown_button_calls_shortcut_handler():
    app, _ = _make_app([{"location": "A"}])
    with patch.object(app, "_handle_shortcut_button") as h:
        _run_loop_with(app, ["btn_5", "btn_1"])
    h.assert_called_once_with("btn_5")


def test_empty_locations_shows_message_and_returns():
    """No locations configured: compositor gets a message image and only Menu button."""
    comp = _make_compositor()
    app = WeatherApp(MagicMock(), _make_input(["btn_1"]), _settings([]), comp)
    app.run()

    comp.set_content.assert_called_once()
    labels = comp.set_buttons.call_args_list[0][0][0]
    assert labels[0] == "Menu"
    assert all(lbl is None for lbl in labels[1:])
