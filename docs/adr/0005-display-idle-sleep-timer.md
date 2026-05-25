# ADR 0005 — Display idle sleep via `threading.Timer`, not explicit caller responsibility

## Status

Accepted

## Context

The Waveshare 7.5" e-Paper V2 datasheet (UC8179 controller) states: *"When the
screen is not being refreshed, set it to sleep mode or power it off. Otherwise,
the screen will remain in a high voltage state for a long time, which will
damage the e-Paper irreparably."* Sources:
[7.5inch_e-Paper_V2_Specification.pdf](https://files.waveshare.com/upload/6/60/7.5inch_e-Paper_V2_Specification.pdf),
[ESPHome issue #4739](https://github.com/esphome/issues/issues/4739).

Sleep must therefore be called when the display is idle.

Three approaches were considered:

**Explicit caller responsibility** — the App calls `sleep()` after each card
display. Simple, but relies on convention. Any future App or code path that
forgets the call risks permanent hardware damage.

**Auto-sleep after every display call** — `display_partial()` / `display_full()`
call `sleep()` before returning. Guarantees protection, but `init()` runs the
full power-on sequence; paying that cost on every card transition adds
perceptible latency to every button press.

**Idle timer (`threading.Timer`)** — each display call resets a countdown. When
the timer fires, `sleep()` is called automatically. The next display call
transparently re-inits if the display is sleeping. Apps never manage sleep
directly.

Deep sleep requires a full `init()` before the next display operation (the
UC8179 deep sleep command is only exited via hardware reset). The timer approach
amortizes that cost: `init()` is only paid after a genuine idle period, not on
every card transition.

## Decision

`Display` owns sleep lifecycle via a `threading.Timer`. Every call to
`display_partial()` or `display_full()` cancels any pending timer and starts a
new one. When the timer fires, `sleep()` is called internally and a `_sleeping`
flag is set. The next display call calls `init()` transparently if `_sleeping`
is True.

`sleep()` remains public for explicit shutdown at process exit. `init()` is
public for the initial startup call only.

Idle timeout defaults to 180 seconds; configurable via `config.yml`.

## Consequences

- Apps are protected from hardware damage without needing to manage sleep
- Button-press latency is low during active use; `init()` cost is only paid
  after a genuine idle period
- Introduces one daemon `threading.Timer` thread — a limited exception to the
  project's otherwise single-threaded, blocking-I/O design
- Unit tests must mock `threading.Timer` to verify sleep/wake behavior
