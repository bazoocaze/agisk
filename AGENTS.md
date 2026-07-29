# AGENTS.md — Agent Integration Guide

This document explains the **agisk** project for AI coding agents that work on this codebase.

## Design Principles

agisk should remain:

- **Small** — focused scope, minimal surface area
- **Dependency-light** — prefer the Python standard library
- **Cross-platform** — works on Linux, macOS, Windows
- **Predictable** — same input, same output
- **Script-friendly** — CLI works non-interactively, exit codes are meaningful
- **Backward compatible** — existing configs and workflows keep working

These principles guide decisions when two implementations are equally correct.

## Priority

When instructions conflict, follow this order:

1. User request
2. System/developer instructions
3. This AGENTS.md
4. Existing project conventions

---

## Hard Requirements

### Commit Messages

Write all commit messages in **English**.

### Version Management

The project version is in `pyproject.toml` (`[project]` → `version`). It is consumed by `uv tool install` / `uv tool upgrade`.

**Before making any change that will be released or committed**, ask the user:

- Whether the version should be incremented
- Which part to bump (major, minor, or patch)

If the user says "yes" or specifies a level, update `pyproject.toml` according to [Semantic Versioning](https://semver.org/):

- **patch** (1.0.0 → 1.0.1): bug fixes, minor tweaks
- **minor** (1.0.0 → 1.1.0): new features, backward compatible
- **major** (1.0.0 → 2.0.0): breaking changes

Do **not** bump without user confirmation.

### Compatibility

Unless requested, preserve:

- CLI compatibility (commands, flags, exit codes)
- Existing config keys (`config.json` schema)
- Existing behavior (deprecated features should remain functional whenever practical)

### Dependencies

Avoid adding dependencies. Prefer the Python standard library unless a dependency is explicitly requested or provides a significant benefit.

---

## Development Conventions

### Code Style

There is no linter, formatter, or type checker configured. Keep code style consistent with what exists.

### Extending Modules

Prefer extending an existing module before creating a new one. Create a new module only when it improves cohesion.

### Refactoring

Refactor only when it directly supports the requested change. Avoid opportunistic cleanup.

### Avoid Unnecessary Changes

Do not:

- Rename public commands or functions
- Reformat unrelated files
- Move modules without request
- Change public behavior while refactoring
- Introduce new dependencies unless requested

### Documentation

If a CLI command changes:

- update `README.md`
- update help text (argparse descriptions, `_epilog()`)
- update examples in documentation

### Tests

If changing behavior:

- update existing tests, or
- add new tests

Do not remove tests unless requested.

---

## Development Commands

```bash
# Install project in editable mode (with dev deps)
uv sync --dev

# Run tests
uv run pytest
uv run pytest tests/ -v           # verbose
uv run pytest tests/test_skills.py  # specific file

# Run the tool directly
uv run agisk --help
uv run python -m agisk list

# Build
uv build
```

---

## Architecture

### High-level data flow

```
CLI (argparse)
  ↓
config (config.json + env vars + flags)
  ↓
resolve directories (skills_dirs, link_target_dirs)
  ↓
dispatch to subcommand
  ↓
business logic (skills.py, install.py, ui.py)
  ↓
filesystem (symlinks, dirs, SKILL.md files)
```

### Data flow in `main()` (cli.py)

1. Parse args → resolve `config_path` (flag → env → `~/.agisk/config.json`)
2. `load_config()` → read `config.json`
3. `get_skills_dirs()` → `list[Path]` of global skills directories (config key `skills_dirs`, fallback to deprecated `skills_dir`)
4. `get_link_target_dirs()` → `list[Path]` of link target directories (config key `link_target_dirs` (list) or fallback to `link_target_dir` (string))
5. Dispatch to subcommand (`use`/`disable`/`install`/`list`/`active`/`doctor`)

Each subcommand calls the corresponding function in `skills.py`, `ui.py`, or `install.py`. The `yaml.py` parser is used by `install.py` and `skill.py` to extract `name` from SKILL.md frontmatter.

Interactive mode (`use` with no args on a TTY) is handled by `ui.py` via `questionary`.

---

## Adding a New Feature

### CLI Pattern

To add a new subcommand, follow the existing pattern in `cli.py`:

1. **Document in `_epilog()`** — add a line like `export <skill>    Export skill to a tar file`
2. **Add an `elif` block** in `main()` after the existing subcommands (before the final `else`)
3. **Implement the logic** in the appropriate module (`skills.py`, `install.py`, or a new one)

### Module Pattern

Each function in `skills.py` and `install.py` follows:

```python
def function_name(param: str, dir_path: Path, ...) -> bool:
    validate_skill_name(param)
    # do work
    return True  # or False if no-op
```

- Return `bool`: `True` = action performed, `False` = no-op (already exists, cancelled)
- Raise `FileNotFoundError`, `ValueError`, `NotADirectoryError` for errors
- Validate skill names with `validate_skill_name()` from `skill.py` (rejects `/`, `\\`, `..`, empty)
- Skill names **must not** contain `/`, `\\`, or `..` — this is a simple string check, not a full path traversal analysis

### Error Pattern in CLI

```python
try:
    result = some_function(args, ...)
    if result:
        print(f"Success: {args}")
except (FileNotFoundError, ValueError, NotADirectoryError) as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
```

---

## Testing

Fixtures shared via `tests/conftest.py`:

| Fixture | What it provides |
|---------|-----------------|
| `tmp_base_dir` | Temporary `~/.agisk` directory (Path) |
| `tmp_skills_dir` | Global skills subdirectory (Path) |
| `tmp_config` | config.json fixture (dict) |
| `sample_skill_dir` | Temp directory with SKILL.md inside (Path) |
| `sample_skill_md` | Standalone SKILL.md file (Path) |

Tests mirror source modules: `test_cli.py` ↔ `cli.py`, `test_skills.py` ↔ `skills.py`, etc. Use `tmp_path` for isolated filesystem tests.

---

## Project File Reference

### Root

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package config, entry point `agisk = agisk.cli:main` |
| `README.md` | End-user documentation |
| `AGENTS.md` | This file |

### Source — `src/agisk/`

| File | Purpose |
|------|---------|
| `__init__.py` | Package marker |
| `__main__.py` | Entry point for `python -m agisk` |
| `cli.py` | CLI argument parsing (`argparse`) and `main()` dispatcher |
| `config.py` | Loads `config.json`, resolves dirs from env vars, flags, and defaults. `get_link_target_dirs()` returns `list[Path]` — reads `link_target_dirs` (list) or falls back to `link_target_dir` (string) |
| `skill.py` | `Skill` dataclass, `Skill.from_dir()`, `validate_skill_name()` |
| `skills.py` | Core: `enable_skill()`, `disable_skill()`, `list_skills()`, `active_skills()`, `find_duplicates()` (used by `doctor`). All functions accept `link_target_dirs: list[Path]` for multiple link targets |
| `install.py` | `install_from_path()` — copies skill into global dir |
| `ui.py` | Interactive mode (`questionary` checkbox) for `use` subcommand |
| `yaml.py` | Minimal YAML frontmatter parser (`parse_frontmatter`, `get_skill_name_from_skillmd`) |

### Tests — `tests/`

| File | Purpose |
|------|---------|
| `conftest.py` | Shared fixtures (see table above) |
| `test_cli.py` | CLI argument parsing and flags |
| `test_config.py` | Config loading, env vars, defaults |
| `test_skill.py` | `Skill` dataclass, `Skill.from_dir()` edge cases |
| `test_skills.py` | Enable/disable/list/active |
| `test_install.py` | Install from dir, file, symlink rejection, overwrite |
| `test_yaml.py` | Frontmatter parsing, edge cases, missing fields |