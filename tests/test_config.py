from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from agisk.config import (
    load_config,
    get_config_path,
    get_skills_dirs,
    get_link_target_dir,
)


def test_load_config_creates_default(monkeypatch, tmp_path: Path):
    """load_config() should create a default config if it does not exist."""
    config_path = tmp_path / "config.json"
    monkeypatch.setenv("AGISK_CONFIG_FILE", str(config_path))
    config = load_config()
    assert config == {"skills_dirs": ["skills"], "link_target_dir": ".agents/skills"}
    assert config_path.exists()
    assert config_path.read_text().strip().endswith("}")


def test_load_config_reads_existing(monkeypatch, tmp_path: Path):
    """load_config() should read existing config file."""
    config_path = tmp_path / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps({"skills_dirs": ["custom"], "link_target_dir": ".custom/skills"})
    )
    monkeypatch.setenv("AGISK_CONFIG_FILE", str(config_path))
    config = load_config()
    assert config == {"skills_dirs": ["custom"], "link_target_dir": ".custom/skills"}


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


def test_get_skills_dirs_from_config_list(tmp_path: Path):
    config_path = tmp_path / ".agisk" / "config.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        '{"skills_dirs": ["my-skills"], "link_target_dir": ".agents/skills"}'
    )
    config = {"skills_dirs": ["my-skills"], "link_target_dir": ".agents/skills"}
    result = get_skills_dirs(config, config_path)
    assert result == [(config_path.parent / "my-skills").resolve()]


def test_get_skills_dirs_multiple(tmp_path: Path):
    config_path = tmp_path / ".agisk" / "config.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        '{"skills_dirs": ["a-skills", "b-skills"], "link_target_dir": ".agents/skills"}'
    )
    base = config_path.parent.resolve()
    config = {"skills_dirs": ["a-skills", "b-skills"], "link_target_dir": ".agents/skills"}
    result = get_skills_dirs(config, config_path)
    assert result == [base / "a-skills", base / "b-skills"]


def test_get_skills_dirs_absolute_in_config(tmp_path: Path):
    config_path = tmp_path / ".agisk" / "config.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        json.dumps({"skills_dirs": [str(tmp_path / "absolute-skills")], "link_target_dir": ".agents/skills"})
    )
    abs_skills = tmp_path / "absolute-skills"
    config = {"skills_dirs": [str(abs_skills)], "link_target_dir": ".agents/skills"}
    result = get_skills_dirs(config, config_path)
    assert result == [abs_skills.resolve()]


def test_get_skills_dirs_fallback_to_old_skills_dir(tmp_path: Path):
    """Old skills_dir (string) should be converted to a single-element list with warning."""
    config_path = tmp_path / ".agisk" / "config.json"
    config_path.parent.mkdir(parents=True)
    config = {"skills_dir": "my-skills", "link_target_dir": ".agents/skills"}
    import io
    import sys
    captured = io.StringIO()
    sys.stderr = captured
    try:
        result = get_skills_dirs(config, config_path)
    finally:
        sys.stderr = sys.__stderr__
    assert result == [(config_path.parent / "my-skills").resolve()]
    assert "deprecated" in captured.getvalue()
    assert "⚠️" in captured.getvalue()


def test_get_skills_dirs_default(tmp_path: Path):
    """When neither skills_dirs nor skills_dir is in config, fallback to ['skills']."""
    base = tmp_path / "custom"
    base.mkdir(parents=True)
    config_path = base / "config.json"
    config_path.write_text('{"link_target_dir": ".agents/skills"}')
    config = {"link_target_dir": ".agents/skills"}
    result = get_skills_dirs(config, config_path)
    assert result == [base / "skills"]


def test_get_link_target_dir_default():
    config = {}
    expected = Path.cwd() / ".agents" / "skills"
    assert get_link_target_dir(config) == expected.resolve()


def test_get_link_target_dir_custom():
    config = {"link_target_dir": ".my-custom/skills"}
    expected = Path.cwd() / ".my-custom" / "skills"
    assert get_link_target_dir(config) == expected.resolve()


