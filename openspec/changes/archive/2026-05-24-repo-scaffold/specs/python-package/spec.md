## ADDED Requirements

### Requirement: Package is importable as `inksink`

The repository SHALL provide a Python package at `src/inksink/` installable
via `pip install -e .` on the dev machine and runnable as
`python3 -m inksink` without installation on the device.

#### Scenario: Entry point runs without error

- **WHEN** `python3 -m inksink` is executed on a machine with the `src/`
  directory on `PYTHONPATH`
- **THEN** the process exits cleanly (exit code 0) with a stub message

### Requirement: Package has `core` and `anki` subpackages

The package SHALL contain `inksink.core` and `inksink.anki` subpackages.
Each subpackage SHALL have stub modules matching the components described
in the build guide.

#### Scenario: Subpackages are importable

- **WHEN** `from inksink import core, anki` is executed
- **THEN** both imports succeed without errors

### Requirement: Test scaffold mirrors package structure

A `tests/` directory SHALL exist with `tests/core/` and `tests/anki/`
subdirectories and a `conftest.py` at the root. Each subdirectory SHALL
contain at least a placeholder test file.

#### Scenario: pytest discovers tests

- **WHEN** `pytest` is run from the repository root
- **THEN** it collects tests without errors (zero failures, zero errors)

### Requirement: `pyproject.toml` defines the project

`pyproject.toml` SHALL include a `[project]` section with `name`, `version`,
`requires-python`, and `dependencies` fields.

#### Scenario: Package metadata is readable

- **WHEN** `python3 -c "from importlib.metadata import metadata; print(metadata('inksink')['Name'])"` is run after `pip install -e .`
- **THEN** it prints `inksink`
