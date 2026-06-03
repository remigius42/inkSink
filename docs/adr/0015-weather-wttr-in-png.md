<!-- cspell:ignore wttr openweathermap weatherwidget dejavu -->

# ADR 0015 — Weather source: wttr.in pre-rendered PNG over data API or JS widget

## Status

Accepted

## Context

The Weather App needs to display current conditions and a 2-day forecast on the
Device. Three approaches were considered:

### Data API (e.g. openweathermap)

Fetch structured JSON and render it with Pillow or an HTML/Jinja2 template. Full
control over layout and typography. Requires building and maintaining a weather
renderer: icon set, layout logic, internationalization. On a Pi Zero,
wkhtmltoimage adds 1–5 s per render; Pillow-only rendering requires significant
bespoke layout code.

### JS weather widget (e.g. weatherwidget.io)

Embed a third-party JS widget rendered via wkhtmltoimage. Compact config, no
renderer to build. Ruled out early: wkhtmltoimage has very limited JS support
and reliably fails to execute widget initialization code.

### [wttr.in](https://github.com/chubin/wttr.in) pre-rendered PNG

[`wttr.in/Zürich.png?2nTFQ`](https://wttr.in/Z%C3%BCrich.png?2nTFQ) returns a
terminal-style weather PNG rendered server-side using DejaVu Sans Mono at [8×14
px/cell](https://github.com/chubin/wttr.in/blob/79e506e0c577dd3cc113a79037bc068e79e1f877/internal/formatter/ansitopng/ansitopng.go#L23-L25).
The narrow 2-day format (`2n`) produces a 696×322 px image that fits the
landscape Content Zone (≈720×456 px) at native resolution without scaling. A
companion JSON fetch (`?format=j1`, once per location at app launch) resolves
the canonical area name and coordinates for the overlay labels. UTF-8 location
names (e.g. `Zürich`) are accepted verbatim.

## Decision

Use wttr.in as the weather data source. Fetch the PNG directly and paste it into
the Content Zone via Pillow, bypassing wkhtmltoimage entirely. Invert the PNG
with `ImageOps.invert()` before compositing — the default wttr.in output uses
white text on black, which must be flipped to black on white for e-ink. Render
location label (top) and coordinates (bottom) as Pillow text overlays using
DejaVu Sans Mono to match the PNG font. The `fonts-dejavu-core` Debian package
is added to the Base role.

## Consequences

- No weather renderer to build or maintain; layout is owned by wttr.in
- Content Zone rendering for the Weather App uses Pillow directly, not
  wkhtmltoimage — an exception to the two-layer pipeline (ADR 0012)
- The app depends on wttr.in availability; network connectivity is a hard
  requirement
- The fetched PNG is inverted via Pillow before compositing; any change to
  wttr.in's default color scheme would require revisiting this
- PNG [flags](https://wttr.in/:help) (`2nTFQ`) are the primary knob for layout
  changes; deep customization (colors, layout, data fields) requires switching
  approach
- wttr.in's PNG dimensions are fixed by their renderer (8×14 px/cell,
  DejaVuSansMono); the narrow 2-day format fits the landscape Content Zone
  without scaling
- `wttr.in/:help` documents `wttr.is` as a fully equivalent fallback domain;
  retrying failed requests against it is an implementation detail left to the
  Weather App
