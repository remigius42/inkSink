# inksink

App synchronization, Python virtualenv, config, shell wrapper, and systemd
service for the inksink application.

## Description

Syncs the inksink source to `/opt/inksink/`, creates a Python virtualenv at
`/opt/inksink-venv/`, installs all Python dependencies, templates the config
and systemd unit, and ensures the service is running and enabled.

## Requirements

- The `base` role must have run first (packages, Waveshare driver, UFW)
- Collections:
  - `ansible.posix` (synchronize)

## Role Variables

| Variable | Default | Description |
| -- | -- | -- |
| `inksink_src_dir` | `{{ playbook_dir }}/../../src/inksink` | Source directory to rsync from the controller |
| `inksink_dest_dir` | `/opt/inksink` | App destination on device |
| `inksink_vendor_dir` | `/opt/waveshare-vendor` | Waveshare driver path (managed by `base`) |
| `inksink_venv_dir` | `/opt/inksink-venv` | Python virtualenv path |
| `inksink_config_dir` | `/etc/inksink` | Config directory |
| `inksink_wrapper` | `/usr/local/bin/inksink` | Shell wrapper path |
| `inksink_service` | `inksink` | systemd service name |
| `inksink_version` | `""` | Version string injected as `INKSINK_VERSION` in the systemd unit; falls back to `git describe --tags --always` when empty |

Vault variables required (set in `group_vars/all/vault.yml`):

| Variable | Description |
| -- | -- |
| `vault_ankiweb_username` | AnkiWeb account email |
| `vault_ankiweb_password` | AnkiWeb account password |

## Dependencies

Depends on the `base` role.

## Example Playbook

```yaml
- hosts: all
  roles:
    - base
    - inksink
```

## License

MIT

## Author Information

Created by Andreas Remigius Schmidt.
