# agisk

[![CI](https://github.com/bazoocaze/agisk/actions/workflows/ci.yml/badge.svg)](https://github.com/bazoocaze/agisk/actions/workflows/ci.yml)

**agisk** (Agent + Skills) — A package manager for AI agent skills.

> **Install AI agent skills once. Reuse them across every project and every coding agent.**

## Quick Start

```bash
# 1. Install agisk
uv tool install git+https://github.com/bazoocaze/agisk

# 2. Install a skill
agisk install ~/Downloads/my-skill

# 3. Activate it in your project
cd my-project
agisk use my-skill

# 4. See the result
tree .agents
```

In under 30 seconds you have a skill installed and linked in your project.

---

## What problem does it solve?

**Without agisk**

```
~/.claude/skills/
~/.pi/skills/
~/.opencode/skills/
project-a/.agents/skills/
project-b/.agents/skills/

Everything gets duplicated.
```

**With agisk**

```
~/.agisk/skills/
        │
        ├── python
        ├── aws
        └── docker

Projects only contain symbolic links → no duplication.
```

Agent skills are reusable prompt packages (usually distributed as a `SKILL.md` file plus optional resources) consumed by AI coding agents. Without a manager, you copy them into every project and every agent's config — and updating means updating each copy.

**agisk** installs, validates and activates agent skills by creating symbolic links,
allowing multiple agents to share the same skill library without duplication.

### Compatible with

| Agent | How it reads skills |
|-------|-------------------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) | `.claude/skills/` directory |
| [Pi](https://github.com/earendil-works/pi-coding-agent) | `.pi/skills/` directory |
| [OpenCode](https://github.com/sst/opencode) | `.opencode/skills/` directory |
| Any tool with `skills_dirs` config | Configurable via `link_target_dirs` |

---

## Installation

```bash
# Via uv (recommended)
uv tool install git+https://github.com/bazoocaze/agisk

# Or via pip
pip install git+https://github.com/bazoocaze/agisk
```

---

## Why symbolic links?

- **Single source of truth** — install once, update once, reuse everywhere.
- **Zero duplication** — no copying skills across projects or agent configs.
- **Instant updates** — update the skill in one place, all projects pick it up.
- **Git-friendly** — links are small text files, not bloated directories.
- **No vendor lock-in** — works with Claude Code, Pi, OpenCode, and any tool that reads a skills directory.

---

## Commands

### `agisk use|enable <skill> [<skill> ...]`

Creates symbolic link(s) of the skill(s) in the current project.

**Interactive mode** (no arguments, TTY): opens a checkbox listing all available
skills, pre-populated with currently linked ones. Toggle with space, confirm with
enter — links are created/removed accordingly.

```
$ agisk use

[ ] docker
[x] python
[ ] rust
[x] aws

Space: toggle  |  Enter: confirm
```

```bash
# Link specific skill(s)
agisk use my-coding-skill
agisk enable my-coding-skill

# Multiple skills at once
agisk use skill-a skill-b skill-c
```

### `agisk disable <skill> [<skill> ...]`

Removes symbolic link(s) of the skill(s).

```bash
agisk disable my-coding-skill
agisk disable skill-a skill-b
```

### `agisk install <path>`

Installs a skill into the global skills directory.

- If it is a **directory**: it must contain `SKILL.md`. Copies the entire directory.
- If it is a `SKILL.md` **file**: extracts the `name` field from the YAML frontmatter.

```bash
# Install from a directory
agisk install ~/projects/my-skill

# Install from a SKILL.md file
agisk install ~/Downloads/SKILL.md
```

### `agisk list`

Lists the skills available in the global directory.

```bash
agisk list
```

### `agisk linked`

Lists the skills currently linked in the current project.

```bash
agisk linked
```

### `agisk doctor`

Validates all installed skills, showing errors, warnings, and duplicate names across
multiple skills directories.

```bash
agisk doctor
```

---

## Flags

| Flag | Description |
|------|-------------|
| `--config PATH` | Config file path (takes precedence over `$AGISK_CONFIG_FILE`) |
| `--force` | Overwrite without asking |
| `--verbose`, `-v` | Verbose output |

```bash
# Force overwrite an existing link
agisk use --force my-skill

# Force overwrite on install
agisk install --force ~/projects/my-skill

# Verbose output
agisk --verbose list
agisk -v linked
```

---

## Configuration

### Configuration file

The configuration file is at `~/.agisk/config.json` by default — override with `--config` or `$AGISK_CONFIG_FILE`.

```json
{
  "skills_dirs": ["skills"],
  "link_target_dir": ".agents/skills",
  "link_target_dirs": [".agents/skills", ".agents/pi-skills"]
}
```

> **Note:** The key `skills_dir` (singular, string) is deprecated. Use `skills_dirs` (plural, list) instead.
> The key `link_target_dir` (string) is still supported. For multiple link targets, use `link_target_dirs` (list of strings). When both are present, `link_target_dirs` takes precedence.

### Environment variables

| Variable | Description |
|----------|-------------|
| `AGISK_CONFIG_FILE` | Config file path (fallback: `~/.agisk/config.json`) |

### Resolution priority

1. `--config` (flag)
2. `$AGISK_CONFIG_FILE` (environment variable)
3. `~/.agisk/config.json` (fallback)

---

## Directory Structure

```
~/.agisk/                  # Base directory
│
├── skills/                # Global skills directory
│   ├── python/
│   ├── aws/
│   └── docker/
│
└── config.json            # Tool configuration


my-project/                # Current project ($PWD)
│
└── .agents/
    └── skills/            # Symbolic links (created by agisk use)
        ├── python -> ~/.agisk/skills/python
        ├── aws    -> ~/.agisk/skills/aws
        └── docker -> ~/.agisk/skills/docker
```

---

## SKILL.md Format

```markdown
---
name: my-skill
description: Skill description
version: 1
---

# My Skill

Skill content...
```

The `name` field in the frontmatter is used by `agisk install` to name the skill
directory when installed from a standalone `SKILL.md` file.

---

## Development

```bash
git clone https://github.com/bazoocaze/agisk
cd agisk
uv sync --dev
uv run pytest
```

---

## License

MIT