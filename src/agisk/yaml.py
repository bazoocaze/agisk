from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Extrai frontmatter YAML entre '---' delimitadores no início do texto.

    Faz parse apenas de chaves/valores simples no top-level:
    - chave: valor
    - Não suporta aninhamento, listas, ou quoted strings complexas.
    - Strings sem aspas, números, booleanos.
    """
    # Padrão: começo da string, opcional whitespace, ---, newline, conteúdo, ---
    m = re.match(r"^\s*---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}

    content = m.group(1)
    result: dict[str, Any] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        # Tenta converter para tipos básicos
        if value.lower() in ("true", "yes", "on"):
            result[key] = True
        elif value.lower() in ("false", "no", "off"):
            result[key] = False
        elif value == "~" or value.lower() == "null":
            result[key] = None
        else:
            # Tenta inteiro ou float
            try:
                result[key] = int(value)
            except ValueError:
                try:
                    result[key] = float(value)
                except ValueError:
                    result[key] = value
    return result


def get_skill_name_from_skillmd(path: Path) -> str:
    """Lê um arquivo SKILL.md, extrai o frontmatter e retorna o campo 'name'."""
    text = path.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)
    name = frontmatter.get("name")
    if not name:
        raise ValueError(
            f"Campo 'name' não encontrado no frontmatter de {path}"
        )
    return str(name)