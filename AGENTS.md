# AGENTS.md

Target: Raspberry Pi OS Lite (Debian-based) on Raspberry Pi Zero 2 W.

## Hardware

- **Display:** Waveshare 7.5" E-Ink HAT V2+ (800×480) via SPI — `waveshare_epd.epd7in5_V2`
- **Power:** PiSugar 3 (battery + RTC) via I2C pogo pins
- **Input:** Tactile buttons on GPIO 4, 5, 6, 12, 13, 16, 19, 26

## Software stack

```text
Custom Python app (Anki client + UI)
HTML renderer (wkhtmltoimage) + Pillow
AnkiWeb API (HTTPS) / Waveshare lib / RPi.GPIO
Raspberry Pi OS Lite
```

## Python tooling

Python files are formatted with **Black** and linted with **Ruff**; type-checked with **Pyright**
(`standard` mode). All three run as pre-commit hooks — do not bypass them.

- Configuration lives in `pyproject.toml` (`[tool.black]`, `[tool.ruff]`, `[tool.pyright]`)
- `RPi.GPIO` is hardware-only and not installed on dev machines; `reportMissingModuleSource` is
  suppressed in the Pyright config
- Run tests via `pytest` from the repository root (activate `.venv` first — see `README.md`)
