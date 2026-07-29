from __future__ import annotations

import sys
from pathlib import Path

import pytest

from agisk.cli import build_parser


def test_parser_use():
    parser = build_parser()
    args = parser.parse_args(["use", "my-skill"])
    assert args.subcommand == "use"
    assert args.args == ["my-skill"]


def test_parser_enable():
    parser = build_parser()
    args = parser.parse_args(["enable", "skill-a"])
    assert args.subcommand == "enable"
    assert args.args == ["skill-a"]


def test_parser_use_multiple():
    parser = build_parser()
    args = parser.parse_args(["use", "skill-a", "skill-b", "skill-c"])
    assert args.subcommand == "use"
    assert args.args == ["skill-a", "skill-b", "skill-c"]


def test_parser_disable():
    parser = build_parser()
    args = parser.parse_args(["disable", "my-skill"])
    assert args.subcommand == "disable"
    assert args.args == ["my-skill"]


def test_parser_disable_multiple():
    parser = build_parser()
    args = parser.parse_args(["disable", "skill-a", "skill-b"])
    assert args.args == ["skill-a", "skill-b"]


def test_parser_install():
    parser = build_parser()
    args = parser.parse_args(["install", "/path/to/skill"])
    assert args.subcommand == "install"
    assert args.args == ["/path/to/skill"]


def test_parser_list():
    parser = build_parser()
    args = parser.parse_args(["list"])
    assert args.subcommand == "list"
    assert args.args == []


def test_parser_linked():
    parser = build_parser()
    args = parser.parse_args(["linked"])
    assert args.subcommand == "linked"


def test_parser_validate():
    parser = build_parser()
    args = parser.parse_args(["validate"])
    assert args.subcommand == "validate"
    assert args.args == []


def test_parser_force_flag():
    parser = build_parser()
    args = parser.parse_args(["--force", "use", "my-skill"])
    assert args.force is True


def test_parser_config():
    parser = build_parser()
    args = parser.parse_args(["--config", "/tmp/agisk/config.json", "list"])
    assert args.config == "/tmp/agisk/config.json"


def test_parser_verbose():
    parser = build_parser()
    args = parser.parse_args(["-v", "list"])
    assert args.verbose is True


def test_parser_verbose_long():
    parser = build_parser()
    args = parser.parse_args(["--verbose", "list"])
    assert args.verbose is True


def test_parser_no_args():
    """With no arguments, the parser accepts (subcommand=None)."""
    parser = build_parser()
    args = parser.parse_args([])
    assert args.subcommand is None


def test_parser_unknown_subcommand():
    """Unknown subcommand should be accepted by the parser but handled later."""
    parser = build_parser()
    args = parser.parse_args(["unknown", "arg"])
    assert args.subcommand == "unknown"


def test_parser_help(capsys):
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])
    captured = capsys.readouterr()
    assert "agisk" in captured.out
    assert "use|enable" in captured.out
    assert "disable" in captured.out
    assert "install" in captured.out
    assert "list" in captured.out
    assert "linked" in captured.out
    assert "doctor" in captured.out


class TestUseEnableInteractive:
    """Tests for the interactive use/enable mode (no args, TTY)."""

    def test_interactive_no_skills_available(self, capsys, monkeypatch, tmp_path):
        """When no skills exist globally, show error."""
        monkeypatch.setattr("sys.argv", ["agisk", "use"])
        monkeypatch.setattr("sys.stdin.isatty", lambda: True)

        base_dir = tmp_path / ".agisk"
        base_dir.mkdir()
        config_path = base_dir / "config.json"
        config_path.write_text(
            '{"skills_dirs": ["skills"], "link_target_dir": ".agents/skills"}'
        )
        (base_dir / "skills").mkdir()

        monkeypatch.setenv("AGISK_CONFIG_FILE", str(config_path))

        with pytest.raises(SystemExit) as exc:
            from agisk.cli import main
            main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "No skills available" in captured.err

    def test_interactive_select_and_enable(self, capsys, monkeypatch, tmp_path):
        """Select skills via checkbox and enable them."""
        base_dir = tmp_path / ".agisk"
        base_dir.mkdir()
        config_path = base_dir / "config.json"
        config_path.write_text(
            '{"skills_dirs": ["skills"], "link_target_dir": ".agents/skills"}'
        )
        skills_dir = base_dir / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill-a").mkdir()
        (skills_dir / "skill-b").mkdir()

        # Create a project dir with .agents/skills
        project = tmp_path / "project"
        project.mkdir()
        (project / ".agents" / "skills").mkdir(parents=True)
        monkeypatch.chdir(project)

        monkeypatch.setattr("sys.argv", ["agisk", "use"])
        monkeypatch.setenv("AGISK_CONFIG_FILE", str(config_path))
        monkeypatch.setattr("sys.stdin.isatty", lambda: True)

        def _fake_interactive(dirs, target, force=False):
            from agisk.skills import enable_skill
            enable_skill("skill-a", dirs, target, force=force)
            print("Link created: skill-a")

        import agisk.cli
        monkeypatch.setattr(agisk.cli, "interactive_enable_skills", _fake_interactive)

        from agisk.cli import main
        main()
        captured = capsys.readouterr()
        assert "Link created: skill-a" in captured.out
        assert (project / ".agents" / "skills" / "skill-a").is_symlink()

    def test_interactive_cancel_selection(self, capsys, monkeypatch, tmp_path):
        """When user cancels (None/empty), exit cleanly."""
        base_dir = tmp_path / ".agisk"
        base_dir.mkdir()
        config_path = base_dir / "config.json"
        config_path.write_text(
            '{"skills_dirs": ["skills"], "link_target_dir": ".agents/skills"}'
        )
        skills_dir = base_dir / "skills"
        skills_dir.mkdir()
        (skills_dir / "skill-a").mkdir()

        project = tmp_path / "project"
        project.mkdir()
        (project / ".agents" / "skills").mkdir(parents=True)
        monkeypatch.chdir(project)

        monkeypatch.setattr("sys.argv", ["agisk", "use"])
        monkeypatch.setenv("AGISK_CONFIG_FILE", str(config_path))
        monkeypatch.setattr("sys.stdin.isatty", lambda: True)

        def _fake_cancel(*args, **kwargs):
            print("Cancelled.")
            import sys
            sys.exit(0)

        import agisk.cli
        monkeypatch.setattr(agisk.cli, "interactive_enable_skills", _fake_cancel)

        from agisk.cli import main
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert "Cancelled." in captured.out
        assert not (project / ".agents" / "skills" / "skill-a").exists()

    def test_interactive_not_tty_uses_args(self, capsys, monkeypatch, tmp_path):
        """When stdin is not a TTY and no args, should error (not enter interactive)."""
        monkeypatch.setattr("sys.argv", ["agisk", "use"])
        monkeypatch.setattr("sys.stdin.isatty", lambda: False)

        base_dir = tmp_path / ".agisk"
        base_dir.mkdir()
        config_path = base_dir / "config.json"
        config_path.write_text(
            '{"skills_dirs": ["skills"], "link_target_dir": ".agents/skills"}'
        )
        monkeypatch.setenv("AGISK_CONFIG_FILE", str(config_path))

        with pytest.raises(SystemExit) as exc:
            from agisk.cli import main
            main()
        assert exc.value.code == 1
        captured = capsys.readouterr()
        assert "requires at least one skill" in captured.err
