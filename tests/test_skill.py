from __future__ import annotations

from pathlib import Path

from agisk.skill import Skill


class TestSkillFromDir:
    def test_no_skillmd(self, tmp_path: Path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        skill = Skill.from_dir(skill_dir)
        assert not skill.valid
        assert skill.dir_name == "my-skill"
        assert skill.name == "my-skill"
        assert "SKILL.md not found" in skill.errors

    def test_no_frontmatter(self, tmp_path: Path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Just content\nNo frontmatter\n")
        skill = Skill.from_dir(skill_dir)
        assert not skill.valid
        assert "Frontmatter not found" in skill.errors[0]

    def test_valid_skill(self, tmp_path: Path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: my-skill\ndescription: A test skill\n---\n# Content"
        )
        skill = Skill.from_dir(skill_dir)
        assert skill.valid
        assert skill.name == "my-skill"
        assert skill.dir_name == "my-skill"
        assert skill.description == "A test skill"
        assert skill.has_skill_md is True
        assert skill.has_frontmatter is True

    def test_missing_name_in_frontmatter(self, tmp_path: Path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\ndescription: no name here\n---\n# Content"
        )
        skill = Skill.from_dir(skill_dir)
        assert not skill.valid
        assert "Field 'name' is missing or empty in frontmatter" in skill.errors
        assert skill.name == "my-skill"

    def test_missing_description(self, tmp_path: Path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: my-skill\n---\n# Content"
        )
        skill = Skill.from_dir(skill_dir)
        assert skill.valid
        assert skill.name == "my-skill"
        assert "Field 'description' is missing or empty in frontmatter" in skill.warnings

    def test_name_mismatch(self, tmp_path: Path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: different-name\ndescription: mismatch\n---\n# Content"
        )
        skill = Skill.from_dir(skill_dir)
        assert skill.valid
        assert skill.name == "different-name"
        assert skill.dir_name == "my-skill"
        assert "Directory name 'my-skill' differs from frontmatter name 'different-name'" in skill.warnings

    def test_both_missing_name_and_description(self, tmp_path: Path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\n---\n# Content"
        )
        skill = Skill.from_dir(skill_dir)
        assert not skill.valid
        assert "Frontmatter not found" in skill.errors[0]

    def test_invalid_name_in_frontmatter(self, tmp_path: Path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: ducker..a/etc/bb\ndescription: bad name\n---\n# Content"
        )
        skill = Skill.from_dir(skill_dir)
        assert not skill.valid
        assert any("must not contain" in e for e in skill.errors)
        assert skill.name == "my-skill"


class TestSkillProperties:
    def test_valid_property(self):
        from agisk.skill import Skill
        valid = Skill(
            path=Path("/tmp"),
            dir_name="test",
            name="test",
            description="desc",
            has_skill_md=True,
            has_frontmatter=True,
            raw_frontmatter={},
        )
        assert valid.valid is True

        invalid = Skill(
            path=Path("/tmp"),
            dir_name="test",
            name="test",
            description="desc",
            has_skill_md=True,
            has_frontmatter=True,
            raw_frontmatter={},
            errors=["some error"],
        )
        assert invalid.valid is False