from __future__ import annotations

from pathlib import Path

import pytest

from agisk.install import install_from_path
from agisk.install import _validate_no_path_traversal


class TestInstallFromDirectory:
    def test_install_directory(self, tmp_skills_dir: Path, sample_skill_dir: Path):
        result = install_from_path(sample_skill_dir, tmp_skills_dir)
        assert result is True
        target = tmp_skills_dir / "my-skill"
        assert target.exists()
        assert (target / "SKILL.md").exists()
        assert (target / "SKILL.md").read_text() == "---\nname: my-skill\n---\n# My Skill\n"

    def test_install_directory_without_skillmd(self, tmp_skills_dir: Path, tmp_path: Path):
        empty_dir = tmp_path / "empty-skill"
        empty_dir.mkdir()
        with pytest.raises(NotADirectoryError, match="does not contain SKILL.md"):
            install_from_path(empty_dir, tmp_skills_dir)

    def test_install_directory_already_exists_no_force(self, tmp_skills_dir: Path, sample_skill_dir: Path):
        # Install once
        install_from_path(sample_skill_dir, tmp_skills_dir)
        # Second time without force, non-interactive mode
        result = install_from_path(sample_skill_dir, tmp_skills_dir, force=False, interactive=False)
        assert result is False

    def test_install_directory_already_exists_force(self, tmp_skills_dir: Path, sample_skill_dir: Path):
        install_from_path(sample_skill_dir, tmp_skills_dir)
        result = install_from_path(sample_skill_dir, tmp_skills_dir, force=True, interactive=False)
        assert result is True

    def test_reject_symlink_dir(self, tmp_skills_dir: Path, tmp_path: Path):
        real_dir = tmp_path / "real-skill"
        real_dir.mkdir()
        (real_dir / "SKILL.md").write_text("---\nname: real-skill\n---\n")
        symlink = tmp_path / "symlink-skill"
        symlink.symlink_to(real_dir)
        # Should reject because it is a symlink
        with pytest.raises(ValueError, match="symlink"):
            install_from_path(str(symlink), tmp_skills_dir)

    def test_path_traversal_in_dirname(self, tmp_skills_dir: Path, tmp_path: Path):
        # Tests that names with '..' are rejected in validation
        from agisk.install import _validate_no_path_traversal
        with pytest.raises(ValueError, match="path traversal"):
            _validate_no_path_traversal("../evil")
        with pytest.raises(ValueError, match="path traversal"):
            _validate_no_path_traversal("sub/../evil")
        with pytest.raises(ValueError, match="path traversal"):
            _validate_no_path_traversal("..\\evil")
        with pytest.raises(ValueError, match="path traversal"):
            _validate_no_path_traversal("skill..name")


class TestInstallFromFile:
    def test_install_skillmd_file(self, tmp_skills_dir: Path, sample_skill_md: Path):
        result = install_from_path(sample_skill_md, tmp_skills_dir)
        assert result is True
        target = tmp_skills_dir / "my-file-skill"
        assert target.exists()
        assert (target / "SKILL.md").exists()
        assert "my-file-skill" in (target / "SKILL.md").read_text()

    def test_install_non_skillmd_file(self, tmp_skills_dir: Path, tmp_path: Path):
        not_skillmd = tmp_path / "README.md"
        not_skillmd.write_text("# README")
        with pytest.raises(ValueError, match="SKILL.md"):
            install_from_path(not_skillmd, tmp_skills_dir)

    def test_install_skillmd_no_name(self, tmp_skills_dir: Path, sample_skill_md_no_name: Path):
        with pytest.raises(ValueError, match="Field 'name' not found"):
            install_from_path(sample_skill_md_no_name, tmp_skills_dir)

    def test_reject_symlink_file(self, tmp_skills_dir: Path, tmp_path: Path):
        real_file = tmp_path / "real-SKILL.md"
        real_file.write_text("---\nname: real-skill\n---\n")
        symlink = tmp_path / "SKILL.md"
        symlink.symlink_to(real_file)
        with pytest.raises(ValueError, match="symlink"):
            install_from_path(symlink, tmp_skills_dir)

    def test_path_traversal_in_name(self, tmp_skills_dir: Path, tmp_path: Path):
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text("---\nname: ../../evil\n---\n")
        with pytest.raises(ValueError, match="path traversal"):
            install_from_path(skill_md, tmp_skills_dir)


class TestInstallEdgeCases:
    def test_path_not_found(self, tmp_skills_dir: Path):
        with pytest.raises(FileNotFoundError):
            install_from_path("/nonexistent/path", tmp_skills_dir)

    def test_install_from_cwd_relative(self, tmp_skills_dir: Path, sample_skill_dir: Path):
        """Tests installation with a relative path."""
        import os
        old_cwd = Path.cwd()
        try:
            os.chdir(sample_skill_dir.parent)
            result = install_from_path(sample_skill_dir.name, tmp_skills_dir)
            assert result is True
            assert (tmp_skills_dir / sample_skill_dir.name).exists()
        finally:
            os.chdir(old_cwd)
