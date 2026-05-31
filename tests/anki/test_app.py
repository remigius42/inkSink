"""Tests for SessionState and ReviewSession behaviors."""

import sys
from unittest.mock import MagicMock, patch

import pytest

# Stub waveshare_epd so Display can be imported on non-Pi
_epd_stub = MagicMock()
sys.modules.setdefault("waveshare_epd", _epd_stub)
sys.modules.setdefault("waveshare_epd.epd7in5_V2", _epd_stub.epd7in5_V2)

from anki.scheduler_pb2 import CardAnswer  # noqa: E402
from PIL import Image  # noqa: E402

from inksink.anki.app import ReviewSession, SessionState  # noqa: E402
from inksink.anki.client import AnkiWebClient  # noqa: E402


def _settings():
    return {"apps": {"anki": {"orientation": "portrait", "display_mode": "1bit"}}}


def _fake_image():
    return Image.new("1", (480, 800))


def _make_entry(card_id: int):
    """Build a mock queued-card entry (mimics anki.scheduler_pb2.QueuedCards.Card)."""
    entry = MagicMock()
    entry.card.id = card_id
    return entry


def _make_client(card_ids: list[int] | None = None):
    """Build a mock AnkiWebClient with a stubbed anki collection."""
    client = MagicMock(spec=AnkiWebClient)
    mock_col = MagicMock()
    client.col = mock_col

    if card_ids is None:
        card_ids = [1]

    entries = [_make_entry(cid) for cid in card_ids]
    queued = MagicMock()
    queued.cards = entries
    mock_col.sched.get_queued_cards.return_value = queued

    def get_card(cid):
        card = MagicMock()
        card.question.return_value = f"<p>Front {cid}</p>"
        card.answer.return_value = f"<p>Back {cid}</p>"
        return card

    mock_col.get_card.side_effect = get_card
    return client


# ---- Behavior 6: SessionState defaults ----


def test_session_state_defaults():
    state = SessionState()
    assert state.review_count == 0
    assert state.current_card_index is None


# ---- Behavior 7: SYNCING — calls client.sync_down() ----


def test_run_calls_sync_down_at_start():
    client = _make_client(card_ids=[])
    ih = MagicMock()
    ih.wait_for_action.return_value = "btn_1"

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", return_value="<html/>"),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    client.sync_down.assert_called_once()


# ---- Behavior 8: QUESTION — renders card front + progress, portrait ----


def test_question_renders_card_front_with_progress():
    client = _make_client(card_ids=[1])
    ih = MagicMock()
    ih.wait_for_action.return_value = "btn_1"

    fill_calls: list[tuple] = []

    def capture_fill(content, progress):
        fill_calls.append((content, progress))
        return "<html/>"

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", return_value="<html/>"),
        patch("inksink.anki.app.fill_review", side_effect=capture_fill),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    assert any("Front 1" in content for content, _ in fill_calls)
    assert any("1 / 1" in progress for _, progress in fill_calls)


