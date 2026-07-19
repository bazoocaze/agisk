from __future__ import annotations

import os
import sys
from pathlib import Path

from .skill import Skill, validate_skill_name


def list_skills(skills_dirs: list[Path]) -> list[Skill]:
    seen: dict[str, Path] = {}
    for d in skills_dirs:
        if not d.exists():
            continue
        for p in d.iterdir():
            if not p.is_dir():
                continue
            if p.name in seen:
                continue
            seen[p.name] = p
    return sorted(
        [Skill.from_dir(p) for p in seen.values()],
        key=lambda s: s.dir_name,
    )


def linked_skills(link_target_dir: Path) -> list[Skill]:
    if not link_target_dir.exists():
        return []
    result: list[Skill] = []
    for p in sorted(link_target_dir.iterdir()):
        if not p.is_symlink():
            continue
        target = p.resolve()
        if not target.exists():
            result.append(
                Skill(
                    path=p,
                    dir_name=p.name,
                    name=p.name,
                    description="",
                    has_skill_md=False,
                    has_frontmatter=False,
                    raw_frontmatter={},
                    errors=["Broken symlink: target does not exist"],
                )
            )
        else:
            skill = Skill.from_dir(target)
            result.append(skill)
    return result


def enable_skill(
    skill_name: str,
    skills_dirs: list[Path],
    link_target_dir: Path,
    force: bool = False,
) -> bool:
    validate_skill_name(skill_name)

    source = _find_skill_dir(skill_name, skills_dirs)
    if source is None:
        searched = ", ".join(str(d) for d in skills_dirs)
        raise FileNotFoundError(
            f"Skill not found in any skills directory: {skill_name}\n"
            f"Searched: {searched}"
        )

    link_target_dir.mkdir(parents=True, exist_ok=True)
    link_path = link_target_dir / skill_name

    if link_path.is_symlink() or link_path.exists():
        if not force:
            return False
        if link_path.is_symlink():
            link_path.unlink()
        elif link_path.is_dir():
            link_path.rmdir()
        else:
            link_path.unlink()

    try:
        rel_source = os.path.relpath(source, link_target_dir)
        link_path.symlink_to(rel_source)
    except ValueError:
        link_path.symlink_to(source)

    return True


def _find_skill_dir(skill_name: str, skills_dirs: list[Path]) -> Path | None:
    for d in skills_dirs:
        candidate = (d / skill_name).resolve()
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


def disable_skill(
    skill_name: str,
    link_target_dir: Path,
) -> bool:
    validate_skill_name(skill_name)

    link_path = link_target_dir / skill_name

    try:
        is_sym = link_path.is_symlink()
    except (OSError, FileNotFoundError):
        is_sym = False

    if not is_sym and not link_path.exists():
        return False

    if is_sym:
        link_path.unlink()
        return True

    raise ValueError(
        f"{link_path} exists but is not a symbolic link. Remove manually."
    )


def find_duplicates(skills_dirs: list[Path]) -> list[tuple[str, list[Path]]]:
    seen: dict[str, list[Path]] = {}
    for d in skills_dirs:
        if not d.exists():
            continue
        for p in d.iterdir():
            if not p.is_dir():
                continue
            if p.name not in seen:
                seen[p.name] = []
            seen[p.name].append(p)
    return [
        (name, paths) for name, paths in seen.items() if len(paths) > 1
    ]