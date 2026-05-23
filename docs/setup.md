<!-- spellchecker:ignore journalctl -->

# inksink Setup Guide

## Prerequisites

- A control machine with Ansible installed (`pip install ansible`)
- Ansible collections installed: `ansible-galaxy collection install -r ansible/collections/requirements.yml`
- A Raspberry Pi Zero 2 W with a MicroSD card
- SSH key pair (control machine key must be added to the Pi)

## 1. Flash the OS

Use **Raspberry Pi Imager** to flash Raspberry Pi OS Lite (64-bit) onto the MicroSD card.

In the Imager's "Advanced options" (gear icon), configure:

- **Hostname:** `inksink`
- **Enable SSH:** yes, with your public key
- **WiFi:** SSID (entered here manually) and password (`vault_wifi_password` in vault stores the password only)
- **Locale / timezone:** as appropriate

Insert the card into the Pi and power on. The device will be reachable at `inksink.local` once it connects to WiFi.

## 2. Set Up Ansible Vault

The secrets file `ansible/group_vars/all/vault.yml` is encrypted with Ansible Vault. To set it up:

```bash
# Copy the example and edit with your real values
cp ansible/group_vars/all/vault.yml.example /tmp/vault-plain.yml
# Edit /tmp/vault-plain.yml with your credentials
ansible-vault encrypt --output ansible/group_vars/all/vault.yml /tmp/vault-plain.yml
rm /tmp/vault-plain.yml
```

Store your vault password in `.vault-password` at the repo root (referenced by `ansible.cfg`, gitignored):

```bash
echo "your-vault-password" > .vault-password
chmod 600 .vault-password
```

## 3. Bootstrap the Device

From the repo root:

```bash
ansible-playbook ansible/playbooks/setup.yml
```

This runs the `base` role (packages, locale, SSH hardening, UFW) and the `inksink` role
(sync source, config, wrapper, systemd service).

## 4. Deploy Updates

After making code changes, sync and restart without re-running the full setup:

```bash
ansible-playbook ansible/playbooks/deploy.yml
```

Note: the device has no Git or pip. All updates go through `deploy.yml` (rsync + service restart).

## 5. Verify

From the repo root:

```bash
ansible-playbook ansible/playbooks/verify.yml
```

All assertions should pass: required packages installed, config file present, service running.

## Troubleshooting

- **SSH timeout:** confirm the Pi is on WiFi (`ping inksink.local`) and SSH key is authorized
- **Vault decryption error:** check `.vault-password` exists at the repo root and is correct
- **Service not starting:** check logs with `journalctl -u inksink -n 50` over SSH
