<!-- spellchecker:ignore stickered -->

# ADR 0007 — Softkey button model: generic GPIO IDs, on-screen labels

## Status

Accepted

## Context

The Device is a multi-App platform (`anki`, `ebooks`, `pdf`, Launcher). Any
fixed physical button labeling — etched, printed, or stickered — locks the
hardware vocabulary to one App and makes labels wrong or meaningless in all
others. The original build guide proposed side-edge buttons named for Anki
(`show_answer`, `again`, `hard`, `good`, `easy`) and a dedicated `power`
button mapped to GPIO 4.

Three questions were in scope:

**Button naming in Core.** App-specific names (`show_answer`, `again`) in
`core/input.py` make Core wrong for every App other than Anki. Generic
positional IDs leave semantic naming to the App layer, where it belongs.

**A dedicated custom power GPIO button.** GPIO pins cannot wake the Pi from
a fully powered-off state — only GPIO 3 (SCL) can do hardware wake, and that
pin is occupied by PiSugar 3's I2C bus. A custom GPIO power button could
only trigger a software shutdown while the Pi is running, which is redundant:
the PiSugar 3 hardware button already handles power-on (hold) and safe
shutdown (long-press triggers the OS shutdown command). Adding a second power
button adds wiring complexity with no benefit.

**Grid size: 4×2 vs 5×2.** The device is used in portrait orientation, making
the short edge (~480 px, ~115 mm) the row width. Five columns gives 96 px per
on-screen label — cramped for e-ink font sizes. Four columns gives 120 px per
label and accommodates all foreseeable use cases: four Anki rating buttons,
Launcher navigation, and spare context actions.

## Decision

The Device has 8 physical buttons identified as `btn_1`–`btn_8`, arranged in
a 4×2 grid on the short (bottom) edge. `core/input.py` maps GPIO pins to
these generic IDs only. Each App state declares its own button→action bindings
and the label to display on screen for each button.

`btn_1` (top-left) is "Menu" by convention in every App, always returning the
user to the Launcher. No `power` entry appears in the GPIO map — power-on and
hardware shutdown are owned by the PiSugar 3 button. A systemd SIGTERM handler
in the App calls `display.sleep()` before exit, keeping the soft-shutdown path
clean without requiring the PiSugar power-manager daemon.

## Consequences

- `core/input.py` is App-agnostic; the Anki app (and every future App) maps
  `btn_*` IDs to semantic action names in its own state logic
- On-screen button labels must be rendered as part of every App layout;
  a blank label means the button is inactive in that state
- The PiSugar 3 hardware button long-press is a hard power-off without the
  daemon — acceptable because the PiSugar UPS prevents file-system corruption
  on unclean shutdown
- GPIO 4 (previously `power`) is freed — it may be assigned as any `btn_*` input or left unused
- Each App must register a SIGTERM handler that calls `display.sleep()` before
  exit; the idle timer is a daemon thread and dies with the process automatically,
  but without an explicit `sleep()` call the e-ink panel stays awake (drawing
  power) after systemd stops the service
