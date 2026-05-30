<!-- spellchecker:ignore timedatectl -->

## Purpose

Define the OS hardening and hardware driver provisioning applied to the
Raspberry Pi Zero 2W by the `base` Ansible role, including locale, timezone,
SSH configuration, firewall, fail2ban, system packages, and the Waveshare
e-ink display driver.

## Requirements

### Requirement: Locale and timezone are configured

The `base` role SHALL configure locale `de_CH.UTF-8` and `en_US.UTF-8` and
set timezone to `Europe/Zurich`.

#### Scenario: Locale is set after base role runs

- **WHEN** `setup.yml` completes on a fresh Pi
- **THEN** `locale -a` includes `de_CH.utf8` and `en_US.utf8`, and
  `timedatectl show --property=Timezone --value` returns `Europe/Zurich`

### Requirement: SSH is hardened

The `base` role SHALL configure SSH with `PermitRootLogin no`,
`PubkeyAuthentication yes`, and `PasswordAuthentication no`.

#### Scenario: SSH hardening is applied

- **WHEN** `setup.yml` completes
- **THEN** `/etc/ssh/sshd_config` contains all three directives and
  the SSH service is running

### Requirement: UFW firewall is active

The `base` role SHALL enable UFW and allow SSH from any source. All other
inbound traffic SHALL be denied by default. fail2ban provides brute-force
protection in lieu of network-level restriction (device moves between
networks).

#### Scenario: UFW is active after base role

- **WHEN** `setup.yml` completes
- **THEN** `ufw status` reports `active` and SSH (port 22) is allowed
  from any source

### Requirement: fail2ban is installed and protects SSH

The `base` role SHALL install fail2ban with an SSH jail enabled.

#### Scenario: fail2ban SSH jail is active

- **WHEN** `setup.yml` completes
- **THEN** `fail2ban-client status sshd` reports the jail as active

### Requirement: Hardware packages are installed

The `base` role SHALL install `wkhtmltopdf` (which provides the
`wkhtmltoimage` binary), `fonts-noto-cjk`, `python3-rpi.gpio`, and `rsync`
via `apt`. `git` SHALL NOT be installed on the device (ADR 0001: no git
required on device). `python3-smbus` SHALL NOT be installed — `smbus2` is
installed into the app's virtualenv in the `inksink` role.

#### Scenario: All hardware packages are present

- **WHEN** `verify.yml` runs after `setup.yml`
- **THEN** `wkhtmltopdf`, `fonts-noto-cjk`, `python3-rpi.gpio`,
  and `rsync` appear in `ansible_facts.packages`, and
  `python3 -c "import smbus2"` succeeds using the app virtualenv

### Requirement: Waveshare e-ink driver is installed

The `base` role SHALL synchronize `vendor/waveshare_epd/` from the control
machine to `/opt/waveshare-vendor/waveshare_epd/` using
`ansible.posix.synchronize`. No pip install or build step is required — the
shell wrapper sets `PYTHONPATH` to include `/opt/waveshare-vendor`.

#### Scenario: Driver is importable after deploy

- **WHEN** `setup.yml` completes
- **THEN** `PYTHONPATH=/opt/waveshare-vendor /opt/inksink-venv/bin/python3 -c "from waveshare_epd
  import epd7in5_V2"` succeeds on the device
