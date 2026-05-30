<!-- spellchecker:ignore idempotently -->

# Hardware Driver Install Commands

Reference commands from the build guide. The Ansible roles replicate these
idempotently — don't just shell out to these directly.

## System packages (apt)

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
sudo apt-get install wkhtmltopdf    # includes wkhtmltoimage
sudo apt-get install fonts-noto-cjk
sudo apt-get install git
sudo apt-get install rsync          # required for ansible synchronize module
```

## Python libraries

```bash
# Legacy manual commands from the build guide — DO NOT replicate in Ansible.
# All app Python deps go into /opt/inksink-venv (see inksink role, task 3.8/3.9).
pip3 install pillow --break-system-packages
pip3 install requests --break-system-packages
pip3 install smbus2 --break-system-packages
```

Note: `RPi.GPIO` is NOT installed via pip — use `python3-rpi.gpio` via apt
(see System packages above). All other Python dependencies (`smbus2`, `Pillow`,
`requests`, etc.) are installed into `/opt/inksink-venv` by the `inksink` role
using `ansible.builtin.pip` with `virtualenv: /opt/inksink-venv` — NOT via
`--break-system-packages`. Do NOT install `python3-smbus` (provides the older
`smbus` API; `smbus2` is a superset and is what `core/state.py` uses).

## Waveshare e-Paper library

Vendored — no install step on the device. Files live in `vendor/waveshare_epd/`
in the repo; Ansible syncs them to `/opt/waveshare-vendor/waveshare_epd/`.
The systemd unit sets `PYTHONPATH=/opt/waveshare-vendor`.

Source files (copy at implementation time, update `VENDOR.md` with SHA):

```text
e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd7in5_V2.py
e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epdconfig.py
```

Verify:
`PYTHONPATH=/opt/waveshare-vendor python3 -c "from waveshare_epd import epd7in5_V2; print('ok')"`

## PiSugar 3

No daemon installation. Battery level and RTC are read directly over I2C
(`smbus2`, address 0x57). `smbus2` is installed into `/opt/inksink-venv` by
the `inksink` role — no apt package (`python3-smbus` provides the older
`smbus` API and is not used).
