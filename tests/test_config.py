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


def test_load_config_creates_default(tmp_path: Path):
    """load_config() deve criar config padrão se não existir."""
    config_path = tmp_path / "agisk-config.json"
    # Config não existe ainda
    old_env = os.environ.get("AGISK_CONFIG")
    try:
        os.environ["AGISK_CONFIG"] = str(config_path)
        config = load_config()
        assert config == {"skills_dir": "skills", "link_target_dir": ".agent/skills"}
        assert config_path.exists()
    finally:
        if old_env is None:
            del os.environ["AGISK_CONFIG"]
        else:
            os.environ["AGISK_CONFIG"] = old_env


def test_load_config_custom_file(tmp_path: Path):
    """load_config() com AGISK_CONFIG apontando para JSON customizado."""
    config_path = tmp_path / "custom-config.json"
    config_path.write_text(json.dumps({
        "skills_dir": "/tmp/my-skills",
        "link_target_dir": ".custom/skills",
    }))
    old_env = os.environ.get("AGISK_CONFIG")
    try:
        os.environ["AGISK_CONFIG"] = str(config_path)
        config = load_config()
        assert config["skills_dir"] == "/tmp/my-skills"
        assert config["link_target_dir"] == ".custom/skills"
    finally:
        if old_env is None:
            del os.environ["AGISK_CONFIG"]
        else:
            os.environ["AGISK_CONFIG"] = old_env


def test_load_config_file_not_found(tmp_path: Path):
    """load_config() com AGISK_CONFIG é criado se não existir, não erro."""
    config_path = tmp_path / "nonexistent" / "config.json"
    old_env = os.environ.get("AGISK_CONFIG")
    try:
        os.environ["AGISK_CONFIG"] = str(config_path)
        config = load_config()
        assert config == {"skills_dir": "skills", "link_target_dir": ".agent/skills"}
        assert config_path.exists()
    finally:
        if old_env is None:
            del os.environ["AGISK_CONFIG"]
        else:
            os.environ["AGISK_CONFIG"] = old_env


def test_get_base_dir_env(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("AGISK_BASE_DIR", str(tmp_path / "custom-base"))
    result = get_base_dir()
    assert result == (tmp_path / "custom-base").resolve()


def test_get_base_dir_default(monkeypatch):
    monkeypatch.delenv("AGISK_BASE_DIR", raising=False)
    result = get_base_dir()
    assert result == Path.home() / ".agisk"


def test_get_skills_dir_env_absolute(monkeypatch, tmp_path: Path):
    skills_path = tmp_path / "my-skills"
    monkeypatch.setenv("AGISK_SKILLS_DIR", str(skills_path))
    result = get_skills_dir()
    assert result == skills_path.resolve()


def test_get_skills_dir_env_relative(monkeypatch, tmp_path: Path):
    old_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        monkeypatch.setenv("AGISK_SKILLS_DIR", "my-skills")
        result = get_skills_dir()
        assert result == (tmp_path / "my-skills").resolve()
    finally:
        os.chdir(old_cwd)


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