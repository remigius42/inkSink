<!-- spellchecker:ignore virtualenv's -->

## ADDED Requirements

### Requirement: Source is synchronized to `/opt/inksink/`

The `inksink` role SHALL synchronize `src/inksink/` from the control machine
to `/opt/inksink/` on the device using `ansible.posix.synchronize`.
`__pycache__/` and `*.pyc` files SHALL be excluded. The `inksink` systemd
service SHALL be restarted after any file change via handler.

#### Scenario: Updated source is present after deploy

- **WHEN** `deploy.yml` is run after a local code change
- **THEN** the changed file appears at `/opt/inksink/` and the service
  has restarted

### Requirement: Config file is templated from vault

The `inksink` role SHALL template `/etc/inksink/config.yml` from vault
variables (`vault_ankiweb_username`, `vault_ankiweb_password`). The file
SHALL be owned by `pi:pi` with mode `0640`. The service SHALL be restarted
if the config changes.

#### Scenario: Config contains credentials after setup

- **WHEN** `setup.yml` completes
- **THEN** `/etc/inksink/config.yml` exists, is readable by `pi`, and
  contains the `apps.anki.ankiweb_username` key

### Requirement: Shell wrapper is installed at `/usr/local/bin/inksink`

The `inksink` role SHALL install a shell wrapper at `/usr/local/bin/inksink`
with mode `0755` that invokes the app virtualenv's Python interpreter
(`/opt/inksink-venv/bin/python3 -m inksink`) with
`PYTHONPATH=/opt/inksink:/opt/waveshare-vendor` so that both the rsync'd
source and the vendored Waveshare driver are importable.

#### Scenario: Wrapper is executable and correct

- **WHEN** `setup.yml` completes
- **THEN** `/usr/local/bin/inksink` exists, is executable, and its content
  references `/opt/inksink-venv/bin/python3 -m inksink`

### Requirement: `inksink.service` runs as `pi` and starts on boot

The `inksink` role SHALL install a systemd unit file for `inksink.service`
with `User=pi`, `ExecStart=/usr/local/bin/inksink`, `Restart=on-failure`,
and `WantedBy=multi-user.target`. The service SHALL be enabled and started.

#### Scenario: Service is running and enabled after setup

- **WHEN** `verify.yml` runs after `setup.yml`
- **THEN** `inksink.service` is `active` and `enabled`

#### Scenario: Service runs as `pi`

- **WHEN** the service unit file is inspected
- **THEN** `User=pi` is present in the `[Service]` section

### Requirement: `INKSINK_VERSION` is set in the systemd unit

The `inksink` role SHALL set `Environment=INKSINK_VERSION=<tag>` in the
`[Service]` section of `inksink.service`, populated at deploy time via
`lookup('pipe', 'git describe --tags --always')` in the Jinja2 template.
This value is read by `core/state.py` and displayed on the Status Screen.

#### Scenario: Version is present in service unit after deploy

- **WHEN** `setup.yml` or `deploy.yml` completes
- **THEN** the `inksink.service` unit contains `Environment=INKSINK_VERSION=`
  followed by a non-empty tag string

### Requirement: Data directory exists with correct ownership

The `inksink` role SHALL create `/var/lib/inksink/` owned by `pi:pi` with
mode `0750`. This directory holds the Anki collection and offline queue.

#### Scenario: Data directory exists after setup

- **WHEN** `verify.yml` runs after `setup.yml`
- **THEN** `/var/lib/inksink/` exists, is a directory, and is owned by `pi`
