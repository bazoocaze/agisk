from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from agisk.config import (
    load_config,
    get_base_dir,
    get_skills_dir,
    get_link_target_dir,
    _default_base_dir,
)


def test_default_base_dir():
    assert _default_base_dir() == Path.home() / ".agisk"


def test_load_config_creates_default(monkeypatch, tmp_path: Path):
    """load_config() should create a default config in base_dir if it does not exist."""
    monkeypatch.setenv("AGISK_BASE_DIR", str(tmp_path))
    config = load_config()
    assert config == {"skills_dir": "skills", "link_target_dir": ".agent/skills"}
    config_path = tmp_path / "config.json"
    assert config_path.exists()
    assert config_path.read_text().strip().endswith('}')


def test_get_base_dir_env(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("AGISK_BASE_DIR", str(tmp_path / "custom-base"))
    result = get_base_dir()
    assert result == (tmp_path / "custom-base").resolve()


def test_get_base_dir_default(monkeypatch):
    monkeypatch.delenv("AGISK_BASE_DIR", raising=False)
    result = get_base_dir()
    assert result == Path.home() / ".agisk"


def test_get_skills_dir_from_config(tmp_path: Path):
    base_dir = tmp_path / ".agisk"
    base_dir.mkdir(parents=True)
    config = {"skills_dir": "my-skills", "link_target_dir": ".agent/skills"}
    result = get_skills_dir(base_dir, config)
    assert result == (base_dir / "my-skills").resolve()


def test_get_skills_dir_absolute_in_config(tmp_path: Path):
    base_dir = tmp_path / ".agisk"
    base_dir.mkdir(parents=True)
    abs_skills = tmp_path / "absolute-skills"
    config = {"skills_dir": str(abs_skills), "link_target_dir": ".agent/skills"}
    result = get_skills_dir(base_dir, config)
    assert result == abs_skills.resolve()


def test_get_link_target_dir_default():
    config = {}
    expected = Path.cwd() / ".agent" / "skills"
    assert get_link_target_dir(config) == expected.resolve()


def test_get_link_target_dir_custom():
    config = {"link_target_dir": ".my-custom/skills"}
    expected = Path.cwd() / ".my-custom" / "skills"
    assert get_link_target_dir(config) == expected.resolve()
