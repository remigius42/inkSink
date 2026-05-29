# base

OS hardening and hardware driver provisioning for the inksink Pi device.

## Description

Brings a freshly flashed Raspberry Pi Zero 2W to a usable state: locale,
timezone, SSH hardening, UFW firewall, fail2ban, hardware packages, and the
vendored Waveshare e-ink driver. The device is non-functional without this role.

## Requirements

- Raspberry Pi OS Lite (Trixie, 64-bit)
- SSH access and WiFi already configured via Raspberry Pi Imager
- Collections:
  - `community.general` (locale_gen, timezone, ufw)
  - `ansible.posix` (synchronize)

Install collections:

```bash
ansible-galaxy collection install -r ansible/collections/requirements.yml
```

## Role Variables

| Variable | Default | Description |
| -- | -- | -- |
| `base_locale_timezone` | `"Europe/Zurich"` | Timezone passed to `community.general.timezone` |
| `base_install_neovim` | `true` | Install `neovim` for on-device editing |
| `base_fail2ban_bantime` | `"1h"` | fail2ban SSH jail ban duration |
| `base_fail2ban_findtime` | `"10m"` | fail2ban SSH jail detection window |
| `base_fail2ban_maxretry` | `5` | fail2ban SSH jail max failed attempts before ban |

## Dependencies

None. Collections declared in `meta/main.yml`.

## Example Playbook

```yaml
- hosts: all
  roles:
    - base
```

## License

MIT

## Author Information

Created by Andreas Remigius Schmidt.
