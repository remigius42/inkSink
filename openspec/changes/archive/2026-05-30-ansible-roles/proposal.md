## Why

The `repo-scaffold` change creates the Ansible directory skeleton with stub
roles and empty playbooks. This change implements them fully — making it
possible to bootstrap a fresh Pi Zero 2W and deploy the inksink app with a
single playbook run.

## What Changes

- `roles/base` — full OS hardening + hardware driver installation: locale
  (de_CH/en_US, Europe/Zurich), SSH hardening, UFW, fail2ban, Waveshare e-ink
  driver, `wkhtmltopdf`, `fonts-noto-cjk`, `python3-rpi.gpio`
- `roles/inksink` — app synchronization, config template, shell wrapper, systemd
  service, data directory
- `ansible.cfg`, `inventory/hosts.yml`, `group_vars/` fully configured
- `playbooks/setup.yml`, `deploy.yml`, `verify.yml` fully implemented

## Capabilities

### New Capabilities

- `device-base`: OS hardening and hardware driver provisioning for the Pi
- `inksink-service`: app deployment, configuration, and systemd service
  management

### Modified Capabilities

## Impact

- Fills in all Ansible stubs from `repo-scaffold`
- Requires vault variables: `vault_ankiweb_username`, `vault_ankiweb_password`,
  `vault_wifi_password`
- `verify.yml` asserts post-state matching `core-infrastructure` and `anki-app`
  dependencies (packages, files, service running)
- Follows project Ansible conventions: SPDX headers, fully-qualified module
  names, `become: true`, fact caching, `cache_valid_time: 3600`
