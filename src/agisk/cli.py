from __future__ import annotations

import argparse
import sys
from pathlib import Path

import questionary

from .config import get_base_dir, get_skills_dir, get_link_target_dir, load_config
from .install import install_from_path
from .skills import enable_skill, disable_skill, list_skills, linked_skills


def _epilog() -> str:
    return """\
subcommands:
  use|enable <skill> [<skill> ...]   Create symbolic link(s) for skill(s)
  disable <skill> [<skill> ...]      Remove symbolic link(s) for skill(s)
  install <path>                     Copy a skill to the global directory
  list                               List available skills in the global directory
  linked                             List linked skills in the current project

global flags:
  --base-dir DIR    Base directory (overrides $AGISK_BASE_DIR)
  --force           Overwrite without asking
  --verbose, -v     Verbose output
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agisk",
        description="Agent Skills — Symbolic link manager for agent skills",
        epilog=_epilog(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=None,
        help="Base directory (overrides $AGISK_BASE_DIR)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Overwrite without asking",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Verbose output",
    )
    parser.add_argument(
        "subcommand",
        nargs="?",
        help="Subcommand: use|enable, disable, install, list, linked",
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="Subcommand arguments",
    )
    return parser


def _log(msg: str, verbose: bool = False) -> None:
    if verbose:
        print(msg, file=sys.stderr)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    verbose = args.verbose
    force = args.force

    # Resolve base_dir
    if args.base_dir:
        base_dir = Path(args.base_dir).resolve()
    else:
        base_dir = get_base_dir()

    _log(f"Base dir: {base_dir}", verbose)

    # Load config
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    skills_dir = get_skills_dir(base_dir, config)
    link_target_dir = get_link_target_dir(config)

    _log(f"Skills dir: {skills_dir}", verbose)
    _log(f"Link target dir: {link_target_dir}", verbose)

    subcommand = args.subcommand

    if not subcommand:
        parser.print_help()
        sys.exit(1)

    sub = subcommand.lower()

    # --- use / enable ---
    if sub in ("use", "enable"):
        skill_names = args.args
        if not skill_names and sys.stdin.isatty():
            # Interactive mode: let user select skills via checkbox
            all_skills = list_skills(skills_dir)
            if not all_skills:
                print("No skills available.", file=sys.stderr)
                sys.exit(1)
            choices = [s.name for s in all_skills]
            selected = questionary.checkbox(
                "Select skills to enable:",
                choices=choices,
                instruction="(space to select, enter to confirm)",
            ).ask()
            if not selected:
                print("No skills selected.")
                sys.exit(0)
            skill_names = list(selected)

        if not skill_names:
            print("Error: use/enable requires at least one skill", file=sys.stderr)
            sys.exit(1)

        for skill_name in skill_names:
            try:
                result = enable_skill(skill_name, skills_dir, link_target_dir, force=force)
                if result:
                    print(f"Link created: {skill_name}")
                else:
                    msg = f"Skill '{skill_name}' is already linked. Use --force to overwrite."
                    if force:
                        print(f"Link overwritten: {skill_name}")
                    else:
                        print(msg, file=sys.stderr)
            except (FileNotFoundError, NotADirectoryError, ValueError) as e:
                print(f"Error enabling '{skill_name}': {e}", file=sys.stderr)
                sys.exit(1)

    # --- disable ---
    elif sub == "disable":
        if not args.args:
            print("Error: disable requires at least one skill", file=sys.stderr)
            sys.exit(1)
        for skill_name in args.args:
            try:
                result = disable_skill(skill_name, link_target_dir)
                if result:
                    print(f"Link removed: {skill_name}")
                else:
                    print(f"Skill '{skill_name}' was not linked.", file=sys.stderr)
            except (ValueError, FileNotFoundError) as e:
                print(f"Error disabling '{skill_name}': {e}", file=sys.stderr)
                sys.exit(1)

    # --- install ---
    elif sub == "install":
        if not args.args:
            print("Error: install requires a path", file=sys.stderr)
            sys.exit(1)
        path = args.args[0]
        try:
            result = install_from_path(path, skills_dir, force=force, interactive=not force)
            if result:
                print(f"Skill installed: {path}")
            else:
                print("Installation cancelled.", file=sys.stderr)
                sys.exit(1)
        except (FileNotFoundError, NotADirectoryError, ValueError) as e:
            print(f"Error installing: {e}", file=sys.stderr)
            sys.exit(1)

    # --- list ---
    elif sub == "list":
        skills = list_skills(skills_dir)
        if not skills:
            print("No skills found.")
        else:
            for s in skills:
                print(s.name)

    # --- linked ---
    elif sub == "linked":
        links = linked_skills(link_target_dir)
        if not links:
            print("No linked skills.")
        else:
            for l in links:
                target = l.resolve()
                print(f"{l.name} -> {target}")

    else:
        print(f"Unknown subcommand: {subcommand}", file=sys.stderr)
        print("Use 'agisk --help' to see available commands.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()