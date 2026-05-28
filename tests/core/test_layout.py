# spellchecker:ignore fullscreen

from datetime import datetime
from unittest.mock import patch

import jinja2
import pytest

from inksink.core.layout import fill_error


def test_fill_fullscreen_returns_complete_html():
    from inksink.core.layout import fill_fullscreen

    result = fill_fullscreen("<p>Hello</p>")
    assert result.strip().startswith("<!DOCTYPE html>") or result.strip().startswith(
        "<html"
    )
    assert "<p>Hello</p>" in result


def test_fill_fullscreen_no_button_bar():
    from inksink.core.layout import fill_fullscreen

    result = fill_fullscreen("<p>content</p>")
    assert "btn_" not in result
    assert "button-bar" not in result


def test_fill_default_injects_content_and_buttons():
    from inksink.core.layout import fill_default

    with (
        patch("inksink.core.layout.wifi_status") as mock_wifi,
        patch("inksink.core.layout.battery_percent", return_value=80),
    ):
        mock_wifi.return_value = type(
            "W", (), {"connected": True, "ssid": "Home", "strength": 70}
        )()
        result = fill_default(
            "<p>Card</p>", ["Menu", "Show Answer", "", "", "", "", "", ""]
        )
    assert "<p>Card</p>" in result
    assert "Menu" in result
    assert "Show Answer" in result


def test_fill_default_wrong_button_count_raises():
    from inksink.core.layout import fill_default

    with pytest.raises(ValueError, match="8"):
        fill_default("<p>x</p>", ["only", "six", "buttons", "here", "a", "b", "c"])


def test_fill_default_status_bar_auto_populated():
    from inksink.core.layout import fill_default

    with (
        patch("inksink.core.layout.wifi_status") as mock_wifi,
        patch("inksink.core.layout.battery_percent", return_value=55),
    ):
        mock_wifi.return_value = type(
            "W", (), {"connected": True, "ssid": "TestNet", "strength": 60}
        )()
        result = fill_default("<p>x</p>", [""] * 8)
    assert "55" in result
    assert "TestNet" in result


def test_fill_default_status_bar_includes_time():
    from inksink.core.layout import fill_default

    fixed = datetime(2026, 5, 27, 14, 30)
    with (
        patch("inksink.core.layout.datetime") as mock_dt,
        patch("inksink.core.layout.wifi_status") as mock_wifi,
        patch("inksink.core.layout.battery_percent", return_value=80),
    ):
        mock_dt.now.return_value = fixed
        mock_wifi.return_value = type(
            "W", (), {"connected": True, "ssid": "X", "strength": 60}
        )()
        result = fill_default("<p>x</p>", [""] * 8)
    assert "14:30" in result


def test_app_layout_independent_of_core(tmp_path):
    from inksink.core import layout as core_layout

    app_layouts = tmp_path / "layouts"
    app_layouts.mkdir()
    (app_layouts / "custom.html.j2").write_text("APP:{{ slot }}")

    app_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(app_layouts)),
        autoescape=False,
    )
    app_result = app_env.get_template("custom.html.j2").render(slot="hello")

    assert app_result == "APP:hello"
    with pytest.raises(jinja2.TemplateNotFound):
        core_layout._ENV.get_template("custom.html.j2")


def test_fill_error_returns_html_with_message():
    result = fill_error("disk full")
    assert "disk full" in result
    assert "Press any button to continue" in result


def test_fill_error_no_status_bar():
    result = fill_error("oops")
    assert "status-bar" not in result
    assert "button-bar" not in result


def test_fill_error_escapes_html_in_message():
    result = fill_error("<script>alert('xss')</script>")
    assert "<script>" not in result
    assert "&lt;script&gt;" in result
