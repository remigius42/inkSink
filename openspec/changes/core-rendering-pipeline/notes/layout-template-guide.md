# Layout Template Authoring Guide

## Slot interface

### `fill_fullscreen(content: str) -> str`

| Variable | Type | Description |
|----------|------|-------------|
| `content` | HTML string | Injected with `{{ content \| safe }}` |

### `fill_default(content: str, buttons: list[str]) -> str`

| Variable | Type | Description |
|----------|------|-------------|
| `content` | HTML string | Injected with `{{ content \| safe }}` |
| `buttons` | list of 8 strings | top row: `buttons[0]`–`buttons[3]` (btn_1–btn_4); bottom row: `buttons[4]`–`buttons[7]` (btn_5–btn_8) |
| `status.time` | string | Auto-injected by Core (e.g. `"14:32"`) |
| `status.wifi` | bool | Auto-injected by Core |
| `status.ssid` | string or None | Auto-injected by Core |
| `status.battery` | int | Auto-injected by Core (`-1` if unavailable) |

Empty string in `buttons` means the button is inactive in that state —
render the cell but leave it visually blank or greyed.

## Default slot values for design-time rendering

Use the Jinja2 `default` filter so templates render correctly when opened
directly in a browser without the Python fill functions:

```html
<!-- fullscreen.html.j2 -->
{{ content | default("<p style='padding:2rem'>[ content placeholder ]</p>") | safe }}

<!-- default.html.j2 — status bar -->
{{ status.time   | default("00:00") }}
{{ status.wifi   | default(false) }}
{{ status.ssid   | default(none) }}
{{ status.battery | default(-1) }}

<!-- default.html.j2 — button cells (repeat for each index) -->
{{ buttons[0] | default("Btn 1") }}
```

The `default` filter is a no-op at runtime — Core always supplies every
variable — so there is no behavioral difference in production.

## Status bar icons

Use inline SVG for WiFi and battery indicators — Noto Sans has no wifi/battery
glyphs, and color emoji (Noto Color Emoji) render poorly on e-ink. Inline SVG
is crisp at any size and has no font dependency.

```html
<!-- WiFi connected -->
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="2">
  <path d="M5 12.55a11 11 0 0 1 14.08 0"/>
  <path d="M1.42 9a16 16 0 0 1 21.16 0"/>
  <path d="M8.53 16.11a6 6 0 0 1 6.95 0"/>
  <circle cx="12" cy="20" r="1" fill="currentColor"/>
</svg>

<!-- WiFi disconnected (strike-through) -->
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="2">
  <line x1="1" y1="1" x2="23" y2="23"/>
  <path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55"/>
  <path d="M5 12.55a11 11 0 0 1 5.17-2.39"/>
  <path d="M10.71 5.05A16 16 0 0 1 22.56 9"/>
  <path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88"/>
  <path d="M8.53 16.11a6 6 0 0 1 6.95 0"/>
  <circle cx="12" cy="20" r="1" fill="currentColor"/>
</svg>

<!-- Battery (fill width 0–100% via inline style) -->
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="14" viewBox="0 0 24 14">
  <rect x="0" y="1" width="20" height="12" rx="2" ry="2"
        fill="none" stroke="currentColor" stroke-width="1.5"/>
  <rect x="20" y="4" width="3" height="6" rx="1" fill="currentColor"/>
  <!-- Replace 0.75 with status.battery / 100 -->
  <rect x="1.5" y="2.5" width="{{ (status.battery | default(75)) * 0.17 | round(1) }}"
        height="9" rx="1" fill="currentColor"/>
</svg>
```

In the `default` template, wrap each icon in a conditional so the WiFi icon
reflects connection state:

```html
{% if status.wifi | default(false) %}
  <!-- connected SVG -->
{% else %}
  <!-- disconnected SVG -->
{% endif %}
```

## CSS baseline

All templates should include this reset to prevent wkhtmltoimage defaulting
to unexpected margins or fonts:

```css
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Noto Sans CJK JP', 'Noto Sans', sans-serif;
  font-size: 20px;
  width: 100vw;
  height: 100vh;
  overflow: hidden;            /* prevent canvas extension */
}
```

Templates use CSS viewport units — no pixel variables are injected. The
renderer sets the wkhtmltoimage `--width`/`--height` viewport from the
resolved orientation dimensions; `100vw`/`100vh` adapt automatically.

The `default` layout should reserve approximately:
- Status bar: 24px (top)
- Button bar: 80px (bottom, 2 rows × 4 columns × ~40px per row)
- Content area: `calc(100vh - 104px)` (remainder)

## Previewing templates in a browser

Fill the template manually with placeholder values to iterate on CSS without
running the full render pipeline:

```bash
python3 - <<'EOF'
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader("src/inksink/core/layouts"))
t = env.get_template("default.html.j2")
print(t.render(
    content="<p>Card front HTML goes here</p>",
    buttons=["Menu", "Show Answer", "", "", "", "", "", ""],
    status={"time": "14:32", "wifi": True, "ssid": "home", "battery": 87},
))
EOF
```

Pipe the output to a file and open in a browser. Preview at 480×800 (portrait)
and 800×480 (landscape) viewport sizes before running the full render pipeline
to verify CSS in both orientations. Then run the full render pipeline to verify
on the e-ink display. Use `mock.patch` on `core.state.wifi_status` and
`core.state.battery_percent` in unit tests — do not add a status override
parameter to `fill_default()`.
