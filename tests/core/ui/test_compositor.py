# spellchecker:ignore getpixel

"""Tests for Compositor timer lifecycle and button API."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from inksink.core.ui import ButtonState
from inksink.core.ui.compositor import Compositor


def _make_display():
    d = MagicMock()
    d.display_partial = MagicMock()
    d.display_full = MagicMock()
    d.display_4gray = MagicMock()
    d._portrait_rotation = 90
    return d


def _settings(
    orientation="portrait", display_mode="1bit", double_v=False, refresh: float = 20
):
    return {
        "display": {
            "portrait_rotation": 90,
            "status_refresh_interval": refresh,
        },
        "apps": {
            "test_app": {
                "orientation": orientation,
                "display_mode": display_mode,
                "display": {"double_vertical_button_size": double_v},
            }
        },
        "_active_app": "test_app",
    }


# ---------------------------------------------------------------------------
# 5.1  start() arms the timer
# ---------------------------------------------------------------------------


def test_start_arms_timer():
    comp = Compositor(_make_display(), _settings())
    assert comp._timer is None
    comp.start()
    try:
        assert comp._timer is not None
    finally:
        comp.stop()


# ---------------------------------------------------------------------------
# 5.2  Timer callback calls display_partial
# ---------------------------------------------------------------------------


def test_timer_callback_calls_display_partial():
    display = _make_display()
    comp = Compositor(display, _settings())
    comp.start()
    # Manually invoke the callback instead of waiting
    comp._status_tick()
    assert display.display_partial.called
    comp.stop()


# ---------------------------------------------------------------------------
# 5.3  stop() cancels timer
# ---------------------------------------------------------------------------


def test_stop_cancels_timer():
    display = _make_display()
    comp = Compositor(display, _settings(refresh=0.05))
    comp.start()
    assert comp._timer is not None
    comp.stop()
    assert comp._timer is None
    count_before = display.display_partial.call_count
    time.sleep(0.15)  # would have fired if not cancelled
    assert display.display_partial.call_count == count_before


# ---------------------------------------------------------------------------
# 5.4  Timer does not fire before start()
# ---------------------------------------------------------------------------


def test_timer_does_not_fire_before_start():
    display = _make_display()
    _comp = Compositor(display, _settings())  # noqa: F841 — prevent GC during sleep
    time.sleep(0.05)
    assert display.display_partial.call_count == 0


# ---------------------------------------------------------------------------
# set_buttons — basic API
# ---------------------------------------------------------------------------


def test_set_buttons_wrong_length_raises():
    comp = Compositor(_make_display(), _settings())
    with pytest.raises(ValueError, match="8"):
        comp.set_buttons(["a"] * 7, [ButtonState.DEFAULT] * 7)


def test_set_buttons_calls_display_partial():
    display = _make_display()
    comp = Compositor(display, _settings())
    labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
    states = [ButtonState.DEFAULT] * 8
    comp.set_buttons(labels, states)
    assert display.display_partial.called


def test_set_button_state_calls_display_partial():
    display = _make_display()
    comp = Compositor(display, _settings())
    labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
    comp.set_buttons(labels, [ButtonState.DEFAULT] * 8)
    display.display_partial.reset_mock()
    comp.set_button_state(1, ButtonState.ACTIVE)
    assert display.display_partial.called


# ---------------------------------------------------------------------------
# Compositor framebuffer initialization
# ---------------------------------------------------------------------------


def test_compositor_initializes_white_framebuffer_portrait():
    comp = Compositor(_make_display(), _settings("portrait"))
    fb = comp._framebuffer
    assert fb.mode == "1"
    assert fb.size == (480, 800)


def test_compositor_initializes_white_framebuffer_landscape():
    comp = Compositor(_make_display(), _settings("landscape"))
    fb = comp._framebuffer
    assert fb.mode == "1"
    assert fb.size == (800, 480)


# ---------------------------------------------------------------------------
# Stale pixel clearing: replacing a labeled slot with None must leave white
# ---------------------------------------------------------------------------


def test_redraw_buttons_clears_stale_pixels():
    """Pixels from a removed button slot must be white after redraw."""
    comp = Compositor(_make_display(), _settings())
    labels_with = ["A", "B", "C", "D", "E", "F", "G", "H"]
    comp.set_buttons(labels_with, [ButtonState.DEFAULT] * 8)

    # Now remove all buttons — slot regions should be cleared to white
    labels_without = [None] * 8
    comp.set_buttons(labels_without, [ButtonState.DEFAULT] * 8)

    # Sample the top-left pixel of the first button slot in portrait layout.
    # Portrait: bar at bottom 80px of 480x800 fb, first slot at x=0, y=720.
    fb = comp._framebuffer
    px = fb.getpixel((1, 721))  # just inside top-left of first slot
    assert px == 1  # white (1-bit mode: 1=white)


# ---------------------------------------------------------------------------
# Scroll: scroll_down / scroll_up
# ---------------------------------------------------------------------------


def _make_tall_content(width: int = 480, height: int = 1600) -> Image.Image:
    return Image.new("RGB", (width, height), color=(200, 200, 200))


def test_scroll_down_returns_can_scroll_down_false_at_bottom():

    display = _make_display()
    comp = Compositor(display, _settings())
    img = _make_tall_content()
    comp.set_content(img)
    display.reset_mock()

    # Scroll all the way down
    can_up, can_down = False, True
    while can_down:
        can_up, can_down = comp.scroll_down()

    assert can_down is False
    assert can_up is True


def test_scroll_up_at_top_is_noop():
    display = _make_display()
    comp = Compositor(display, _settings())
    comp.set_content(_make_tall_content())
    display.reset_mock()

    can_up, can_down = comp.scroll_up()
    assert can_up is False
    assert can_down is True
    display.display_partial.assert_not_called()


def test_scroll_down_at_bottom_is_noop():
    from inksink.core.ui import STATUS_BAR_HEIGHT

    display = _make_display()
    comp = Compositor(display, _settings())
    # Without buttons, Content Zone = fb_height - STATUS_BAR_HEIGHT
    cz_h = comp._fb_height() - STATUS_BAR_HEIGHT
    img = _make_tall_content(480, cz_h)
    comp.set_content(img)
    display.reset_mock()

    can_up, can_down = comp.scroll_down()
    assert can_up is False
    assert can_down is False
    display.display_partial.assert_not_called()


def test_scroll_down_calls_display_partial():
    display = _make_display()
    comp = Compositor(display, _settings())
    comp.set_content(_make_tall_content())
    display.reset_mock()

    comp.scroll_down()
    display.display_partial.assert_called_once()


def test_scroll_down_increases_offset():
    display = _make_display()
    comp = Compositor(display, _settings())
    comp.set_content(_make_tall_content())
    before = comp._scroll_offset
    comp.scroll_down()
    assert comp._scroll_offset > before


def test_scroll_offset_clamped_at_max():
    display = _make_display()
    comp = Compositor(display, _settings())
    tall = _make_tall_content(480, 2000)
    comp.set_content(tall)
    comp._scroll_offset = 10000  # force beyond max
    can_up, can_down = comp.scroll_down()
    cz_h = comp._content_zone_height()
    assert comp._scroll_offset == tall.height - cz_h
    assert can_up is True
    assert can_down is False


def test_scroll_step_default_is_50():
    comp = Compositor(_make_display(), _settings())
    assert comp._scroll_step == 50


def test_scroll_step_per_app_override():
    s = _settings()
    s["apps"]["test_app"]["display"]["vertical_scroll_step"] = 120
    comp = Compositor(_make_display(), s)
    assert comp._scroll_step == 120


def test_scroll_step_falls_back_to_global():
    s = _settings()
    s["display"]["vertical_scroll_step"] = 75
    comp = Compositor(_make_display(), s)
    assert comp._scroll_step == 75


# ---------------------------------------------------------------------------
# set_status_bar_visible
# ---------------------------------------------------------------------------


def test_set_status_bar_visible_does_not_trigger_display():
    """set_status_bar_visible only updates state; set_content triggers the refresh."""
    display = _make_display()
    comp = Compositor(display, _settings())
    display.reset_mock()
    comp.set_status_bar_visible(False)
    display.display_full.assert_not_called()
    display.display_partial.assert_not_called()
    display.display_4gray.assert_not_called()


def test_content_zone_equals_screen_height_when_no_chrome():
    comp = Compositor(_make_display(), _settings())
    comp.set_status_bar_visible(False)
    assert comp._content_zone_height() == comp._fb_height()


def test_content_pasted_at_y0_when_status_bar_hidden():
    """With status bar hidden, content starts at the very top of the framebuffer."""
    comp = Compositor(_make_display(), _settings())
    comp.set_status_bar_visible(False)
    # All-black image — any pixel at (0, 0) should be black after set_content
    img = Image.new("1", (480, 800), color=0)
    comp.set_content(img)
    assert comp._framebuffer.getpixel((0, 0)) == 0  # black = content at top


def test_status_bar_not_drawn_over_content_when_hidden():
    """When hidden, chrome must not overwrite content in the status bar region."""
    comp = Compositor(_make_display(), _settings())
    comp.set_status_bar_visible(False)
    # White content — if _redraw_chrome still draws status bar text (fill=0),
    # pixel turns black.
    img = Image.new("RGB", (480, 800), color=(255, 255, 255))
    comp.set_content(img)
    # PIL default font renders time-string black pixels at y=4; white content
    # must not be overwritten.
    assert comp._framebuffer.getpixel((6, 4)) != 0


def test_status_bar_row_is_not_overwritten_when_visible():
    """Status bar region must remain white (chrome) when status bar is visible."""
    from inksink.core.ui import STATUS_BAR_HEIGHT

    comp = Compositor(_make_display(), _settings())
    # Status bar visible by default; black image must not blacken row 0.
    img = Image.new("1", (480, 800), color=0)
    comp.set_content(img)
    # Row 0 is in the status bar — white (chrome), not content.
    assert comp._framebuffer.getpixel((0, 0)) == 1  # white = status bar chrome
    # Row STATUS_BAR_HEIGHT is in content zone — should be black
    assert comp._framebuffer.getpixel((0, STATUS_BAR_HEIGHT)) == 0


# ---------------------------------------------------------------------------
# set_content acquires lock (no race with _status_tick)
# ---------------------------------------------------------------------------


def test_set_content_accepts_pil_image_and_calls_display_full():

    display = _make_display()
    comp = Compositor(display, _settings())
    img = Image.new("RGB", (480, 800), color=(255, 255, 255))
    comp.set_content(img)
    assert display.display_full.called


def test_set_content_holds_lock_during_framebuffer_update():
    """set_content must hold self._lock while mutating the framebuffer."""
    display = _make_display()
    comp = Compositor(display, _settings())

    lock_acquired_during_redraw = []
    original_redraw = comp._redraw_chrome

    def spy_redraw():
        lock_acquired_during_redraw.append(comp._lock.locked())
        original_redraw()

    fake_img = Image.new("RGB", (480, 800), color=(255, 255, 255))
    with patch.object(comp, "_redraw_chrome", spy_redraw):
        comp.set_content(fake_img)

    assert any(lock_acquired_during_redraw), "lock must be held during _redraw_chrome"


def test_set_content_holds_lock_during_display_call():
    """display_full must be called while self._lock is held, not after release."""
    display = _make_display()
    comp = Compositor(display, _settings())

    lock_held_during_display: list[bool] = []

    def spy_display_full(fb):
        lock_held_during_display.append(comp._lock.locked())

    display.display_full.side_effect = spy_display_full

    fake_img = Image.new("RGB", (480, 800), color=(255, 255, 255))
    comp.set_content(fake_img)

    assert lock_held_during_display, "display_full was never called"
    assert all(lock_held_during_display), "lock must be held during display_full"


def test_set_content_4gray_calls_display_4gray():

    display = _make_display()
    comp = Compositor(display, _settings(display_mode="4gray"))
    img = Image.new("RGB", (480, 800), color=(128, 128, 128))
    comp.set_content(img)
    assert display.display_4gray.called
    assert not display.display_full.called


def test_set_content_resets_scroll_offset_to_zero():

    display = _make_display()
    comp = Compositor(display, _settings())
    comp._scroll_offset = 100
    img = Image.new("RGB", (480, 800), color=(255, 255, 255))
    comp.set_content(img)
    assert comp._scroll_offset == 0


def test_set_content_retains_full_content_image():

    display = _make_display()
    comp = Compositor(display, _settings())
    img = Image.new("RGB", (480, 1600), color=(255, 255, 255))
    comp.set_content(img)
    assert comp._content_image is not None
    assert comp._content_image.size == (480, 1600)
