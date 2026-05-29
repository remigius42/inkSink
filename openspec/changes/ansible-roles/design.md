<!-- spellchecker:ignore importability -->

## Notes

- [notes/ansible-conventions.md](notes/ansible-conventions.md) — `ansible.cfg`,
  `vars.yml`, role structure, task/handler conventions, and `verify.yml`
  assertion patterns
- [notes/hardware-install-commands.md](notes/hardware-install-commands.md) — apt
  packages, Waveshare driver install; reference for translating to idempotent
  Ansible tasks
- [notes/bluetooth-neovim.md](notes/bluetooth-neovim.md) — Bluetooth/Neovim
  impact on `base` role optional packages (`base_install_neovim` flag)

### Build guide references

- Hardware assembly steps →
  [`docs/build_guide.md#assembly-order`](../../../docs/build_guide.md#assembly-order)

## Context

Ansible conventions (see `notes/ansible-conventions.md`):

- All YAML files start with `# SPDX-License-Identifier: MIT`
- Fully-qualified module names (`ansible.builtin.*`, `community.general.*`)
- `become: true` on all privileged tasks
- `cache_valid_time: 3600` on all `apt` tasks
- Handlers for service restart/reload; notify by name
- `defaults/main.yml` + `meta/main.yml` in every role
- `ansible.cfg` enables fact caching in `.ansible/facts_cache`

Target: Raspberry Pi Zero 2W, Raspberry Pi OS Lite (Trixie), 64-bit aarch64.
Device is reachable over WiFi after OS bootstrap (Imager or firstrun.sh). All
roles are idempotent — safe to re-run.

## Goals / Non-Goals

**Goals:**

- Bring a fresh Pi to a fully operational inksink device in one playbook run
- Keep `deploy.yml` fast — rsync + service restart only, no apt/driver work
- `verify.yml` catches drift: missing packages, files, or stopped service

**Non-Goals:**

- WiFi/SSH bootstrapping (handled by Imager before Ansible runs)
- Bluetooth keyboard pairing (manual, post-deploy)
- Monitoring or alerting

## Decisions

### `base` role bundles hardening + hardware drivers

OS hardening (locale, SSH, UFW, fail2ban) and hardware driver installation are
combined in a single `base` role to keep the role count low. If the role becomes
unwieldy, extraction into sub-roles is straightforward.

Alternative: separate roles per concern (locales, ssh, ufw, fail2ban). Rejected
— adds complexity without benefit at this project's scale.

### Waveshare driver: vendored source files

`epd7in5_V2.py` and `epdconfig.py` from the upstream e-Paper repo live in
`vendor/waveshare_epd/` in this repository. Each file has a header comment with
source URL and commit SHA; `vendor/waveshare_epd/VENDOR.md` records the full
provenance (repo, commit SHA, date, files copied).

Ansible syncs `vendor/waveshare_epd/` to `/opt/waveshare-vendor/waveshare_epd/`
on the device. The `/usr/local/bin/inksink` shell wrapper (a Jinja2 template)
sets `PYTHONPATH=/opt/inksink:/opt/waveshare-vendor` so `from waveshare_epd
import epd7in5_V2` resolves without any install step.

Alternatives rejected:

- `git clone + setup.py install`: deprecated PEP 517, network dependency at
  provision time.
- PyPI (`waveshare-epaper`): unofficial mirror, inconsistent versioning.

### No `pisugar` role — raw I2C via `smbus2`

The PiSugar power-manager daemon was considered for low-battery auto-shutdown.
Rejected: a crashed app cannot invoke the daemon's clean shutdown anyway, and
the UPS eliminates sudden power loss. Battery level and RTC are read directly
over I2C by the app using `smbus2` (PyPI), declared in `pyproject.toml`.

The older `python3-smbus` apt package is not installed — `smbus2` offers a
superset of that API including context-manager support used by `core/state.py`.

### Python dependencies installed into an app virtualenv

All Python dependencies (`anki`, `smbus2`, `Pillow`, `PyYAML`, `Jinja2`,
`requests`) are installed via pip into a dedicated virtualenv at
`/opt/inksink-venv` rather than into the system Python or with
`--break-system-packages`.

Rationale: `--break-system-packages` can corrupt OS-managed Python packages on
Debian and is explicitly discouraged. A virtualenv is isolated, reproducible,
and standard practice for app deployments.

The `inksink` role creates the venv with `python3 -m venv /opt/inksink-venv`
and runs `pip install` for all dependencies declared in `pyproject.toml`. The
pip install task is idempotent — it is a no-op when versions are already
satisfied. No apt-installed Python packages (`python3-pillow`,
`python3-requests`) are needed for the app.

The shell wrapper uses `/opt/inksink-venv/bin/python3` so the venv's
site-packages are always active:

```sh
PYTHONPATH=/opt/inksink:/opt/waveshare-vendor \
  /opt/inksink-venv/bin/python3 -m inksink "$@"
```

`PYTHONPATH` remains necessary for the rsync'd source (`/opt/inksink`) and
the vendored Waveshare driver (`/opt/waveshare-vendor`), which are not
pip-installed into the venv.

`verify.yml` checks importability with
`/opt/inksink-venv/bin/python3 -c "import smbus2"` rather than an apt
package assertion.

### `inksink` role uses `ansible.posix.synchronize` (rsync)

Per ADR 0001. Source: `{{ playbook_dir }}/../src/inksink/`, destination:
`/opt/inksink/`. The `rsync_opts` exclude `__pycache__` and `*.pyc`. After sync,
the systemd service is restarted via handler.

### Config file: `/etc/inksink/config.yml` templated from vault

Jinja2 template (`config.yml.j2`) renders AnkiWeb credentials and default
settings as YAML. File permissions: `0640`, owner `pi`, group `pi`. The
`anki-app` change reads this via `core/config.py` `load_settings()`.

### `verify.yml` asserts post-deployment state

Asserts: packages installed, Waveshare driver present, `/opt/inksink/` synced,
`/etc/inksink/config.yml` exists and contains `apps.anki` structure,
`inksink.service` running and enabled.

## Risks / Trade-offs

- **Vendored Waveshare files need manual updates**: upstream bug fixes require
  copying new files and updating `VENDOR.md`. Acceptable for a stable,
  well-established display driver.

- **`synchronize` requires `rsync` on both control machine and Pi**: `rsync` is
  present on RPi OS Lite by default. Control machine requirement is documented
  in `docs/setup.md`.

## Resolved

- **UFW SSH rule**: allow from any source (not LAN-only). The device moves
  between networks; fail2ban provides brute-force protection in lieu of
  network-level restriction.
