from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import get_base_dir, get_skills_dir, get_link_target_dir, load_config
from .install import install_from_path
from .skills import enable_skill, disable_skill, list_skills, linked_skills


def _epilog() -> str:
    return """\
subcomandos:
  use|enable <skill> [<skill> ...]   Cria link(s) simbólico(s) da(s) skill(s)
  disable <skill> [<skill> ...]      Remove link(s) simbólico(s) da(s) skill(s)
  install <caminho>                  Copia uma skill para o diretório global
  list                               Lista skills disponíveis no diretório global
  linked                             Lista skills linkadas no projeto atual

flags globais:
  --base-dir DIR    Diretório base (prioridade sobre $AGISK_BASE_DIR)
  --force           Sobrescrever sem perguntar
  --verbose, -v     Saída detalhada
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agisk",
        description="Agent Skills — Gerenciador de links simbólicos para skills de agentes",
        epilog=_epilog(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=None,
        help="Diretório base (prioridade sobre $AGISK_BASE_DIR)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Sobrescrever sem perguntar",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Saída detalhada",
    )
    parser.add_argument(
        "subcommand",
        nargs="?",
        help="Subcomando: use|enable, disable, install, list, linked",
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="Argumentos do subcomando",
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

    # Carrega config
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(f"Erro: {e}", file=sys.stderr)
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
        if not args.args:
            print("Erro: use/enable requer pelo menos uma skill", file=sys.stderr)
            sys.exit(1)
        for skill_name in args.args:
            try:
                result = enable_skill(skill_name, skills_dir, link_target_dir, force=force)
                if result:
                    print(f"Link criado: {skill_name}")
                else:
                    msg = f"Skill '{skill_name}' já está linkada. Use --force para sobrescrever."
                    if force:
                        print(f"Link sobrescrito: {skill_name}")
                    else:
                        print(msg, file=sys.stderr)
            except (FileNotFoundError, NotADirectoryError, ValueError) as e:
                print(f"Erro ao habilitar '{skill_name}': {e}", file=sys.stderr)
                sys.exit(1)

    # --- disable ---
    elif sub == "disable":
        if not args.args:
            print("Erro: disable requer pelo menos uma skill", file=sys.stderr)
            sys.exit(1)
        for skill_name in args.args:
            try:
                result = disable_skill(skill_name, link_target_dir)
                if result:
                    print(f"Link removido: {skill_name}")
                else:
                    print(f"Skill '{skill_name}' não estava linkada.", file=sys.stderr)
            except (ValueError, FileNotFoundError) as e:
                print(f"Erro ao desabilitar '{skill_name}': {e}", file=sys.stderr)
                sys.exit(1)

    # --- install ---
    elif sub == "install":
        if not args.args:
            print("Erro: install requer um caminho", file=sys.stderr)
            sys.exit(1)
        path = args.args[0]
        try:
            result = install_from_path(path, skills_dir, force=force, interactive=not force)
            if result:
                print(f"Skill instalada: {path}")
            else:
                print("Instalação cancelada.", file=sys.stderr)
                sys.exit(1)
        except (FileNotFoundError, NotADirectoryError, ValueError) as e:
            print(f"Erro ao instalar: {e}", file=sys.stderr)
            sys.exit(1)

    # --- list ---
    elif sub == "list":
        skills = list_skills(skills_dir)
        if not skills:
            print("Nenhuma skill encontrada.")
        else:
            for s in skills:
                print(s.name)

    # --- linked ---
    elif sub == "linked":
        links = linked_skills(link_target_dir)
        if not links:
            print("Nenhuma skill linkada.")
        else:
            for l in links:
                target = l.resolve()
                print(f"{l.name} -> {target}")

    else:
        print(f"Subcomando desconhecido: {subcommand}", file=sys.stderr)
        print("Use 'agisk --help' para ver os comandos disponíveis.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()