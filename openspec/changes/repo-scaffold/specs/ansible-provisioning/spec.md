## ADDED Requirements

### Requirement: `setup.yml` bootstraps a fresh device

Running `ansible-playbook playbooks/setup.yml` on a freshly flashed Pi SHALL
apply all roles (`base`, `inksink`) and leave the device in a fully
operational state.

#### Scenario: Idempotent re-run

- **WHEN** `setup.yml` is run a second time on an already-configured device
- **THEN** it completes with no failures and reports no unexpected changes

### Requirement: `deploy.yml` updates the application

Running `ansible-playbook playbooks/deploy.yml` SHALL synchronize
`src/inksink/` to `/opt/inksink/` on the device and restart the `inksink`
systemd service.

#### Scenario: Application is updated

- **WHEN** `deploy.yml` is run after a local code change
- **THEN** the updated files are present on the device and the service
  is running the new version

### Requirement: `verify.yml` asserts post-deployment state

Running `ansible-playbook playbooks/verify.yml` SHALL assert that all
expected packages are installed, configuration files exist, and the
`inksink` systemd service is running and enabled.

#### Scenario: Verification passes after setup

- **WHEN** `verify.yml` is run on a device that has completed `setup.yml`
- **THEN** all assertions pass with no failures

### Requirement: Secrets are managed via Ansible Vault

The repository SHALL store AnkiWeb credentials (`vault_ankiweb_username`,
`vault_ankiweb_password`) and WiFi password (`vault_wifi_password`) in
`group_vars/all/vault.yml`, encrypted with Ansible Vault. A
`vault.yml.example` with placeholder values SHALL be committed.

#### Scenario: Playbook fails without vault

- **WHEN** `setup.yml` is run without a `.vault_pass` file
- **THEN** Ansible refuses to run and reports a vault decryption error

### Requirement: Application runs as the `pi` user

The `inksink` systemd service and all deployed files SHALL be owned by and
run as the `pi` user.

#### Scenario: Service user is `pi`

- **WHEN** the `inksink.service` unit file is inspected on the device
- **THEN** `User=pi` is present in the `[Service]` section
