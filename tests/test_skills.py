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
        assert list_skills([skills_dir]) == []

    def test_non_existent_dir(self, tmp_path: Path):
        skills_dir = tmp_path / "nonexistent"
        assert list_skills([skills_dir]) == []

    def test_with_skills(self, tmp_skills_dir: Path):
        (tmp_skills_dir / "skill-a").mkdir()
        (tmp_skills_dir / "skill-b").mkdir()
        result = list_skills([tmp_skills_dir])
        assert len(result) == 2
        assert result[0].dir_name == "skill-a"
        assert result[1].dir_name == "skill-b"

    def test_ignores_files(self, tmp_skills_dir: Path):
        (tmp_skills_dir / "skill-a").mkdir()
        (tmp_skills_dir / "not-a-skill.txt").write_text("")
        result = list_skills([tmp_skills_dir])
        assert len(result) == 1
        assert result[0].dir_name == "skill-a"

    def test_multiple_dirs_dedup(self, tmp_path: Path):
        d1 = tmp_path / "dir1"
        d2 = tmp_path / "dir2"
        d1.mkdir()
        d2.mkdir()
        (d1 / "skill-a").mkdir()
        (d1 / "skill-b").mkdir()
        (d2 / "skill-b").mkdir()
        (d2 / "skill-c").mkdir()
        result = list_skills([d1, d2])
        names = [s.dir_name for s in result]
        assert names == ["skill-a", "skill-b", "skill-c"]

    def test_multiple_dirs_first_wins(self, tmp_path: Path):
        d1 = tmp_path / "dir1"
        d2 = tmp_path / "dir2"
        d1.mkdir()
        d2.mkdir()
        (d1 / "skill-a").mkdir()
        (d2 / "skill-a").mkdir()
        result = list_skills([d1, d2])
        assert len(result) == 1
        assert result[0].path.parent == d1


