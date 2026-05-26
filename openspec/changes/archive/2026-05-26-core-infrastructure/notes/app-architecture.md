# Application Architecture

From the build guide. Maps directly to the module structure in
`src/inksink/core/` and `src/inksink/anki/`.

## Software Stack

```
┌─────────────────────────────────┐
│     Custom Python Application   │
│   (Anki client + UI handler)    │  ← src/inksink/anki/app.py
├─────────────────────────────────┤
│  HTML Renderer (wkhtmltoimage)  │
│  Image Processing (Pillow)      │  ← src/inksink/core/renderer.py
│  Font Support (Noto CJK)        │
├─────────────────────────────────┤
│  AnkiWeb API (HTTPS/JSON)       │  ← src/inksink/anki/client.py
│  E-ink Driver (Waveshare lib)   │  ← src/inksink/core/display.py
│  GPIO Buttons (RPi.GPIO)        │  ← src/inksink/core/input.py
│  Framebuffer (/dev/fb0)         │
├─────────────────────────────────┤
│   Raspberry Pi OS Lite (Debian) │
└─────────────────────────────────┘
```

## Five Main Components → Module Mapping

| Build Guide Component | Module | Responsibility |
| --------------------- | ------ | -------------- |
| AnkiWeb API Client | `anki/client.py` | Fetch cards, submit reviews, offline queue |
| Card Renderer | `core/renderer.py` | HTML → PNG → 1-bit via wkhtmltoimage + Pillow |
| Display Manager | `core/display.py` | Waveshare driver, partial/full refresh |
| Input Handler | `core/input.py` | GPIO debounce, button → action mapping |
| State Manager | `core/state.py` | Battery (PiSugar I2C), settings, session state |

## Card Rendering Pipeline

```
AnkiWeb API → Card JSON (question, answer, HTML, media)
    ↓
HTML Template (with CSS, Kanji fonts)
    ↓
wkhtmltoimage (headless rendering)
    ↓
PNG Image (800×480 pixels)
    ↓
Pillow (convert to 1-bit B&W, optimize)
    ↓
Framebuffer (/dev/fb0)
    ↓
E-ink Display (0.4s partial refresh)
```
