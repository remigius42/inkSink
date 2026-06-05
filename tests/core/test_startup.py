import io
from unittest.mock import MagicMock, patch

from PIL import Image


def _make_png_bytes(width: int = 800, height: int = 480) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=(255, 255, 255)).save(buf, format="PNG")
    return buf.getvalue()


def _stub_wkhtmltoimage(png_bytes: bytes):
    from pathlib import Path

    def _run(cmd, **_):
        Path(cmd[-1]).write_bytes(png_bytes)
        return MagicMock(returncode=0)

    return _run


def test_startup_returns_compositor_when_display_provided():
    from inksink.core import startup

    display = MagicMock()
    mock_compositor = MagicMock()
    with (
        patch("inksink.core.startup.renderer.configure_from_settings"),
        patch(
            "inksink.core.ui.compositor.Compositor", return_value=mock_compositor
        ) as compositor_cls,
    ):
        result = startup.startup({}, display=display, active_app="weather")

    compositor_cls.assert_called_once_with(display, {"_active_app": "weather"})
    assert result is mock_compositor


def test_startup_returns_none_without_display():
    from inksink.core import startup

    with patch("inksink.core.startup.renderer.configure_from_settings"):
        assert startup.startup({}) is None


def test_startup_configures_renderer_cache_from_settings():
    from inksink.core import renderer, startup

    renderer.configure(max_size=100)  # reset to known state
    startup.startup({"renderer": {"cache_max_size": 1}})

    stub = MagicMock(side_effect=_stub_wkhtmltoimage(_make_png_bytes()))
    with (
        patch("subprocess.run", stub),
        patch(
            "inksink.core.renderer.shutil.which", return_value="/usr/bin/wkhtmltoimage"
        ),
    ):
        renderer.render("<p>a</p>", mode="1bit")
        renderer.render("<p>b</p>", mode="1bit")  # evicts <p>a</p>

    with (
        patch("subprocess.run", stub),
        patch(
            "inksink.core.renderer.shutil.which", return_value="/usr/bin/wkhtmltoimage"
        ),
    ):
        renderer.render("<p>a</p>", mode="1bit")  # must re-render — was evicted
    assert stub.call_count == 3
