"""Anki review session: state machine driving the e-ink review loop."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from anki.scheduler_pb2 import CardAnswer

from inksink.anki.client import AnkiWebClient, AuthError
from inksink.anki.layout import fill_review
from inksink.core import renderer
from inksink.core.layout import fill_content
from inksink.core.state import wifi_status
from inksink.core.ui import ButtonState

_RATING_MAP: dict[str, int] = {
    "btn_5": CardAnswer.AGAIN,
    "btn_6": CardAnswer.HARD,
    "btn_7": CardAnswer.GOOD,
    "btn_8": CardAnswer.EASY,
}

_QUESTION_BUTTONS: list[str] = ["Menu", "Show Answer", "", "", "", "", "", ""]
_ANSWER_BUTTONS: list[str] = ["Menu", "", "", "", "Again", "Hard", "Good", "Easy"]


@dataclass
class SessionState:
    current_card_index: int | None = None
    review_count: int = 0
    last_sync: datetime | None = None


class ReviewSession:
    def __init__(
        self,
        client: AnkiWebClient,
        display,
        input_handler,
        settings: dict,
        compositor=None,
    ) -> None:
        """Initialize a review session."""
        self._client = client
        self._display = display
        self._input = input_handler
        self._orientation = settings["apps"]["anki"]["orientation"]
        self._mode = settings["apps"]["anki"].get("display_mode", "1bit")
        self._compositor = compositor

    def _render(self, html: str) -> None:
        if self._compositor is not None:
            self._compositor.set_content(html)
        else:
            image = renderer.render(
                html, mode=self._mode, orientation=self._orientation
            )
            self._display.display_full(image)

    def _set_buttons(self, labels: list[str]) -> None:
        if self._compositor is not None:
            converted = [lbl if lbl != "" else None for lbl in labels]
            states = [
                ButtonState.DEFAULT if lbl is not None else ButtonState.DISABLED
                for lbl in converted
            ]
            self._compositor.set_buttons(converted, states)

    def _review_card(
        self, rich_card: Any, entry: Any, state: SessionState, progress: str, sched: Any
    ) -> bool:
        """Run question+answer loop for one card. Returns True if user quit (btn_1)."""
        # QUESTION
        while True:
            self._set_buttons(_QUESTION_BUTTONS)
            self._render(fill_review(rich_card.question(), progress))
            action = self._input.wait_for_action()
            if action == "btn_1":
                return True
            if action == "btn_2":
                break

        # ANSWER
        while True:
            self._set_buttons(_ANSWER_BUTTONS)
            self._render(fill_review(rich_card.answer(), progress))
            action = self._input.wait_for_action()
            if action == "btn_1":
                return True
            if action in _RATING_MAP:
                answer = sched.build_answer(
                    card=rich_card,
                    states=entry.states,
                    rating=_RATING_MAP[action],
                )
                sched.answer_card(answer)
                state.review_count += 1
                return False

    def _show_done_screen(self, state: SessionState, elapsed_min: int) -> None:
        """Render the session summary and wait for btn_1."""
        summary = (
            f"<p>Done! {state.review_count} cards reviewed"
            f" in {elapsed_min} minutes.</p>"
        )
        self._render(fill_content(summary, has_statusbar=False, has_buttons=False))
        while True:
            if self._input.wait_for_action() == "btn_1":
                return

    def run(self) -> None:
        state = SessionState()

        self._render(
            fill_content("<p>Syncing…</p>", has_statusbar=False, has_buttons=False)
        )
        self._client.sync_down()
        state.last_sync = datetime.now()
        if not wifi_status().connected:
            self._render(
                fill_content(
                    "<p>Offline — using last sync</p>",
                    has_statusbar=False,
                    has_buttons=False,
                )
            )
            time.sleep(2)

        col = self._client.col
        sched: Any = col.sched  # DummyScheduler stub; runtime is v3.Scheduler
        queued = sched.get_queued_cards(fetch_limit=9999)
        entries = list(queued.cards)
        total = len(entries)
        start_time = time.monotonic()

        for i, entry in enumerate(entries):
            state.current_card_index = i
            rich_card = col.get_card(entry.card.id)  # type: ignore[arg-type]
            rich_card.start_timer()
            if self._review_card(rich_card, entry, state, f"{i + 1} / {total}", sched):
                self._client.sync_up()
                return

        elapsed_min = int((time.monotonic() - start_time) / 60)
        self._show_done_screen(state, elapsed_min)
        self._client.sync_up()


def run_anki(display, input_handler, settings: dict, compositor=None) -> None:
    """Entry point registered in the Launcher APPS list."""
    try:
        client = AnkiWebClient(settings)
    except AuthError as exc:
        html = fill_content(
            f"<p>Anki auth error: {exc}</p>",
            has_statusbar=False,
            has_buttons=False,
        )
        if compositor is not None:
            compositor.set_content(html)
        else:
            image = renderer.render(
                html,
                orientation=settings["apps"]["anki"].get("orientation", "portrait"),
            )
            display.display_full(image)
        time.sleep(3)
        return

    try:
        ReviewSession(client, display, input_handler, settings, compositor).run()
    finally:
        client.close()
