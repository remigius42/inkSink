"""HTTP request handler and bound server for POST /render."""

from __future__ import annotations

import io
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import TYPE_CHECKING

from PIL import Image

from inksink.core.renderer import Orientation, render

if TYPE_CHECKING:
    from inksink.display_server._server import DisplayServer

_MAX_BODY_BYTES = 5 * 1024 * 1024  # 5 MiB
_VALID_MODES = ("1bit", "4gray")
_READ_TIMEOUT = 30  # seconds


class _ReadTimeout(Exception):
    pass


class _RequestHandler(BaseHTTPRequestHandler):
    """Handles POST /render for both HTTP and HTTPS servers."""

    def _server(self) -> "_BoundHTTPServer":
        """Return the bound server, typed correctly."""
        return self.server  # type: ignore[return-value]

    # `format` matches BaseHTTPRequestHandler.log_message's parameter name;
    # renaming would trigger a Pyright incompatible-override error since the
    # base class uses it as a positional-or-keyword parameter.
    def log_message(
        self,
        format: str,  # noqa: A002  # pylint: disable=redefined-builtin
        *args: object,
    ) -> None:
        import logging

        logging.debug("display_server: " + format, *args)

    def do_POST(self) -> None:  # noqa: N802
        """Dispatch POST requests; only /render is accepted."""
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/render":
            self._respond(404)
            return
        self._do_post_render(parsed)

    def _validate_render_auth(self) -> bool:
        """Check Bearer token when HTTPS + token are configured.

        Returns False and responds on failure.
        """
        if not (self._server().is_https and self._server().token):
            return True
        auth = self.headers.get("Authorization", "")
        if not auth:
            self._respond(401)
            return False
        if auth != f"Bearer {self._server().token}":
            self._respond(403)
            return False
        return True

    def _parse_content_length(self) -> int | None:
        """Parse and range-check Content-Length; respond on error."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            self._respond(400)
            return None
        if content_length <= 0:
            self._respond(411)
            return None
        if content_length > _MAX_BODY_BYTES:
            self._respond(413)
            return None
        return content_length

    def _validate_render_request(
        self, parsed: urllib.parse.ParseResult
    ) -> tuple[str, str, bytes] | None:
        """Validate mode, content-type, and body.

        Returns (mode, media_type, body) or None.
        """
        if not self._validate_render_auth():
            return None

        params = urllib.parse.parse_qs(parsed.query)
        mode = params.get("mode", ["1bit"])[0]
        if mode not in _VALID_MODES:
            self._respond(400)
            return None

        content_length = self._parse_content_length()
        if content_length is None:
            return None

        raw_ct = self.headers.get("Content-Type", "")
        media_type = raw_ct.split(";")[0].strip().lower()

        if media_type not in ("image/png", "text/html"):
            self._respond(415)
            return None

        try:
            body = self._read_body(content_length)
        except _ReadTimeout:
            self._respond(408)
            return None
        # Defensive: _read_body returns None only when buf exceeds _MAX_BODY_BYTES,
        # which can't happen given Content-Length is already bounded above.
        if body is None:  # pragma: no cover
            self._respond(413)
            return None
        if len(body) < content_length:
            self._respond(400)
            return None

        return mode, media_type, body

    def _do_post_render(self, parsed: urllib.parse.ParseResult) -> None:
        """Decode body, render if HTML, push to display slot."""
        validated = self._validate_render_request(parsed)
        if validated is None:
            return
        mode, media_type, body = validated

        if media_type == "image/png":
            try:
                img = Image.open(io.BytesIO(body))
                img.load()
            except Exception:  # noqa: BLE001
                self._respond(400)
                return
        else:
            html = body.decode("utf-8", errors="replace").strip()
            if not html:
                self._respond(400)
                return
            try:
                img = render(
                    html,
                    mode=mode,
                    orientation=Orientation(self._server().orientation),
                )
            except Exception:  # noqa: BLE001
                self._respond(500)
                return

        if not self._server().display_server.try_set(img, mode):
            self._respond(429)
            return

        self._respond(200)

    def _read_body(self, declared_length: int) -> bytes | None:
        """Read body; return None if oversized; raise _ReadTimeout on stall."""
        try:
            self.connection.settimeout(_READ_TIMEOUT)  # type: ignore[attr-defined]
        except AttributeError:
            pass  # not in a real server context (e.g. unit tests)
        buf = b""
        remaining = declared_length if declared_length > 0 else _MAX_BODY_BYTES
        while remaining > 0:
            chunk_size = min(remaining, 65536)
            try:
                chunk = self.rfile.read(chunk_size)
            except OSError as e:
                raise _ReadTimeout from e
            if not chunk:
                break
            buf += chunk
            remaining -= len(chunk)
            # Defensive: callers validate Content-Length ≤ _MAX_BODY_BYTES before
            # calling _read_body, so buf can never grow past the limit in practice.
            if len(buf) > _MAX_BODY_BYTES:  # pragma: no cover
                return None
        return buf

    def _respond(self, status: int) -> None:
        """Send a response with the given status code and no body."""
        self.send_response(status)
        self.end_headers()


class _BoundHTTPServer(HTTPServer):
    def __init__(
        self,
        address: tuple[str, int],
        handler: type,
        *,
        display_server: "DisplayServer",
        is_https: bool,
        token: str,
        orientation: str,
    ) -> None:
        super().__init__(address, handler)
        self.display_server = display_server
        self.is_https = is_https
        self.token = token
        self.orientation = orientation
