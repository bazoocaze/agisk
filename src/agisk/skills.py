from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence


def list_skills(skills_dir: Path) -> list[Path]:
    """List directories in the global skills directory.

    Returns only directories (ignores loose files).
    """
    if not skills_dir.exists():
        return []
    return sorted(
        [p for p in skills_dir.iterdir() if p.is_dir()]
    )


def linked_skills(link_target_dir: Path) -> list[Path]:
    """List symlinks in the target directory.

    Returns only valid symbolic links (existing target or not).
    """
    if not link_target_dir.exists():
        return []
    return sorted(
        [p for p in link_target_dir.iterdir() if p.is_symlink()]
    )


def _validate_skill_name(name: str) -> None:
    """Validate the skill name against path traversal."""
    if not name or name.strip() == "":
        raise ValueError("Skill name cannot be empty")
    if "/" in name or "\\" in name or ".." in name:
        raise ValueError(
            f"Invalid skill name (path traversal detected): {name}"
        )


def enable_skill(
    skill_name: str,
    skills_dir: Path,
    link_target_dir: Path,
    force: bool = False,
) -> bool:
    """Create a symbolic link for the skill in the target directory.

    Returns True if the link was created, False if it already existed and not --force.
    """
    _validate_skill_name(skill_name)

    source = (skills_dir / skill_name).resolve()
    if not source.exists():
        raise FileNotFoundError(
            f"Skill not found: {source}"
        )
    if not source.is_dir():
        raise NotADirectoryError(
            f"Skill is not a directory: {source}"
        )

    link_target_dir.mkdir(parents=True, exist_ok=True)
    link_path = link_target_dir / skill_name

    if link_path.is_symlink() or link_path.exists():
        if not force:
            return False
        # Remove existing (file, directory or symlink)
        if link_path.is_symlink():
            link_path.unlink()
        elif link_path.is_dir():
            link_path.rmdir()
        else:
            link_path.unlink()

    # Try to create relative link when possible
    try:
        rel_source = os.path.relpath(source, link_target_dir)
        link_path.symlink_to(rel_source)
    except ValueError:
        link_path.symlink_to(source)

    return True


def disable_skill(
    skill_name: str,
    link_target_dir: Path,
) -> bool:
    """Remove the symbolic link for the skill.

    Returns True if removed, False if it did not exist.
    Idempotent: if it does not exist, no error.
    """
    _validate_skill_name(skill_name)

    link_path = link_target_dir / skill_name

    # Use stat() to check symlink without resolving
    try:
        is_sym = link_path.is_symlink()
    except (OSError, FileNotFoundError):
        is_sym = False

    if not is_sym and not link_path.exists():
        return False

    if is_sym:
        link_path.unlink()
        return True

    # Exists but is not a symlink — we do not remove it
    raise ValueError(
        f"{link_path} exists but is not a symbolic link. Remove manually."
    )