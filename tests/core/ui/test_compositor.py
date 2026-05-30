# spellchecker:ignore getpixel

"""Tests for Compositor timer lifecycle and button API."""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest

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
# set_content acquires lock (no race with _status_tick)
# ---------------------------------------------------------------------------


def test_set_content_holds_lock_during_framebuffer_update():
    """set_content must hold self._lock while mutating the framebuffer."""
    from unittest.mock import patch

    from PIL import Image

    display = _make_display()
    comp = Compositor(display, _settings())

    lock_acquired_during_redraw = []

    original_redraw = comp._redraw_chrome

    def spy_redraw():
        lock_acquired_during_redraw.append(comp._lock.locked())
        original_redraw()

    fake_img = Image.new("RGB", (480, 800), color=(255, 255, 255))

    with (
        patch("inksink.core.renderer.render", return_value=fake_img),
        patch.object(comp, "_redraw_chrome", spy_redraw),
    ):
        comp.set_content("<p>test</p>")

    assert any(lock_acquired_during_redraw), "lock must be held during _redraw_chrome"


def test_set_content_holds_lock_during_display_call():
    """display_full must be called while self._lock is held, not after release."""
    from unittest.mock import patch

    from PIL import Image

    display = _make_display()
    comp = Compositor(display, _settings())

    lock_held_during_display: list[bool] = []

    def spy_display_full(fb):
        lock_held_during_display.append(comp._lock.locked())

    display.display_full.side_effect = spy_display_full

    fake_img = Image.new("RGB", (480, 800), color=(255, 255, 255))
    with patch("inksink.core.renderer.render", return_value=fake_img):
        comp.set_content("<p>test</p>")

    assert lock_held_during_display, "display_full was never called"
    assert all(lock_held_during_display), "lock must be held during display_full"
