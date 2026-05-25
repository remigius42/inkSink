## Already done (repo-scaffold change)

- [x] 0.1 Add `Pillow` and `smbus2` to `pyproject.toml` `[project.dependencies]`
- [x] 0.2 Add `wkhtmltopdf` to `ansible/roles/base/` apt packages
- [x] 0.3 Add `python3-rpi.gpio` to `ansible/roles/base/` apt packages

## 1. Display Driver

- [ ] 1.1 Implement `Display` class in `core/display.py` with `init()`,
  `display_partial(image)`, `display_full(image)`, `display_4gray(image)`,
  `sleep()`
- [ ] 1.2 Add partial-refresh counter; auto-trigger full refresh after
  `apps.<name>.full_refresh_interval` (default 20); skip counter entirely
  in `"4gray"` mode
- [ ] 1.3 Raise `RuntimeError` if `display_partial()` or `display_full()` called
  before `init()`
- [ ] 1.4 Implement idle sleep timer: `threading.Timer` reset on every display
  call; fires `sleep()` after configurable timeout (default 180s, from
  `config.yml`); next display call transparently re-inits if sleeping
- [ ] 1.5 Write unit tests: `RuntimeError` before `init()`, partial-refresh
  counter increments, auto full-refresh at threshold, timer fires sleep,
  display call re-inits after sleep (mock `waveshare_epd`)

## 2. Button Input

- [ ] 2.1 Implement `InputHandler` in `core/input.py` with default GPIO→action
  mapping from build guide
- [ ] 2.2 Configure all button pins as `GPIO.IN` with `GPIO.PUD_UP` on init
- [ ] 2.3 Implement `wait_for_action()` polling loop with 10ms sleep and 50ms
  debounce
- [ ] 2.4 Support mapping override from `config.yml`
- [ ] 2.5 Add lazy GPIO import with graceful fallback for non-Pi hosts
- [ ] 2.6 Write unit tests for debounce logic (mock GPIO)

## 3. Card Renderer

- [ ] 3.1 Implement `render(html: str) -> PIL.Image` in `core/renderer.py` using
  `wkhtmltoimage` subprocess
- [ ] 3.2 Wrap HTML in template with Noto CJK font, 800px width, UTF-8 charset
- [ ] 3.3 Accept `mode` arg (`"1bit"` / `"4gray"`); convert output PNG via
  Pillow to mode `"1"` or `"L"` quantized to 4 levels; verify 800×480
- [ ] 3.4 Add in-memory cache keyed by `(hashlib.sha256(html), mode)`
- [ ] 3.5 Write temp files to `/tmp/` and clean up in `finally` block
- [ ] 3.6 Write unit tests: output size/mode for both `"1bit"` and `"4gray"`,
  cache hit skips subprocess, cleanup on success and exception

## 4. Config & Device State

- [ ] 4.1 Implement `DEFAULTS` dict, `load_settings() -> dict`, and
  `save_settings(settings: dict)` in `core/config.py`; deep-merge loaded YAML
  over `DEFAULTS`
- [ ] 4.2 Implement `battery_percent() -> int` in `core/state.py` via `smbus2`
  at I2C address 0x57; return -1 if unavailable
- [ ] 4.3 Implement `WifiStatus` dataclass and `wifi_status() -> WifiStatus` in
  `core/state.py`; shell out to `nmcli -t -f active,ssid,signal dev wifi`;
  parse active row; return sentinel (`connected=False`, `ssid=None`,
  `strength=-1`) if `nmcli` fails or is absent
- [ ] 4.4 Write unit tests: settings round-trip, missing file returns defaults,
  battery returns -1 when I2C unavailable, wifi connected/disconnected/nmcli-absent
  (mock subprocess)

## 5. Dependencies & Config

- [ ] 5.1 Add `fonts-noto-cjk` to `ansible/roles/base/` apt packages
- [ ] 5.2 Restructure `ansible/roles/inksink/templates/config.yml.j2`: move
  `ankiweb_username` and `ankiweb_password` under `apps.anki`; add
  `apps.anki.display_mode: "1bit"` and `apps.anki.full_refresh_interval: 20`;
  add top-level `display.idle_timeout: 180`
