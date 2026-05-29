<!-- spellchecker:ignore bantime findtime importability maxretry mdformat nocows tmpfiles -->

## 1. Inventory and Global Config

- [x] 1.1 Fix `ansible.cfg`: add `fact_caching = jsonfile`,
  `fact_caching_connection = .ansible/facts_cache`,
  `fact_caching_timeout = 86400` under `[defaults]` (not a separate section —
  Ansible ignores unknown sections); add missing `[defaults]` keys: `nocows = 1`,
  `retry_files_enabled = False`, `display_skipped_hosts = no`,
  `allow_world_readable_tmpfiles = True`
- [x] 1.2 Add SPDX header (`# SPDX-License-Identifier: MIT`) to
  `ansible/inventory/hosts.yml`
- [x] 1.3 Add SPDX header to `ansible/group_vars/all/vars.yml`; add
  `base_fail2ban_bantime`, `base_fail2ban_findtime`, `base_fail2ban_maxretry` defaults
- [x] 1.4 Add SPDX header to `ansible/group_vars/all/vault.yml.example`

## 2. `base` Role

- [x] 2.1 Create `roles/base/defaults/main.yml` and `meta/main.yml` (SPDX
  headers; meta declares `community.general` and `ansible.posix` dependencies)
- [x] 2.2 Fix locale tasks: add `de_CH.UTF-8` locale (currently only
  `en_US.UTF-8`); add `community.general.timezone` task using
  `base_locale_timezone`
- [x] 2.3 Fix SSH hardening: add missing `PubkeyAuthentication yes` lineinfile
  task
- [x] 2.4 Fix apt package list: remove `python3-pillow`, `python3-requests`,
  `python3-pip`, `git` (none needed on device — app deps go into venv, ADR 0001
  rules out git, pip not needed when venv is created with `python3 -m venv`);
  add `fail2ban`; keep `rsync`, `python3-rpi.gpio`, `wkhtmltopdf`,
  `fonts-noto-cjk`, `python3`, `ufw`
- [x] 2.5 Implement fail2ban tasks: deploy SSH jail drop-in to
  `/etc/fail2ban/jail.d/sshd.conf` using
  `base_fail2ban_bantime`/`base_fail2ban_findtime`/`base_fail2ban_maxretry` vars; enable and
  start service; add `Restart fail2ban` handler
- [x] 2.6 Move Waveshare vendor sync here from `inksink` role:
  `ansible.posix.synchronize` `vendor/waveshare_epd/` → `{{ inksink_vendor_dir
  }}/waveshare_epd/` (note: dest must be `.../waveshare_epd/` not `.../` —
  trailing-slash rsync behavior would flatten the package directory and break
  `from waveshare_epd import epd7in5_V2`)
- [x] 2.7 Add SPDX header to `roles/base/tasks/main.yml`
- [x] 2.8 Add SPDX header to `roles/base/handlers/main.yml`; replace
  `ansible.builtin.service` with `ansible.builtin.systemd` (add `daemon_reload:
  true`, `become: true`); add `Restart fail2ban` handler
- [x] 2.9 Add `become: true` to every privileged task in
  `roles/base/tasks/main.yml`; remove `become: true` from playbook level in all
  three playbooks

## 3. `inksink` Role

- [x] 3.1 Create `roles/inksink/defaults/main.yml` and `meta/main.yml` (SPDX
  headers); add `inksink_venv_dir: /opt/inksink-venv` to
  `ansible/group_vars/all/vars.yml`
- [x] 3.2 Fix directory task: add `/var/lib/inksink/` (pi:pi 0750) to the loop;
  remove `{{ inksink_vendor_dir }}` (now managed by `base`)
- [x] 3.3 Remove Waveshare vendor sync tasks from `roles/inksink/tasks/main.yml`
  (moved to `base`)
- [x] 3.4 Fix config template deploy: change mode from `"0600"` to `"0640"` (per
  `inksink-service` spec)
- [x] 3.5 Convert `roles/inksink/files/inksink.service` from static file to
  template (`roles/inksink/templates/inksink.service.j2`); add
  `Environment=INKSINK_VERSION={{ lookup('pipe', 'git describe --tags --always')
  }}` to `[Service]` section; update the copy task to use
  `ansible.builtin.template`
- [x] 3.6 Add SPDX header to `roles/inksink/tasks/main.yml`; add `become: true`
  to all privileged tasks
- [x] 3.7 Add SPDX header to `roles/inksink/handlers/main.yml`; replace
  `ansible.builtin.service` with `ansible.builtin.systemd` (`become: true`)
- [x] 3.8 Create app virtualenv: add `ansible.builtin.command` task to run
  `python3 -m venv {{ inksink_venv_dir }}` (with `creates:` guard so it is
  idempotent); set ownership to `pi:pi`
- [x] 3.9 Install Python dependencies into venv: `ansible.builtin.pip` task with
  `name: [anki==25.9.4, "smbus2>=0.6.1,<0.7", Pillow, PyYAML, Jinja2,
  requests]`, `virtualenv: "{{ inksink_venv_dir }}"`, `virtualenv_python:
  python3`; `become: true`, `become_user: pi`
- [x] 3.10 Update `roles/inksink/templates/inksink.j2` wrapper to use `{{
  inksink_venv_dir }}/bin/python3` instead of bare `python3`

## 4. Playbooks

- [x] 4.1 Add SPDX header to `playbooks/setup.yml`, `deploy.yml`, `verify.yml`
- [x] 4.2 Remove `become: true` from play level in all three playbooks
  (convention: per-task only)
- [x] 4.3 Fix `verify.yml`:
  - Add `{{ inksink_venv_dir }}/bin/python3 -c "from waveshare_epd import
    epd7in5_V2"` importability check
  - Change `{{ inksink_venv_dir }}/bin/python3 -c "import smbus2"` check to use
    venv python (currently uses bare `python3`)
  - Add fail2ban service state assertion
  - Fix `/var/lib/inksink/` check\_mode assertion to use mode `"0750"`
    (currently `"0755"`, inconsistent with `inksink-service` spec and task 3.2)
  - Add `rsync` and `fail2ban` to the package assertion loop (currently missing)

## 5. Documentation

- [x] 5.1 Create `ansible/roles/base/README.md` and
  `ansible/roles/inksink/README.md` with variable reference tables
- [x] 5.2 Update `docs/setup.md` Step 1 to make explicit that pasting the SSH
  public key in Imager's advanced options is the only key-delivery mechanism,
  and that this must happen before `setup.yml` runs (which disables password
  authentication)
- [x] 5.3 Update `README.md` Build Guide section to link to `docs/setup.md`
- [x] 5.4 Run pre-commit hooks (`pre-commit run --all-files`) and fix any issues
- [x] 5.5 `pyproject.toml` `[tool.pyright]`: add `exclude = ["vendor"]` so
  vendored Waveshare Python files are not type-checked
- [x] 5.6 `.cspell.yaml` `ignorePaths`: add `vendor/**/*.py` and
  `vendor/**/*.scad` so vendored source files are not spell-checked; `VENDOR.md`
  files remain checked by cspell, markdownlint, and mdformat
