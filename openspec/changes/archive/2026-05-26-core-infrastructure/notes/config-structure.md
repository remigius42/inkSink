# Target config.yml structure

`/etc/inksink/config.yml` after this change:

```yaml
display:
  idle_timeout: 180      # seconds before display sleeps; see ADR 0005

renderer:
  cache_max_size: 100    # max LRU entries in the in-memory render cache

apps:
  anki:
    ankiweb_username: "user@example.com"
    ankiweb_password: "secret"
    display_mode: "1bit"           # "1bit" (partial, fast) or "4gray" (full, quality)
    full_refresh_interval: 20      # only applies when display_mode is "1bit"
```

## Key decisions reflected here

- All app-specific settings (including credentials) live under `apps.<app_name>`
- `display.idle_timeout` is top-level: hardware protection applies regardless of App
- `renderer.cache_max_size` is top-level: the render cache is Core infrastructure,
  not hardware and not per-App
- `display_mode` and `full_refresh_interval` are per-App: different Apps have
  different speed/quality needs, and `full_refresh_interval` is meaningless in
  `"4gray"` mode (every 4-gray refresh is already a full refresh)
- Defaults live in `core/config.py` (`DEFAULTS` dict), not in `state.py` —
  defaults are policy, not state; keeps `state.py` focused on I/O
- Per-App config files (`anki.yml`, `ebooks.yml`) are YAGNI — `apps:` nesting
  in one file is the right stopping point
