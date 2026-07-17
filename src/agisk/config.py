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
    """Create default config if it does not exist."""
    config_path = base_dir / "config.json"
    if not config_path.exists():
        base_dir.mkdir(parents=True, exist_ok=True)
        cfg = _default_config()
        config_path.write_text(json.dumps(cfg, indent=2) + "\n")
        # Secure permission: 600
        config_path.chmod(0o600)
    return config_path


def load_config(base_dir: Path | None = None) -> dict[str, Any]:
    """Load the config.json from <base_dir>/config.json.

    Creates a default config if the file does not exist.
    """
    if base_dir is None:
        base_dir = get_base_dir()
    config_path = _ensure_config(base_dir)
    return json.loads(config_path.read_text())


def get_base_dir() -> Path:
    """Resolve the base directory.

    Priority:
    1. --base-dir (passed as argument, resolved externally)
    2. $AGISK_BASE_DIR
    3. ~/.agisk/
    """
    env_base = os.environ.get("AGISK_BASE_DIR")
    if env_base:
        return Path(env_base).resolve()
    return _default_base_dir()


def get_skills_dir(base_dir: Path | None = None, config: dict[str, Any] | None = None) -> Path:
    """Resolve the global skills directory.

    Reads from config > fallback <base_dir>/skills/.
    """
    if base_dir is None:
        base_dir = get_base_dir()
    if config is None:
        config = load_config(base_dir)

    skills_dir_str = config.get("skills_dir", "skills")
    p = Path(skills_dir_str)
    if p.is_absolute():
        return p.resolve()
    return (base_dir / p).resolve()


def get_link_target_dir(config: dict[str, Any] | None = None) -> Path:
    """Resolve the target directory for links.

    Reads from config > fallback .agent/skills.
    Resolved relative to CWD.
    """
    if config is None:
        config = load_config()
    target = config.get("link_target_dir", ".agent/skills")
    return (Path.cwd() / Path(target)).resolve()