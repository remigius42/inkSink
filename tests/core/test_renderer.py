# spellchecker:ignore autouse getpixel tobytes putpixel

import io
import subprocess  # noqa: S404  # nosec B404 — imported to mock subprocess.run in tests, not for live execution
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image


def _make_png_bytes(width: int = 800, height: int = 480) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=(255, 255, 255)).save(buf, format="PNG")
    return buf.getvalue()


def _stub_wkhtmltoimage(png_bytes: bytes):
    """Return a side_effect for subprocess.run writing png_bytes to the output path."""

    def _run(cmd, **_):
        out_path = cmd[-1]  # last arg is the output PNG path
        Path(out_path).write_bytes(png_bytes)
        return MagicMock(returncode=0)

    return _run


@pytest.fixture(autouse=True)
def clear_renderer_cache():
    from inksink.core import renderer

    renderer.configure(max_size=100)
    yield
    renderer.configure(max_size=100)


@pytest.fixture(autouse=True)
def wkhtmltoimage_on_path():
    with patch(
        "inksink.core.renderer.shutil.which", return_value="/usr/bin/wkhtmltoimage"
    ):
        yield


def test_render_1bit_landscape_returns_800x480_mode_1():
    from inksink.core.renderer import Orientation, render

    with patch(
        "subprocess.run",
        side_effect=_stub_wkhtmltoimage(_make_png_bytes(800, 480)),
    ):
        img = render("<p>hello</p>", mode="1bit", orientation=Orientation.LANDSCAPE)
    assert img.size == (800, 480)
    assert img.mode == "1"


def test_render_1bit_portrait_returns_480x800_mode_1():
    from inksink.core.renderer import Orientation, render

    with patch(
        "subprocess.run",
        side_effect=_stub_wkhtmltoimage(_make_png_bytes(480, 800)),
    ):
        img = render("<p>hello</p>", mode="1bit", orientation=Orientation.PORTRAIT)
    assert img.size == (480, 800)
    assert img.mode == "1"


def test_render_default_orientation_is_portrait():
    from inksink.core.renderer import render

    with patch(
        "subprocess.run",
        side_effect=_stub_wkhtmltoimage(_make_png_bytes(480, 800)),
    ):
        img = render("<p>hello</p>", mode="1bit")
    assert img.size == (480, 800)


def test_render_html_with_curly_braces():
    from inksink.core.renderer import Orientation, render

    with patch(
        "subprocess.run",
        side_effect=_stub_wkhtmltoimage(_make_png_bytes(480, 800)),
    ):
        img = render(
            "<style>.x{color:red;}</style>",
            mode="1bit",
            orientation=Orientation.PORTRAIT,
        )
    assert img.size == (480, 800)
    assert img.mode == "1"


