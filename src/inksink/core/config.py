"""Settings persistence for /etc/inksink/config.yml.

DEFAULTS defines the full config structure. load_settings() deep-merges
a YAML file over DEFAULTS so missing keys always fall back to defaults.
save_settings() writes only the provided dict — DEFAULTS are not persisted.
"""

import copy

import yaml

DEFAULTS: dict = {
    "display": {
        "idle_timeout": 180,
        "portrait_rotation": 90,
        "landscape_rotation": 0,
        "full_refresh_interval": 20,
        "status_refresh_interval": 20,
        "vertical_scroll_step": 50,
    },
    "renderer": {"cache_max_size": 100, "max_image_height": 8000},
    "apps": {
        "anki": {
            "display_mode": "1bit",
            "full_refresh_interval": 20,
            "orientation": "portrait",
            "ankiweb_username": "",
            "ankiweb_password": "",
            "display": {"double_vertical_button_size": False},
        },
        "launcher": {
            "orientation": "portrait",
            "display": {"double_vertical_button_size": False},
        },
    },
}

_CONFIG_PATH = "/etc/inksink/config.yml"


def _deep_merge(base: dict, override: dict) -> dict:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_settings(path: str = _CONFIG_PATH) -> dict:
    """Load config from path, deep-merging over DEFAULTS.

    Returns a copy of DEFAULTS if the file is absent.
    """
    try:
        with open(path, encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
        if not isinstance(loaded, dict):
            raise ValueError(
                f"{path}: expected a YAML mapping, got {type(loaded).__name__}"
            )
        return _deep_merge(DEFAULTS, loaded)
    except FileNotFoundError:
        return copy.deepcopy(DEFAULTS)


def save_settings(settings: dict, path: str = _CONFIG_PATH) -> None:
    """Write settings dict to path as YAML. DEFAULTS are not written."""
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(settings, f, default_flow_style=False)
