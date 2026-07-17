from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence


def list_skills(skills_dir: Path) -> list[Path]:
    """Lista diretórios no diretório global de skills.

    Retorna apenas diretórios (ignora arquivos soltos).
    """
    if not skills_dir.exists():
        return []
    return sorted(
        [p for p in skills_dir.iterdir() if p.is_dir()]
    )


def linked_skills(link_target_dir: Path) -> list[Path]:
    """Lista symlinks no diretório de destino.

    Retorna apenas links simbólicos válidos (target existente ou não).
    """
    if not link_target_dir.exists():
        return []
    return sorted(
        [p for p in link_target_dir.iterdir() if p.is_symlink()]
    )


def _validate_skill_name(name: str) -> None:
    """Valida o nome da skill contra path traversal."""
    if not name or name.strip() == "":
        raise ValueError("Nome da skill não pode ser vazio")
    if "/" in name or "\\" in name or ".." in name:
        raise ValueError(
            f"Nome de skill inválido (path traversal detectado): {name}"
        )


def enable_skill(
    skill_name: str,
    skills_dir: Path,
    link_target_dir: Path,
    force: bool = False,
) -> bool:
    """Cria um link simbólico da skill no diretório de destino.

    Retorna True se o link foi criado, False se já existia e não --force.
    """
    _validate_skill_name(skill_name)

    source = (skills_dir / skill_name).resolve()
    if not source.exists():
        raise FileNotFoundError(
            f"Skill não encontrada: {source}"
        )
    if not source.is_dir():
        raise NotADirectoryError(
            f"Skill não é um diretório: {source}"
        )

    link_target_dir.mkdir(parents=True, exist_ok=True)
    link_path = link_target_dir / skill_name

    if link_path.is_symlink() or link_path.exists():
        if not force:
            return False
        # Remove existente (arquivo, diretório ou symlink)
        if link_path.is_symlink():
            link_path.unlink()
        elif link_path.is_dir():
            link_path.rmdir()
        else:
            link_path.unlink()

    # Tenta criar link relativo quando possível
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
    """Remove o link simbólico da skill.

    Retorna True se removeu, False se não existia.
    Idempotente: se não existir, não erro.
    """
    _validate_skill_name(skill_name)

    link_path = link_target_dir / skill_name

    # Usar stat() para verificar symlink sem resolver
    try:
        is_sym = link_path.is_symlink()
    except (OSError, FileNotFoundError):
        is_sym = False

    if not is_sym and not link_path.exists():
        return False

    if is_sym:
        link_path.unlink()
        return True

    # Existe mas não é symlink — não removemos
    raise ValueError(
        f"{link_path} existe mas não é um link simbólico. Remova manualmente."
    )