<!-- spellchecker:ignore sched -->

## 1. `anki` Package Setup

- [x] 1.1 Add `anki` (pinned version, e.g. `anki==25.9.4`) to `pyproject.toml`
  `[project.dependencies]`; remove any `fsrs` reference; `requests` already
  present

## 2. AnkiWeb Client

- [x] 2.1 Implement `AnkiWebClient.__init__` — load credentials from settings,
  open `anki.collection.Collection("/var/lib/inksink/collection.anki2")`
- [x] 2.2 Implement authentication — call `col.sync_login(username, password,
  None)` to obtain `SyncAuth`; raise `AuthError` (wrapping the anki exception)
  if credentials are invalid or empty
- [x] 2.3 Implement `sync_down()` — check `core/state.wifi_status().connected`;
  if online call `col.sync_collection(auth, sync_media=False)`; if offline show
  "Offline — using last sync" and proceed with local Collection
- [x] 2.4 Implement `sync_up()` — if online call `col.sync_collection(auth,
  sync_media=False)` to push local review history; skip silently if offline
  (reviews persist in Collection for next session)
- [x] 2.5 Write unit tests: auth success/failure (mock `col.sync_login`),
  offline detection skips sync, Collection closes cleanly on exit

## 3. Review Session

- [x] 3.1 Implement `SessionState` dataclass in `anki/app.py` with
  `current_card_index`, `review_count`, `last_sync`; in-memory only
- [x] 3.2 Implement `ReviewSession` in `anki/app.py` — accept `AnkiWebClient`,
  `Display`, `InputHandler`, `settings: dict`; use `core/layout.py` +
  `anki/layouts/review.html.j2` for rendering; load due cards via
  `col.sched.get_queued_cards(fetch_limit=9999)` + `col.get_card()`
- [x] 3.3 Create `anki/layouts/review.html.j2` — Anki-specific layout: content
  area, progress slot (`{{ progress }}`), button bar; btn_1=Menu, btn_2=Show
  Answer in QUESTION; btn_5=Again, btn_6=Hard, btn_7=Good, btn_8=Easy in ANSWER;
  inherits CSS baseline from `core/layouts/`
- [x] 3.4 Implement SYNCING state — show sync screen via `fill_fullscreen()`,
  call `sync_down()`; handle offline gracefully
- [x] 3.5 Implement QUESTION state — fill `review.html.j2` with card front HTML
  - progress ("N / M"); render with `orientation="portrait"`; `btn_2` advances
  to ANSWER; `btn_1` calls `sync_up()` then returns from `run()` (abandon
  session with sync); ignore other buttons
- [x] 3.6 Implement ANSWER state — fill `review.html.j2` with card back HTML;
  `btn_5`=Again, `btn_6`=Hard, `btn_7`=Good, `btn_8`=Easy; record review via
  `sched.build_answer(card=..., states=..., rating=...)` then
  `sched.answer_card(answer)`; `btn_1` calls `sync_up()` then returns from
  `run()`
- [x] 3.7 Implement DONE state — show summary screen; call `sync_up()` if
  online; `btn_1` ("Menu") returns from `run()`
- [x] 3.8 Wire state machine loop in `ReviewSession.run()`; ensure `run()`
  always returns (never calls `sys.exit()`)
- [x] 3.9 Write unit tests: state transitions (mock core modules +
  `anki.collection.Collection`), offline start, end-of-session summary, btn_1
  mid-session returns

## 4. Config

- [x] 4.1 Add `ankiweb_username` and `ankiweb_password` keys (empty strings) to
  the `apps.anki` section of `core/config.py` `DEFAULTS` (`orientation` is
  already present); absent credential keys cause `AuthError` at runtime with no
  clear message

## 5. Launcher Integration

- [x] 5.1 Expose `run_anki(display, input_handler, settings)` as the callable
  registered in `launcher/app.py` APPS list; instantiates `AnkiWebClient`,
  `ReviewSession`, and calls `session.run()`
- [x] 5.2 Handle `AuthError` inside `run_anki()` — display error message on
  screen for 3 seconds, then return (Launcher catches and resumes MENU)
- [x] 5.3 Register `run_anki` in `launcher/app.py` APPS list (replacing the
  `NotImplementedError` stub added in `launcher-app` change)

## 6. Docs, Ansible, and housekeeping

- [x] 6.1 Update `CONTEXT.md` glossary if any terms need amending (Anki Session,
  Anki Collection, offline queue)
- [x] 6.2 Update `ansible/playbooks/verify.yml`: add assertions for
  `/var/lib/inksink/` directory exists and is writable; `ankiweb_username` and
  `ankiweb_password` keys present in `/etc/inksink/config.yml`
- [x] 6.3 Run pre-commit hooks (`pre-commit run --all-files`) and fix any issues
