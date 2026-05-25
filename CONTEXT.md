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
own Python subpackage under `src/inksink/`. The first App is `anki`; future
Apps include `ebooks` and `pdf`.

## Base role

The Ansible role that brings a freshly flashed Pi to a usable state: OS
packages, locale/timezone, WiFi, SSH hardening, firewall, and the Waveshare
e-ink driver. The Device is non-functional without it.

## Config

The file `/etc/inksink/config.yml`, deployed by Ansible and owned by the `pi`
user. All app settings are nested under `apps.<app_name>` (e.g. `apps.anki.*`).
Hardware-level settings (e.g. `display.idle_timeout`) sit at the top level.
Defaults are defined in `core/config.py` and merged at load time.

## Core

Shared infrastructure used by all Apps: display driver wrapper, GPIO input
handler, HTML-to-image renderer, config (settings load/save), and hardware
state (battery, WiFi). Lives in `src/inksink/core/`. Session state belongs to
each App, not Core.

## Deploy

The act of syncing `src/inksink/` from the control machine to `/opt/inksink/`
on the Device via Ansible's `synchronize` module, followed by a service
restart. Does not involve `git` or `pip` on the Device.

## Display mode

A per-App setting (`apps.<name>.display_mode` in Config) controlling the
rendering pipeline. `"1bit"` uses partial refresh (~0.4s, black/white) suited
to fast card-flipping. `"4gray"` uses full refresh (~3-4s, four gray levels)
suited to image-heavy content. Only meaningful on V2 screens sold after Oct
2023\. `full_refresh_interval` is ignored in `"4gray"` mode.

## Device

The physical appliance: Raspberry Pi Zero 2W + Waveshare 7.5" e-ink HAT +
PiSugar 3 battery, housed in a 3D-printed case. A single-purpose, standalone
unit controlled by physical buttons.
