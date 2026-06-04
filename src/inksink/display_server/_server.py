"""DisplayServer: pending-slot and HTTP/HTTPS listener lifecycle."""

from __future__ import annotations

import ssl
import threading
from http.server import HTTPServer
from typing import Optional

from PIL import Image

from inksink.display_server._handler import _BoundHTTPServer, _RequestHandler


class DisplayServer:
    """Thread-safe single-slot image queue between HTTP handler and main loop."""

    def __init__(
        self,
        settings: dict,
        notify_event: Optional[threading.Event] = None,
    ) -> None:
        """Read display_server config and initialise the pending slot."""
        ds_cfg = settings["apps"]["display_server"]
        self._http_port: int = ds_cfg["http_port"]
        self._https_port: int = ds_cfg["https_port"]
        self._token: str = ds_cfg["token"]
        self._orientation: str = ds_cfg["orientation"]
        self._lock = threading.Lock()
        self._pending: Optional[tuple[Image.Image, str]] = None
        self._servers: list[HTTPServer] = []
        self._notify_event = notify_event

    def try_set(self, image: Image.Image, mode: str) -> bool:
        """Store image+mode in the slot. Returns False (429) if slot occupied."""
        with self._lock:
            if self._pending is not None:
                return False
            self._pending = (image, mode)
        if self._notify_event is not None:
            self._notify_event.set()
        return True

    def take(self) -> Optional[tuple[Image.Image, str]]:
        """Consume and return the pending slot, or None if empty."""
        with self._lock:
            result = self._pending
            self._pending = None
            return result

    def start(self) -> None:
        """Start HTTP (and HTTPS if cert exists) listeners on daemon threads."""
        http_server = _BoundHTTPServer(
            ("", self._http_port),
            _RequestHandler,
            display_server=self,
            is_https=False,
            token=self._token,
            orientation=self._orientation,
        )
        self._servers.append(http_server)
        threading.Thread(target=http_server.serve_forever, daemon=True).start()

        cert = "/etc/inksink/display_server/cert.pem"
        key = "/etc/inksink/display_server/key.pem"
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(cert, key)
        except (FileNotFoundError, ssl.SSLError):
            import logging

            logging.warning("display_server: HTTPS cert/key not found, skipping HTTPS")
            return

        https_server = _BoundHTTPServer(
            ("", self._https_port),
            _RequestHandler,
            display_server=self,
            is_https=True,
            token=self._token,
            orientation=self._orientation,
        )
        https_server.socket = ctx.wrap_socket(https_server.socket, server_side=True)
        self._servers.append(https_server)
        threading.Thread(target=https_server.serve_forever, daemon=True).start()

    def stop(self) -> None:
        """Shut down all running listeners."""
        for s in self._servers:
            s.shutdown()
        self._servers.clear()
