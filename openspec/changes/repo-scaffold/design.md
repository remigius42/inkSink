## Context

The repository exists with tooling (pre-commit, ruff, pyright, markdownlint)
and a build guide but no source code, hardware files, or deployment
infrastructure. The target device is a Raspberry Pi Zero 2W running Raspberry
Pi OS Lite, managed entirely from a control machine via Ansible.

Key constraints from ADRs and grilling session:

- No Git or pip on the device — deployment uses `ansible.builtin.synchronize`
  (see ADR 0001)
- 3D case sources in OpenSCAD — plain text, version-control friendly
  (see ADR 0002)
- App runs as the `pi` user — hardware security is SD-card-level; a dedicated
  service user adds no meaningful protection
- Entry point is `python3 -m inksink` wrapped in `/usr/local/bin/inksink`

## Goals / Non-Goals

**Goals:**

- Establish directory structure for all future changes to build on
- Provide a working `python -m inksink` entry point (stub, not functional)
- Provide Ansible roles and playbooks that can bootstrap and deploy to the device
- Provide OpenSCAD stubs for the two-piece case
- Provide `tests/` scaffold so future test additions have a home

**Non-Goals:**

- Implementing any application logic (Anki client, display driver, etc.)
- Producing a printable case (stubs only — real geometry comes later)
- WiFi/SSH bootstrapping (delegated to Raspberry Pi Imager; documented in
  `docs/setup.md` with steps for Raspberry Pi Imager / firstrun.sh)

## Decisions

### Python package layout: src layout with `core/` and `anki/` subpackages

`src/inksink/core/` holds shared infrastructure (display, input, renderer,
state); `src/inksink/anki/` holds the first app. Future apps (ebooks, pdf)
land as siblings to `anki/`. This separation prevents app-specific code from
leaking into shared infrastructure from the start.

Alternative considered: flat package — rejected because the build guide already
anticipates multiple app modes and mixing them with infrastructure would
require a disruptive refactor later.

### Ansible role split: `base`, `inksink`

Two roles only:

`base` covers everything needed for a functional device: OS packages, locale,
SSH hardening, firewall, and the Waveshare e-ink driver (vendored — see below).

`inksink` synchronizes `src/inksink/` to `/opt/inksink/`, templates
`/etc/inksink/config.yml` from vault variables, installs the shell wrapper at
`/usr/local/bin/inksink`, and manages the systemd service.

No `pisugar` role: battery level and RTC are read directly over I2C (`smbus2`)
by the app. The PiSugar power-manager daemon was considered for auto-shutdown
but offers no advantage — a crashed app can't invoke it, and the UPS prevents
sudden power loss. `python3-smbus` is installed via apt in the `base` role.

### Waveshare driver: vendored source files

`epd7in5_V2.py` and `epdconfig.py` live in `vendor/waveshare_epd/`. Each file
carries a header comment with the source URL and commit SHA; `VENDOR.md`
records full provenance. Ansible syncs the directory to
`/opt/waveshare-vendor/` on the device; the systemd unit sets
`PYTHONPATH=/opt/waveshare-vendor`.

Alternatives rejected: `git clone + setup.py install` (deprecated, network
dependency at provision time); PyPI `waveshare-epaper` (unofficial mirror,
inconsistent versioning).

### Secrets: Ansible Vault in `group_vars/all/vault.yml`

Three secrets:
`vault_ankiweb_username`, `vault_ankiweb_password`, `vault_wifi_password`.

### Shell wrapper at `/usr/local/bin/inksink`

Keeps `ExecStart` in the systemd unit clean and provides a convenient command
for manual invocation over SSH. Deployed as a static file by the `inksink`
Ansible role.

## Risks / Trade-offs

- **Stub-only implementation**: Tasks will create placeholder files. Each stub
  must be clearly marked so future changes don't skip implementing them.
  → Mitigation: use `# TODO` markers and keep stubs minimal (no fake logic).

- **`synchronize` means no on-device `git pull`**: Quick hotfixes require
  running a playbook. Acceptable for a personal appliance but worth noting.
  → Mitigation: `deploy.yml` is fast (rsync + service restart); document this
  in `docs/setup.md`.

- **OpenSCAD stubs won't render anything useful**: The case geometry requires
  careful measurement of actual hardware. Stubs establish structure only.
  → Mitigation: annotate stubs with the dimensions from the build guide so
  the next implementer has the numbers at hand.
