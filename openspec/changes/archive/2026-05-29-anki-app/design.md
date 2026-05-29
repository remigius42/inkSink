<!-- spellchecker:ignore manylinux revlog sched -->

## Notes

- [notes/ankiweb-stub.md](notes/ankiweb-stub.md) — build guide AnkiWebClient stub
  and AnkiWeb sync endpoint reference
- [notes/review-workflow.md](notes/review-workflow.md) — intended user experience
  and button→rating mapping; use as acceptance test for the session flow

## Context

AnkiWeb does not publish an official public API. The `anki` Python package
(MIT licensed, pip-installable) wraps a Rust backend that implements the full
AnkiWeb sync protocol, the Collection object model, and the FSRS scheduler.
On 64-bit aarch64 (Pi OS Trixie), official `manylinux_2_36_aarch64` wheels
are available on PyPI up to 25.9.4 and install via `pip install anki`.

The sync API exposed by the package (no Qt/aqt required):

- `col.sync_login(username, password, None)` — exchange credentials for
  `SyncAuth`; `None` endpoint uses AnkiWeb
- `col.sync_collection(auth, sync_media=False)` — bidirectional sync with
  AnkiWeb; downloads remote changes and uploads local changes in one call

A practical alternative for a read/review device is the **AnkiConnect** local
plugin — but that requires a desktop Anki instance running, which defeats the
purpose of a standalone device.

## Goals / Non-Goals

**Goals:**

- Fetch due cards and conduct a review session entirely on-device
- Submit completed reviews back to AnkiWeb (online) or queue them (offline)
- Display card question and answer HTML using `core/renderer`
- Advance through cards using the 4-button rating scheme (Again/Hard/Good/Easy)

**Non-Goals:**

- Deck management, card editing, or note creation
- Media sync (images/audio in cards) — deferred; text-only cards first
- Multiple deck selection — reviews all due cards across all decks
- Real-time sync during a session — sync happens at session start and end

## Decisions

### Use `anki` Python package for Collection, scheduling, and sync

The `anki` package provides the Collection object model, FSRS scheduler
(default since Anki 23.10), and AnkiWeb sync — all backed by a Rust binary.
On 64-bit aarch64 (Pi OS Trixie), the official PyPI wheel installs without
compilation.

```python
from anki.scheduler_pb2 import CardAnswer

col     = Collection("/var/lib/inksink/collection.anki2")
sched   = col.sched                                # runtime: v3.Scheduler
queued  = sched.get_queued_cards(fetch_limit=9999) # QueuedCards with .cards list
entry   = queued.cards[0]                          # has .card (proto) and .states
card    = col.get_card(entry.card.id)              # rich Card; has .question()/.answer()
card.start_timer()                                 # must be called before rendering question
html_q  = card.question()                          # complete HTML including <style>
html_a  = card.answer()

answer  = sched.build_answer(card=card, states=entry.states, rating=CardAnswer.GOOD)
sched.answer_card(answer)                          # AGAIN=0 HARD=1 GOOD=2 EASY=3
```

This eliminates DIY SQLite parsing of `cards`/`notes`/`revlog` and the
separate `fsrs` package.

Alternative: DIY SQLite parsing + `fsrs`. Rejected — the `anki` package is
now installable on the target architecture; DIY parsing adds fragility and a
separate scheduling dependency. See
[ADR 0004](../../../docs/adr/0004-anki-collection-sqlite-with-fsrs.md)
(superseded) and
[ADR 0011](../../../docs/adr/0011-anki-package-aarch64.md).

Alternative: AnkiConnect desktop extension. Rejected — requires desktop
Anki running permanently on the network; user does not run desktop Anki.

### Sync strategy: `col.sync_collection()` at Anki Session boundaries

`col.sync_collection(auth, sync_media=False)` performs a bidirectional sync —
pulling remote changes at SYNCING state and pushing local review history at
DONE state. This is the same mechanism Anki desktop uses; no DIY HTTP client
needed for sync.

`sync_down()` and `sync_up()` are timing-based names (session start / session
end), not directional — both call the same bidirectional `col.sync_collection()`.
The distinction is when they run, not what they do.

