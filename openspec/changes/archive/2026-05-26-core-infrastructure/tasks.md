<!-- spellchecker:ignore docstrings -->

## Already done (repo-scaffold change)

- [x] 0.1 Add `Pillow` and `smbus2` to `pyproject.toml` `[project.dependencies]`
- [x] 0.2 Add `wkhtmltopdf` to `ansible/roles/base/` apt packages
- [x] 0.3 Add `python3-rpi.gpio` to `ansible/roles/base/` apt packages

## 1. Display Driver

- [x] 1.1 Implement `Display` class in `core/display.py` with `init()`,
  `display_partial(image)`, `display_full(image)`, `display_4gray(image)`,
  `sleep()`
- [x] 1.2 Add partial-refresh counter; auto-trigger full refresh after
  `apps.<name>.full_refresh_interval` (default 20); skip counter entirely
  in `"4gray"` mode
- [x] 1.3 Raise `RuntimeError` if `display_partial()` or `display_full()` called
  before `init()`
- [x] 1.4 Implement idle sleep timer: `threading.Timer` reset on every display
  call; fires `sleep()` after configurable timeout (default 180s, from
  `config.yml`); next display call transparently re-inits if sleeping
- [x] 1.5 Write unit tests: `RuntimeError` before `init()`, partial-refresh
  counter increments, auto full-refresh at threshold, timer fires sleep,
  display call re-inits after sleep (mock `waveshare_epd`)

## 2. Button Input

- [x] 2.1 Implement `InputHandler` in `core/input.py` with default GPIO→action
  mapping from build guide
- [x] 2.2 Configure all button pins as `GPIO.IN` with `GPIO.PUD_UP` on init
- [x] 2.3 Implement `wait_for_action()` polling loop with 10ms sleep and 50ms
  debounce
- [x] 2.4 Support mapping override from `config.yml`
- [x] 2.5 Add lazy GPIO import with graceful fallback for non-Pi hosts
- [x] 2.6 Write unit tests for debounce logic (mock GPIO)

## 3. Card Renderer

- [x] 3.1 Implement `render(html: str) -> PIL.Image` in `core/renderer.py` using
  `wkhtmltoimage` subprocess
- [x] 3.2 Wrap HTML in template with Noto CJK font, 800px width, UTF-8 charset
- [x] 3.3 Accept `mode` arg (`"1bit"` / `"4gray"`); convert output PNG via
  Pillow to mode `"1"` or `"L"` quantized to 4 levels; verify 800×480
- [x] 3.4 Add in-memory cache keyed by `(hashlib.sha256(html), mode)`
- [x] 3.5 Write temp files to `/tmp/` and clean up in `finally` block
- [x] 3.6 Write unit tests: output size/mode for both `"1bit"` and `"4gray"`,
  cache hit skips subprocess, cleanup on success and exception

## 4. Config & Device State

- [x] 4.1 Implement `DEFAULTS` dict, `load_settings() -> dict`, and
  `save_settings(settings: dict)` in `core/config.py`; deep-merge loaded YAML
  over `DEFAULTS`
- [x] 4.2 Implement `battery_percent() -> int` in `core/state.py` via `smbus2`
  at I2C address 0x57; return -1 if unavailable
- [x] 4.3 Implement `WifiStatus` dataclass and `wifi_status() -> WifiStatus` in
  `core/state.py`; shell out to `nmcli -t -f active,ssid,signal dev wifi`;
  parse active row; return sentinel (`connected=False`, `ssid=None`,
  `strength=-1`) if `nmcli` fails or is absent
- [x] 4.4 Write unit tests: settings round-trip, missing file returns defaults,
  battery returns -1 when I2C unavailable, wifi connected/disconnected/nmcli-absent
  (mock subprocess)

## 5. Dependencies & Config

- [x] 5.1 Add `fonts-noto-cjk` to `ansible/roles/base/` apt packages
- [x] 5.2 Restructure `ansible/roles/inksink/templates/config.yml.j2`: move
  `ankiweb_username` and `ankiweb_password` under `apps.anki`; add
  `apps.anki.display_mode: "1bit"` and `apps.anki.full_refresh_interval: 20`;
  add top-level `display.idle_timeout: 180`
- [x] 5.3 Update `ansible/playbooks/verify.yml`: add package assertions for
  `wkhtmltopdf` and `fonts-noto-cjk`; add a config structure check verifying
  `apps.anki` keys are present in `/etc/inksink/config.yml`
- [x] 5.4 Review all `core/` modules and ensure meaningful docstrings are
  present at module level and on public classes/functions where the purpose
  is not obvious from the name alone
- [x] 5.5 Run pre-commit static checks (ruff, black, pyright) across all
  changed files and fix any flagged issues
