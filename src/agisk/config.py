from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


DEFAULT_SKILLS_DIRS = ["skills"]
DEFAULT_LINK_TARGET_DIR = ".agents/skills"


def _default_config() -> dict[str, Any]:
    return {
        "skills_dirs": DEFAULT_SKILLS_DIRS,
        "link_target_dir": DEFAULT_LINK_TARGET_DIR,
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


def get_skills_dirs(config: dict[str, Any], config_path: Path) -> list[Path]:
    base_dir = config_path.parent.resolve()

    dirs: list[str] | None = config.get("skills_dirs")
    if dirs is not None:
        if not isinstance(dirs, list):
            raise ValueError("'skills_dirs' must be a list of paths")
        return [_resolve_skills_dir(d, base_dir) for d in dirs]

    old = config.get("skills_dir")
    if old is not None:
        print(
            "⚠️  Config key 'skills_dir' is deprecated, use 'skills_dirs' (list)",
            file=sys.stderr,
        )
        return [_resolve_skills_dir(old, base_dir)]

    return [_resolve_skills_dir(DEFAULT_SKILLS_DIRS[0], base_dir)]


def _resolve_skills_dir(dir_str: str, base_dir: Path) -> Path:
    p = Path(dir_str).expanduser()
    if p.is_absolute():
        return p.resolve()
    return (base_dir / p).resolve()


def get_link_target_dir(config: dict[str, Any] | None = None) -> Path:
    if config is None:
        config = load_config()
    target = config.get("link_target_dir", DEFAULT_LINK_TARGET_DIR)
    return (Path.cwd() / Path(target)).resolve()