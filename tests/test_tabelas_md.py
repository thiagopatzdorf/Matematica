"""Guarda: tabela Markdown com `|` solto dentro da célula.

Por que existe: no GFM, todo `|` não escapado separa célula, inclusive dentro de crases
(`|U|`, `|Stab|`, `Σ |G|/|Aut(C)|`). A linha ganha colunas a mais e o GitHub corta o
excedente; se for o cabeçalho, a tabela inteira deixa de existir e vira texto cru
(docs/attack/SETCOVER_2026-10-04.md e docs/exatos/LP_FATIA_TERNARIO.md estavam assim).
Barra de conteúdo se escreve `\\|`.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DELIMITADOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
CERCA = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def colunas(linha: str) -> int:
    linha = linha.strip().replace("\\|", "")
    linha = linha[1:] if linha.startswith("|") else linha
    linha = linha[:-1] if linha.endswith("|") else linha
    return len(linha.split("|"))


def linhas_tortas(texto: str) -> list[tuple[int, int, int]]:
    """(linha, colunas achadas, colunas do delimitador) de cada linha de tabela torta."""
    linhas = texto.split("\n")
    achados, cerca = [], False
    for i, linha in enumerate(linhas):
        if CERCA.match(linha):
            cerca = not cerca
        if cerca or i + 1 >= len(linhas) or "|" not in linha or not DELIMITADOR.match(linhas[i + 1]):
            continue
        esperado = colunas(linhas[i + 1])
        corpo = [i]
        j = i + 2
        while j < len(linhas) and "|" in linhas[j] and linhas[j].strip():
            corpo.append(j)
            j += 1
        achados += [(k + 1, colunas(linhas[k]), esperado) for k in corpo if colunas(linhas[k]) != esperado]
    return achados


def test_tabela_md_com_barra_solta_ganha_coluna_e_o_github_corta():
    saida = subprocess.run(["git", "ls-files", "*.md"], cwd=RAIZ, capture_output=True, text=True, check=True)
    problemas = [
        f"{p}:{n}: {achadas} colunas, o delimitador tem {esperadas} (escape o `|` de conteúdo como `\\|`)"
        for p in saida.stdout.split()
        for n, achadas, esperadas in linhas_tortas((RAIZ / p).read_text(encoding="utf-8"))
    ]
    assert not problemas, "\n".join(problemas)


def test_detector_pega_modulo_entre_crases_na_celula():
    assert linhas_tortas("| a | b |\n|---|---|\n| `|U|` | 1 |\n") == [(3, 4, 2)]
    assert linhas_tortas("| a | b |\n|---|---|\n| `\\|U\\|` | 1 |\n") == []
