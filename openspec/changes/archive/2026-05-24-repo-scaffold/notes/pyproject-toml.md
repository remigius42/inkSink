<!-- spellchecker:ignore switzerlandeu -->

# pyproject.toml — Current State and What to Add

**Build guide references:**

- BOM table → [`docs/anki-eink-device-build-guide.md#core-electronics`](../../../docs/anki-eink-device-build-guide.md)
- Where to buy (CH/EU) → [`docs/anki-eink-device-build-guide.md#where-to-buy-switzerlandeu`](../../../docs/anki-eink-device-build-guide.md)

## Current state (tooling only, no `[project]` section)

```toml
[tool.black]
line-length = 88
target-version = ["py313"]

[tool.ruff]
line-length = 88
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "W", "I"]  # pycodestyle, pyflakes, isort

[tool.pyright]
pythonVersion = "3.13"
typeCheckingMode = "standard"
# RPi.GPIO is hardware-only and not installed on dev machines
reportMissingModuleSource = "none"
```

## `[project]` section to add (task 1.1)

```toml
[project]
name = "inksink"
version = "0.1.0"
requires-python = ">=3.13"  # RPi OS Trixie ships Python 3.13
dependencies = [
    "Pillow",
    "requests",
    "smbus2",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-mock",
]

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
```

## Notes

- `RPi.GPIO` and `anki` are **not** in `dependencies` — they are device-only,
  not installable on dev machines without extra work. Install via apt
  (`python3-rpi.gpio`) or pip on the device only.
- `requires-python = ">=3.13"` matches RPi OS Trixie and the tooling targets.
- `[tool.setuptools.packages.find]` with `where = ["src"]` is required for
  the src layout to work with `pip install -e .`.
