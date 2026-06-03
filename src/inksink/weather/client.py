"""HTTP client for wttr.in weather data."""

from __future__ import annotations

import io
from dataclasses import dataclass
from urllib.parse import quote

import requests
from PIL import Image, ImageOps


class WeatherFetchError(Exception):
    """Raised when both https://wttr.in and https://wttr.is are unreachable."""


@dataclass
class LocationMeta:
    label: str
    latitude: str
    longitude: str


_HOSTS = ("https://wttr.in", "https://wttr.is")
_PNG_PARAMS = "?2nTFQ"
_JSON_PARAMS = "?format=j1"


def _get(url: str) -> requests.Response:
    resp = requests.get(url, timeout=10)  # noqa: S113
    resp.raise_for_status()
    return resp


def fetch_png(location: str) -> Image.Image:
    """Fetch the wttr.in forecast PNG for *location* and return it inverted."""
    last_exc: Exception | None = None
    for host in _HOSTS:
        url = f"{host}/{quote(location)}.png{_PNG_PARAMS}"
        try:
            resp = _get(url)
            img = Image.open(io.BytesIO(resp.content)).convert("L")
            return ImageOps.invert(img).convert("1")
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
    raise WeatherFetchError(
        f"Both https://wttr.in and https://wttr.is are unreachable: {last_exc}"
    )


def fetch_metadata(location: str) -> LocationMeta:
    """Fetch JSON metadata for *location*; return LocationMeta with label/coords."""
    last_exc: Exception | None = None
    for host in _HOSTS:
        url = f"{host}/{quote(location)}{_JSON_PARAMS}"
        try:
            resp = _get(url)
            data = resp.json()
            area = data["nearest_area"][0]
            return LocationMeta(
                label=area["areaName"][0]["value"],
                latitude=area["latitude"],
                longitude=area["longitude"],
            )
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
    raise WeatherFetchError(
        f"Both https://wttr.in and https://wttr.is are unreachable: {last_exc}"
    )