class TestLinkedSkills:
    def test_empty_dir(self, tmp_path: Path):
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        assert linked_skills([link_dir]) == []

    def test_non_existent_dir(self, tmp_path: Path):
        link_dir = tmp_path / "nonexistent"
        assert linked_skills([link_dir]) == []

    def test_with_links(self, tmp_path: Path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill-a").mkdir()
        (skills_dir / "skill-b").mkdir()
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        (link_dir / "skill-a").symlink_to(skills_dir / "skill-a")
        (link_dir / "skill-b").symlink_to(skills_dir / "skill-b")
        result = linked_skills([link_dir])
        assert len(result) == 2
        names = [s.dir_name for s in result]
        assert "skill-a" in names
        assert "skill-b" in names

    def test_multiple_dirs_dedup(self, tmp_path: Path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill-a").mkdir()
        link_dir1 = tmp_path / "links1"
        link_dir1.mkdir()
        link_dir2 = tmp_path / "links2"
        link_dir2.mkdir()
        (link_dir1 / "skill-a").symlink_to(skills_dir / "skill-a")
        (link_dir2 / "skill-a").symlink_to(skills_dir / "skill-a")
        result = linked_skills([link_dir1, link_dir2])
        assert len(result) == 1
        assert result[0].dir_name == "skill-a"

    def test_multiple_dirs_union(self, tmp_path: Path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill-a").mkdir()
        (skills_dir / "skill-b").mkdir()
        link_dir1 = tmp_path / "links1"
        link_dir1.mkdir()
        link_dir2 = tmp_path / "links2"
        link_dir2.mkdir()
        (link_dir1 / "skill-a").symlink_to(skills_dir / "skill-a")
        (link_dir2 / "skill-b").symlink_to(skills_dir / "skill-b")
        result = linked_skills([link_dir1, link_dir2])
        assert len(result) == 2
        names = [s.dir_name for s in result]
        assert "skill-a" in names
        assert "skill-b" in names


class TestEnableSkill:
    def test_simple_enable(self, tmp_skills_dir: Path, tmp_path: Path):
        skill_dir = tmp_skills_dir / "my-skill"
        skill_dir.mkdir()
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        result = enable_skill("my-skill", [tmp_skills_dir], [link_dir])
        assert result is True
        link_path = link_dir / "my-skill"
        assert link_path.is_symlink()
        assert link_path.resolve() == skill_dir.resolve()

    def test_creates_link_dir(self, tmp_skills_dir: Path, tmp_path: Path):
        (tmp_skills_dir / "my-skill").mkdir()
        link_dir = tmp_path / "links"
        result = enable_skill("my-skill", [tmp_skills_dir], [link_dir])
        assert result is True
        assert link_dir.exists()

    def test_skill_not_found(self, tmp_skills_dir: Path, tmp_path: Path):
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        with pytest.raises(FileNotFoundError):
            enable_skill("nonexistent", [tmp_skills_dir], [link_dir])

    def test_idempotent_no_force(self, tmp_skills_dir: Path, tmp_path: Path):
        (tmp_skills_dir / "my-skill").mkdir()
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        enable_skill("my-skill", [tmp_skills_dir], [link_dir])
        result = enable_skill("my-skill", [tmp_skills_dir], [link_dir])
        assert result is False

    def test_force_overwrite(self, tmp_skills_dir: Path, tmp_path: Path):
        (tmp_skills_dir / "my-skill").mkdir()
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        enable_skill("my-skill", [tmp_skills_dir], [link_dir])
        result = enable_skill("my-skill", [tmp_skills_dir], [link_dir], force=True)
        assert result is True

    def test_path_traversal(self, tmp_skills_dir: Path, tmp_path: Path):
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        with pytest.raises(ValueError, match="must not contain"):
            enable_skill("../evil", [tmp_skills_dir], [link_dir])

    def test_multiple_skills(self, tmp_skills_dir: Path, tmp_path: Path):
        (tmp_skills_dir / "skill-a").mkdir()
        (tmp_skills_dir / "skill-b").mkdir()
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        for name in ("skill-a", "skill-b"):
            result = enable_skill(name, [tmp_skills_dir], [link_dir])
            assert result is True
            assert (link_dir / name).is_symlink()

    def test_enable_from_second_dir(self, tmp_path: Path):
        d1 = tmp_path / "dir1"
        d2 = tmp_path / "dir2"
        d1.mkdir()
        d2.mkdir()
        (d2 / "my-skill").mkdir()
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        result = enable_skill("my-skill", [d1, d2], [link_dir])
        assert result is True
        link_path = link_dir / "my-skill"
        assert link_path.is_symlink()
        assert link_path.resolve() == (d2 / "my-skill").resolve()

    def test_multiple_link_dirs(self, tmp_skills_dir: Path, tmp_path: Path):
        (tmp_skills_dir / "my-skill").mkdir()
        link_dir1 = tmp_path / "links1"
        link_dir2 = tmp_path / "links2"
        result = enable_skill("my-skill", [tmp_skills_dir], [link_dir1, link_dir2])
        assert result is True
        assert link_dir1.exists()
        assert link_dir2.exists()
        assert (link_dir1 / "my-skill").is_symlink()
        assert (link_dir2 / "my-skill").is_symlink()

    def test_multiple_link_dirs_idempotent(self, tmp_skills_dir: Path, tmp_path: Path):
        """When link exists in both dirs, return False (no-op)."""
        (tmp_skills_dir / "my-skill").mkdir()
        link_dir1 = tmp_path / "links1"
        link_dir2 = tmp_path / "links2"
        enable_skill("my-skill", [tmp_skills_dir], [link_dir1, link_dir2])
        result = enable_skill("my-skill", [tmp_skills_dir], [link_dir1, link_dir2])
        assert result is False

    def test_multiple_link_dirs_partial_no_force(self, tmp_skills_dir: Path, tmp_path: Path):
        """When link exists in one dir but not the other, create in the other."""
        (tmp_skills_dir / "my-skill").mkdir()
        link_dir1 = tmp_path / "links1"
        link_dir2 = tmp_path / "links2"
        link_dir1.mkdir()
        (link_dir1 / "my-skill").symlink_to(tmp_skills_dir / "my-skill")
        result = enable_skill("my-skill", [tmp_skills_dir], [link_dir1, link_dir2])
        assert result is True
        assert (link_dir2 / "my-skill").is_symlink()


class TestDisableSkill:
    def test_simple_disable(self, tmp_path: Path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "my-skill").mkdir()
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        enable_skill("my-skill", [skills_dir], [link_dir])
        result = disable_skill("my-skill", [link_dir])
        assert result is True
        assert not (link_dir / "my-skill").exists()

    def test_idempotent(self, tmp_path: Path):
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        result = disable_skill("nonexistent", [link_dir])
        assert result is False

    def test_path_traversal(self, tmp_path: Path):
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        with pytest.raises(ValueError, match="must not contain"):
            disable_skill("../evil", [link_dir])

    def test_multiple_link_dirs(self, tmp_path: Path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "my-skill").mkdir()
        link_dir1 = tmp_path / "links1"
        link_dir2 = tmp_path / "links2"
        enable_skill("my-skill", [skills_dir], [link_dir1, link_dir2])
        result = disable_skill("my-skill", [link_dir1, link_dir2])
        assert result is True
        assert not (link_dir1 / "my-skill").exists()
        assert not (link_dir2 / "my-skill").exists()

    def test_multiple_link_dirs_partial(self, tmp_path: Path):
        """Disable from multiple dirs where one doesn't have the link."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "my-skill").mkdir()
        link_dir1 = tmp_path / "links1"
        link_dir2 = tmp_path / "links2"
        link_dir1.mkdir()
        (link_dir1 / "my-skill").symlink_to(skills_dir / "my-skill")
        result = disable_skill("my-skill", [link_dir1, link_dir2])
        assert result is True
        assert not (link_dir1 / "my-skill").exists()