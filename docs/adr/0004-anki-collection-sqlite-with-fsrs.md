# ADR 0004 — Direct SQLite parsing of Anki Collection with `fsrs` for scheduling

## Status

Accepted

## Context

The app needs to read due cards from the user's Anki Collection, conduct
reviews, update scheduling, and sync back to AnkiWeb. Several approaches
were considered:

**`anki` Python package** — the same library Anki desktop uses internally.
Ideal, but ships Rust extensions (`anki_backend`) with no ARM wheels on PyPI
(x86-64 only, verified 2026-05-23). Cross-compiling Rust for ARMv7 is
fragile and breaks on every Anki release.

**AnkiConnect desktop extension** — exposes a local REST API from a running
Anki desktop instance. Handles all scheduling and sync natively. Requires
desktop Anki running permanently on the network; not viable since the user
does not run desktop Anki.

**Old pure-Python `anki` (≤2.1.49)** — pre-Rust builds install on ARM but
use the outdated SM-2 scheduler, diverge from modern Anki versions, and
receive no security fixes.

**Direct SQLite + `fsrs`** — the Anki Collection is a SQLite database with
a stable v2 schema. The `fsrs` package (pure Python, `py3-none-any`,
actively maintained) implements the FSRS algorithm that Anki desktop uses
by default since version 23.10.

## Decision

Parse the Anki Collection SQLite file directly and use the `fsrs` package
for scheduling. Sync is handled via HTTP download/upload of the collection
zip from AnkiWeb (no `anki` package required for sync either).

Pin the expected SQLite schema version (`col.scm`) and fail loudly if it
changes rather than silently corrupting data.

## Consequences

- No Rust toolchain or cross-compilation required
- `fsrs` scheduling matches what Anki desktop produces — due dates stay
  consistent after sync
- Direct SQLite access means schema changes in a future Anki version could
  break the integration; mitigated by the schema version guard
- AnkiConnect remains a viable future alternative if the user ever runs a
  home server with Anki
