from __future__ import annotations

import sys
from pathlib import Path

import questionary

from .skill import Skill
from .skills import enable_skill, disable_skill, list_skills, linked_skills


def interactive_enable_skills(
    skills_dirs: list[Path],
    link_target_dirs: list[Path],
    force: bool = False,
) -> None:
    try:
        _interactive_enable_skills_impl(skills_dirs, link_target_dirs, force=force)
    except KeyboardInterrupt:
        print("Cancelled.")
        sys.exit(0)


def _interactive_enable_skills_impl(
    skills_dirs: list[Path],
    link_target_dirs: list[Path],
    force: bool = False,
) -> None:
    all_skills = list_skills(skills_dirs)
    if not all_skills:
        print("No skills available.", file=sys.stderr)
        sys.exit(1)

    linked = linked_skills(link_target_dirs)
    linked_names = {s.dir_name for s in linked}

    choices = [
        questionary.Choice(
            title=_format_skill_choice(s),
            value=s.dir_name,
            checked=s.dir_name in linked_names,
        )
        for s in all_skills
    ]

    selected = questionary.checkbox(
        "Select skills to enable:",
        choices=choices,
        instruction="(space to toggle, enter to confirm, ctrl+c to cancel)",
    ).ask()
    if selected is None:
        print("Cancelled.")
        sys.exit(0)

    selected_names = set(selected)

    for skill_name in selected_names - linked_names:
        try:
            result = enable_skill(
                skill_name, skills_dirs, link_target_dirs, force=force
            )
            if result:
                print(f"Link created: {skill_name}")
        except (FileNotFoundError, NotADirectoryError, ValueError) as e:
            print(f"Error enabling '{skill_name}': {e}", file=sys.stderr)
            sys.exit(1)

    for skill_name in linked_names - selected_names:
        try:
            result = disable_skill(skill_name, link_target_dirs)
            if result:
                print(f"Link removed: {skill_name}")
        except (ValueError, FileNotFoundError) as e:
            print(f"Error disabling '{skill_name}': {e}", file=sys.stderr)
            sys.exit(1)


def _format_skill_choice(skill: Skill) -> str:
    prefix = skill.name
    if skill.valid:
        label = f"✅ {prefix}"
    else:
        label = f"⚠️  {prefix}"
    if skill.description:
        return f"{label} — {skill.description}"
    return label
