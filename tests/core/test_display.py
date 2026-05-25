# spellchecker:ignore reinit

import sys
import threading
from unittest.mock import MagicMock

import pytest

# Stub waveshare_epd before importing display
_epd_stub = MagicMock()
_epd_stub.epd7in5_V2.EPD.side_effect = lambda: MagicMock()
sys.modules.setdefault("waveshare_epd", _epd_stub)
sys.modules.setdefault("waveshare_epd.epd7in5_V2", _epd_stub.epd7in5_V2)

from inksink.core.display import Display  # noqa: E402


def _make_display(**kwargs) -> Display:
    return Display(**kwargs)


def test_display_raises_on_zero_idle_timeout():
    with pytest.raises(ValueError, match="idle_timeout"):
        Display(idle_timeout=0)


def test_display_raises_on_negative_idle_timeout():
    with pytest.raises(ValueError, match="idle_timeout"):
        Display(idle_timeout=-1)


def test_display_raises_on_zero_full_refresh_interval():
    with pytest.raises(ValueError, match="full_refresh_interval"):
        Display(full_refresh_interval=0)


def test_display_partial_raises_before_init():
    d = _make_display()
    with pytest.raises(RuntimeError):
        d.display_partial(MagicMock())


def test_display_full_raises_before_init():
    d = _make_display()
    with pytest.raises(RuntimeError):
        d.display_full(MagicMock())


def test_display_4gray_raises_before_init():
    d = _make_display()
    with pytest.raises(RuntimeError):
        d.display_4gray(MagicMock())


def test_partial_counter_increments():
    d = _make_display(idle_timeout=9999, full_refresh_interval=5)
    d.init()
    d.display_partial(MagicMock())
    d.display_partial(MagicMock())
    assert d._partial_count == 2


def test_display_4gray_does_not_affect_partial_count():
    d = _make_display(idle_timeout=9999, full_refresh_interval=5)
    d.init()
    d.display_partial(MagicMock())
    d.display_partial(MagicMock())
    count_before = d._partial_count
    d.display_4gray(MagicMock())
    assert d._partial_count == count_before


def test_auto_full_refresh_at_threshold():
    d = _make_display(idle_timeout=9999, full_refresh_interval=3)
    d.init()
    img = MagicMock()
    d.display_partial(img)
    d.display_partial(img)
    d.display_partial(img)  # 3rd call triggers full refresh
    assert d._partial_count == 0
    d._epd.display.assert_called()  # full refresh path


def test_init_arms_idle_timer(mocker):
    mocker.patch("inksink.core.display.threading.Timer", autospec=True)
    d = _make_display(idle_timeout=9999)
    d.init()
    assert d._timer is not None


def test_timer_fires_sleep(mocker):
    mocker.patch("inksink.core.display.threading.Timer", autospec=True)
    d = _make_display(idle_timeout=1)
    d.init()
    d.display_partial(MagicMock())
    # Timer was created; manually invoke its callback
    timer_instance = d._timer
    assert timer_instance is not None
    d._on_idle()
    assert d._sleeping is True


def test_reinit_after_sleep():
    d = _make_display(idle_timeout=9999)
    d.init()
    d.sleep()
    assert d._sleeping is True
    d.init()
    img = MagicMock()
    d.display_partial(img)  # should not raise
    assert d._sleeping is False


def test_display_partial_transparent_wake_after_idle_sleep():
    """display_partial after idle sleep must transparently re-init, not raise."""
    d = _make_display(idle_timeout=9999)
    d.init()
    d.sleep()  # simulates idle timer firing
    assert d._sleeping is True
    d.display_partial(MagicMock())  # must NOT raise RuntimeError
    assert d._sleeping is False


def test_display_full_transparent_wake_after_idle_sleep():
    d = _make_display(idle_timeout=9999)
    d.init()
    d.sleep()
    d.display_full(MagicMock())
    assert d._sleeping is False


def test_display_4gray_transparent_wake_after_idle_sleep():
    d = _make_display(idle_timeout=9999)
    d.init()
    d.sleep()
    d.display_4gray(MagicMock())
    assert d._sleeping is False


def test_init_blocks_while_lock_is_held():
    """init() must acquire self._lock — concurrent sleep() cannot interleave."""
    d = _make_display(idle_timeout=9999)
    init_completed = threading.Event()
    thread_started = threading.Event()

    def do_init():
        thread_started.set()
        d.init()
        init_completed.set()

    with d._lock:
        t = threading.Thread(target=do_init)
        t.start()
        assert thread_started.wait(timeout=1.0), "worker thread never started"
        assert (
            not init_completed.is_set()
        ), "init() ran while lock was held — not thread-safe"

    t.join(timeout=1.0)
    assert init_completed.is_set()
