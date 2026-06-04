## ADDED Requirements

### Requirement: `display_server` role generates a self-signed TLS certificate

The `display_server` Ansible role SHALL generate a self-signed certificate
and private key at `/etc/inksink/display_server/cert.pem` and
`/etc/inksink/display_server/key.pem` on the device, owned by the `pi` user.
Generation SHALL be idempotent: if the files already exist they SHALL NOT be
regenerated (to preserve client trust).

#### Scenario: Cert generated on first deploy

- **WHEN** `setup.yml` is run on a device with no existing cert files
- **THEN** `cert.pem` and `key.pem` are present at
  `/etc/inksink/display_server/` after the run

#### Scenario: Existing cert is not regenerated

- **WHEN** `setup.yml` is run on a device where `cert.pem` already exists
- **THEN** the existing `cert.pem` is unchanged after the run

### Requirement: `setup.yml` applies the `display_server` role

`playbooks/setup.yml` SHALL include the `display_server` role so that cert
generation runs as part of a standard device setup.

#### Scenario: Cert present after fresh setup

- **WHEN** `setup.yml` completes on a freshly flashed device
- **THEN** `/etc/inksink/display_server/cert.pem` exists on the device
