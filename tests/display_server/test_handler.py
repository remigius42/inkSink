"""Tests for _RequestHandler HTTP behavior."""

from __future__ import annotations

import email
import io
from typing import Optional
from unittest.mock import patch

from PIL import Image

from inksink.display_server._handler import (
    _MAX_BODY_BYTES,
    _BoundHTTPServer,
    _RequestHandler,
)
from inksink.display_server._server import DisplayServer

_TEST_TOKEN = "secret"  # noqa: S105  # nosec B105 — test fixture, not a real credential
_TEST_AUTH_HEADER = f"Bearer {_TEST_TOKEN}"  # noqa: S106  # nosec B106 — test fixture

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


def _make_server(
    *,
    is_https: bool = False,
    token: str = "",
    orientation: str = "portrait",
    ds: Optional[DisplayServer] = None,
) -> _BoundHTTPServer:
    if ds is None:
        ds = DisplayServer(_SETTINGS)
    return _BoundHTTPServer(
        ("127.0.0.1", 0),
        _RequestHandler,
        display_server=ds,
        is_https=is_https,
        token=token,
        orientation=orientation,
    )


def _png_bytes(width: int = 4, height: int = 4) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=(100, 100, 100)).save(buf, format="PNG")
    return buf.getvalue()


def _call_handler_raw(
    header_str: str,
    path: str = "/render",
    body: bytes = b"",
    rfile: io.BufferedIOBase | None = None,
) -> int:
    """Call handler with raw header string (no automatic Content-Length)."""
    captured: list[int] = []

    def fake_respond(self_h, status: int) -> None:
        captured.append(status)

    handler = _RequestHandler.__new__(_RequestHandler)
    handler.server = _make_server()  # type: ignore[assignment]
    handler.path = path
    handler.headers = email.message_from_string(header_str)
    handler.rfile = rfile if rfile is not None else io.BytesIO(body)

    with patch.object(_RequestHandler, "_respond", fake_respond):
        handler.do_POST()

    return captured[0] if captured else 0


def _call_handler(
    server: _BoundHTTPServer,
    body: bytes,
    content_type: str,
    path: str = "/render",
    extra_headers: dict[str, str] | None = None,
) -> int:
    """Instantiate a handler, feed it a POST request, return the status code."""
    captured: list[int] = []

    def fake_respond(self_h, status: int) -> None:
        captured.append(status)

    handler = _RequestHandler.__new__(_RequestHandler)
    handler.server = server  # type: ignore[assignment]
    handler.path = path

    header_str = f"Content-Type: {content_type}\r\nContent-Length: {len(body)}\r\n"
    if extra_headers:
        for k, v in extra_headers.items():
            header_str += f"{k}: {v}\r\n"
    handler.headers = email.message_from_string(header_str)
    handler.rfile = io.BytesIO(body)

    with patch.object(_RequestHandler, "_respond", fake_respond):
        handler.do_POST()

    return captured[0] if captured else 0


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------


def test_post_to_unknown_path_returns_404():
    assert (
        _call_handler(_make_server(), _png_bytes(), "image/png", path="/unknown") == 404
    )


def test_respond_sends_status_and_ends_headers():
    handler = _RequestHandler.__new__(_RequestHandler)
    handler.server = _make_server()  # type: ignore[assignment]
    with (
        patch.object(handler, "send_response") as mock_send,
        patch.object(handler, "end_headers") as mock_end,
    ):
        handler._respond(204)
    mock_send.assert_called_once_with(204)
    mock_end.assert_called_once_with()


def test_log_message_delegates_to_logging_debug():
    import logging

    handler = _RequestHandler.__new__(_RequestHandler)
    handler.server = _make_server()  # type: ignore[assignment]
    with patch.object(logging, "debug") as mock_debug:
        handler.log_message("hello %s", "world")
    mock_debug.assert_called_once_with("display_server: hello %s", "world")


# ---------------------------------------------------------------------------
# PNG
# ---------------------------------------------------------------------------


def test_valid_png_returns_200():
    ds = DisplayServer(_SETTINGS)
    assert _call_handler(_make_server(ds=ds), _png_bytes(), "image/png") == 200


def test_invalid_png_returns_400():
    assert _call_handler(_make_server(), b"not a png", "image/png") == 400


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------


def test_valid_html_returns_200():
    ds = DisplayServer(_SETTINGS)
    fake_img = Image.new("RGB", (480, 800))
    with patch("inksink.display_server._handler.render", return_value=fake_img):
        assert (
            _call_handler(
                _make_server(ds=ds), b"<html><body>hi</body></html>", "text/html"
            )
            == 200
        )


def test_empty_html_returns_400():
    assert _call_handler(_make_server(), b"   ", "text/html") == 400


def test_render_failure_returns_500():
    with patch(
        "inksink.display_server._handler.render", side_effect=RuntimeError("boom")
    ):
        assert _call_handler(_make_server(), b"<html>hi</html>", "text/html") == 500


# ---------------------------------------------------------------------------
# Content-Type
# ---------------------------------------------------------------------------


