<!-- spellchecker:ignore docstrings -->

## 1. Renderer — orientation-aware

- [x] 1.1 Define `Orientation(enum.StrEnum)` with `PORTRAIT = "portrait"`
  and `LANDSCAPE = "landscape"` in `core/renderer.py`; replace
  `render(html, mode)` signature with
  `render(html, mode="1bit", orientation=Orientation.PORTRAIT)`; add
  `_ORIENTATION_DIMS = {Orientation.PORTRAIT: (_PANEL_H, _PANEL_W),
  Orientation.LANDSCAPE: (_PANEL_W, _PANEL_H)}`; resolve to pixel dimensions
  internally for wkhtmltoimage and `img.resize()` calls
- [x] 1.2 Delete `_HTML_TEMPLATE` and the fragment-wrapping logic; `render()`
  passes the `html` argument directly to wkhtmltoimage — callers supply a
  complete HTML document (from `fill_*()` or an App-specific template)
- [x] 1.3 Update LRU cache key from `(sha256, mode)` to
  `(sha256, mode, orientation)`
- [x] 1.4 Update renderer module docstring to reflect new signature
- [x] 1.5 Update existing unit tests to use `orientation="landscape"` for the
  800×480 case; add portrait tests with `orientation="portrait"`

## 2. Display — config-driven rotation

- [x] 2.1 Add `display.portrait_rotation: 90`, `display.landscape_rotation: 0`,
  and `apps.launcher.orientation: "portrait"` to `core/config.py` DEFAULTS;
  each App change adds its own `apps.<name>.orientation` key
- [x] 2.2 Add `portrait_rotation` and `landscape_rotation` parameters to
  `Display.__init__`; read from settings passed in at construction time
- [x] 2.3 Implement `_rotate(image) -> Image` in `Display`: detect portrait
  (`height > width`), apply `Image.rotate(angle, expand=True)` for the
  corresponding config angle; return image unchanged if angle is 0
- [x] 2.4 Call `_rotate()` inside `display_partial()`, `display_full()`, and
  `display_4gray()` before passing image to `self._epd`
- [x] 2.5 Write unit tests: portrait image rotated 90° → 800×480; landscape
  image at 0° → unchanged; landscape image at 180° → rotated

## 3. Layout system — `core/layout.py` and templates

- [x] 3.1 Add `jinja2` to `pyproject.toml` `[project.dependencies]`
- [x] 3.2 Create `core/layouts/fullscreen.html.j2` — complete HTML document
  with `{{ content | safe }}` occupying the full viewport; include base CSS
  (Noto fonts, zero margin, body fills viewport)
- [x] 3.3 Create `core/layouts/default.html.j2` — status bar row (time, WiFi,
  battery), content area (`{{ content | safe }}`), and button bar arranged
  as 2 rows × 4 columns matching the physical 4×2 grid: top row =
  `{{ buttons[0] }}`–`{{ buttons[3] }}` (btn_1–btn_4), bottom row =
  `{{ buttons[4] }}`–`{{ buttons[7] }}` (btn_5–btn_8); CSS uses viewport
  units with fixed-height regions for status bar (~24px) and button bar
  (2 rows × ~40px = ~80px); content area fills the remainder via
  `calc(100vh - 104px)`
- [x] 3.4 Implement `fill_fullscreen(content: str) -> str` in `core/layout.py`:
  load and render `fullscreen.html.j2` with `content`
- [x] 3.5 Implement `fill_default(content: str, buttons: list[str]) -> str`:
  validate `len(buttons) == 8` (raise `ValueError` otherwise); call
  `wifi_status()`, `battery_percent()`, `datetime.now()` internally; render
  `default.html.j2` with all values
- [x] 3.6 Write unit tests: `fill_fullscreen` returns HTML containing content;
  `fill_default` with 8 buttons returns HTML with labels; wrong button count
  raises `ValueError`; status values appear in output (mock `core/state`)

## 4. Integration and verification

- [x] 4.1 Replace `docs/adr/0008-portrait-landscape-orientation.md` with the
  content of `notes/adr-0008-updated.md`; remove the `> **Note**` blockquote
  at the top before writing; delete `notes/adr-0008-updated.md` after applying
- [x] 4.2 Define `_PANEL_W: int = 800` and `_PANEL_H: int = 480` in
  `core/display.py`; replace all bare `800`/`480` literals in `display.py`
  and `renderer.py` with these constants; `_ORIENTATION_DIMS` in
  `renderer.py` derives from them:
  `{Orientation.PORTRAIT: (_PANEL_H, _PANEL_W), Orientation.LANDSCAPE: (_PANEL_W, _PANEL_H)}`
- [x] 4.3 Run full test suite; fix any callers broken by renderer signature change
- [x] 4.4 Ensure all changed and new production code has type hints on function
  signatures and module-level variables
- [x] 4.5 Ensure all new modules have a module-level docstring; add function
  docstrings where the purpose is not obvious from the signature
- [x] 4.6 Ensure all changed and new production code is covered by unit tests;
  no new logic without a corresponding test
- [x] 4.7 Run pre-commit on all modified files (`pre-commit run --files <files>`)
  and fix all violations before marking tasks complete

## 5. Button input — generic positional IDs

- [x] 5.1 Add the two truly new GPIO entries to `_DEFAULT_PIN_MAP`: `btn_5`
  (GPIO 19) and `btn_8` (GPIO 27); GPIO 17 was rejected (conflicts with
  Waveshare HAT RST line); GPIO 19 confirmed against physical HAT wiring
- [x] 5.2 Rename all existing Anki-specific keys in `_DEFAULT_PIN_MAP`:
  `power`→`btn_1`, `show_answer`→`btn_2`, `again`→`btn_3`, `hard`→`btn_4`,
  `good`→`btn_6`, `easy`→`btn_7`
- [x] 5.3 Remove any `setup()` logic that treated the former `power` entry as
  a special case (e.g. shutdown callbacks on GPIO 4); GPIO 4 is now a regular
  softkey (`btn_1`)
- [x] 5.4 Update existing unit tests: replace `"show_answer"`, `"again"`,
  `"hard"`, `"good"`, `"easy"` assertions with the new `btn_*` IDs
- [x] 5.5 Search codebase for all `wait_for_action()` callers matching on
  Anki-specific names and update to `btn_*` (currently only stub callers)

## 6. Wire renderer cache size from config

- [x] 6.1 Add `configure_from_settings(settings: dict) -> None` to
  `core/renderer.py`: reads `settings["renderer"]["cache_max_size"]` and calls
  `configure(max_size=...)`
- [x] 6.2 Write unit test: `configure_from_settings({"renderer": {"cache_max_size": 2}})`
  causes the 3rd unique render to evict the oldest entry (4 subprocess calls total)
- [x] 6.3 Create `core/startup.py` with `startup(settings: dict) -> None` that
  calls `renderer.configure_from_settings(settings)`; write integration test in
  `tests/core/test_startup.py` verifying cache size is applied end-to-end
- [x] 6.4 Wire `__main__.py` to call `startup(load_settings())` at boot
