from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

from .yaml import get_skill_name_from_skillmd


def _validate_no_path_traversal(name: str) -> None:
    """Valida nome contra path traversal."""
    if not name or name.strip() == "":
        raise ValueError("Nome da skill não pode ser vazio")
    if "/" in name or "\\" in name or ".." in name:
        raise ValueError(
            f"Nome de skill inválido (path traversal detectado): {name}"
        )


def _prompt_overwrite(name: str) -> bool:
    """Pergunta interativamente se quer sobrescrever."""
    try:
        resposta = input(
            f"Skill '{name}' já existe. Sobrescrever? [s/N] "
        )
        return resposta.strip().lower() in ("s", "sim", "y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


def install_from_path(
    path: str | Path,
    skills_dir: Path,
    force: bool = False,
    interactive: bool = True,
) -> bool:
    """Instala uma skill a partir de um diretório ou arquivo SKILL.md.

    Args:
        path: Caminho para o diretório (com SKILL.md dentro) ou arquivo SKILL.md.
        skills_dir: Diretório global de skills.
        force: Se True, sobrescreve sem perguntar.
        interactive: Se True, pergunta interativamente antes de sobrescrever.

    Returns:
        True se instalou com sucesso, False se cancelado.

    Raises:
        FileNotFoundError: Se o path não existe.
        ValueError: Se o path é um symlink, ou nome inválido.
        NotADirectoryError: Se path é diretório sem SKILL.md.
    """
    src_path = Path(path)

    # Verificar symlink ANTES de resolver
    if src_path.is_symlink():
        raise ValueError(
            f"Não é permitido instalar a partir de um symlink: {src_path}"
        )

    src = src_path.resolve()

    if not src.exists():
        raise FileNotFoundError(f"Caminho não encontrado: {src}")

    if src.is_dir():
        return _install_from_directory(src, skills_dir, force, interactive)
    elif src.is_file():
        return _install_from_file(src, skills_dir, force, interactive)
    else:
        raise ValueError(f"Tipo de caminho não suportado: {src}")


def _install_from_directory(
    src: Path,
    skills_dir: Path,
    force: bool,
    interactive: bool,
) -> bool:
    """Instala a partir de um diretório que contém SKILL.md."""
    skill_md = src / "SKILL.md"
    if not skill_md.exists():
        raise NotADirectoryError(
            f"Diretório não contém SKILL.md: {src}"
        )

    name = src.name
    _validate_no_path_traversal(name)
    # Valida também se o nome do diretório em si contém path traversal
    if ".." in src.name or src.name.startswith("/"):
        raise ValueError(
            f"Nome de skill inválido (path traversal detectado): {src.name}"
        )
    target = (skills_dir / name).resolve()

    # Verifica se já existe
    if target.exists():
        if not force:
            if not interactive or not _prompt_overwrite(name):
                return False
        # Remove existente
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
    """Instala a partir de um arquivo SKILL.md, extraindo name do frontmatter."""
    if src.name != "SKILL.md":
        raise ValueError(
            f"Arquivo deve ser SKILL.md, mas é: {src.name}"
        )

    name = get_skill_name_from_skillmd(src)
    _validate_no_path_traversal(name)
    target = (skills_dir / name).resolve()

    # Verifica se já existe
    if target.exists():
        if not force:
            if not interactive or not _prompt_overwrite(name):
                return False
        shutil.rmtree(target)

    skills_dir.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    shutil.copy2(src, target / "SKILL.md")
    return True