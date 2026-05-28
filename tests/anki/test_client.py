"""Tests for AnkiWebClient behaviors."""

from unittest.mock import MagicMock, patch

import pytest
from anki.errors import SyncError, SyncErrorKind

from inksink.anki.client import AnkiWebClient, AuthError


def _settings(username="user@example.com", password="secret"):
    return {
        "apps": {
            "anki": {
                "ankiweb_username": username,
                "ankiweb_password": password,
            }
        }
    }


def _make_client(settings=None):
    if settings is None:
        settings = _settings()
    mock_col = MagicMock()
    with patch("inksink.anki.client.Collection", return_value=mock_col):
        client = AnkiWebClient(settings)
    return client, mock_col


# ---- Behavior 1: empty credentials raise AuthError ----


def test_empty_username_raises_auth_error():
    with patch("inksink.anki.client.Collection"):
        with pytest.raises(AuthError, match=r"config\.yml"):
            AnkiWebClient(_settings(username="", password="secret"))


def test_empty_password_raises_auth_error():
    with patch("inksink.anki.client.Collection"):
        with pytest.raises(AuthError, match=r"config\.yml"):
            AnkiWebClient(_settings(username="user@example.com", password=""))


# ---- Behavior 2: bad credentials (anki raises) wrapped in AuthError ----


def test_bad_credentials_wrapped_in_auth_error():
    mock_col = MagicMock()
    mock_col.sync_login.side_effect = SyncError(
        "invalid credentials", None, None, None, SyncErrorKind.AUTH
    )
    with patch("inksink.anki.client.Collection", return_value=mock_col):
        with pytest.raises(AuthError):
            AnkiWebClient(_settings())
    mock_col.close.assert_called_once()


def test_non_auth_sync_error_propagates():
    mock_col = MagicMock()
    mock_col.sync_login.side_effect = SyncError(
        "server error", None, None, None, SyncErrorKind.OTHER
    )
    with patch("inksink.anki.client.Collection", return_value=mock_col):
        with pytest.raises(SyncError):
            AnkiWebClient(_settings())


def test_non_auth_sync_error_closes_collection():
    mock_col = MagicMock()
    mock_col.sync_login.side_effect = SyncError(
        "server error", None, None, None, SyncErrorKind.OTHER
    )
    with patch("inksink.anki.client.Collection", return_value=mock_col):
        with pytest.raises(SyncError):
            AnkiWebClient(_settings())
    mock_col.close.assert_called_once()


def test_unexpected_exception_closes_collection():
    mock_col = MagicMock()
    mock_col.sync_login.side_effect = RuntimeError("unexpected")
    with patch("inksink.anki.client.Collection", return_value=mock_col):
        with pytest.raises(RuntimeError):
            AnkiWebClient(_settings())
    mock_col.close.assert_called_once()


# ---- Behavior 3: sync_down() online calls col.sync_collection ----


def test_sync_down_online_calls_sync_collection():
    client, mock_col = _make_client()
    mock_auth = MagicMock()
    client._auth = mock_auth

    with patch(
        "inksink.anki.client.wifi_status", return_value=MagicMock(connected=True)
    ):
        client.sync_down()

    mock_col.sync_collection.assert_called_once_with(mock_auth, sync_media=False)


# ---- Behavior 4: sync_down() offline skips sync ----


def test_sync_down_offline_skips_sync():
    client, mock_col = _make_client()

    with patch(
        "inksink.anki.client.wifi_status", return_value=MagicMock(connected=False)
    ):
        client.sync_down()

    mock_col.sync_collection.assert_not_called()


# ---- Behavior 5: sync_up() online / offline ----


def test_sync_up_online_calls_sync_collection():
    client, mock_col = _make_client()
    mock_auth = MagicMock()
    client._auth = mock_auth

    with patch(
        "inksink.anki.client.wifi_status", return_value=MagicMock(connected=True)
    ):
        client.sync_up()

    mock_col.sync_collection.assert_called_once_with(mock_auth, sync_media=False)


def test_sync_up_offline_skips_sync():
    client, mock_col = _make_client()

    with patch(
        "inksink.anki.client.wifi_status", return_value=MagicMock(connected=False)
    ):
        client.sync_up()

    mock_col.sync_collection.assert_not_called()
