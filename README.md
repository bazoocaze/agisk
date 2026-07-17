# agisk

**agisk** (Agent + Skills) — Gerenciador de links simbólicos para skills de agentes.

Permite gerenciar skills de agentes de forma centralizada, com instalação, listagem e
ativação via links simbólicos.

## Instalação

```bash
# Via uv (recomendado)
uv tool install git+https://github.com/usuario/agisk

# Ou via pip
pip install git+https://github.com/usuario/agisk
```

## Comandos

### `agisk use|enable <skill> [<skill> ...]`

Cria link(s) simbólico(s) da(s) skill(s) no projeto atual.

```bash
# Linkar uma skill
agisk use my-coding-skill
agisk enable my-coding-skill

# Múltiplas skills de uma vez
agisk use skill-a skill-b skill-c
```

### `agisk disable <skill> [<skill> ...]`

Remove link(s) simbólico(s) da(s) skill(s).

```bash
agisk disable my-coding-skill
agisk disable skill-a skill-b
```

### `agisk install <caminho>`

Instala uma skill no diretório global de skills.

- Se for um **diretório**: deve conter `SKILL.md`. Copia o diretório inteiro.
- Se for um **arquivo SKILL.md**: extrai o campo `name` do frontmatter YAML.

```bash
# Instalar a partir de um diretório
agisk install ~/projetos/minha-skill

# Instalar a partir de um arquivo SKILL.md
agisk install ~/Downloads/SKILL.md
```

### `agisk list`

Lista as skills disponíveis no diretório global.

```bash
agisk list
```

### `agisk linked`

Lista as skills atualmente linkadas no projeto atual.

```bash
agisk linked
```

## Flags

| Flag | Descrição |
|------|-----------|
| `--base-dir DIR` | Diretório base (prioridade sobre `$AGISK_BASE_DIR`) |
| `--force` | Sobrescrever sem perguntar |
| `--verbose`, `-v` | Saída detalhada |

## Configuração

### Arquivo de configuração

O arquivo de configuração fica em `<base_dir>/config.json` (padrão: `~/.agisk/config.json`).

```json
{
  "skills_dir": "skills",
  "link_target_dir": ".agent/skills"
}
```

### Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `AGISK_BASE_DIR` | Diretório base (fallback: `~/.agisk/`) |
| `AGISK_SKILLS_DIR` | Diretório global de skills |
| `AGISK_CONFIG` | Caminho para arquivo JSON de configuração |

### Prioridade de resolução

1. `--base-dir` (flag)
2. `$AGISK_BASE_DIR` (variável de ambiente)
3. `~/.agisk/` (fallback)

## Estrutura de Diretórios

```
~/.agisk/                  # Diretório base
├── skills/                # Diretório global de skills
│   ├── my-skill-1/
│   │   ├── SKILL.md
│   │   └── ...
│   └── my-skill-2/
│       ├── SKILL.md
│       └── ...
└── config.json            # Configuração da ferramenta
```

```
meu-projeto/               # Projeto atual ($PWD)
└── .agent/
    └── skills/            # Links simbólicos (criados por agisk use)
        ├── my-skill-1 -> ~/.agisk/skills/my-skill-1
        └── my-skill-2 -> ~/.agisk/skills/my-skill-2
```

## Formato SKILL.md

```markdown
---
name: my-skill
description: Descrição da skill
version: 1
---

# My Skill

Conteúdo da skill...
```

O campo `name` no frontmatter é usado pelo `agisk install` para nomear o diretório
da skill quando instalada a partir de um arquivo `SKILL.md` avulso.

## Desenvolvimento

```bash
git clone https://github.com/usuario/agisk
cd agisk
uv venv
uv pip install -e .
pytest tests/
```

## Licença

MIT
