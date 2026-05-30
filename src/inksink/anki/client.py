"""AnkiWeb sync client wrapping anki.collection.Collection."""

from __future__ import annotations

from anki.collection import Collection
from anki.errors import SyncError, SyncErrorKind

from inksink.core.state import wifi_status

_COLLECTION_PATH = "/var/lib/inksink/collection.anki2"


class AuthError(Exception):
    """Raised when AnkiWeb credentials are missing or rejected."""


class AnkiWebClient:
    def __init__(self, settings: dict) -> None:
        """Initialize the AnkiWeb client from settings."""
        anki_cfg = settings["apps"]["anki"]
        username = anki_cfg.get("ankiweb_username", "")
        password = anki_cfg.get("ankiweb_password", "")
        if not username or not password:
            raise AuthError(
                "AnkiWeb credentials missing. "
                "Set apps.anki.ankiweb_username and apps.anki.ankiweb_password "
                "in /etc/inksink/config.yml."
            )
        self.col = Collection(_COLLECTION_PATH)
        try:
            self._auth = self.col.sync_login(username, password, None)
        except SyncError as exc:
            self.col.close()
            if exc.kind == SyncErrorKind.AUTH:
                raise AuthError(f"AnkiWeb login failed: {exc}") from exc
            raise
        except Exception:
            self.col.close()
            raise

    def sync_down(self) -> None:
        if wifi_status().connected:
            self.col.sync_collection(self._auth, sync_media=False)

    def sync_up(self) -> None:
        if wifi_status().connected:
            self.col.sync_collection(self._auth, sync_media=False)

    def close(self) -> None:
        self.col.close()
