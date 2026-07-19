from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .yaml import parse_frontmatter


def validate_skill_name(name: str) -> None:
    if not name or name.strip() == "":
        raise ValueError("Skill name cannot be empty")
    if "/" in name or "\\" in name or ".." in name:
        raise ValueError(
            f"Invalid skill name '{name}': must not contain '/', '\\\\', or '..'"
        )


@dataclass
class Skill:
    path: Path
    dir_name: str
    name: str
    description: str
    has_skill_md: bool
    has_frontmatter: bool
    raw_frontmatter: dict[str, Any]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.errors) == 0

    @classmethod
    def from_dir(cls, path: Path) -> Skill:
        errors: list[str] = []
        warnings: list[str] = []

        skill_md = path / "SKILL.md"
        has_skill_md = skill_md.exists()

        if not has_skill_md:
            errors.append("SKILL.md not found")
            return cls(
                path=path,
                dir_name=path.name,
                name=path.name,
                description="",
                has_skill_md=False,
                has_frontmatter=False,
                raw_frontmatter={},
                errors=errors,
                warnings=warnings,
            )

        text = skill_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        has_frontmatter = bool(fm)

        if not has_frontmatter:
            errors.append("Frontmatter not found (missing `---` delimiters)")
            return cls(
                path=path,
                dir_name=path.name,
                name=path.name,
                description="",
                has_skill_md=True,
                has_frontmatter=False,
                raw_frontmatter={},
                errors=errors,
                warnings=warnings,
            )

        name = fm.get("name", "")
        if not name:
            errors.append("Field 'name' is missing or empty in frontmatter")
            name = path.name
        else:
            try:
                validate_skill_name(str(name))
            except ValueError as e:
                errors.append(str(e))
                name = path.name
            if str(name) != path.name:
                warnings.append(
                    f"Directory name '{path.name}' differs from frontmatter name '{name}'"
                )

        description = str(fm.get("description", ""))
        if not description:
            warnings.append("Field 'description' is missing or empty in frontmatter")

        return cls(
            path=path,
            dir_name=path.name,
            name=str(name),
            description=description,
            has_skill_md=True,
            has_frontmatter=True,
            raw_frontmatter=fm,
            errors=errors,
            warnings=warnings,
        )