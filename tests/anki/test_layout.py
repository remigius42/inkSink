from inksink.anki.layout import fill_review


def test_fill_review_returns_complete_html():
    result = fill_review("<p>Question</p>", "1 / 10")
    assert result.strip().startswith("<!DOCTYPE html>") or result.strip().startswith(
        "<html"
    )
    assert "<p>Question</p>" in result


def test_fill_review_progress_appears_in_output():
    result = fill_review("<p>Q</p>", "7 / 42")
    assert "7 / 42" in result


def test_fill_review_no_live_chrome_in_html():
    result = fill_review("<p>Q</p>", "1 / 5")
    assert "wifi" not in result.lower()
    assert "battery" not in result.lower()
    assert "<button" not in result.lower()


def test_fill_review_has_no_chrome_reservation():
    from inksink.anki.layout import PROGRESS_BAR_HEIGHT

    result = fill_review("<p>Q</p>", "1 / 5")
    assert "status-chrome" not in result
    assert "button-chrome" not in result
    assert str(PROGRESS_BAR_HEIGHT) in result
