## ADDED Requirements

### Requirement: Settings persist to `/etc/inksink/config.yml`

`config.py` SHALL provide `load_settings() -> dict` and
`save_settings(settings: dict)` functions. Settings SHALL be stored as YAML
at `/etc/inksink/config.yml`, readable and writable by the `pi` user.
Missing keys SHALL fall back to defaults defined in `DEFAULTS` without error.

Top-level keys allowed: `display.*` (hardware settings, e.g.
`display.idle_timeout`) and `apps.*`. All app settings are nested under
`apps.<app_name>`, including credentials (e.g. `apps.anki.ankiweb_username`).
Apps read their own subtree via `load_settings()["apps"][app_name]`.

#### Scenario: Missing config file returns defaults

- **WHEN** `load_settings()` is called and `/etc/inksink/config.yml` does not exist
- **THEN** a dict of default values is returned without raising an exception

#### Scenario: Saved settings round-trip correctly

- **WHEN** `save_settings({"apps": {"anki": {"refresh_interval": 15}}})` is called followed by `load_settings()`
- **THEN** `load_settings()` returns a dict containing `{"apps": {"anki": {"refresh_interval": 15}}}`
