from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Extracts YAML frontmatter between '---' delimiters at the start of the text.

    Parses only simple top-level key/value pairs:
    - key: value
    - Does not support nesting, lists, or complex quoted strings.
    - Unquoted strings, numbers, booleans.
    """
    # Pattern: start of string, optional whitespace, ---, newline, content, ---
    m = re.match(r"^\s*---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}

    content = m.group(1)
    result: dict[str, Any] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        # Try to convert to basic types
        if value.lower() in ("true", "yes", "on"):
            result[key] = True
        elif value.lower() in ("false", "no", "off"):
            result[key] = False
        elif value == "~" or value.lower() == "null":
            result[key] = None
        else:
            # Try int or float
            try:
                result[key] = int(value)
            except ValueError:
                try:
                    result[key] = float(value)
                except ValueError:
                    result[key] = value
    return result


def get_skill_name_from_skillmd(path: Path) -> str:
    """Reads a SKILL.md file, extracts the frontmatter and returns the 'name' field."""
    text = path.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)
    name = frontmatter.get("name")
    if not name:
        raise ValueError(
            f"Field 'name' not found in frontmatter of {path}"
        )
    return str(name)
