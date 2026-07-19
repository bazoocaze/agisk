from __future__ import annotations

import os
import warnings
from pathlib import Path


def list_skills(skills_dirs: list[Path]) -> list[Path]:
    """List skill directories across multiple global directories.

    Iterates through each directory in order; the first occurrence of a
    skill name wins.  Emits a warning for each duplicate that is skipped.
    Returns only directories (ignores loose files).
    """
    seen: dict[str, Path] = {}
    for d in skills_dirs:
        if not d.exists():
            continue
        for p in d.iterdir():
            if not p.is_dir():
                continue
            if p.name in seen:
                warnings.warn(
                    f"⚠️  Skill '{p.name}' found in multiple directories; "
                    f"using '{seen[p.name]}' and ignoring '{p.resolve()}'",
                    stacklevel=2,
                )
            else:
                seen[p.name] = p
    return sorted(seen.values(), key=lambda x: x.name)


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
    skills_dirs: list[Path],
    link_target_dir: Path,
    force: bool = False,
) -> bool:
    """Create a symbolic link for the skill in the target directory.

    Searches through ``skills_dirs`` in order and uses the first directory
    that contains the skill.

    Returns True if the link was created, False if it already existed and not --force.
    """
    _validate_skill_name(skill_name)

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