# agisk

**agisk** (Agent + Skills) — Symbolic link manager for agent skills.

Allows managing agent skills in a centralized way, with installation, listing, and
activation via symbolic links.

## Installation

```bash
# Via uv (recommended)
uv tool install git+https://github.com/usuario/agisk

# Or via pip
pip install git+https://github.com/usuario/agisk
```

## Commands

### `agisk use|enable <skill> [<skill> ...]`

Creates symbolic link(s) of the skill(s) in the current project.

**Interactive mode** (no arguments, TTY): opens a checkbox listing all available
skills, pre-populated with currently linked ones. Toggle with space, confirm with
enter — links are created/removed accordingly.

```bash
# Interactive mode — select skills via checkbox
agisk use

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

## Flags

| Flag | Description |
|------|-------------|
| `--base-dir DIR` | Base directory (takes precedence over `$AGISK_BASE_DIR`) |
| `--force` | Overwrite without asking |
| `--verbose`, `-v` | Verbose output |

## Configuration

### Configuration file

The configuration file is at `<base_dir>/config.json` (default: `~/.agisk/config.json`).

```json
{
  "skills_dir": "skills",
  "link_target_dir": ".agent/skills"
}
```

### Environment variables

| Variable | Description |
|----------|-------------|
| `AGISK_BASE_DIR` | Base directory (fallback: `~/.agisk/`) |

### Resolution priority

1. `--base-dir` (flag)
2. `$AGISK_BASE_DIR` (environment variable)
3. `~/.agisk/` (fallback)

## Directory Structure

```
~/.agisk/                  # Base directory
├── skills/                # Global skills directory
│   ├── my-skill-1/
│   │   ├── SKILL.md
│   │   └── ...
│   └── my-skill-2/
│       ├── SKILL.md
│       └── ...
└── config.json            # Tool configuration
```

```
my-project/                # Current project ($PWD)
└── .agent/
    └── skills/            # Symbolic links (created by agisk use)
        ├── my-skill-1 -> ~/.agisk/skills/my-skill-1
        └── my-skill-2 -> ~/.agisk/skills/my-skill-2
```

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

## Development

```bash
git clone https://github.com/usuario/agisk
cd agisk
uv venv
uv pip install -e .
pytest tests/
```

## License

MIT
