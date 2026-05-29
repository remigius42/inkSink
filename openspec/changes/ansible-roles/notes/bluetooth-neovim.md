<!-- spellchecker:ignore bluez hotspot uart -->

# Bluetooth and Neovim

From the build guide. Neither is in scope for the current `ansible-roles`
change, but both affect optional package decisions in the `base` role.

## Bluetooth Features (Pi Zero 2W BT 4.2)

| Use case | Notes |
| -------- | ----- |
| Bluetooth keyboard pairing | Neovim editing + maintenance |
| File transfer | Update cards, sync data |
| Serial console | SSH-like access for debugging |
| Internet tethering | Sync via phone hotspot when no WiFi |

Normal use is standalone (buttons only). Bluetooth is for maintenance.

**Impact on `base` role:** `bluetooth` and `bluez` packages are present on
RPi OS Lite by default. No additional apt packages needed unless enabling
Bluetooth audio (not required here). Pairing is manual post-deploy.

## Neovim for Maintenance

Install: `sudo apt-get install neovim`

Use cases on device:

- Edit Python application code in `/opt/inksink/`
- Modify `/etc/inksink/config.json`
- View logs: `journalctl -u inksink`
- Manual card content editing (if needed)

Access methods:

- SSH over WiFi: `ssh pi@inksink.local`
- SSH over Bluetooth serial console
- UART serial (debugging)

RAM usage when active: ~10-20MB (acceptable given ~350MB free)

**Impact on `base` role:** Add `neovim` to the apt package list as an
optional package, controlled by a `base_install_neovim: true` default.
Allows skipping on minimal installs.