Alternative: DIY reverse-engineered sync protocol. Rejected — the `anki`
package's Rust backend is the authoritative implementation and stays
compatible with AnkiWeb across desktop releases.

Alternative: Card-by-card API calls per review. Rejected — AnkiWeb has no
public per-card review endpoint; the sync protocol operates on collections.

### Offline behavior: Collection file persists reviews; sync merges on next session

`sched.answer_card()` writes reviews directly to the local
`/var/lib/inksink/collection.anki2` SQLite file. If WiFi is unavailable,
`sync_collection()` is skipped; the reviews remain durably in the Collection.
On the next online session, `sync_collection()` at SYNCING state merges local
changes with remote — the same conflict resolution Anki desktop uses.

No `queue.json` needed — the Collection file is the persistent store.

If both the device and AnkiWeb have diverged independently (full conflict),
Anki's sync protocol performs a full sync: one side's collection wins. This
matches desktop Anki behavior and is acceptable for a single primary review
device.

### Credential keys registered in `core/config.py` DEFAULTS

`apps.anki.ankiweb_username` and `apps.anki.ankiweb_password` are added to
`DEFAULTS` as empty strings. This makes the expected config structure
self-documenting and allows `AnkiWebClient` to detect missing credentials
(empty string) and raise `AuthError` with a clear message instead of a
`KeyError`. `col.sync_login()` raises its own exception on bad credentials;
`AuthError` wraps it with a user-facing message pointing to `config.yml`.

Alternative: raise `KeyError` / `AttributeError` on absent keys. Rejected —
error message gives no hint to the user about which config file to edit.

### Anki Session flow (state machine)

`ReviewSession.run()` is called by the Launcher and returns when the session
ends (DONE → btn_1 pressed) or when the user exits mid-session (btn_1 in
QUESTION or ANSWER state). The Launcher resumes after `run()` returns.

```text
SYNCING → QUESTION → ANSWER → [QUESTION | DONE]
                                        ↓
                              btn_1 → return to Launcher
```

- `SYNCING`: show "Syncing…" screen, download collection (or skip if offline)
- `QUESTION`: render card front + progress ("N / M") via Anki layout
  template; `btn_2` = Show Answer; `btn_1` = Menu (return to Launcher)
- `ANSWER`: render card back; `btn_5`=Again, `btn_6`=Hard, `btn_7`=Good,
  `btn_8`=Easy; `btn_1` = Menu (abandon session, return to Launcher)
- `DONE`: show session summary (cards reviewed, time taken); `btn_1` = Menu;
  call `sync_up()` if online before returning

### Progress indicator in Anki layout template

The card count ("3 / 47") is a named slot in `anki/layouts/review.html.j2`,
filled alongside the card content HTML. It is not a PIL overlay. The layout
template reserves a fixed region (e.g. top-right of the content area) for the
progress string. This closes the open question from the initial design.

## Risks / Trade-offs

- **`anki` package API stability**: The `anki` PyPI package API is not
  formally versioned independently of Anki desktop. A major release could
  rename `get_queued_cards()`, `build_answer()`, `answer_card()`, or the sync API.
  → Mitigation: pin `anki` version in `pyproject.toml`; test on hardware
  after each Anki desktop release before updating the pin.

- **aarch64 wheel availability**: Future `anki` releases must continue
  publishing `manylinux_aarch64` wheels. Currently continuous through 25.9.4;
  no sign of dropping ARM64 support.
  → Mitigation: if a release drops aarch64 wheels, pin to the last good
  version until the project publishes them again.

- **Large collection sync on slow WiFi**: First sync of a large collection
  (10k+ cards with media) could be slow. `sync_media=False` is set, so only
  card data syncs.
  → Mitigation: show progress screen during SYNCING state; no timeout.

- **Full-sync conflict**: If both device and AnkiWeb have diverged (device
  offline for extended period while user reviews on desktop), Anki triggers a
  full sync where one side wins.
  → Mitigation: this matches desktop Anki behavior; acceptable for a
  single-primary-device usage pattern.
