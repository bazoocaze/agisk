from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _default_base_dir() -> Path:
    return Path.home() / ".agisk"


def _default_config() -> dict[str, Any]:
    return {
        "skills_dir": "skills",
        "link_target_dir": ".agent/skills",
    }


def _ensure_config(base_dir: Path) -> Path:
    """Cria config padrão se não existir."""
    config_path = base_dir / "config.json"
    if not config_path.exists():
        base_dir.mkdir(parents=True, exist_ok=True)
        cfg = _default_config()
        config_path.write_text(json.dumps(cfg, indent=2) + "\n")
        # Permissão segura: 600
        config_path.chmod(0o600)
    return config_path


def load_config() -> dict[str, Any]:
    """Carrega o config.json.

    Prioridade:
    1. $AGISK_CONFIG → arquivo JSON customizado
    2. <base_dir>/config.json
    """
    config_source = os.environ.get("AGISK_CONFIG")
    if config_source:
        config_path = Path(config_source)
        if not config_path.exists():
            # Se AGISK_CONFIG foi explicitamente definido, cria o config
            config_path.parent.mkdir(parents=True, exist_ok=True)
            cfg = _default_config()
            config_path.write_text(json.dumps(cfg, indent=2) + "\n")
            config_path.chmod(0o600)
    else:
        base_dir = _default_base_dir()
        config_path = _ensure_config(base_dir)

    return json.loads(config_path.read_text())


def get_base_dir() -> Path:
    """Resolve o diretório base.

    Prioridade:
    1. --base-dir (passado como argumento, resolvido externamente)
    2. $AGISK_BASE_DIR
    3. ~/.agisk/
    """
    env_base = os.environ.get("AGISK_BASE_DIR")
    if env_base:
        return Path(env_base).resolve()
    return _default_base_dir()


def get_skills_dir(base_dir: Path | None = None, config: dict[str, Any] | None = None) -> Path:
    """Resolve o diretório global de skills.

    Prioridade:
    1. $AGISK_SKILLS_DIR (absoluto ou relativo ao CWD)
    2. Config: skills_dir (relativo ao base_dir, ou absoluto se começar com /)
    3. <base_dir>/skills/
    """
    env_skills = os.environ.get("AGISK_SKILLS_DIR")
    if env_skills:
        p = Path(env_skills)
        if p.is_absolute():
            return p
        return Path.cwd() / p

    if base_dir is None:
        base_dir = get_base_dir()
    if config is None:
        config = load_config()

    skills_dir_str = config.get("skills_dir", "skills")
    p = Path(skills_dir_str)
    if p.is_absolute():
        return p.resolve()
    return (base_dir / p).resolve()


def get_link_target_dir(config: dict[str, Any] | None = None) -> Path:
    """Resolve o diretório de destino para os links.

    Lê de config > fallback .agent/skills.
    Resolve relativo ao CWD.
    """
    if config is None:
        config = load_config()
    target = config.get("link_target_dir", ".agent/skills")
    return (Path.cwd() / Path(target)).resolve()