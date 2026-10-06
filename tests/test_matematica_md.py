"""Guarda: matemática em Markdown que o GitHub estraga.

Por que existe: o Markdown do GitHub aplica os escapes de barra invertida ANTES de
renderizar a matemática. Dentro de `$$...$$` ou `$...$`, `\\{` vira `{`, `\\;` vira `;`,
`\\,` vira `,`, e assim por diante. O resultado foi o erro vermelho
"Missing or unrecognized delimiter for \\bigl" em docs/PHILOSOPHY.md e pontos e
vírgulas literais em `lower \\le K_q(n,R) \\le upper`.

O que é seguro (documentação do GitHub, "Writing mathematical expressions"):
  - matemática em bloco dentro de uma cerca ```math (o conteúdo não passa pelo Markdown);
  - matemática na linha no formato $`...`$ (o conteúdo é um code span).

Este teste falha se algum .md versionado tiver `$$...$$` ou `$...$` fora dessas duas
formas com barra invertida seguida de pontuação ASCII (o conjunto que o CommonMark
trata como escape: `\\{ \\} \\; \\, \\! \\\\ \\|` e os demais).
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# Pontuação ASCII que o CommonMark aceita depois de `\` como escape.
_PONTUACAO = re.escape("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
ESCAPE_COMIDO = re.compile(r"\\[" + _PONTUACAO + "]")

CERCA = re.compile(r"^ {0,3}(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)
BLOCO = re.compile(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$", re.S)
# Como no pandoc: o `$` de fechamento não pode vir colado a um dígito ("US$1 ... US$25").
LINHA = re.compile(r"(?<![\\$])\$(?![\s$])([^$\n]+?)(?<![\s\\])\$(?![$\d])")


def _sem_cercas(texto: str) -> str:
    """Troca o conteúdo de blocos cercados (inclusive ```math) por linhas vazias."""
    saida: list[str] = []
    abertura: str | None = None
    anterior_vazia_ou_codigo = True
    for linha in texto.splitlines():
        m = CERCA.match(linha)
        if abertura is None:
            # Bloco de código indentado (4 espaços depois de linha vazia): shell com $VAR, não matemática.
            if linha.startswith(("    ", "\t")) and anterior_vazia_ou_codigo:
                saida.append("")
                continue
            anterior_vazia_ou_codigo = not linha.strip()
            if m:
                abertura = m.group(1)
                saida.append("")
                continue
            saida.append(linha)
        else:
            if m and m.group(1)[0] == abertura[0] and len(m.group(1)) >= len(abertura) \
                    and linha.strip() == m.group(1):
                abertura = None
            saida.append("")
    return "\n".join(saida)


def matematica_quebrada(texto: str) -> list[tuple[int, str]]:
    """Devolve (linha, trecho) de cada expressão que o GitHub vai estragar."""
    texto = _sem_cercas(texto)
    # Code spans (inclusive o miolo de $`...`$) saem, preservando as quebras de linha.
    texto = CODE_SPAN.sub(lambda m: "C" * 1 + "\n" * m.group(0).count("\n"), texto)
    achados: list[tuple[int, str]] = []
    for padrao in (BLOCO, LINHA):
        for m in padrao.finditer(texto):
            if ESCAPE_COMIDO.search(m.group(1)):
                achados.append((texto.count("\n", 0, m.start()) + 1, m.group(0)[:80]))
        if padrao is BLOCO:
            texto = BLOCO.sub(lambda m: "B" + "\n" * m.group(0).count("\n"), texto)
    return sorted(achados)


def _md_versionados() -> list[Path]:
    saida = subprocess.run(["git", "ls-files", "*.md"], cwd=RAIZ, capture_output=True, text=True, check=True)
    return [RAIZ / p for p in saida.stdout.split()]


def test_matematica_em_md_com_escape_que_o_github_come():
    problemas = []
    for caminho in _md_versionados():
        for linha, trecho in matematica_quebrada(caminho.read_text(encoding="utf-8")):
            problemas.append(f"{caminho.relative_to(RAIZ)}:{linha}: {trecho}")
    assert not problemas, (
        "Matemática que o GitHub renderiza errado (use ```math para bloco e $`...`$ na linha):\n"
        + "\n".join(problemas)
    )


def test_detector_pega_o_bigl_que_virou_erro_vermelho():
    ruim = r"$$K \;=\; \min\bigl\{\,|C| \,\bigr\}$$"
    assert matematica_quebrada(ruim)
    assert matematica_quebrada(r"limite $a \;\le\; b$ aqui")


def test_detector_aceita_cerca_math_e_span_com_crase():
    bom = "```math\nK \\;=\\; \\min\\bigl\\lbrace\\, x \\,\\bigr\\rbrace\n```\n\nna linha $`a \\;\\le\\; b`$.\n"
    assert matematica_quebrada(bom) == []
    # Matemática sem escape de pontuação continua valendo no formato antigo.
    assert matematica_quebrada(r"$N$ tarefas e $$\text{custo} = D \cdot s$$") == []
    # Código cercado comum (shell com $VAR e \) não é matemática.
    assert matematica_quebrada("```sh\necho $HOME \\; ls $X\\,\n```\n") == []
    assert matematica_quebrada("texto\n\n    export A=$PWD/a\\; B=$PWD/b\n") == []
