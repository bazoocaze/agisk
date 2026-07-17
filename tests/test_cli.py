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


def test_parser_force_flag():
    parser = build_parser()
    args = parser.parse_args(["--force", "use", "my-skill"])
    assert args.force is True


def test_parser_base_dir():
    parser = build_parser()
    args = parser.parse_args(["--base-dir", "/tmp/agisk", "list"])
    assert args.base_dir == "/tmp/agisk"


def test_parser_verbose():
    parser = build_parser()
    args = parser.parse_args(["-v", "list"])
    assert args.verbose is True


def test_parser_verbose_long():
    parser = build_parser()
    args = parser.parse_args(["--verbose", "list"])
    assert args.verbose is True


def test_parser_no_args():
    """Sem argumentos, o parser aceita (subcommand=None)."""
    parser = build_parser()
    args = parser.parse_args([])
    assert args.subcommand is None


def test_parser_unknown_subcommand():
    """Subcomando desconhecido deve ser aceito pelo parser mas tratado depois."""
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