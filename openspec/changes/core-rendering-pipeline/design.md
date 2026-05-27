## Notes

- [notes/portrait-rendering-gotchas.md](notes/portrait-rendering-gotchas.md) —
  PIL `expand=True` requirement, wkhtmltoimage at portrait dimensions, cache
  key pitfall
- [notes/layout-template-guide.md](notes/layout-template-guide.md) —
  Jinja2 slot variable reference, CSS baseline, browser preview recipe
- [ADR 0008](../../../docs/adr/0008-portrait-landscape-orientation.md) —
  per-App orientation; rotation at display boundary; config-driven angles
- [ADR 0009](../../../docs/adr/0009-jinja2-layout-templates.md) —
  Jinja2 layout templates with dedicated slots; Core owns status injection

### Build guide references

- Renderer architecture → [`docs/anki-eink-device-build-guide.md#software`](../../../docs/anki-eink-device-build-guide.md)

## Context

`core/renderer.py` renders HTML to a fixed 800×480 image. `core/display.py`
passes that image directly to the Waveshare driver with no rotation. There is
no layout abstraction — Apps would have to construct raw HTML for every screen
state, re-implement status bar logic, and manage button label composition
themselves.

The device needs portrait-first Apps (Anki, ebooks) at 480×800 and landscape
Apps (future). Rotation is a hardware-assembly concern: which edge
faces up depends on how the Pi + HAT stack is mounted in the 3D-printed case.
Apps should work in logical pixels; `Display` should resolve physical rotation
from Config.

Apps also need a consistent way to compose status bar + content + button
labels without duplicating HTML boilerplate. Jinja2 templates with named
slots, auto-populated status data, and enforced button-bar structure solve
this at the Core layer.

## Goals / Non-Goals

**Goals:**

- `render()` accepts `orientation` (`"portrait"` | `"landscape"`); Core
  resolves to pixel dimensions via `_PANEL_W`/`_PANEL_H` constants;
  wkhtmltoimage and the LRU cache key adapt accordingly
- `Display` rotates images at the boundary before driver handoff; rotation
  angle is config-driven, not hardcoded
- Two built-in Jinja2 layouts: `fullscreen` (content only) and `default`
  (content + button label bar + auto status bar)
- `core/layout.py` provides named filling functions; Apps pass content HTML
  and button labels; Core injects time, WiFi, battery

**Non-Goals:**

- App-specific layouts — Apps define those in `<app>/layouts/`
- Dynamic status bar updates during a render (values sampled once per fill)
- Animated or partial-region layout updates
- Renaming GPIO button IDs — covered by the `button-input` spec separately

## Decisions

### Orientation expressed as a StrEnum; Core owns the dimension mapping

`render()` accepts `orientation: Orientation` where `Orientation` is
`class Orientation(enum.StrEnum)` with `PORTRAIT = "portrait"` and
`LANDSCAPE = "landscape"`. Because it inherits from `str`, enum values compare
equal to their string equivalents — config strings convert cleanly via
`Orientation(settings["apps"]["<name>"]["orientation"])` with no extra mapping.
Core resolves orientation to pixel dimensions internally via `_ORIENTATION_DIMS`
keyed by `Orientation` members.

Each App declares its orientation via `apps.<name>.orientation` in Config
DEFAULTS (stored as a plain string; converted to `Orientation` at the call
site). Apps never handle raw pixel dimensions.

Alternative: `render()` accepts `width` and `height` integers. Rejected —
forces every call site to repeat `width=480, height=800`; no runtime or
static validation of valid combinations.

Alternative: plain `str` with `Literal["portrait", "landscape"]`. Rejected —
`enum.StrEnum` gives the same static type safety plus runtime validation and
IDE autocomplete at no extra friction thanks to the `str` inheritance.

### Rotation angle config-driven, not computed from orientation alone

The physical rotation needed before driver handoff depends on how the PCB
stack is mounted in the case — a 90° CCW rotation in one assembly may be
270° CCW in another. Config values are in PIL CCW convention (positive =
counterclockwise), passed directly to `Image.rotate(angle, expand=True)`.
`display.portrait_rotation` (default 90) and
`display.landscape_rotation` (default 0) let an integrator correct for
assembly without code changes.

### Renderer cache wired via `configure_from_settings`

`renderer.cache_max_size` in Config DEFAULTS is applied by calling
`renderer.configure_from_settings(settings)` at application startup. This keeps
the renderer stateless with respect to config — it does not read config itself,
and startup code is responsible for calling `configure_from_settings` after
`load_settings()`. Until called, the renderer uses its hardcoded default of 100.

`core/startup.py` owns the startup sequence: `startup(settings)` is the single
call site that applies all config-driven Core defaults. `__main__.py` calls
`startup(load_settings())` at boot. New subsystems that need config wiring add
their call inside `startup()`.

### `core/layout.py` exposes named functions, not a generic fill

`fill_default(content, buttons)` and `fill_fullscreen(content)` make slot
mismatches a call-site error rather than a missing-key at render time. Named
parameters document intent. A generic `fill(template, context)` would allow
any key to be passed silently wrong.

### Status bar auto-injected by Core; Apps do not provide it

Time, WiFi, and battery are device-global. Requiring each App to call
`wifi_status()` and `battery_percent()` before every render duplicates I/O
logic and introduces inconsistency. `fill_default()` calls Core state
functions internally; the values are always fresh (sampled once per fill).

Alternative: App passes status dict. Rejected — status is not the App's
domain; forgetting to pass it would silently produce a blank status bar.

## Risks / Trade-offs

- **Breaking renderer API**: all `render()` callers must pass `orientation`
  instead of the implicit 800×480. Only stub callers exist today so blast
  radius is minimal; the change must land before any App implementation.
  → No migration needed — update stubs in the same PR.

- **wkhtmltoimage behavior at portrait dimensions**: rendering at 480×800
  may expose layout edge cases. Templates use viewport units so no pixel
  variables need injecting, but overflow behavior should be tested.
  → Mitigation: integration test at both orientations during this change.

- **PIL `Image.rotate(angle, expand=True)` correctness**: `expand=True` is
  required so the rotated image dimensions match the 800×480 driver buffer.
  Forgetting `expand=True` silently produces a wrong-sized buffer.
  → Mitigation: unit test asserts driver always receives exactly 800×480.

- **Jinja2 status bar I/O on every fill**: `wifi_status()` shells out to
  `nmcli`; `battery_percent()` reads I2C. On each fill call this adds a few
  hundred milliseconds — acceptable on an e-ink device where renders take
  0.4–4 s anyway.
  → No mitigation needed; document the expected latency.
