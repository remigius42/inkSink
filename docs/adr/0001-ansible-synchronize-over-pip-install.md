# ADR 0001 — Ansible `synchronize` over `git clone` + `pip install` for deployment

## Status

Accepted

## Context

The Device needs a way to receive application updates from the control machine.
Options considered:

- **`synchronize`** (rsync via Ansible): pushes files directly, no tooling
  required on the Device
- **`git clone` + `pip install`**: requires Git and pip on the Device, enables
  `git pull` for manual on-device updates
- **PyPI publish + `pip install`**: cleanest install UX, but requires
  maintaining a PyPI release pipeline

The Device is a personal appliance with no meaningful hardware security (SD
card extraction defeats any software isolation). Keeping the Device lean and
the deployment path simple is the primary concern.

## Decision

Use Ansible's `synchronize` module to push `src/inksink/` to `/opt/inksink/`
on the Device. No Git or pip required on the Device.

## Consequences

- Fewer moving parts on the Device
- All updates go through Ansible — no ad-hoc `git pull` on the Device
- PyPI publishing remains a future option if the package is ever made public;
  switching would require adding a `[project]` section to `pyproject.toml` and
  updating the `inksink` Ansible role
