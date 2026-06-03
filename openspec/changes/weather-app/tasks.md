<!-- spellchecker:ignore httpx pressable -->

> **Implementation notes:** [wttr.in integration](notes/wttr-in-integration.md)
> · [Compositor fix](notes/compositor-fix.md)

## 1. Compositor Bug Fix

- [ ] 1.1 Fix `_content_zone_height()` in `src/inksink/core/ui/compositor.py` to
  only subtract `BUTTON_BAR_SIZE` from height when `_button_bar_edge()` returns
  `"top"` or `"bottom"`
- [ ] 1.2 Add unit tests covering portrait (subtracts), landscape side bar (does
  not subtract), and landscape top/bottom bar (subtracts)

## 2. Ansible Base Role

- [ ] 2.1 Add `fonts-dejavu-core` to the package list in
  `ansible/roles/base/tasks/main.yml`
- [ ] 2.2 Add assertion to `ansible/playbooks/verify.yml` that
  `fonts-dejavu-core` is installed

## 3. Weather App Scaffold

- [ ] 3.1 Create `src/inksink/weather/__init__.py`
- [ ] 3.2 Create `src/inksink/weather/app.py` with a `run()` entry point and
  landscape orientation config
- [ ] 3.3 Add `apps.weather` defaults to `src/inksink/core/config.py`:
  `cycle_speed_seconds=30`, `location_shortcuts=[0,1,2,3]`

## 4. wttr.in HTTP Client

- [ ] 4.1 Implement `weather/client.py` with `fetch_png(location: str) -> Image`
  — fetches `wttr.in/{location}.png?2nTFQ`, returns inverted PIL Image
- [ ] 4.2 Implement `fetch_metadata(location: str) -> LocationMeta` — fetches
  `wttr.in/{location}?format=j1`, parses `areaName`, `latitude`, `longitude`
- [ ] 4.3 Implement `wttr.is` fallback: retry failed requests against
  `wttr.is/{location}...` before raising
- [ ] 4.4 Raise `WeatherFetchError` (typed exception) when both hosts fail;
  exception message SHALL state that both `https://wttr.in` and
  `https://wttr.is` are unreachable; callers catch this to display the error
- [ ] 4.5 Add `tests/weather/conftest.py` with `responses` (or `pytest-httpx`)
  fixtures serving canned PNG and JSON payloads for `wttr.in` and `wttr.is`
- [ ] 4.6 Add unit tests for `fetch_png` and `fetch_metadata` using the
  fixtures; cover primary host success, primary failure + fallback success, both
  fail (assert `WeatherFetchError` is raised with expected message)

## 5. Location Overlay Rendering

- [ ] 5.1 Implement `weather/overlay.py` with `render_content(png: Image, label:
  str, coords: str | None, content_zone_size: tuple) -> Image` — pastes PNG
  centered, draws label at top and coords at bottom using DejaVu Sans Mono 13pt
- [ ] 5.2 Add unit tests for overlay rendering (label present, label absent,
  coords absent)

## 6. Weather App Logic

- [ ] 6.1 Implement startup JSON fetch for all configured locations in `app.py`;
  cache results as `list[LocationMeta]`
- [ ] 6.2 Implement `_show_location(idx)` — fetches PNG, builds overlay image,
  calls `compositor.set_content()`
- [ ] 6.3 Implement cycling state machine with `threading.Timer`; cycling on by
  default
- [ ] 6.4 Wire btn_1 (Menu/return), btn_2 (Prev), btn_3 (Pause/Resume), btn_4
  (Next)
- [ ] 6.5 Wire btn_5–btn_8 as direct location shortcuts per `location_shortcuts`
  config; render button with `None` label (invisible, non-pressable) for
  out-of-range indices
- [ ] 6.6 Implement SIGTERM handler calling `display.sleep()`

## 7. Launcher Registration

- [ ] 7.1 Register the Weather App in `launcher/app.py` with label "Weather"

## 8. CONTEXT.md Update

- [ ] 8.1 Add `weather` to the list of content Apps in the `App` entry of
  `CONTEXT.md`

## 9. Pre-commit and Verification

- [ ] 9.1 Run pre-commit hooks (`black`, `ruff`, `pyright`) and fix any issues
