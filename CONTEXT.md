# inksink — Glossary

## Anki Collection

The local copy of the user's Anki database (`.anki2` file) stored at
`/var/lib/inksink/collection.anki2`. Downloaded from AnkiWeb at Anki Session
start; uploaded back at Anki Session end. The unit of sync — not individual
cards.

## Anki Session

A single review run on the Device: the state machine that takes the user
from SYNCING through QUESTION/ANSWER cycles to DONE. Distinct from
`requests.Session` (HTTP) and Python's `SessionState` dataclass (in-memory
progress tracker within an Anki Session).

## App

A self-contained mode of operation running on the Device. Each App owns its
own Python subpackage under `src/inksink/`. The Launcher is the first App to
run on boot; content Apps (`anki`, `ebooks`, `pdf`) are launched from it.

## Base role

The Ansible role that brings a freshly flashed Pi to a usable state: OS
packages, locale/timezone, SSH hardening, firewall, and the Waveshare e-ink
driver. WiFi is configured via Raspberry Pi Imager before Ansible runs. The
Device is non-functional without it.

## Button

One of 8 physical momentary switches (`btn_1`–`btn_8`) arranged in a 4×2
grid on the short (bottom) edge of the Device in portrait orientation. Buttons
carry no physical labels — each App state declares what each button does and
what label to show on screen. `btn_1` (top-left) is "Menu" by
convention, always returning to the Launcher. The PiSugar 3 hardware button
handles power-on/off separately and is not a Button in this sense.

## Config

The file `/etc/inksink/config.yml`, deployed by Ansible and owned by the `pi`
user. Per-app settings nest under `apps.<app_name>` (e.g. `apps.anki.*`).
Hardware-level settings (e.g. `display.idle_timeout`) and Core infrastructure
settings (e.g. `renderer.cache_max_size`) use named top-level sections.
Defaults are defined in `core/config.py` and merged at load time.

## Compositor

Stateful object in `core/ui/compositor.py` that owns the in-memory 1-bit
framebuffer and orchestrates the two-layer rendering pipeline. wkhtmltoimage
renders the content zone; Pillow renders chrome (status bar, button bar) onto
the framebuffer. Drives `display.display_partial()` for chrome-only updates
(button highlights, status bar refresh) without re-invoking wkhtmltoimage.
One instance exists for the process lifetime, instantiated at boot alongside
`Display`. Timer loop refreshes the status bar every
`display.status_refresh_interval` seconds (default 20 s) via a daemon thread.

## Core

Shared infrastructure used by all Apps: display driver wrapper, GPIO input
handler, orientation-aware HTML-to-image renderer, Jinja2 layout system,
Compositor, config (settings load/save), and hardware state (battery, WiFi).
Lives in `src/inksink/core/`. Session state belongs to each App, not Core.

## Deploy

The act of syncing `src/inksink/` from the control machine to `/opt/inksink/`
on the Device via Ansible's `synchronize` module, followed by a service
restart. Does not involve `git` or `pip` on the Device.

## Device

The physical appliance: Raspberry Pi Zero 2W + Waveshare 7.5" e-ink HAT
(800×480 px) + PiSugar 3 battery, housed in a 3D-printed case. Used in
portrait orientation by default (effective 480×800 px); landscape orientation
is supported per App. Controlled by 8 physical Buttons on the short (bottom)
edge. Physical rotation angle is configurable in Config
(`display.portrait_rotation`, `display.landscape_rotation`) to account for
case-assembly variation.

## Display mode

A per-App setting (`apps.<name>.display_mode` in Config) controlling the
rendering pipeline. `"1bit"` uses partial refresh (~0.4s, black/white) suited
to fast card-flipping. `"4gray"` uses full refresh (~3-4s, four gray levels)
suited to image-heavy content. Only meaningful on V2 screens sold after Oct
2023\. `full_refresh_interval` is ignored in `"4gray"` mode.

## Launcher

The App that runs on Device boot (`__main__.py` → systemd). Single-pass:
renders MENU, handles one user selection (App launch / Status / Settings /
Logs / Sleep), then returns; `__main__.py` restarts it in a loop. Acts as
the parent of all content Apps; `btn_1` ("Menu") in any App returns to the
Launcher. Implemented in `src/inksink/launcher/app.py`.

## Layout

An HTML Jinja2 template that defines the screen structure for a rendered App
state. One built-in layout: `content` (`fill_content(content, has_statusbar, has_buttons)`)
which reserves blank white regions for Pillow-rendered chrome.
Apps may define their own layout templates in `<app>/layouts/`.

## Status Screen

A Launcher screen (reached via `btn_5` in MENU) that displays live device
diagnostics: time, battery, WiFi SSID + signal, hostname, IP address,
Bluetooth state + connected devices, system load averages, memory, storage,
and deployed tag version (`INKSINK_VERSION` env var). Read-only; `btn_1`
returns to MENU. Does not scroll in v1.
