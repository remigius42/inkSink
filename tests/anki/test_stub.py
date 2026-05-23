from inksink import anki


def test_anki_importable() -> None:
    assert anki is not None
