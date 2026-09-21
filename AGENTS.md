# AGENTS.md — Agent Integration Guide

Guidelines for AI agents working on this project. **MUST** = mandatory; **PREFER** = tiebreaker when two implementations are equally correct.

## Priority

When instructions conflict, follow this order:

1. User request
2. System/developer instructions
3. This AGENTS.md
4. Existing project conventions

## Rules & Principles

### MUST

- **Commits in English.**
- **Before any change that will be committed or released**: ask the user whether the version should be bumped and which part (patch = bug fix, minor = backward-compatible feature, major = breaking). Do not bump without confirmation. Version lives in `pyproject.toml` (`[project].version`), consumed by `uv tool install` / `uv tool upgrade`.
- **No new dependencies** — prefer the standard library, unless explicitly requested or a significant benefit.
- **Preserve compatibility** (unless requested): CLI (commands, flags, exit codes), `config.json` schema, behavior of deprecated features.

### PREFER

- **Small** — focused scope, minimal surface area
- **Cross-platform** — Linux, macOS, Windows
- **Predictable** — same input, same output
- **Script-friendly** — non-interactive CLI, meaningful exit codes
- **Backward compatible** — existing configs and workflows keep working

## Changing Code

- **Style**: no linter/formatter/type-checker configured — match existing code.
- **Minimal scope**: do not rename public commands/functions, do not reformat unrelated files, do not move modules, refactor only when the change requires it.
- **Extend** an existing module before creating a new one (create only if it improves cohesion).
- **CLI changed** → update `README.md`, help text (argparse + `_epilog()`), examples.
- **Behavior changed** → update or add tests (see Testing). Do not remove tests unless requested.

## Commands

```bash
uv sync --dev              # install (editable, with dev deps)
uv run pytest              # run tests
uv run pytest tests/ -v    # verbose
uv run pytest tests/test_skills.py   # specific file
uv run agisk --help        # run the tool
uv run python -m agisk list
uv build                   # build
```

## Architecture

```
CLI (argparse) → config (config.json + env vars + flags) → resolve dirs
(skills_dirs, link_target_dirs) → dispatch subcommand → business logic
(skills.py, install.py, ui.py) → filesystem (symlinks, dirs, SKILL.md)
```

In `main()` (cli.py): parse args → resolve `config_path` (flag → env → `~/.agisk/config.json`) → `load_config()` → `get_skills_dirs()` (list, or deprecated fallback `skills_dir`) and `get_link_target_dirs()` (list, or fallback `link_target_dir`) → dispatch (`use`/`disable`/`install`/`list`/`active`/`doctor`). Each subcommand calls the matching function in `skills.py`, `ui.py` or `install.py`; `yaml.py` extracts `name` from SKILL.md frontmatter. Interactive mode (`use` without args on a TTY) is handled by `ui.py`/`questionary`.

## Patterns

### New subcommand (CLI)

1. Document it in `_epilog()` — e.g. `export <skill>    Export skill to a tar file`
2. Add an `elif` block in `main()` before the final `else`
3. Implement the logic in the appropriate module (`skills.py`, `install.py`, or a new one)

### Module (skills.py, install.py)

```python
def function_name(param: str, dir_path: Path, ...) -> bool:
    validate_skill_name(param)
    # do work
    return True  # True = action performed, False = no-op (already exists, cancelled)
```

- Errors: `FileNotFoundError` / `ValueError` / `NotADirectoryError`
- Names validated with `validate_skill_name()` from `skill.py` (rejects `/`, `\`, `..`, empty — simple string check, not full path traversal analysis)

### CLI error handling

```python
try:
    result = fn(args, ...)
    if result:
        print(f"Success: {args}")
except (FileNotFoundError, ValueError, NotADirectoryError) as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

## Testing

Fixtures live in `tests/conftest.py`: `tmp_base_dir`, `tmp_skills_dir`, `tmp_config`, `sample_skill_dir`, `sample_skill_md`. Tests mirror the source modules (`test_cli.py` ↔ `cli.py`, `test_skills.py` ↔ `skills.py`, ...). Use `tmp_path` for isolated filesystem tests.

## File Reference

| Path | Purpose |
|------|---------|
| `pyproject.toml` | Package config, entry point `agisk = agisk.cli:main` |
| `README.md` | End-user documentation |
| `src/agisk/cli.py` | argparse + `main()` dispatcher |
| `src/agisk/config.py` | config.json, env vars, defaults; `get_link_target_dirs()` → `list[Path]` |
| `src/agisk/skill.py` | `Skill`, `Skill.from_dir()`, `validate_skill_name()` |
| `src/agisk/skills.py` | `enable_skill`, `disable_skill`, `list_skills`, `active_skills`, `find_duplicates` — all accept `link_target_dirs: list[Path]` |
| `src/agisk/install.py` | `install_from_path()` — copies skill into global dir |
| `src/agisk/ui.py` | Interactive mode (`questionary` checkbox) for `use` |
| `src/agisk/yaml.py` | Minimal frontmatter parser (`parse_frontmatter`, `get_skill_name_from_skillmd`) |
| `tests/` | `conftest.py` (fixtures) + `test_*.py` mirroring modules |