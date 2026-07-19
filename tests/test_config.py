from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from agisk.config import (
    load_config,
    get_config_path,
    get_skills_dir,
    get_link_target_dir,
)


def test_load_config_creates_default(monkeypatch, tmp_path: Path):
    """load_config() should create a default config if it does not exist."""
    config_path = tmp_path / "config.json"
    monkeypatch.setenv("AGISK_CONFIG_FILE", str(config_path))
    config = load_config()
    assert config == {"skills_dir": "skills", "link_target_dir": ".agent/skills"}
    assert config_path.exists()
    assert config_path.read_text().strip().endswith("}")


def test_load_config_reads_existing(monkeypatch, tmp_path: Path):
    """load_config() should read existing config file."""
    config_path = tmp_path / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps({"skills_dir": "custom", "link_target_dir": ".custom/skills"})
    )
    monkeypatch.setenv("AGISK_CONFIG_FILE", str(config_path))
    config = load_config()
    assert config == {"skills_dir": "custom", "link_target_dir": ".custom/skills"}


def test_get_config_path_explicit(tmp_path: Path):
    """get_config_path with explicit path should return that path."""
    config_path = tmp_path / "custom" / "config.json"
    result = get_config_path(config_path)
    assert result == config_path.resolve()
    assert result.exists()


def test_get_config_path_env(monkeypatch, tmp_path: Path):
    """get_config_path should use AGISK_CONFIG_FILE env var."""
    config_path = tmp_path / "env-config.json"
    monkeypatch.setenv("AGISK_CONFIG_FILE", str(config_path))
    result = get_config_path()
    assert result == config_path.resolve()
    assert result.exists()


def test_get_config_path_default(monkeypatch):
    """get_config_path should fallback to ~/.agisk/config.json."""
    monkeypatch.delenv("AGISK_CONFIG_FILE", raising=False)
    result = get_config_path()
    assert result == (Path.home() / ".agisk" / "config.json").resolve()
    assert result.exists()


def test_get_config_path_precedence(monkeypatch, tmp_path: Path):
    """Explicit path should take precedence over env var."""
    explicit_path = tmp_path / "explicit.json"
    env_path = tmp_path / "env.json"
    monkeypatch.setenv("AGISK_CONFIG_FILE", str(env_path))
    result = get_config_path(explicit_path)
    assert result == explicit_path.resolve()
    assert result.exists()
    assert not env_path.exists()


def test_get_skills_dir_from_config(tmp_path: Path):
    config_path = tmp_path / ".agisk" / "config.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text('{"skills_dir": "my-skills", "link_target_dir": ".agent/skills"}')
    config = {"skills_dir": "my-skills", "link_target_dir": ".agent/skills"}
    result = get_skills_dir(config, config_path)
    assert result == (config_path.parent / "my-skills").resolve()


def test_get_skills_dir_absolute_in_config(tmp_path: Path):
    config_path = tmp_path / ".agisk" / "config.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        json.dumps({"skills_dir": str(tmp_path / "absolute-skills"), "link_target_dir": ".agent/skills"})
    )
    abs_skills = tmp_path / "absolute-skills"
    config = {"skills_dir": str(abs_skills), "link_target_dir": ".agent/skills"}
    result = get_skills_dir(config, config_path)
    assert result == abs_skills.resolve()


def test_get_link_target_dir_default():
    config = {}
    expected = Path.cwd() / ".agent" / "skills"
    assert get_link_target_dir(config) == expected.resolve()


def test_get_link_target_dir_custom():
    config = {"link_target_dir": ".my-custom/skills"}
    expected = Path.cwd() / ".my-custom" / "skills"
    assert get_link_target_dir(config) == expected.resolve()


def test_get_skills_dir_default_skills(tmp_path: Path):
    """When skills_dir is not in config, fallback to 'skills' relative to config parent."""
    base = tmp_path / "custom"
    base.mkdir(parents=True)
    config_path = base / "config.json"
    config_path.write_text('{"link_target_dir": ".agent/skills"}')
    config = {"link_target_dir": ".agent/skills"}
    result = get_skills_dir(config, config_path)
    assert result == (base / "skills").resolve()