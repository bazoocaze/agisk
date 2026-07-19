from __future__ import annotations

import sys
from pathlib import Path

import questionary

from .skills import enable_skill, disable_skill, list_skills, linked_skills


def interactive_enable_skills(
    skills_dirs: list[Path],
    link_target_dir: Path,
    force: bool = False,
) -> None:
    """Present a checkbox UI for the user to select skills to enable/disable."""
    all_skills = list_skills(skills_dirs)
    if not all_skills:
        print("No skills available.", file=sys.stderr)
        sys.exit(1)

    linked = linked_skills(link_target_dir)
    linked_names = {l.name for l in linked}

    choices = [
        questionary.Choice(
            title=s.name,
            value=s.name,
            checked=s.name in linked_names,
        )
        for s in all_skills
    ]

    selected = questionary.checkbox(
        "Select skills to enable:",
        choices=choices,
        instruction="(space to toggle, enter to confirm)",
    ).ask()
    if selected is None:
        print("Cancelled.")
        sys.exit(0)

    selected_names = set(selected)

    for skill_name in selected_names - linked_names:
        try:
            result = enable_skill(
                skill_name, skills_dirs, link_target_dir, force=force
            )
            if result:
                print(f"Link created: {skill_name}")
        except (FileNotFoundError, NotADirectoryError, ValueError) as e:
            print(f"Error enabling '{skill_name}': {e}", file=sys.stderr)
            sys.exit(1)

    for skill_name in linked_names - selected_names:
        try:
            result = disable_skill(skill_name, link_target_dir)
            if result:
                print(f"Link removed: {skill_name}")
        except (ValueError, FileNotFoundError) as e:
            print(f"Error disabling '{skill_name}': {e}", file=sys.stderr)
            sys.exit(1)