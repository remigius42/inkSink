# spellchecker:ignore fullscreen

import jinja2
import pytest

from inksink.core.layout import fill_content, fill_error


def test_fill_content_returns_complete_html():
    result = fill_content("<p>Hello</p>")
    assert result.strip().startswith("<!DOCTYPE html>") or result.strip().startswith(
        "<html"
    )
    assert "<p>Hello</p>" in result


def test_fill_content_has_no_chrome_reservation():
    result = fill_content("<p>content</p>")
    assert "button-chrome" not in result
    assert "status-chrome" not in result


def test_app_layout_independent_of_core(tmp_path):
    from inksink.core import layout as core_layout

    app_layouts = tmp_path / "layouts"
    app_layouts.mkdir()
    (app_layouts / "custom.html.j2").write_text("APP:{{ slot }}")

    app_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(app_layouts)),
        autoescape=False,  # nosec B701  # nosemgrep — testing that templates render without autoescape
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
    assert "status-chrome" not in result
    assert "button-chrome" not in result


def test_fill_error_escapes_html_in_message():
    result = fill_error("<script>alert('xss')</script>")
    assert "<script>" not in result
    assert "&lt;script&gt;" in result
