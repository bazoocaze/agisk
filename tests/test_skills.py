from __future__ import annotations

from pathlib import Path

import pytest

from agisk.skills import (
    enable_skill,
    disable_skill,
    list_skills,
    linked_skills,
)


class TestListSkills:
    def test_empty_dir(self, tmp_path: Path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        assert list_skills(skills_dir) == []

    def test_non_existent_dir(self, tmp_path: Path):
        skills_dir = tmp_path / "nonexistent"
        assert list_skills(skills_dir) == []

    def test_with_skills(self, tmp_skills_dir: Path):
        (tmp_skills_dir / "skill-a").mkdir()
        (tmp_skills_dir / "skill-b").mkdir()
        result = list_skills(tmp_skills_dir)
        assert len(result) == 2
        assert result[0].name == "skill-a"
        assert result[1].name == "skill-b"

    def test_ignores_files(self, tmp_skills_dir: Path):
        (tmp_skills_dir / "skill-a").mkdir()
        (tmp_skills_dir / "not-a-skill.txt").write_text("")
        result = list_skills(tmp_skills_dir)
        assert len(result) == 1
        assert result[0].name == "skill-a"


class TestLinkedSkills:
    def test_empty_dir(self, tmp_path: Path):
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        assert linked_skills(link_dir) == []

    def test_non_existent_dir(self, tmp_path: Path):
        link_dir = tmp_path / "nonexistent"
        assert linked_skills(link_dir) == []

    def test_with_links(self, tmp_path: Path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill-a").mkdir()
        (skills_dir / "skill-b").mkdir()
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        (link_dir / "skill-a").symlink_to(skills_dir / "skill-a")
        (link_dir / "skill-b").symlink_to(skills_dir / "skill-b")
        result = linked_skills(link_dir)
        assert len(result) == 2
        names = [r.name for r in result]
        assert "skill-a" in names
        assert "skill-b" in names


class TestEnableSkill:
    def test_simple_enable(self, tmp_skills_dir: Path, tmp_path: Path):
        skill_dir = tmp_skills_dir / "my-skill"
        skill_dir.mkdir()
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        result = enable_skill("my-skill", tmp_skills_dir, link_dir)
        assert result is True
        link_path = link_dir / "my-skill"
        assert link_path.is_symlink()
        assert link_path.resolve() == skill_dir.resolve()

    def test_creates_link_dir(self, tmp_skills_dir: Path, tmp_path: Path):
        (tmp_skills_dir / "my-skill").mkdir()
        link_dir = tmp_path / "links"
        # link_dir não existe ainda
        result = enable_skill("my-skill", tmp_skills_dir, link_dir)
        assert result is True
        assert link_dir.exists()

    def test_skill_not_found(self, tmp_skills_dir: Path, tmp_path: Path):
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        with pytest.raises(FileNotFoundError):
            enable_skill("nonexistent", tmp_skills_dir, link_dir)

    def test_idempotent_no_force(self, tmp_skills_dir: Path, tmp_path: Path):
        (tmp_skills_dir / "my-skill").mkdir()
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        enable_skill("my-skill", tmp_skills_dir, link_dir)
        # Segunda vez sem --force retorna False
        result = enable_skill("my-skill", tmp_skills_dir, link_dir)
        assert result is False

    def test_force_overwrite(self, tmp_skills_dir: Path, tmp_path: Path):
        (tmp_skills_dir / "my-skill").mkdir()
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        enable_skill("my-skill", tmp_skills_dir, link_dir)
        result = enable_skill("my-skill", tmp_skills_dir, link_dir, force=True)
        assert result is True

    def test_path_traversal(self, tmp_skills_dir: Path, tmp_path: Path):
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        with pytest.raises(ValueError, match="path traversal"):
            enable_skill("../evil", tmp_skills_dir, link_dir)

    def test_multiple_skills(self, tmp_skills_dir: Path, tmp_path: Path):
        (tmp_skills_dir / "skill-a").mkdir()
        (tmp_skills_dir / "skill-b").mkdir()
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        for name in ("skill-a", "skill-b"):
            result = enable_skill(name, tmp_skills_dir, link_dir)
            assert result is True
            assert (link_dir / name).is_symlink()


class TestDisableSkill:
    def test_simple_disable(self, tmp_path: Path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "my-skill").mkdir()
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        enable_skill("my-skill", skills_dir, link_dir)
        result = disable_skill("my-skill", link_dir)
        assert result is True
        assert not (link_dir / "my-skill").exists()

    def test_idempotent(self, tmp_path: Path):
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        result = disable_skill("nonexistent", link_dir)
        assert result is False

    def test_path_traversal(self, tmp_path: Path):
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        with pytest.raises(ValueError, match="path traversal"):
            disable_skill("../evil", link_dir)