def test_question_renders_in_portrait_orientation():
    client = _make_client(card_ids=[1])
    ih = MagicMock()
    ih.wait_for_action.return_value = "btn_1"

    render_calls: list[dict] = []

    def capture_render(html, mode="1bit", orientation="portrait"):
        render_calls.append({"orientation": orientation})
        return _fake_image()

    with (
        patch("inksink.anki.app.renderer.render", side_effect=capture_render),
        patch("inksink.anki.app.fill_content", return_value="<html/>"),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    assert all(c["orientation"] == "portrait" for c in render_calls)


# ---- Behavior 9: btn_1 in QUESTION → run() returns ----


def test_btn1_in_question_returns():
    client = _make_client(card_ids=[1])
    ih = MagicMock()
    ih.wait_for_action.return_value = "btn_1"

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", return_value="<html/>"),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()
        # No exception → returned cleanly


# ---- Behavior 9b: btn_1 in QUESTION → sync_up called ----


def test_btn1_in_question_calls_sync_up():
    client = _make_client(card_ids=[1])
    ih = MagicMock()
    ih.wait_for_action.return_value = "btn_1"

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", return_value="<html/>"),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    client.sync_up.assert_called_once()


# ---- Behavior 10: non-btn_1/btn_2 in QUESTION → ignored ----


def test_other_buttons_in_question_are_ignored():
    client = _make_client(card_ids=[1])
    ih = MagicMock()
    ih.wait_for_action.side_effect = ["btn_3", "btn_4", "btn_1"]

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", return_value="<html/>"),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    # btn_3 and btn_4 ignored, btn_1 exits → 3 wait_for_action calls
    assert ih.wait_for_action.call_count == 3


# ---- Behavior 11: btn_2 in QUESTION → ANSWER (card back rendered) ----


def test_btn2_in_question_shows_answer():
    client = _make_client(card_ids=[1])
    ih = MagicMock()
    ih.wait_for_action.side_effect = ["btn_2", "btn_1"]

    fill_calls: list[str] = []

    def capture_fill(content, progress):
        fill_calls.append(content)
        return "<html/>"

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", return_value="<html/>"),
        patch("inksink.anki.app.fill_review", side_effect=capture_fill),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    # First fill_review call: Front (QUESTION); second: Back (ANSWER)
    assert any("Front 1" in c for c in fill_calls)
    assert any("Back 1" in c for c in fill_calls)


# ---- Behavior 12: rating button records review with correct rating ----


def test_rating_button_good_records_correct_rating():
    client = _make_client(card_ids=[1])
    ih = MagicMock()
    ih.wait_for_action.side_effect = ["btn_2", "btn_7", "btn_1"]  # Good → DONE → Menu

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", return_value="<html/>"),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    client.col.sched.build_answer.assert_called_once()
    kwargs = client.col.sched.build_answer.call_args.kwargs
    assert kwargs["rating"] == CardAnswer.GOOD


@pytest.mark.parametrize(
    "btn,expected_rating",
    [
        ("btn_5", CardAnswer.AGAIN),
        ("btn_6", CardAnswer.HARD),
        ("btn_7", CardAnswer.GOOD),
        ("btn_8", CardAnswer.EASY),
    ],
)
def test_all_rating_buttons_map_correctly(btn, expected_rating):
    client = _make_client(card_ids=[1])
    ih = MagicMock()
    ih.wait_for_action.side_effect = ["btn_2", btn, "btn_1"]

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", return_value="<html/>"),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    kwargs = client.col.sched.build_answer.call_args.kwargs
    assert kwargs["rating"] == expected_rating


# ---- Behavior 13b: btn_1 in ANSWER → sync_up called ----


def test_btn1_in_answer_calls_sync_up():
    client = _make_client(card_ids=[1])
    ih = MagicMock()
    ih.wait_for_action.side_effect = ["btn_2", "btn_1"]

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", return_value="<html/>"),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    client.sync_up.assert_called_once()


# ---- Behavior 13: btn_1 in ANSWER → returns without recording ----


def test_btn1_in_answer_returns_without_recording():
    client = _make_client(card_ids=[1])
    ih = MagicMock()
    ih.wait_for_action.side_effect = ["btn_2", "btn_1"]

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", return_value="<html/>"),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    client.col.sched.answer_card.assert_not_called()


# ---- Behavior 14: after last card → DONE screen shows card count ----


def test_done_screen_shows_review_count():
    client = _make_client(card_ids=[1])
    ih = MagicMock()
    ih.wait_for_action.side_effect = ["btn_2", "btn_7", "btn_1"]

    fullscreen_calls: list[str] = []

    def capture_fullscreen(content, **kwargs):
        fullscreen_calls.append(content)
        return "<html/>"

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", side_effect=capture_fullscreen),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    # Last fullscreen call is the DONE summary
    done_text = fullscreen_calls[-1]
    assert "1" in done_text  # 1 card reviewed


# ---- Behavior 15: btn_1 in DONE → sync_up() called ----


def test_btn1_in_done_calls_sync_up():
    client = _make_client(card_ids=[1])
    ih = MagicMock()
    ih.wait_for_action.side_effect = ["btn_2", "btn_7", "btn_1"]

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", return_value="<html/>"),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    client.sync_up.assert_called_once()


# ---- Behavior 14b: done screen shows correct count for multiple cards ----


def test_done_screen_shows_correct_multi_card_count():
    """After reviewing N cards the DONE screen must say N."""
    client = _make_client(card_ids=[1, 2, 3])
    ih = MagicMock()
    # Rate each card Good, then press Menu on the DONE screen
    ih.wait_for_action.side_effect = [
        "btn_2",
        "btn_7",
    ] * 3 + [  # QUESTION→ANSWER→Good for each card
        "btn_1"
    ]  # Menu on DONE screen

    fullscreen_calls: list[str] = []

    def capture_fullscreen(content, **kwargs):
        fullscreen_calls.append(content)
        return "<html/>"

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", side_effect=capture_fullscreen),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    done_text = fullscreen_calls[-1]
    assert "3" in done_text


# ---- No-cards session goes straight to DONE ----


def test_run_anki_auth_error_displays_error_and_returns():
    """run_anki must catch AuthError, show an error screen, and return cleanly."""
    from inksink.anki.app import run_anki

    settings = {
        "apps": {
            "anki": {
                "orientation": "portrait",
                "display_mode": "1bit",
                "ankiweb_username": "",
                "ankiweb_password": "",
            }
        }
    }
    display = MagicMock()
    display.display_full = MagicMock()

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", return_value="<html/>") as mock_fs,
        patch("inksink.anki.app.time.sleep"),
    ):
        run_anki(display, MagicMock(), settings)

    display.display_full.assert_called()
    # Error screen shown (fill_fullscreen called with error content)
    assert mock_fs.called


