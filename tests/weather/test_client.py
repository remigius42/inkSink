# spellchecker:ignore Effretikon getpixel

"""Tests for weather HTTP client (fetch_png, fetch_metadata, fallback, errors)."""

from __future__ import annotations

import io
import json
from unittest.mock import MagicMock, patch

import pytest
import requests
from PIL import Image

from inksink.weather.client import (
    LocationMeta,
    WeatherFetchError,
    fetch_metadata,
    fetch_png,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ok_png(width: int = 100, height: int = 50) -> MagicMock:
    img = Image.new("1", (width, height), color=0)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    resp = MagicMock()
    resp.status_code = 200
    resp.raise_for_status = MagicMock()
    resp.content = buf.getvalue()
    return resp


def _ok_json(
    area: str = "Effretikon", lat: str = "47.433", lon: str = "8.683"
) -> MagicMock:
    payload = {
        "nearest_area": [
            {
                "areaName": [{"value": area}],
                "country": [{"value": "Switzerland"}],
                "latitude": lat,
                "longitude": lon,
            }
        ]
    }
    resp = MagicMock()
    resp.status_code = 200
    resp.raise_for_status = MagicMock()
    resp.content = json.dumps(payload).encode()
    resp.json = MagicMock(return_value=payload)
    return resp


def _error() -> MagicMock:
    resp = MagicMock()
    resp.raise_for_status.side_effect = requests.HTTPError("503")
    return resp


# ---------------------------------------------------------------------------
# fetch_png — primary host success
# ---------------------------------------------------------------------------


def test_fetch_png_returns_inverted_pil_image():
    """Successful fetch returns an inverted PIL Image (black PNG → white image)."""
    with patch("requests.get", return_value=_ok_png()) as mock_get:
        result = fetch_png("Effretikon")
    assert isinstance(result, Image.Image)
    mock_get.assert_called_once()
    assert "wttr.in" in mock_get.call_args[0][0]


def test_fetch_png_url_contains_format_flags():
    with patch("requests.get", return_value=_ok_png()) as mock_get:
        fetch_png("Effretikon")
    url = mock_get.call_args[0][0]
    assert "2nTFQ" in url


def test_fetch_png_inverts_image():
    """All-black PNG must become all-white after inversion."""
    with patch("requests.get", return_value=_ok_png()):
        result = fetch_png("Effretikon")
    # all-black input → after invert must be non-black (white)
    assert result.getpixel((0, 0)) != 0


# ---------------------------------------------------------------------------
# fetch_png — fallback to wttr.is
# ---------------------------------------------------------------------------


def test_fetch_png_falls_back_to_wttr_is_on_primary_failure():
    """If wttr.in fails, retry against wttr.is."""
    with patch("requests.get", side_effect=[_error(), _ok_png()]) as mock_get:
        result = fetch_png("Effretikon")
    assert isinstance(result, Image.Image)
    assert mock_get.call_count == 2
    urls = [c[0][0] for c in mock_get.call_args_list]
    assert any("wttr.in" in u for u in urls)
    assert any("wttr.is" in u for u in urls)


# ---------------------------------------------------------------------------
# fetch_png — both hosts fail → WeatherFetchError
# ---------------------------------------------------------------------------


def test_fetch_png_raises_weather_fetch_error_when_both_fail():
    with patch("requests.get", side_effect=[_error(), _error()]):
        with pytest.raises(WeatherFetchError) as exc_info:
            fetch_png("Effretikon")
    msg = str(exc_info.value)
    assert "wttr.in" in msg
    assert "wttr.is" in msg


# ---------------------------------------------------------------------------
# fetch_metadata — primary host success
# ---------------------------------------------------------------------------


def test_fetch_metadata_returns_location_meta_instance():
    with patch("requests.get", return_value=_ok_json()):
        meta = fetch_metadata("Effretikon")
    assert isinstance(meta, LocationMeta)


def test_fetch_metadata_returns_label_lat_lon():
    with patch("requests.get", return_value=_ok_json()):
        meta = fetch_metadata("Effretikon")
    assert meta.label == "Effretikon"
    assert meta.latitude == "47.433"
    assert meta.longitude == "8.683"


def test_fetch_metadata_uses_j1_format():
    with patch("requests.get", return_value=_ok_json()) as mock_get:
        fetch_metadata("Effretikon")
    url = mock_get.call_args[0][0]
    assert "format=j1" in url


# ---------------------------------------------------------------------------
# fetch_metadata — fallback to wttr.is
# ---------------------------------------------------------------------------


def test_fetch_metadata_falls_back_to_wttr_is():
    with patch("requests.get", side_effect=[_error(), _ok_json()]) as mock_get:
        meta = fetch_metadata("Effretikon")
    assert meta.label == "Effretikon"
    assert mock_get.call_count == 2


# ---------------------------------------------------------------------------
# fetch_metadata — both fail → WeatherFetchError
# ---------------------------------------------------------------------------


def test_fetch_metadata_raises_weather_fetch_error_when_both_fail():
    with patch("requests.get", side_effect=[_error(), _error()]):
        with pytest.raises(WeatherFetchError) as exc_info:
            fetch_metadata("Effretikon")
    msg = str(exc_info.value)
    assert "wttr.in" in msg
    assert "wttr.is" in msg


# ---------------------------------------------------------------------------
# fetch_metadata — coordinate input
# ---------------------------------------------------------------------------


def test_fetch_metadata_with_coordinate_string():
    with patch(
        "requests.get", return_value=_ok_json(area="Zürich", lat="47.377", lon="8.542")
    ):
        meta = fetch_metadata("47.377,8.542")
    assert meta.label == "Zürich"
    assert meta.latitude == "47.377"


# ---------------------------------------------------------------------------
# URL encoding
# ---------------------------------------------------------------------------


def test_fetch_png_url_encodes_spaces():
    """Location with spaces must be percent-encoded in the request URL."""
    with patch("requests.get", return_value=_ok_png()) as mock_get:
        fetch_png("New York")
    url = mock_get.call_args[0][0]
    assert " " not in url
    assert "New%20York" in url


def test_fetch_metadata_url_encodes_spaces():
    """Location with spaces must be percent-encoded in the metadata URL."""
    with patch("requests.get", return_value=_ok_json()) as mock_get:
        fetch_metadata("New York")
    url = mock_get.call_args[0][0]
    assert " " not in url
    assert "New%20York" in url
