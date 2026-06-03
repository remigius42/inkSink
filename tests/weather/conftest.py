# spellchecker:ignore Effretikon

"""Shared fixtures for weather tests."""

from __future__ import annotations

import io
import json
from unittest.mock import MagicMock

import pytest
from PIL import Image


def _make_png_bytes(width: int = 100, height: int = 50, color: int = 0) -> bytes:
    img = Image.new("1", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


CANNED_PNG = _make_png_bytes(width=100, height=50, color=0)

CANNED_JSON = json.dumps(
    {
        "nearest_area": [
            {
                "areaName": [{"value": "Effretikon"}],
                "country": [{"value": "Switzerland"}],
                "latitude": "47.433",
                "longitude": "8.683",
            }
        ]
    }
).encode()


def _ok_response(content: bytes, content_type: str = "image/png") -> MagicMock:
    resp = MagicMock()
    resp.status_code = 200
    resp.raise_for_status = MagicMock()
    resp.content = content
    resp.json = MagicMock(
        return_value=json.loads(content) if content_type == "application/json" else None
    )
    return resp


def _error_response() -> MagicMock:
    import requests

    resp = MagicMock()
    resp.raise_for_status.side_effect = requests.HTTPError("500")
    return resp


@pytest.fixture
def png_bytes() -> bytes:
    return CANNED_PNG


@pytest.fixture
def json_bytes() -> bytes:
    return CANNED_JSON
