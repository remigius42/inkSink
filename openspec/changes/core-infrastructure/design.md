<!-- spellchecker:ignore gpiozero imgkit iwconfig -->

## Notes

- [notes/gpio-pins.md](notes/gpio-pins.md) — BCM pin assignments for display HAT,
  PiSugar, and buttons; I2C address 0x57
- [notes/code-snippets.md](notes/code-snippets.md) — build guide starting-point code
  for display, renderer, and input; RAM budget
- [notes/app-architecture.md](notes/app-architecture.md) — software stack diagram,
  five-component → module mapping, card rendering pipeline
- [notes/config-structure.md](notes/config-structure.md) — target `config.yml`
  layout with all keys and their defaults

### Build guide references

- Software setup checklist → [`docs/anki-eink-device-build-guide.md#software-setup`](../../../docs/anki-eink-device-build-guide.md)
- Testing & validation → [`docs/anki-eink-device-build-guide.md#testing--validation`](../../../docs/anki-eink-device-build-guide.md)
- Troubleshooting (display, software) → [`docs/anki-eink-device-build-guide.md#troubleshooting`](../../../docs/anki-eink-device-build-guide.md)

## Context

Target hardware: Raspberry Pi Zero 2W (1GHz quad-core, 512MB RAM), Waveshare
7.5" e-ink HAT V2 (800×480, SPI), PiSugar 3 (I2C battery/RTC), 6-8 tactile
buttons (GPIO, active-low with internal pull-ups). OS: Raspberry Pi OS Lite
(console-only). All code runs as the `pi` user.

RAM budget (from build guide): ~160MB total; Python + libraries ~20MB; the
renderer's `wkhtmltoimage` subprocess peaks at ~30MB while active but is
short-lived.

## Goals / Non-Goals

**Goals:**

- Provide a stable, hardware-specific API for the four shared concerns
- Keep App code (anki, ebooks, etc.) free of direct hardware calls
- Support dev-machine testing for renderer and state (no GPIO/SPI required)

**Non-Goals:**

- Async/event loop — blocking I/O is fine for a single-app device
- Multi-display or multi-input-device support
- Fonts beyond Noto CJK (sufficient for Japanese/Chinese Anki cards)

## Decisions

### Display: thin wrapper around Waveshare library, not an abstraction layer

The Waveshare Python library (`waveshare_epd.epd7in5_V2`) is the de-facto
interface for this display. Wrapping it thinly (init, partial refresh, full
refresh, sleep) avoids reinventing it while centralizing the partial/full
refresh logic (full refresh every N cards to clear ghosting).

The driver also uses a PWR pin (BCM 18) for power enable; `epdconfig.py`
defines `PWR_PIN = 18`. `init()` must assert it before SPI communication.

Full-refresh interval is per-App (`apps.<name>.full_refresh_interval`,
default 20) and only applies in `"1bit"` mode — in `"4gray"` mode every
refresh is already a full refresh, making the counter meaningless.

Alternative: abstract behind a `Display` protocol to support other displays
later. Rejected — YAGNI; the device is built around this specific display.

### Display sleep: idle timer, not explicit caller responsibility

Leaving the display in a high-voltage state for extended periods causes
irreversible damage (per the UC8179 datasheet). Sleep cannot be left to the
caller.

`Display` manages sleep automatically via a `threading.Timer`. Every call to
`display_partial()` or `display_full()` cancels any pending timer and starts a
new one. When the timer fires, `sleep()` is called and `_sleeping` is set.
The next display call transparently calls `init()` first if `_sleeping` is
True — the caller never needs to manage this.

`sleep()` remains public for explicit process-exit shutdown. `init()` is
public for the initial startup call only.

Idle timeout defaults to 180 seconds; configurable in `config.yml`.

Alternative: auto-sleep after every display call. Rejected — `init()` runs
the full power-on sequence; paying that cost on every card transition would
add perceptible latency to each button press.

Alternative: explicit caller responsibility. Rejected — hardware damage risk
is too high to leave to convention.

### Input: polling loop, not GPIO interrupts