def test_unsupported_content_type_returns_415():
    assert _call_handler(_make_server(), b"{}", "application/json") == 415


def test_html_with_charset_param_returns_200():
    ds = DisplayServer(_SETTINGS)
    fake_img = Image.new("RGB", (480, 800))
    with patch("inksink.display_server._handler.render", return_value=fake_img):
        assert (
            _call_handler(
                _make_server(ds=ds),
                b"<html><body>hi</body></html>",
                "text/html; charset=utf-8",
            )
            == 200
        )


# ---------------------------------------------------------------------------
# Mode query parameter
# ---------------------------------------------------------------------------


def test_mode_4gray_stored_correctly():
    ds = DisplayServer(_SETTINGS)
    fake_img = Image.new("RGB", (480, 800))
    with patch("inksink.display_server._handler.render", return_value=fake_img):
        _call_handler(
            _make_server(ds=ds),
            b"<html><body>hi</body></html>",
            "text/html",
            path="/render?mode=4gray",
        )
    result = ds.take()
    assert result is not None
    assert result[1] == "4gray"


def test_default_mode_is_1bit():
    ds = DisplayServer(_SETTINGS)
    _call_handler(_make_server(ds=ds), _png_bytes(), "image/png")
    result = ds.take()
    assert result is not None
    assert result[1] == "1bit"


def test_invalid_mode_returns_400():
    assert (
        _call_handler(
            _make_server(), _png_bytes(), "image/png", path="/render?mode=color"
        )
        == 400
    )


# ---------------------------------------------------------------------------
# 429 / slot
# ---------------------------------------------------------------------------


def test_second_push_while_occupied_returns_429():
    ds = DisplayServer(_SETTINGS)
    srv = _make_server(ds=ds)
    _call_handler(srv, _png_bytes(), "image/png")
    assert _call_handler(srv, _png_bytes(), "image/png") == 429


def test_cleared_slot_accepts_new_push():
    ds = DisplayServer(_SETTINGS)
    srv = _make_server(ds=ds)
    _call_handler(srv, _png_bytes(), "image/png")
    ds.take()
    assert _call_handler(srv, _png_bytes(), "image/png") == 200


# ---------------------------------------------------------------------------
# HTTPS token
# ---------------------------------------------------------------------------


def test_https_correct_token_accepted():
    ds = DisplayServer(_SETTINGS)
    assert (
        _call_handler(
            _make_server(ds=ds, is_https=True, token=_TEST_TOKEN),
            _png_bytes(),
            "image/png",
            extra_headers={"Authorization": _TEST_AUTH_HEADER},
        )
        == 200
    )


def test_https_missing_token_returns_401():
    assert (
        _call_handler(
            _make_server(is_https=True, token=_TEST_TOKEN),
            _png_bytes(),
            "image/png",
        )
        == 401
    )


def test_https_wrong_token_returns_403():
    assert (
        _call_handler(
            _make_server(is_https=True, token=_TEST_TOKEN),
            _png_bytes(),
            "image/png",
            extra_headers={"Authorization": "Bearer wrong_token"},
        )
        == 403
    )


def test_http_ignores_token():
    ds = DisplayServer(_SETTINGS)
    assert (
        _call_handler(
            _make_server(ds=ds, is_https=False, token=_TEST_TOKEN),
            _png_bytes(),
            "image/png",
        )
        == 200
    )


# ---------------------------------------------------------------------------
# Read timeout
# ---------------------------------------------------------------------------


def test_stalled_client_returns_408():
    import socket
    from unittest.mock import MagicMock

    mock_rfile = MagicMock()
    mock_rfile.read.side_effect = socket.timeout
    assert (
        _call_handler_raw(
            "Content-Type: image/png\r\nContent-Length: 100\r\n",
            rfile=mock_rfile,
        )
        == 408
    )


# ---------------------------------------------------------------------------
# Truncated body
# ---------------------------------------------------------------------------


def test_truncated_html_body_returns_400():
    fake_img = Image.new("RGB", (480, 800))
    partial_html = b"<p>hello</p>"  # 12 bytes, but we declare 1000
    with patch("inksink.display_server._handler.render", return_value=fake_img):
        result = _call_handler_raw(
            "Content-Type: text/html\r\nContent-Length: 1000\r\n",
            body=partial_html,
        )
    assert result == 400


# ---------------------------------------------------------------------------
# 413 body size limit
# ---------------------------------------------------------------------------


def test_zero_content_length_returns_411():
    assert _call_handler(_make_server(), b"", "image/png") == 411


def test_missing_content_length_returns_411():
    assert _call_handler_raw("Content-Type: image/png\r\n") == 411


def test_non_numeric_content_length_returns_400():
    assert (
        _call_handler_raw("Content-Type: image/png\r\nContent-Length: abc\r\n") == 400
    )


def test_oversized_content_length_returns_413():
    assert (
        _call_handler_raw(
            f"Content-Type: image/png\r\nContent-Length: {_MAX_BODY_BYTES + 1}\r\n"
        )
        == 413
    )
