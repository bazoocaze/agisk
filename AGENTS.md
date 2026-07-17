# AGENTS.md — Agent Integration Guide

This document explains how AI coding agents (like **pi**, Claude Code, Cline, Aider, etc.) can consume and use **agisk** skills.

## Agent Instructions

When working on this project, always write commit messages in **English**.

---

## Overview

**agisk** manages symbolic links to agent skills. Each skill is a directory containing a `SKILL.md` file (and optionally other files). Agent tools can read these linked skills to discover available capabilities, instructions, or context files.

## Skill Structure

A skill is a directory placed under the global skills directory (`~/.agisk/skills/` by default) and linked into a project's `.agent/skills/` folder.

```
~/.agisk/skills/
├── my-coding-skill/
│   ├── SKILL.md
│   ├── instructions.md
│   └── examples/
│       └── sample.py
└── my-review-skill/
    └── SKILL.md
```

## How Agents Can Consume Skills

### 1. Reading Linked Skills at Startup

An agent can scan `.agent/skills/` to discover which skills are active in the current project:

```python
from pathlib import Path

skills_dir = Path.cwd() / ".agent" / "skills"
if skills_dir.exists():
    active_skills = [p for p in skills_dir.iterdir() if p.is_dir() or p.is_symlink()]
    for skill in active_skills:
        skill_md = skill / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text()
            # Parse frontmatter, inject instructions, etc.
```

### 2. Parsing SKILL.md Frontmatter

Each `SKILL.md` can contain YAML frontmatter for metadata:

```markdown
---
name: my-coding-skill
description: Coding guidelines for Python projects
version: 1
tags: [python, coding, style]
model: claude-3.5-sonnet
---

# My Coding Skill

Instructions and context for the agent...
```

Agents should parse the `---` delimited frontmatter (top-level key/value pairs) to extract metadata like `name`, `description`, `tags`, or even a preferred `model`.

### 3. Using Skills as Context Directories

Skills can bundle multiple files. An agent may:

- Read all `.md` files inside a skill directory as supplemental instructions
- Use files like `instructions.md`, `rules.yaml`, or `prompts/` as context
- Treat each skill as a **plugin** that adds capabilities or constraints

```python
for skill in active_skills:
    for file in skill.rglob("*.md"):
        content = file.read_text()
        # Merge into system prompt or context
```

### 4. Detecting Skills via Environment or Config

Agents can also discover the global skills directory via the environment variable:

- `AGISK_BASE_DIR` — custom base directory (default: `~/.agisk/`)

```python
import os
from pathlib import Path

base_dir = Path(os.environ.get("AGISK_BASE_DIR", Path.home() / ".agisk"))
skills_dir = base_dir / "skills"
```

## Recommended Agent Integration Patterns

### Pattern A: Startup Hook

On project open, the agent checks `.agent/skills/` and loads all `SKILL.md` files into its system prompt or context.

```python
def load_active_skills():
    skills_path = Path.cwd() / ".agent" / "skills"
    if not skills_path.exists():
        return []
    contexts = []
    for entry in skills_path.iterdir():
        skill_md = entry / "SKILL.md"
        if skill_md.exists():
            contexts.append({"name": entry.name, "content": skill_md.read_text()})
    return contexts
```

### Pattern B: Skill as Command Provider

A skill directory may contain executable scripts or agent commands. The agent reads a manifest (e.g., `commands.json`) inside the skill and registers them.

```
my-tool-skill/
├── SKILL.md
├── commands.json     # { "command": "...", "handler": "..." }
└── handlers/
    └── tool.py
```

### Pattern C: Layered Skill Composition

Multiple skills can be linked simultaneously. The agent loads them in order, merging or overriding instructions.

```python
# Loading order matters: later skills can override earlier ones
skills = sorted(active_skills)
for skill in skills:
    apply_skill_instructions(skill)
```

## Example: pi Agent Integration

For **pi** (the coding agent harness), skills can be discovered automatically:

```yaml
# pi configuration (config.yaml)
skills:
  auto_discover: true
  directory: .agent/skills
```

Or loaded explicitly in a pi extension:

```python
# pi extension
from pathlib import Path

def load_skills(tool_context):
    skills_dir = Path.cwd() / ".agent" / "skills"
    if skills_dir.exists():
        for skill in skills_dir.iterdir():
            if skill.is_symlink() or skill.is_dir():
                skill_md = skill / "SKILL.md"
                if skill_md.exists():
                    tool_context.add_context(skill_md.read_text())
```

## Security Considerations

- **Path traversal**: Agents should validate skill names don't contain `..` or `/` when accessing files
- **Trust boundary**: Skills are symlinked from a central location. Agents should verify the source is trusted before executing any code from a skill directory
- **File permissions**: Config files (`config.json`) use permissions `600` (owner-only)

## Project File Reference

Below is every file in the `agisk` project with a short description of its purpose. An agent can read this summary to quickly understand the codebase layout.

### Root

| File | Purpose |
|------|---------|
| `pyproject.toml` | Python package config (`uv tool install`), entry point `agisk = agisk.cli:main` |
| `README.md` | End-user documentation (commands, install, config) |
| `AGENTS.md` | This file — agent integration guide |
| `GOAL.md` | Original requirements (Portuguese) |
| `PLAN.md` | Implementation plan (Portuguese) |

### Source — `src/agisk/`

| File | Purpose |
|------|---------|
| `__init__.py` | Package marker |
| `__main__.py` | Entry point for `python -m agisk` |
| `cli.py` | CLI argument parsing (`argparse`) and `main()` dispatcher |
| `config.py` | Loads `config.json`, resolves `skills_dir` and `link_target_dir` from env vars, flags, and defaults |
| `skills.py` | Core operations: `enable_skill()`, `disable_skill()`, `list_skills()`, `linked_skills()` |
| `install.py` | `install_from_path()` — copies a skill directory or `SKILL.md` file into the global skills dir |
| `yaml.py` | Minimal inline YAML frontmatter parser (`parse_frontmatter`, `get_skill_name_from_skillmd`) |

### Tests — `tests/`

| File | Purpose |
|------|---------|
| `conftest.py` | `pytest` fixtures: `tmp_base_dir`, `tmp_skills_dir`, `tmp_config`, `sample_skill_dir`, `sample_skill_md` |
| `test_cli.py` | Tests for argument parsing and flags |
| `test_config.py` | Tests for config loading, env vars, default creation |
| `test_skills.py` | Tests for enable/disable/list/linked operations |
| `test_install.py` | Tests for install from directory, file, symlink rejection, overwrite logic |
| `test_yaml.py` | Tests for frontmatter parsing, edge cases, missing fields |

## Quick Reference

| Path | Purpose |
|------|---------|
| `~/.agisk/skills/<name>/` | Global skill storage |
| `.agent/skills/<name>` | Project-local symlink (created by `agisk use`) |
| `.agent/skills/<name>/SKILL.md` | Main skill metadata + content |
| `~/.agisk/config.json` | Tool configuration |