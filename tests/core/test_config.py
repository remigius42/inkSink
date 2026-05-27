import pytest

from inksink.core.config import DEFAULTS, load_settings, save_settings


def test_missing_file_returns_defaults():
    result = load_settings(path="/nonexistent/path/config.yml")
    assert result == DEFAULTS


def test_round_trip_saves_and_restores(tmp_path):
    path = str(tmp_path / "config.yml")
    save_settings({"apps": {"anki": {"full_refresh_interval": 15}}}, path=path)
    result = load_settings(path=path)
    assert result["apps"]["anki"]["full_refresh_interval"] == 15
    assert result["apps"]["anki"]["display_mode"] == "1bit"  # default filled in
    assert result["display"]["idle_timeout"] == 180  # default filled in


def test_non_dict_yaml_raises(tmp_path):
    path = str(tmp_path / "config.yml")
    (tmp_path / "config.yml").write_text("- item1\n- item2\n")
    with pytest.raises(ValueError, match=r"config\.yml"):
        load_settings(path=path)


def test_scalar_yaml_raises(tmp_path):
    path = str(tmp_path / "config.yml")
    (tmp_path / "config.yml").write_text("just a string\n")
    with pytest.raises(ValueError, match=r"config\.yml"):
        load_settings(path=path)


def test_empty_file_raises(tmp_path):
    path = str(tmp_path / "config.yml")
    (tmp_path / "config.yml").write_text("")
    with pytest.raises(ValueError, match=r"config\.yml"):
        load_settings(path=path)


def test_save_uses_safe_dump(tmp_path):
    path = str(tmp_path / "config.yml")
    save_settings({"key": "value"}, path=path)
    content = (tmp_path / "config.yml").read_text()
    assert "!!" not in content  # no Python-specific YAML tags


def test_defaults_include_rotation_config():
    result = load_settings(path="/nonexistent/path/config.yml")
    assert result["display"]["portrait_rotation"] == 90
    assert result["display"]["landscape_rotation"] == 0


def test_defaults_include_launcher_orientation():
    result = load_settings(path="/nonexistent/path/config.yml")
    assert result["apps"]["launcher"]["orientation"] == "portrait"
