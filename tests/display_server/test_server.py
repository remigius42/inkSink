"""Tests for DisplayServer pending slot (try_set / take) and lifecycle."""

from __future__ import annotations

import threading
from unittest import mock

from PIL import Image

from inksink.display_server._server import DisplayServer

_SETTINGS = {
    "apps": {
        "display_server": {
            "enabled": False,
            "http_port": 0,
            "https_port": 0,
            "token": "",
            "orientation": "portrait",
        }
    }
}


def _img() -> Image.Image:
    return Image.new("RGB", (4, 4))


def test_take_returns_none_when_empty():
    ds = DisplayServer(_SETTINGS)
    assert ds.take() is None


def test_try_set_returns_true_when_slot_empty():
    ds = DisplayServer(_SETTINGS)
    assert ds.try_set(_img(), "1bit") is True


def test_try_set_stores_image_and_mode():
    ds = DisplayServer(_SETTINGS)
    img = _img()
    ds.try_set(img, "4gray")
    result = ds.take()
    assert result is not None
    assert result[0] is img
    assert result[1] == "4gray"


def test_try_set_returns_false_when_slot_occupied():
    ds = DisplayServer(_SETTINGS)
    ds.try_set(_img(), "1bit")
    assert ds.try_set(_img(), "1bit") is False


def test_take_clears_slot():
    ds = DisplayServer(_SETTINGS)
    ds.try_set(_img(), "1bit")
    ds.take()
    assert ds.take() is None


def test_try_set_sets_notify_event():
    event = threading.Event()
    ds = DisplayServer(_SETTINGS, notify_event=event)
    ds.try_set(_img(), "1bit")
    assert event.is_set()


def test_try_set_does_not_set_notify_event_when_slot_occupied():
    event = threading.Event()
    ds = DisplayServer(_SETTINGS, notify_event=event)
    ds.try_set(_img(), "1bit")
    event.clear()
    ds.try_set(_img(), "1bit")  # slot occupied → returns False
    assert not event.is_set()


def test_start_http_only_when_certs_absent():
    """When cert files are absent, only the HTTP listener starts; no HTTPS."""
    ds = DisplayServer(_SETTINGS)
    with mock.patch("inksink.display_server._server.ssl.SSLContext") as mock_ctx_cls:
        mock_ctx_cls.return_value.load_cert_chain.side_effect = FileNotFoundError
        ds.start()
    try:
        assert len(ds._servers) == 1
    finally:
        ds.stop()
