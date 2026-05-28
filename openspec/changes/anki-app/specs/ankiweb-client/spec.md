<!-- spellchecker:ignore sched -->

## ADDED Requirements

### Requirement: Client authenticates with AnkiWeb using credentials from config

`client.py` SHALL provide an `AnkiWebClient` that reads `ankiweb_username`
and `ankiweb_password` from the settings dict (loaded via `core/config.py`
`load_settings()`) and exchanges them for a session token on first use.

#### Scenario: Successful authentication

- **WHEN** valid credentials are present in config and WiFi is available
- **THEN** `AnkiWebClient` obtains a session token without raising an exception

#### Scenario: Invalid credentials raise AuthError

- **WHEN** incorrect credentials are provided
- **THEN** `AnkiWebClient` raises `AuthError` with a descriptive message

### Requirement: Client syncs the Anki Collection with AnkiWeb when online

`AnkiWebClient.sync_down()` SHALL synchronize the local Collection with
AnkiWeb at session start (pulls remote changes). `AnkiWebClient.sync_up()`
SHALL synchronize at session end (pushes local review history). Both
operations use `col.sync_collection(auth, sync_media=False)`.

#### Scenario: Collection syncs on session start when online

- **WHEN** `sync_down()` is called and WiFi is available
- **THEN** the local Collection at `/var/lib/inksink/collection.anki2` is
  synchronized with AnkiWeb without error

#### Scenario: Collection syncs on session end when online

- **WHEN** `sync_up()` is called after reviews and WiFi is available
- **THEN** local review history is pushed to AnkiWeb

### Requirement: Offline reviews persist in the Collection between sessions

When WiFi is unavailable, `sync_down()` and `sync_up()` SHALL skip sync and
proceed with the local Collection. Reviews recorded via
`col.sched.answer_card()` are written directly to the Collection file and
persist across reboots. On the next online session, `sync_down()` SHALL
upload those pending reviews as part of the normal bidirectional sync.

#### Scenario: Sync skipped when offline

- **WHEN** `sync_down()` is called and WiFi is unavailable
- **THEN** no network call is made and the existing local Collection is used

#### Scenario: Offline reviews synced on next online session

- **WHEN** `sync_down()` is called on a subsequent online session after
  offline reviews were recorded
- **THEN** those reviews are pushed to AnkiWeb as part of the sync
