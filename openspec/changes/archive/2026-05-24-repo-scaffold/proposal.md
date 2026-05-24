## Why

The repository has tooling and docs but no runnable code, no hardware sources,
and no deployment infrastructure. This change lays the foundational skeleton
so that all subsequent changes have a consistent place to land.

## What Changes

- Add `src/inksink/` Python package with `core/` and `anki/` subpackages and
  a `__main__.py` entry point
- Add `tests/` scaffold mirroring the package structure
- Add `hardware/case/` with OpenSCAD sources for the 3D-printed device case
- Add `ansible/` directory with roles, playbooks, inventory, and `ansible.cfg`
- Add `docs/setup.md` covering inksink-specific setup steps
- Update `pyproject.toml` with a `[project]` section

## Capabilities

### New Capabilities

- `python-package`: Python package skeleton (`src/inksink/core/`, `src/inksink/anki/`, `__main__.py`) with test scaffold
- `ansible-provisioning`: Ansible roles and playbooks for device bootstrap, app deployment, and verification
- `case-sources`: OpenSCAD sources for the 3D-printed two-piece device case

### Modified Capabilities

## Impact

- `pyproject.toml` gains a `[project]` section
- New top-level directories: `src/`, `hardware/`, `ansible/`, `tests/`
- No breaking changes — no existing code is modified
