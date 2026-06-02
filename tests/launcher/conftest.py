# spellchecker:ignore autouse

from unittest.mock import patch

import pytest
from PIL import Image


@pytest.fixture(autouse=True)
def stub_renderer_render():
    """Stub renderer.render for all launcher tests — wkhtmltoimage is not available."""
    fake = Image.new("1", (480, 800), color=1)
    with patch("inksink.core.renderer.render", return_value=fake):
        yield
