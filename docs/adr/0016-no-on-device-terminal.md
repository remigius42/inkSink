<!-- spellchecker:ignore fbpad fbterm fbtft pyte userspace -->

# ADR 0016 — No on-device terminal App; SSH is the maintenance path

## Status

Accepted

## Context

The Device runs Raspberry Pi OS Lite (console-only). The question arose whether
inkSink should provide a Terminal App — a full terminal emulator running
on-device and rendered to the e-ink display via the Compositor, usable with a
Bluetooth keyboard.

Three paths were considered:

**Kernel framebuffer driver.** Expose the Waveshare 7.5" display as `/dev/fb0`
via a custom kernel module or fbtft, then use `fbterm` or `fbpad` as the
terminal. Existing kernel framebuffer drivers for Waveshare e-ink panels target
other models and are experimental; porting one to the V2+ is non-trivial kernel
work outside the scope of this project.

**Userspace terminal emulator (pyte).** Run Neovim in a PTY, pipe output through
the `pyte` VT100 emulator, render the character grid via Pillow into the
Compositor. Stays within the App architecture. Meaningful implementation work,
and still limited by e-ink refresh latency.

**SSH from a remote machine.** The user connects to the Device over WiFi and
edits files remotely. SSH access is already provided by the Base Ansible role.
No new code required.

The fundamental constraint is e-ink refresh latency: 0.4 s per partial refresh
in 1-bit mode. A terminal emulator that re-renders on every keystroke produces a
typing experience that is painful for extended editing, regardless of
implementation path.

## Decision

No Terminal App will be built. SSH is the designated path for configuration and
file editing on the Device. SSH access is provided by the Base role and requires
no additional work.

## Consequences

- The `text editor` use case is removed from the project scope and README
- If a Terminal App is reconsidered in the future, the `pyte` userspace path is
  preferred over a kernel module approach