def _make_png_bytes_all_gray_bands(width: int = 800, height: int = 480) -> bytes:
    """PNG with pixels in all four quantization bands (0, 85, 170, 255)."""
    buf = io.BytesIO()
    img = Image.new("L", (width, height))
    pixels = img.load()
    assert pixels is not None
    band_height = height // 4
    for y in range(height):
        band = min(y // band_height, 3)
        gray = [20, 90, 170, 240][band]
        for x in range(width):
            pixels[x, y] = gray
    img.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


def test_render_4gray_landscape_returns_800x480_mode_l_with_four_values():
    from inksink.core.renderer import Orientation, render

    with patch(
        "subprocess.run",
        side_effect=_stub_wkhtmltoimage(_make_png_bytes_all_gray_bands()),
    ):
        img = render("<p>hello</p>", mode="4gray", orientation=Orientation.LANDSCAPE)
    assert img.size == (800, 480)
    assert img.mode == "L"
    assert set(img.tobytes()) == {0, 85, 170, 255}


def test_render_4gray_portrait_returns_480x800_mode_l_with_four_values():
    from inksink.core.renderer import Orientation, render

    with patch(
        "subprocess.run",
        side_effect=_stub_wkhtmltoimage(_make_png_bytes_all_gray_bands(480, 800)),
    ):
        img = render("<p>hello</p>", mode="4gray", orientation=Orientation.PORTRAIT)
    assert img.size == (480, 800)
    assert img.mode == "L"
    assert set(img.tobytes()) == {0, 85, 170, 255}


def test_render_different_orientations_bypass_cache():
    from inksink.core.renderer import Orientation, render

    stub = MagicMock(
        side_effect=lambda cmd, **_: (
            Path(cmd[-1]).write_bytes(_make_png_bytes(480, 800))
            or MagicMock(returncode=0)
            if "--width" in cmd and cmd[cmd.index("--width") + 1] == "480"
            else Path(cmd[-1]).write_bytes(_make_png_bytes(800, 480))
            or MagicMock(returncode=0)
        )
    )
    with patch("subprocess.run", stub):
        img_p = render("<p>hi</p>", mode="1bit", orientation=Orientation.PORTRAIT)
        img_l = render("<p>hi</p>", mode="1bit", orientation=Orientation.LANDSCAPE)
    assert stub.call_count == 2
    assert img_p.size == (480, 800)
    assert img_l.size == (800, 480)


def test_render_subprocess_restricts_local_file_access():
    import tempfile

    from inksink.core.renderer import render

    stub = MagicMock(side_effect=_stub_wkhtmltoimage(_make_png_bytes()))
    with patch("subprocess.run", stub):
        render("<p>hi</p>", mode="1bit")
    args = stub.call_args[0][0]
    tmp = tempfile.gettempdir()
    assert "--enable-local-file-access" in args
    allow_idx = args.index("--allow")
    assert args[allow_idx + 1] == tmp


def test_render_raises_on_invalid_mode():
    from inksink.core.renderer import render

    with patch("subprocess.run") as stub:
        with pytest.raises(ValueError, match="mode"):
            render("<p>hi</p>", mode="bad")
    stub.assert_not_called()


def test_cache_hit_skips_subprocess():
    from inksink.core.renderer import render

    stub = MagicMock(side_effect=_stub_wkhtmltoimage(_make_png_bytes()))
    with patch("subprocess.run", stub):
        render("<p>hi</p>", mode="1bit")
        render("<p>hi</p>", mode="1bit")
    assert stub.call_count == 1


def test_cache_returns_independent_copies():
    from inksink.core.renderer import render

    stub = MagicMock(side_effect=_stub_wkhtmltoimage(_make_png_bytes()))
    with patch("subprocess.run", stub):
        img1 = render("<p>hi</p>", mode="1bit")
        img2 = render("<p>hi</p>", mode="1bit")
    assert img1 is not img2  # separate objects, not the same cached reference


def test_mutating_returned_image_does_not_corrupt_cache():
    from inksink.core.renderer import render

    stub = MagicMock(side_effect=_stub_wkhtmltoimage(_make_png_bytes()))
    with patch("subprocess.run", stub):
        img1 = render("<p>hi</p>", mode="1bit")
    original_pixel = img1.getpixel((0, 0))
    img1.putpixel((0, 0), 0 if original_pixel else 255)  # flip the pixel

    # Second call must return a fresh copy with the original pixel value
    with patch("subprocess.run", stub):
        img2 = render("<p>hi</p>", mode="1bit")
    assert img2.getpixel((0, 0)) == original_pixel


def test_different_mode_bypasses_cache():
    from inksink.core.renderer import render

    stub = MagicMock(side_effect=_stub_wkhtmltoimage(_make_png_bytes()))
    with patch("subprocess.run", stub):
        render("<p>hi</p>", mode="1bit")
        render("<p>hi</p>", mode="4gray")
    assert stub.call_count == 2


def test_no_tmp_files_left_after_success(tmp_path):
    from inksink.core.renderer import render

    before = set(tmp_path.glob("*.html")) | set(tmp_path.glob("*.png"))
    with patch("inksink.core.renderer.tempfile.gettempdir", return_value=str(tmp_path)):
        with patch(
            "subprocess.run", side_effect=_stub_wkhtmltoimage(_make_png_bytes())
        ):
            render("<p>clean</p>", mode="1bit")
    after = set(tmp_path.glob("*.html")) | set(tmp_path.glob("*.png"))
    assert after == before


def test_no_tmp_files_left_after_failure(tmp_path):
    from inksink.core.renderer import render

    before = set(tmp_path.glob("*.html")) | set(tmp_path.glob("*.png"))
    err = subprocess.CalledProcessError(1, "wkhtmltoimage")
    with patch("inksink.core.renderer.tempfile.gettempdir", return_value=str(tmp_path)):
        with patch("subprocess.run", side_effect=err):
            with pytest.raises(subprocess.CalledProcessError):
                render("<p>boom</p>", mode="1bit")
    after = set(tmp_path.glob("*.html")) | set(tmp_path.glob("*.png"))
    assert after == before


def test_render_raises_when_wkhtmltoimage_missing():
    from inksink.core.renderer import render

    with patch("inksink.core.renderer.shutil.which", return_value=None):
        with pytest.raises(RuntimeError, match="wkhtmltoimage"):
            render("<p>hi</p>", mode="1bit")


def test_lru_evicts_oldest_entry_when_full():
    from inksink.core import renderer

    renderer.configure(max_size=2)
    stub = MagicMock(side_effect=_stub_wkhtmltoimage(_make_png_bytes()))
    with patch("subprocess.run", stub):
        renderer.render("<p>a</p>", mode="1bit")
        renderer.render("<p>b</p>", mode="1bit")
        renderer.render("<p>c</p>", mode="1bit")  # evicts <p>a</p>

    # <p>a</p> must have been evicted — a 4th subprocess call is needed to re-render it
    with patch("subprocess.run", stub):
        renderer.render("<p>a</p>", mode="1bit")
    assert stub.call_count == 4


def test_lru_access_promotes_entry_past_eviction():
    from inksink.core import renderer

    renderer.configure(max_size=2)
    stub = MagicMock(side_effect=_stub_wkhtmltoimage(_make_png_bytes()))
    with patch("subprocess.run", stub):
        renderer.render("<p>a</p>", mode="1bit")  # oldest
        renderer.render("<p>b</p>", mode="1bit")
        renderer.render("<p>a</p>", mode="1bit")  # re-access promotes <p>a</p>
        renderer.render("<p>c</p>", mode="1bit")  # evicts <p>b</p>, not <p>a</p>

    # <p>b</p> was evicted; <p>a</p> was not
    assert stub.call_count == 3  # a, b, c (second a was a cache hit)
    with patch("subprocess.run", stub):
        renderer.render("<p>b</p>", mode="1bit")  # must re-render
    assert stub.call_count == 4


def test_configure_from_settings_applies_cache_max_size():
    from inksink.core import renderer

    renderer.configure_from_settings({"renderer": {"cache_max_size": 2}})
    stub = MagicMock(side_effect=_stub_wkhtmltoimage(_make_png_bytes()))
    with patch("subprocess.run", stub):
        renderer.render("<p>a</p>", mode="1bit")
        renderer.render("<p>b</p>", mode="1bit")
        renderer.render("<p>c</p>", mode="1bit")  # evicts <p>a</p>

    with patch("subprocess.run", stub):
        renderer.render("<p>a</p>", mode="1bit")  # must re-render
    assert stub.call_count == 4


def test_configure_replaces_cache_and_enforces_new_limit():
    from inksink.core import renderer

    stub = MagicMock(side_effect=_stub_wkhtmltoimage(_make_png_bytes()))
    with patch("subprocess.run", stub):
        renderer.render("<p>x</p>", mode="1bit")  # populate cache

    renderer.configure(max_size=1)  # clears and re-sizes

    # previous entry gone — must re-render
    with patch("subprocess.run", stub):
        renderer.render("<p>x</p>", mode="1bit")
    assert stub.call_count == 2
