## 1. core/ui/ subpackage and constants

- [x] 1.1 Create `src/inksink/core/ui/__init__.py`
- [x] 1.2 Add `BUTTON_BAR_SIZE` and `STATUS_BAR_HEIGHT` constants to
  `core/ui/__init__.py`
- [x] 1.3 Define `ButtonState` enum (`DEFAULT`, `ACTIVE`, `DISABLED`) in
  `core/ui/__init__.py`

## 2. Pillow button rendering

- [x] 2.1 Implement `_draw_button(draw, x, y, w, h, label, state)` in
  `core/ui/buttons.py` — default, active, and disabled (dashed outline) tristate
- [x] 2.2 Implement `_dashed_rectangle(draw, x0, y0, x1, y1)` helper for
  disabled outline
- [x] 2.3 Implement portrait button bar renderer: 2 rows × 4 columns, horizontal
  text
- [x] 2.4 Implement landscape button bar renderer (narrow, 4×2): 4 rows × 2
  columns, vertical text
- [x] 2.5 Implement landscape button bar renderer (wide, 4×4): 4 rows × 4
  columns, vertical text + ● marker per button
- [x] 2.6 Implement `_button_bar_edge(portrait_rotation, orientation)` — derives
  edge from rotation config per design D4 table
- [x] 2.7 Implement `None` slot handling — skip drawing entirely, preserve grid
  spacing; ignore `ButtonState` for `None` slots
- [x] 2.8 Implement `""` slot merging — collapse consecutive `""` slots into the
  preceding slot; left-align (portrait) / top-align (landscape) label and ●;
  use first slot's `ButtonState` for merged group; validate no `""` as first
  slot or crossing row boundary
- [x] 2.9 Implement `_resolve_slots(labels)` — validates merge rules, handles
  `None` slots, returns resolved slot groups with states
- [x] 2.10 Implement `_compute_bounding_boxes(slot_groups, orientation, double_vertical)` —
  computes per-slot `(x, y, w, h)` for portrait and landscape narrow/wide layouts
  using `_button_bar_edge` output

## 3. Button rendering tests

- [x] 3.1 Test `_button_bar_edge(portrait_rotation, orientation)` — table-driven,
  all 4 rotations × 2 orientations = 8 cases
- [x] 3.2 Test `_resolve_slots(labels)` — covers:
  all strings, None slots, single merge (`["Wide", "", "A", "B", "C", "D", "E", "F"]`),
  chain merge (`[None, "foo", "", "", "bar", None, "baz", ""]`),
  ValueError on `""` as first slot (`["", "foo", ...]`) with message
  matching `"slot 0: .* cannot start a row"`,
  ValueError on run crossing row boundary
  (`["a", "b", "c", "", "", "d", "e", "f"]`) with message matching
  `"slot 4: .* crosses row boundary"`
- [x] 3.3 Test `_compute_bounding_boxes` — portrait and landscape narrow/wide;
  assert (x, y, w, h) for normal, None, and merged slots
- [x] 3.4 Test ACTIVE button drawing — assert pixel just inside border corner is
  black (fill); do not assert center (text-unsafe)
- [x] 3.5 Test DEFAULT button drawing — assert pixel just inside border corner is
  white
- [x] 3.6 Test DISABLED button drawing — assert border pixel at known dash-on
  position is black; at dash-gap position is white
- [x] 3.7 Test None slot drawing — assert border pixels are white; assert center
  is white; assert region is unchanged after `set_button_state(idx, ACTIVE)`
  (no inversion)
- [x] 3.8 Test merged slot drawing — assert no border line at the internal
  boundary between merged slots; assert label is left-aligned (portrait) /
  top-aligned (landscape); assert ● marker is at first slot's position

## 4. Pillow status bar rendering

- [x] 4.1 Implement `_draw_status_bar(draw, w)` in
  `core/ui/status.py` — time, WiFi, battery via `core/state.py`

## 5. Status bar timer tests

- [x] 5.1 Test `compositor.start()` arms the timer
- [x] 5.2 Test timer callback calls `display_partial()` (mock timer, invoke
  callback manually)
- [x] 5.3 Test `compositor.stop()` cancels the timer and prevents further
  `display_partial()` calls
- [x] 5.4 Test timer does not fire before `start()` is called

## 6. Compositor

- [x] 6.1 Implement `Compositor.__init__(display, settings)` — initializes 1-bit
  framebuffer at orientation dimensions
- [x] 6.2 Implement `Compositor.set_content(html)` — renders via
  `renderer.render()`, composites onto framebuffer, redraws chrome; calls
  `display.display_full()` for 1-bit mode or `display.display_4gray()` for
  4gray mode (determined by `apps.<name>.display_mode` in settings)
- [x] 6.3 Implement `Compositor.set_buttons(labels, states)` — validates length
  8, redraws button bar region, calls `display.display_partial()`
- [x] 6.4 Implement `Compositor.set_button_state(idx, state)` — redraws single
  button region, calls `display.display_partial()`
- [x] 6.5 Implement `Compositor.start()` — starts status bar daemon timer thread
- [x] 6.6 Implement `Compositor.stop()` — cancels timer thread
- [x] 6.7 Implement status bar timer loop — redraws status bar region, calls
  `display.display_partial()` every `status_refresh_interval` seconds

## 7. Layout system

- [x] 7.1 Create `core/layouts/content.html.j2` — single template with
  conditional chrome regions (blank space sized by `BUTTON_BAR_SIZE` /
  `STATUS_BAR_HEIGHT`)
- [x] 7.2 Add `fill_content(content, has_statusbar=True, has_buttons=True)` to
  `core/layout.py`
- [x] 7.3 Remove `fill_fullscreen()` and `fill_default()` from `core/layout.py`
- [x] 7.4 Delete `core/layouts/fullscreen.html.j2` and
  `core/layouts/default.html.j2`

## 8. Config

- [x] 8.1 Add `display.status_refresh_interval: 20` default to `core/config.py`
- [x] 8.2 Add `apps.<name>.display.double_vertical_button_size: False` default
  for each App in `core/config.py`

## 9. Startup wiring

- [x] 9.1 Instantiate `Compositor` in `core/startup.py` alongside `Display`
- [x] 9.2 Call `compositor.start()` in `__main__.py` after `display.init()` (not
  in `startup.py` — must follow display init)

## 10. Caller updates

- [x] 10.1 Update `anki/app.py` — replace `fill_default` / `fill_fullscreen`
  with `fill_content`; replace button label passing with
  `compositor.set_buttons()`; call `compositor.set_button_state()` on button
  press
- [x] 10.2 Update `launcher/app.py` — same replacements as 10.1
- [x] 10.3 Add `compositor.stop()` to SIGTERM handler in `anki/app.py` and
  `launcher/app.py` alongside `display.sleep()`

## 11. Documentation

- [x] 11.1 Update `CONTEXT.md` — add `Compositor` term; update `Layout` and
  `Core` definitions
- [x] 11.2 Write new ADR: two-layer rendering pipeline (wkhtmltoimage content +
  Pillow chrome)
- [x] 11.3 Write new ADR: chrome always 1-bit despite App display mode
- [x] 11.4 Update ADR 0009 to reflect `fill_content` consolidation and removal
  of `fill_fullscreen` / `fill_default`

## 12. Verification and quality

- [x] 12.1 Update `ansible/playbooks/verify.yml` if compositor startup is
  verifiable on device
- [x] 12.2 Run pre-commit hooks (`black`, `ruff`, `pyright`) and fix all issues
