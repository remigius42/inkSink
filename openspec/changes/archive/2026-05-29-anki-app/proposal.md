## Why

`core-infrastructure` provides the hardware abstraction layer. This change
builds the first App on top of it: a complete Anki review session driven by
physical buttons on the e-ink device.

## What Changes

- `anki/client.py` — AnkiWeb sync client wrapping `anki.collection.Collection`:
  `sync_login()` for auth, `sync_collection()` at session start/end; offline
  detection skips sync and lets the Collection file persist reviews for the
  next online session
- `anki/app.py` — `SessionState` dataclass (current card index, review count,
  last sync); `ReviewSession.run()` callable by the Launcher; review session
  loop: show question → show answer → rate → advance to next card, with
  progress display and end-of-session summary
- `anki/layouts/review.html.j2` — Anki-specific Jinja2 layout template:
  content area + progress indicator slot + button bar

## Capabilities

### New Capabilities

- `ankiweb-client`: AnkiWeb API authentication, due-card fetching, review
  submission, and offline queue with background sync
- `anki-review-session`: full button-driven review loop using core display,
  input, renderer, and state modules

### Modified Capabilities

## Impact

- Fills in `src/inksink/anki/` stub modules from `repo-scaffold`
- Does NOT modify `__main__.py` — the Launcher owns the entry point
  (`launcher-app` change); Anki exposes `ReviewSession.run()` only
- Adds `anki` to `pyproject.toml` dependencies (`requests` already present
  from `core-infrastructure`; `jinja2` already present from
  `core-rendering-pipeline`; `fsrs` not needed — built into `anki`)
- Requires AnkiWeb credentials in `/etc/inksink/config.yml` under
  `apps.anki.ankiweb_username` and `apps.anki.ankiweb_password`
- Depends on `core-rendering-pipeline` (layout system, orientation-aware
  renderer) and `launcher-app` (Launcher registers Anki in its APPS list)
- No changes to `core/` modules
