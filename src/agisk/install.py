from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Optional

from .skill import Skill, validate_skill_name
from .yaml import get_skill_name_from_skillmd


def _prompt_overwrite(name: str) -> bool:
    """Interactively ask if user wants to overwrite."""
    try:
        answer = input(
            f"Skill '{name}' already exists. Overwrite? [y/N] "
        )
        return answer.strip().lower() in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


def install_from_path(
    path: str | Path,
    skills_dir: Path,
    force: bool = False,
    interactive: bool = True,
) -> bool:
    """Install a skill from a directory or SKILL.md file.

    Args:
        path: Path to the directory (with SKILL.md inside) or SKILL.md file.
        skills_dir: Global skills directory.
        force: If True, overwrite without asking.
        interactive: If True, interactively ask before overwriting.

    Returns:
        True if installed successfully, False if cancelled.

    Raises:
        FileNotFoundError: If the path does not exist.
        ValueError: If the path is a symlink, or invalid name.
        NotADirectoryError: If path is a directory without SKILL.md.
    """
    src_path = Path(path)

    # Check symlink BEFORE resolving
    if src_path.is_symlink():
        raise ValueError(
            f"Installing from a symlink is not allowed: {src_path}"
        )

    src = src_path.resolve()

    if not src.exists():
        raise FileNotFoundError(f"Path not found: {src}")

    if src.is_dir():
        return _install_from_directory(src, skills_dir, force, interactive)
    elif src.is_file():
        return _install_from_file(src, skills_dir, force, interactive)
    else:
        raise ValueError(f"Unsupported path type: {src}")


def _install_from_directory(
    src: Path,
    skills_dir: Path,
    force: bool,
    interactive: bool,
) -> bool:
    """Install from a directory that contains SKILL.md."""
    skill_md = src / "SKILL.md"
    if not skill_md.exists():
        raise NotADirectoryError(
            f"Directory does not contain SKILL.md: {src}"
        )

    skill = Skill.from_dir(src)
    for w in skill.warnings:
        print(f"Warning: {w}", file=sys.stderr)
    if not skill.valid:
        for e in skill.errors:
            print(f"Error: {e}", file=sys.stderr)
        raise ValueError(f"Invalid skill in {src}")

    name = src.name
    validate_skill_name(name)
    target = (skills_dir / name).resolve()

    # Check if already exists
    if target.exists():
        if not force:
            if not interactive or not _prompt_overwrite(name):
                return False
        shutil.rmtree(target)

    skills_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, target)
    return True


def _install_from_file(
    src: Path,
    skills_dir: Path,
    force: bool,
    interactive: bool,
) -> bool:
    """Install from a SKILL.md file, extracting name from frontmatter."""
    if src.name != "SKILL.md":
        raise ValueError(
            f"File must be SKILL.md, but got: {src.name}"
        )

    name = get_skill_name_from_skillmd(src)
    validate_skill_name(name)
    target = (skills_dir / name).resolve()

    # Check if already exists
    if target.exists():
        if not force:
            if not interactive or not _prompt_overwrite(name):
                return False
        shutil.rmtree(target)

    skills_dir.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    shutil.copy2(src, target / "SKILL.md")
    return True