`RPi.GPIO` edge-detection callbacks are available but introduce threading
complexity. A tight polling loop with 10ms sleep and 50ms debounce is
simpler, has negligible CPU impact on a dedicated device, and avoids
callback-threading bugs.

Alternative: `gpiozero` `Button` class (higher-level, event-driven). Rejected
to keep dependencies minimal; `RPi.GPIO` is already required for the display
HAT setup anyway.

### Renderer: subprocess call to `wkhtmltoimage`, not a Python HTML renderer

`wkhtmltoimage` handles complex Anki card HTML (MathJax, images, CJK fonts)
correctly. Pure-Python HTML renderers (e.g. `html2image`, `imgkit`) either
lack CJK font support or are wrappers around the same binary. The build guide
confirms this approach.

Rendered PNGs are written to `/tmp/` and converted to the target bit depth
by Pillow. Optional card cache keyed by content hash avoids re-rendering
unchanged cards.

### Display mode: both 1-bit and 4-gray supported; App chooses via config

The V2 driver supports both 1-bit partial refresh (~0.4s) and 4-gray full
refresh (~3-4s, screens sold after Oct 2023). These suit different Apps:
fast card-flipping (anki) favours 1-bit; image-heavy reading (ebooks) may
prefer 4-gray quality.

`Display` exposes both `display_partial(image)` (PIL mode `"1"`) and
`display_4gray(image)` (PIL mode `"L"` quantized to 4 levels). `Renderer`
accepts a `mode` argument (`"1bit"` or `"4gray"`) and returns the appropriate
PIL image. Apps read `display_mode` from `config.yml` and wire the two calls
accordingly.

Default per App: `anki` → `"1bit"`. Future Apps may override.

### Config: YAML file, all I/O in `core/config.py`

Settings persist to `/etc/inksink/config.yml`, owned by `pi`. All
app-specific keys are nested under `apps.<app_name>` — there are no top-level
app keys. Hardware settings (e.g. `display.idle_timeout`) sit at their own
top-level section. App credentials (e.g. `apps.anki.ankiweb_username`) live
alongside other App settings such as `apps.anki.display_mode`.

`core/config.py` owns both the `DEFAULTS` dict and `load_settings()` /
`save_settings()`. Tests import `DEFAULTS` directly without touching I/O.
Splitting into per-App config files is YAGNI — one `config.yml` with `apps:`
nesting is sufficient.

Alternative: SQLite for settings. Rejected — overkill for a handful of scalar
values.

### State: hardware reads only

`core/state.py` provides on-demand hardware reads. No session state lives
here; session tracking belongs to each App.

`battery_percent() -> int` reads from PiSugar 3 over I2C (address 0x57).
Returns -1 when I2C is unavailable (dev machine).

`wifi_status() -> WifiStatus` shells out to `nmcli -t -f active,ssid,signal
dev wifi` and parses the active row. `WifiStatus` is a dataclass with
`connected: bool`, `ssid: str | None`, and `strength: int` (0–100 when
connected, -1 when disconnected or `nmcli` unavailable). Using `nmcli` rather
than `iwconfig` gives structured, parseable output without screen-scraping
and is the standard interface on NetworkManager-managed Pi OS Lite.

## Risks / Trade-offs

- **wkhtmltoimage is slow (~1-2s per render)**: Acceptable for card transitions
  (user reads the card before pressing a button); pre-rendering the next card
  in the background is a future optimization.
  → Mitigation: cache rendered images by content hash.

- **RPi.GPIO not available on dev machines**: Importing it at module level
  breaks tests on non-Pi hosts.
  → Mitigation: lazy import with a `HardwareNotAvailable` fallback; pyright
  config already sets `reportMissingModuleSource = "none"`.

- **PiSugar I2C address conflicts**: PiSugar 3 uses I2C address 0x57.
  Waveshare HAT does not use I2C, so no conflict.

- **wkhtmltoimage security**: renders local HTML only (written to `/tmp/`
  by the renderer itself). No user-supplied URLs are passed.
