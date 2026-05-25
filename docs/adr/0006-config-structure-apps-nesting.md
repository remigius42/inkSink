# ADR 0006 — Config structure: `apps.<name>` nesting, defaults in `core/config.py`

## Status

Accepted

## Context

The device runs multiple Apps (`anki`, future `ebooks`, `pdf`). Each App has
its own settings (credentials, display mode, refresh behavior). A config
format was needed that:

- Keeps App settings isolated from each other
- Accommodates hardware-level settings that apply across all Apps
- Has a clear home for defaults that is reachable by both `state.py` and tests
- Does not over-engineer for Apps that do not yet exist

**Flat top-level keys** — e.g. `ankiweb_username`, `display_mode` at root.
Simple now, but collides as Apps multiply; migration of deployed config files
is disruptive.

**Per-App files** — e.g. `/etc/inksink/apps/anki.yml`. Clean isolation, but
YAGNI: adds file deployment complexity, path management, and a loading layer
for a problem that does not yet exist.

**Single file with `apps.<name>` nesting** — all App settings under
`apps.anki.*`, `apps.ebooks.*`, etc.; hardware settings at a top-level
`display.*` key. Adding a new App requires adding a new subtree, not a new
file or a schema migration.

For defaults: embedding them in `state.py` couples policy to I/O. A separate
`core/config.py` with a `DEFAULTS` dict keeps `state.py` focused on
persistence and makes defaults importable by tests without loading the full
state module.

## Decision

Use a single `/etc/inksink/config.yml` with this structure:

```yaml
display:
  idle_timeout: 180

renderer:
  cache_max_size: 100

apps:
  anki:
    ankiweb_username: "..."
    ankiweb_password: "..."
    display_mode: "1bit"
    full_refresh_interval: 20
```

Defaults live in `core/config.py` as a `DEFAULTS` dict. `load_settings()` in
`core/state.py` deep-merges the loaded YAML over `DEFAULTS`. `save_settings()`
writes only explicit values — `DEFAULTS` is not persisted.

`full_refresh_interval` is per-App and documented as a no-op when
`display_mode` is `"4gray"` (every 4-gray refresh is already a full refresh).

## Consequences

- New Apps add a subtree under `apps:` with no schema migration
- `core/config.py` is the single source of truth for defaults; tests import
  it directly
- Deployed `config.yml` files must be migrated when restructuring (task 5.2
  handles the initial migration from the flat repo-scaffold layout)
- Per-App config files remain an option if isolation needs grow, but are not
  needed now
- `load_settings()` raises `ValueError` when the YAML root is not a mapping
  (list, scalar, or `null`) — a missing file returns defaults, but a
  structurally wrong file is treated as a fault worth surfacing
- Core infrastructure settings that are neither hardware nor per-App (e.g.
  `renderer.cache_max_size`) get their own named top-level section rather than
  being forced under `display.*` or `apps.*`
