## MODIFIED Requirements

### Requirement: `setup.yml` bootstraps a fresh device

Running `ansible-playbook playbooks/setup.yml` on a freshly flashed Pi SHALL
apply all roles (`base`, `inksink`) and leave the device in a fully
operational state. The `base` role SHALL install `fonts-dejavu-core` as part
of the base package set.

#### Scenario: Idempotent re-run

- **WHEN** `setup.yml` is run a second time on an already-configured device
- **THEN** it completes with no failures and reports no unexpected changes

#### Scenario: DejaVu fonts available after setup

- **WHEN** `setup.yml` completes on a fresh device
- **THEN** `DejaVuSansMono.ttf` is available on the device (provided by
  `fonts-dejavu-core`)
