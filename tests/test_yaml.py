from __future__ import annotations

from pathlib import Path

from agisk.yaml import parse_frontmatter, get_skill_name_from_skillmd


def test_parse_frontmatter_simple():
    text = "---\nname: my-skill\n---\n# Content"
    result = parse_frontmatter(text)
    assert result == {"name": "my-skill"}


def test_parse_frontmatter_multiple_fields():
    text = "---\nname: my-skill\ndescription: A test skill\nversion: 1\n---\n# Content"
    result = parse_frontmatter(text)
    assert result == {"name": "my-skill", "description": "A test skill", "version": 1}


def test_parse_frontmatter_no_frontmatter():
    text = "# Just content\nNo frontmatter here"
    result = parse_frontmatter(text)
    assert result == {}


def test_parse_frontmatter_empty():
    result = parse_frontmatter("")
    assert result == {}


def test_parse_frontmatter_only_delimiters():
    text = "---\n---\n# Content"
    result = parse_frontmatter(text)
    assert result == {}


def test_parse_frontmatter_booleans():
    text = "---\nenabled: true\nvisible: yes\nactive: on\ndisabled: false\nhidden: no\ninactive: off\n---\n"
    result = parse_frontmatter(text)
    assert result == {
        "enabled": True,
        "visible": True,
        "active": True,
        "disabled": False,
        "hidden": False,
        "inactive": False,
    }


def test_parse_frontmatter_null():
    text = "---\nvalue: null\nempty: ~\n---\n"
    result = parse_frontmatter(text)
    assert result == {"value": None, "empty": None}


def test_parse_frontmatter_numbers():
    text = "---\ncount: 42\npi: 3.14\n---\n"
    result = parse_frontmatter(text)
    assert result == {"count": 42, "pi": 3.14}


def test_parse_frontmatter_comments():
    text = "---\nname: my-skill\n# this is a comment\ndesc: something\n---\n"
    result = parse_frontmatter(text)
    assert result == {"name": "my-skill", "desc": "something"}


def test_get_skill_name_from_skillmd(tmp_path: Path):
    path = tmp_path / "SKILL.md"
    path.write_text("---\nname: test-skill\n---\n# Content")
    assert get_skill_name_from_skillmd(path) == "test-skill"


def test_get_skill_name_from_skillmd_missing_name(tmp_path: Path):
    path = tmp_path / "SKILL.md"
    path.write_text("---\ndescription: no name\n---\n# Content")
    import pytest
    with pytest.raises(ValueError, match="Field 'name' not found"):
        get_skill_name_from_skillmd(path)