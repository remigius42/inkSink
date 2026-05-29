<!-- spellchecker:ignore apkg pylib syncserver -->

# AnkiWebClient Build Guide Stub (OBSOLETE)

> **Obsolete:** The DIY sync protocol approach below was superseded by the
> `anki` Python package (`pip install anki`), which provides
> `col.sync_login()` and `col.sync_collection()` on aarch64. See `design.md`.

The build guide includes this starting-point stub. It sketches the interface
but leaves the sync protocol implementation blank. The design doc explains
why direct SQLite parsing + `fsrs` + full collection sync is the right approach
rather than the per-card endpoints hinted at here. The stub's `sync_cards` /
`submit_review` methods do **not** reflect the final interface — see `design.md`
for the authoritative `sync_down()` / `sync_up()` API.

```python
import requests
import json

class AnkiWebClient:
    def __init__(self, username, password):
        self.session = requests.Session()
        self.auth_token = None
        self.login(username, password)

    def login(self, username, password):
        """Authenticate with AnkiWeb"""
        # Exchange credentials for hkey via:
        # POST https://sync.ankiweb.net/sync/hostKey
        # body: {"u": username, "p": password}
        # returns: {"key": "<hkey>"}
        pass

    def sync_cards(self):
        """Fetch due cards from AnkiWeb"""
        response = self.session.get(
            'https://sync.ankiweb.net/sync/meta',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        return response.json()

    def submit_review(self, card_id, rating, time_taken):
        """Submit review to AnkiWeb"""
        payload = {
            'card_id': card_id,
            'rating': rating,  # 1=Again, 2=Hard, 3=Good, 4=Easy
            'time': time_taken
        }
        response = self.session.post(
            'https://sync.ankiweb.net/sync/reviews',
            json=payload,
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        return response.ok
```

## Important caveat

The `sync/reviews` endpoint above does **not** exist as a public API.
The actual sync protocol operates on full collections, not individual
card reviews. See `design.md` — we use the raw sync protocol directly
with direct SQLite parsing + `fsrs` (the `anki` Python package is not
used; no ARM wheels available). Use this stub only as a reference for
the credential exchange pattern.

## AnkiWeb sync endpoint reference

| Endpoint | Purpose |
| -------- | ------- |
| `POST /sync/hostKey` | Exchange credentials for `hkey` session token |
| `POST /sync/meta` | Collection metadata (mod time, schema) |
| `POST /sync/apkg` | Upload or download full collection |

These are reverse-engineered from the Anki desktop client source
(`pylib/anki/syncserver/`). Our implementation calls them directly —
the `anki` Python package is not used (no ARM wheels; see `design.md`).
