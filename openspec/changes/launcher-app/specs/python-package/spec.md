## MODIFIED Requirements

### Requirement: Package is importable as `inksink`

The repository SHALL provide a Python package at `src/inksink/` installable
via `pip install -e .` on the dev machine and runnable as
`python3 -m inksink` without installation on the device.

#### Scenario: Entry point runs without error

- **WHEN** `python3 -m inksink` is executed on a machine with the `src/`
  directory on `PYTHONPATH`
- **THEN** the Launcher starts (display init may fail on non-Pi hardware, but
  the process does not exit with an unhandled exception from `__main__.py`)

### Requirement: Package has `core`, `anki`, and `launcher` subpackages

The package SHALL contain `inksink.core`, `inksink.anki`, and
`inksink.launcher` subpackages. Each subpackage SHALL have an `__init__.py`.

#### Scenario: Subpackages are importable

- **WHEN** `from inksink import core, anki, launcher` is executed
- **THEN** all three imports succeed without errors

> Passes once task 1.1 (`launcher/__init__.py`) is complete.
