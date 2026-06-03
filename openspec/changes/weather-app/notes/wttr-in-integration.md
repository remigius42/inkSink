<!-- spellchecker:ignore areaname bezirk chubin effretikon pfäffikon superquiet svizra svizzera -->

# wttr.in Integration Notes

## Format string: `?2nTFQ`

| Flag | Meaning |
| ---- | ------- |
| `2` | 2-day forecast (current + 2 days) |
| `n` | Narrow version (day + night only, no morning/afternoon split) |
| `T` | No terminal ANSI color codes |
| `F` | No "Follow @igor_chubin" link at bottom (**not** "wind" — easy to misread) |
| `Q` | Superquiet: no "Weather report:" header, no city name header |

### Why `Q` and not `q`

`q` removes the "Weather report:" header but keeps the resolved location at the
bottom as:

```text
Ort: Effretikon, Bezirk Pfäffikon, Zürich, 8307, Schweiz/Suisse/Svizzera/Svizra [47.4283137,8.6869714]
```

That line is ~103 chars × 8 px = **824 px** — wider than the 720 px content
zone. `Q` strips it entirely, which is why the JSON fetch is needed to recover
the location name and coordinates for the overlays.

## PNG pixel dimensions

wttr.in renders PNG using DejaVu Sans Mono at `CHAR_WIDTH=8`, `CHAR_HEIGHT=14`
px per cell
([source](https://github.com/chubin/wttr.in/blob/79e506e0c577dd3cc113a79037bc068e79e1f877/internal/formatter/ansitopng/ansitopng.go#L23-L25)).

| Format | Lines | Max chars | PNG width | PNG height |
| ------ | ----- | --------- | --------- | ---------- |
| `?TF2` (full, non-narrow) | ~45 | ~115 | 920 px | 630 px |
| `?2nTFQ` (chosen) | ~23 | ~87 | **696 px** | **322 px** |
| `?0TFQ` (current only) | ~3 | ~78 | 624 px | 42 px |

Landscape content zone with `portrait_rotation=90` (button bar on right):

- Width: 800 − 80 (button bar) = **720 px**
- Height: 480 − 24 (status bar) = **456 px**

`?2nTFQ` at 696×322 px fits with 24 px horizontal margin and 134 px vertical
slack — enough for the label (14 px) and coordinates (14 px) overlays.

## Why inversion is required

`T` removes ANSI colors but the terminal default is white text on black
background. After `PIL.ImageOps.invert()` this becomes black text on white —
correct for e-ink. The `background=ffffff` URL parameter does not help here
because with `T` the foreground remains the terminal default (white), which
would be invisible on a white background.

## JSON response structure

Endpoint: `https://wttr.in/{location}?format=j1`

```json
{
  "nearest_area": [
    {
      "areaName": [{ "value": "Effretikon" }],
      "country":  [{ "value": "Switzerland" }],
      "latitude":  "47.433",
      "longitude": "8.683"
    }
  ]
}
```

Parse as:

```python
area = data["nearest_area"][0]
label    = area["areaName"][0]["value"]
latitude = area["latitude"]
longitude = area["longitude"]
```

Works identically when `location` is a city name, UTF-8 string (e.g. `Zürich`),
or coordinate pair (e.g. `47.4283,8.6870`).

## DejaVu Sans Mono font path on Debian

Package: `fonts-dejavu-core`

Path on Debian/Raspberry Pi OS:

```text
/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf
```

Load in Pillow:

```python
from PIL import ImageFont
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 13)
```

Font size 13 pt at the wttr.in renderer produces 8×14 px cells — use the same
size for overlays to visually match the PNG text.

## Fallback host

`https://wttr.is` is a fully equivalent fallback domain. URL pattern is
identical — substitute the host and retry on any connection/HTTP error from
`wttr.in`. Both hosts are operated by the same maintainer.
