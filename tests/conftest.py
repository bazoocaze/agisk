from __future__ import annotations

import json
import os
from pathlib import Path

import pytest


@pytest.fixture
def tmp_base_dir(tmp_path: Path) -> Path:
    """Creates a temporary base directory."""
    base = tmp_path / ".agisk"
    base.mkdir(parents=True)
    return base


@pytest.fixture
def tmp_skills_dir(tmp_base_dir: Path) -> Path:
    """Creates a temporary skills directory inside base_dir."""
    skills = tmp_base_dir / "skills"
    skills.mkdir(parents=True)
    return skills


@pytest.fixture
def tmp_config(tmp_base_dir: Path) -> Path:
    """Creates a default config.json in base_dir."""
    cfg = tmp_base_dir / "config.json"
    cfg.write_text(json.dumps({
        "skills_dir": "skills",
        "link_target_dir": ".agents/skills",
    }) + "\n")
    return cfg


@pytest.fixture
def cwd_with_agent(tmp_path: Path) -> Path:
    """Creates a project directory with .agents/skills."""
    project = tmp_path / "my-project"
    project.mkdir(parents=True)
    agent_skills = project / ".agents" / "skills"
    agent_skills.mkdir(parents=True)
    return project


@pytest.fixture
def sample_skill_dir(tmp_path: Path) -> Path:
    """Creates a sample skill directory with SKILL.md."""
    skill = tmp_path / "my-skill"
    skill.mkdir(parents=True)
    skill_md = skill / "SKILL.md"
    skill_md.write_text("---\nname: my-skill\n---\n# My Skill\n")
    return skill


@pytest.fixture
def sample_skill_md(tmp_path: Path) -> Path:
    """Creates a standalone SKILL.md file."""
    path = tmp_path / "SKILL.md"
    path.write_text("---\nname: my-file-skill\n---\n# My File Skill\n")
    return path


@pytest.fixture
def sample_skill_md_no_name(tmp_path: Path) -> Path:
    """Creates a SKILL.md without a name field."""
    path = tmp_path / "SKILL.md"
    path.write_text("---\ndescription: sem nome\n---\n# No Name\n")
    return path
