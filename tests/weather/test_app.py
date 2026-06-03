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


def test_empty_locations_shows_message_and_returns():
    """No locations configured: compositor gets a message image and only Menu button."""
    comp = _make_compositor()
    app = WeatherApp(MagicMock(), _make_input(["btn_1"]), _settings([]), comp)
    app.run()

    comp.set_content.assert_called_once()
    labels = comp.set_buttons.call_args_list[0][0][0]
    assert labels[0] == "Menu"
    assert all(lbl is None for lbl in labels[1:])
