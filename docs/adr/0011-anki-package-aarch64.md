<!-- spellchecker:ignore manylinux sched -->

# ADR 0011 — Use `anki` Python package on 64-bit aarch64 (supersedes ADR 0004)

## Status

Accepted

## Context

ADR 0004 chose direct SQLite parsing + `fsrs` because the `anki` PyPI package
had no ARM wheels (x86-64 only at the time). The target OS was Pi OS Lite
32-bit ARMv7.

The Raspberry Pi Foundation officially recommends 64-bit Pi OS Lite for the
Pi Zero 2W (BCM2710A1, Cortex-A53, ARMv8). Pi OS Trixie (Debian 13) is the
current release and ships Python 3.13 and glibc 2.41.

On 64-bit aarch64, the `anki` package publishes official `manylinux_2_36_aarch64`
wheels on PyPI (verified through 25.9.4). `pip install anki` requires no Rust
toolchain or cross-compilation.

The `anki` package provides via its Rust backend (no Qt/aqt required):

- `Collection` object model — `find_cards()`, `get_card()`, `get_note()`
- FSRS scheduler built in since Anki 23.10 — `col.sched.answer_card(card, rating)`
- AnkiWeb sync — `col.sync_login()` + `col.sync_collection()`

## Decision

Switch the target OS to Pi OS Lite (Trixie) 64-bit aarch64. Use the `anki`
Python package for Collection access, scheduling, and sync. Remove the DIY
SQLite parsing layer and the `fsrs` package.

## Consequences

- `pip install anki` (pinned version) replaces DIY SQLite + `fsrs`
- No reverse-engineered sync protocol — the Rust backend handles AnkiWeb sync
- Offline reviews persist in the Collection file; `sync_collection()` merges
  them on the next online session — no `queue.json` needed
- `anki` package API must be pinned and tested after each Anki desktop release
- All existing apt packages in the Ansible `base` role are available on
  aarch64 Trixie without change
- The `anki` Rust backend increases resident memory vs. plain sqlite3 + `fsrs`;
  estimate ~120 MB (needs benchmarking on Pi Zero 2W with a real collection)
