<!-- spellchecker:ignore Effretikon -->

> **Implementation notes:** [wttr.in integration
> details](notes/wttr-in-integration.md) (format flags, pixel math, JSON
> structure, font path) · [Compositor fix details](notes/compositor-fix.md)
> (exact location, before/after)

## Context

The Device has an established two-layer rendering pipeline (ADR 0012):
wkhtmltoimage renders App HTML into a PIL Image for the content zone; Pillow
renders chrome (status bar, button bar) onto the framebuffer. All existing
content Apps use this pipeline. The Compositor owns the framebuffer and drives
display refresh.

The Weather App is the first App whose content is not HTML. wttr.in serves
pre-rendered weather PNGs that are already sized to fit the landscape content
zone at native resolution. There is no custom renderer to build. See ADR 0015
for source selection rationale (wttr.in PNG vs. data API vs. JS widget).

A latent compositor bug affects any landscape App: `_content_zone_height()`
subtracts `BUTTON_BAR_SIZE` from the framebuffer height even when the button bar
is on a side edge (right/left). The Weather App is the first landscape-primary
App and will expose this bug immediately.

## Goals / Non-Goals

### Goals

- Add a Weather App that fetches and displays wttr.in forecast PNGs
- Support multiple configured locations with auto-cycling and manual navigation
- Render location label (top) and coordinates (bottom) as Pillow overlays
- Fix the compositor landscape content zone height calculation
- Add `fonts-dejavu-core` to the Ansible base role
- Register the Weather App in the Launcher menu

### Non-Goals

- Offline/cached weather display
- Custom weather rendering (icons, data layout)
- More than 4 direct-shortcut buttons (hardware constraint)
- Animated or partial-refresh weather updates

## Decisions

### Content rendering via direct Pillow paste (not wkhtmltoimage)

The wttr.in PNG endpoint returns a ready-to-display image. Routing it through
wkhtmltoimage (embedding in HTML) adds 1–5 s latency on Pi Zero for no benefit.
The Weather App calls `Compositor.set_content(img)` with a PIL Image directly —
an existing interface that already accepts PIL Images (ADR 0014 established this
as the content interface for vertical scroll).

Chrome (status bar, button bar) continues to render via the normal Pillow path.
The two-layer pipeline is preserved at the Compositor level; only the App-side
content preparation differs.

### PNG inversion

The default wttr.in PNG has white text on black background. E-ink displays
expect black ink on white paper. `PIL.ImageOps.invert()` is applied to the
fetched PNG before passing it to `set_content()`. This is applied in the Weather
App, not the Compositor — it is a data concern, not a display concern.

### Location config schema

```yaml
apps:
  weather:
    locations:
      - location: "Effretikon"   # passed verbatim to wttr.in
        label: "Home"            # optional; overrides JSON-resolved name
      - location: "47.3769,8.5417"
    cycle_speed_seconds: 30      # default
    location_shortcuts: [0, 1]   # btn_5–8 indices; default [0,1,2,3]
```

`location` is passed verbatim to wttr.in — the service handles city names,
coordinates, IATA codes, and UTF-8 strings. The app does not validate or
normalize it. If `label` is absent, the resolved `areaName` from the JSON
response is used as the display label.

### JSON fetch at startup

`wttr.in/{location}?format=j1` is fetched once per location at app startup. The
response provides `nearest_area[0].areaName[0].value` (label fallback) and
`latitude`/`longitude` (coordinate footer). The result is cached in memory for
the process lifetime. The resolved coordinates are always shown in the footer,
regardless of whether a label was configured.

### Compositor landscape height fix

`content_zone_height()` SHALL only subtract `BUTTON_BAR_SIZE` from height when
the button bar edge is `"top"` or `"bottom"`. When the edge is `"left"` or
`"right"`, the button bar reduces the content zone width (via
`content_zone_width()`), not its height.

### Public content zone API

`Compositor` exposes `content_zone_height() -> int` and `content_zone_width() ->
int` as public methods. Apps use these to size their content images; they do not
access private compositor internals. `content_zone_width()` subtracts
`BUTTON_BAR_SIZE` when the button bar is on a side edge (`left`/`right`),
mirroring the height logic for top/bottom bars.

### Single-location and empty-locations behavior

With exactly one location configured, Prev (btn_2) and Next (btn_4) are rendered
as `None` (invisible). The cycle timer still fires at `cycle_speed_seconds` — it
wraps back to index 0, re-fetching and re-rendering the same location. This
makes the cycle interval serve as the refresh interval with no special-casing in
the advance logic.

With zero locations configured, the app renders a PIL "No weather locations
configured." message inline, shows only btn_1 (Menu), and returns immediately on
any button press.

### Cycling state machine

The app maintains two pieces of state: current location index and cycling
on/off. On launch, cycling is enabled and the first location is shown. The cycle
timer (`threading.Timer`, restarted after each transition) triggers
`_advance()`. `btn_3` toggles cycling and updates its label to "Pause" /
"Resume". Manual navigation (btn_2/btn_4) advances the index and resets the
timer without disabling cycling.

## Risks / Trade-offs

- **wttr.in availability** → No mitigation in v1. `wttr.is` is a documented
  equivalent fallback domain; retry logic is deferred to implementation.
- **wttr.in PNG format changes** → The `2nTFQ` format flags are the integration
  surface. A server-side change to cell dimensions or layout would break fit.
  Monitored by visual inspection on deploy; no automated guard.
- **Inversion assumption** → If wttr.in ever serves a light-background PNG,
  inversion will produce a dark background. The flag combination `2nTFQ` (no
  ANSI colors) currently yields white-on-black consistently.
- **Pi Zero HTTP latency** → PNG fetch (~30–100 KB) over WiFi should complete in
  < 1 s. The cycle timer is reset only after the new image is composited, so
  slow fetches delay the next transition rather than causing visual glitches.

## Open Questions

None — all decisions resolved during the grilling session.
