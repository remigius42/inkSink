# ADR 0010 — Launcher-first architecture: dedicated Launcher App runs on boot

## Status

Accepted

## Context

The Device is a multi-App platform. Something must run on boot and decide
which App to start. The original design had `__main__.py` launch the Anki App
directly — reasonable for a single-purpose device, but it forecloses navigation
between Apps and forces the Anki App to handle concerns (settings access, status
display) that are not part of a review session.

Three approaches were considered:

**Direct Anki launch (current).** `__main__.py` starts `ReviewSession`
immediately. Simple. Breaks the moment a second App exists — there is no way
to reach it without SSHing into the device.

**Anki as the top-level shell.** Anki's DONE state offers a menu to launch
other Apps. Leaks non-Anki concerns into the Anki App; every new App
requires modifying Anki.

**Dedicated Launcher App.** A dedicated App (`src/inksink/launcher/`) runs
on boot. It shows available Apps, basic device status, and minimal settings.
Content Apps (`anki`, `ebooks`, `pdf`) are launched from it and return to it
when the user presses `btn_1` ("Menu").

## Decision

A dedicated Launcher App (`src/inksink/launcher/`) runs on device boot via
the systemd service. `__main__.py` instantiates and runs the Launcher, not
the Anki App directly.

`btn_1` ("Menu") is reserved across all App layouts as the return-to-Launcher
action. Apps do not know about each other — only the Launcher knows which Apps
exist and how to start them. The Launcher provides at a minimum: App selection,
device status (time, WiFi, and battery), and access to basic settings.

## Consequences

- `__main__.py` becomes the Launcher's entry point, not Anki's
- The Anki App's entry point becomes a callable function (e.g.
  `run_anki()`), not a top-level script
- Every App layout must reserve `btn_1` for "Menu"; App states may not
  reassign `btn_1` to a different action
- The Launcher is the natural home for device-wide settings (WiFi credentials,
  display settings) that do not belong to any single App
- Adding a new App in the future requires only registering it in the Launcher —
  no changes to existing Apps