def test_offline_start_shows_offline_message_and_sleeps():
    """When WiFi is down at session start, shows 'Offline' notice for 2 s."""
    client = _make_client(card_ids=[])
    ih = MagicMock()
    ih.wait_for_action.return_value = "btn_1"

    fullscreen_calls: list[str] = []

    def capture_fullscreen(content, **kwargs):
        fullscreen_calls.append(content)
        return "<html/>"

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", side_effect=capture_fullscreen),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
        patch(
            "inksink.anki.app.wifi_status",
            return_value=MagicMock(connected=False),
        ),
        patch("inksink.anki.app.time.sleep") as mock_sleep,
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    offline_msgs = [c for c in fullscreen_calls if "Offline" in c]
    assert offline_msgs, "expected an 'Offline' screen to be shown"
    mock_sleep.assert_any_call(2)


def test_no_due_cards_shows_done_immediately():
    client = _make_client(card_ids=[])
    ih = MagicMock()
    ih.wait_for_action.return_value = "btn_1"

    fullscreen_calls: list[str] = []

    def capture_fullscreen(content, **kwargs):
        fullscreen_calls.append(content)
        return "<html/>"

    with (
        patch("inksink.anki.app.renderer.render", return_value=_fake_image()),
        patch("inksink.anki.app.fill_content", side_effect=capture_fullscreen),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
    ):
        ReviewSession(client, MagicMock(), ih, _settings()).run()

    assert any("Done" in c for c in fullscreen_calls)


# ---------------------------------------------------------------------------
# Compositor path: set_content and set_buttons are called; "" slots → None
# ---------------------------------------------------------------------------


def test_compositor_path_calls_set_content_and_set_buttons():
    """With a compositor, ReviewSession must use set_content/set_buttons."""
    client = _make_client(card_ids=[1])
    ih = MagicMock()
    # btn_2 shows answer, then btn_5 (AGAIN) answers, then btn_1 exits
    ih.wait_for_action.side_effect = ["btn_2", "btn_5", "btn_1"]

    compositor = MagicMock()

    with (
        patch("inksink.anki.app.fill_content", return_value="<html/>"),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
        patch("inksink.anki.app.wifi_status", return_value=MagicMock(connected=True)),
        patch("inksink.anki.app.time.sleep"),
    ):
        ReviewSession(client, MagicMock(), ih, _settings(), compositor).run()

    compositor.set_content.assert_called()
    compositor.set_buttons.assert_called()

    # All set_buttons calls must pass None instead of "" for empty slots
    for call in compositor.set_buttons.call_args_list:
        labels_arg = call.args[0]
        assert "" not in labels_arg, f"'' must be converted to None: {labels_arg}"

    # None slots must have DISABLED state; labeled slots must have DEFAULT state
    from inksink.core.ui import ButtonState

    for call in compositor.set_buttons.call_args_list:
        labels_arg, states_arg = call.args[0], call.args[1]
        for lbl, state in zip(labels_arg, states_arg, strict=True):
            if lbl is None:
                assert (
                    state == ButtonState.DISABLED
                ), f"None slot must be DISABLED, got {state}"
            else:
                assert (
                    state == ButtonState.DEFAULT
                ), f"labeled slot must be DEFAULT, got {state}"


def test_run_anki_does_not_stop_injected_compositor():
    """run_anki must not stop a compositor it didn't create."""
    from inksink.anki.app import run_anki

    settings = {
        "apps": {
            "anki": {
                "orientation": "portrait",
                "display_mode": "1bit",
                "ankiweb_username": "u",
                "ankiweb_password": "p",
            }
        }
    }
    compositor = MagicMock()

    ih = MagicMock()
    ih.wait_for_action.return_value = "btn_1"

    with (
        patch("inksink.anki.app.AnkiWebClient") as mock_client_cls,
        patch("inksink.anki.app.fill_content", return_value="<html/>"),
        patch("inksink.anki.app.fill_review", return_value="<html/>"),
        patch("inksink.anki.app.wifi_status", return_value=MagicMock(connected=True)),
        patch("inksink.anki.app.time.sleep"),
    ):
        client = mock_client_cls.return_value
        client.col.sched.get_queued_cards.return_value.cards = []

        run_anki(MagicMock(), ih, settings, compositor)

    compositor.stop.assert_not_called()
