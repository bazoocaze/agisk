from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _default_config() -> dict[str, Any]:
    return {
        "skills_dir": "skills",
        "link_target_dir": ".agent/skills",
    }


def get_config_path(explicit: Path | None = None) -> Path:
    if explicit is not None:
        p = explicit.resolve()
    else:
        env = os.environ.get("AGISK_CONFIG_FILE")
        if env:
            p = Path(env).resolve()
        else:
            p = (Path.home() / ".agisk" / "config.json").resolve()

    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        cfg = _default_config()
        p.write_text(json.dumps(cfg, indent=2) + "\n")
        p.chmod(0o600)
    return p


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    if config_path is None:
        config_path = get_config_path()
    return json.loads(config_path.read_text())


def get_skills_dir(config: dict[str, Any], config_path: Path) -> Path:
    base_dir = config_path.parent.resolve()
    skills_dir_str = config.get("skills_dir", "skills")
    p = Path(skills_dir_str)
    if p.is_absolute():
        return p.resolve()
    return (base_dir / p).resolve()


def get_link_target_dir(config: dict[str, Any] | None = None) -> Path:
    if config is None:
        config = load_config()
    target = config.get("link_target_dir", ".agent/skills")
    return (Path.cwd() / Path(target)).resolve()