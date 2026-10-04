"""Os docs da porta de entrada não podem apontar para arquivo que não existe.

Confere, em README.md, CONTRIBUTING.md, AGENTS.md, SECURITY.md, CODE_OF_CONDUCT.md e docs/*.md:
  * links markdown relativos `[texto](alvo)` (resolvidos a partir da pasta do documento);
  * caminhos entre crases (resolvidos a partir da raiz do repositório) que têm barra e extensão
    conhecida, ou terminam em barra. Globs e placeholders (`*`, `<`, `{`, `$`) são ignorados.
Fora da conferência: blocos de código (cercados e indentados) e a seção "Em construção".
"""
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
DOCS = [RAIZ / n for n in ("README.md", "CONTRIBUTING.md", "AGENTS.md", "SECURITY.md", "CODE_OF_CONDUCT.md")]
DOCS += sorted((RAIZ / "docs").glob("*.md"))

EXT = (".py .md .json .jsonl .c .h .sh .lean .yml .yaml .toml .txt .pdf .tex .cff .svg .csv .lock").split()
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
CRASE = re.compile(r"`([^`\n]+)`")


def prosa(texto: str):
    """Linhas de prosa (numero, linha): sem blocos de código e sem a seção 'Em construção'."""
    cerca, em_construcao = False, False
    for i, linha in enumerate(texto.splitlines(), 1):
        if linha.lstrip().startswith("```"):
            cerca = not cerca
            continue
        if cerca:
            continue
        titulo = re.match(r"^#{1,6}\s+(.*)$", linha)
        if titulo:
            em_construcao = titulo.group(1).strip().lower() == "em construção"
        if em_construcao:
            continue
        if re.match(r"^( {4,}|\t)\S", linha):  # bloco de código indentado
            continue
        yield i, linha


def alvos_de(doc: Path):
    """Gera (linha, tipo, alvo, pasta_base) para cada referência conferível do documento."""
    for i, linha in prosa(doc.read_text(encoding="utf-8")):
        for alvo in LINK.findall(linha):
            if re.match(r"^[a-z][a-z0-9+.-]*:", alvo) or alvo.startswith("#"):
                continue  # URL externa, mailto, âncora da própria página
            yield i, "link", alvo.split("#")[0], doc.parent
        for token in CRASE.findall(linha):
            if re.search(r"[*<>{}$\s]", token) or token.startswith(("http", "/", "~", "-")):
                continue
            raiz_md = "/" not in token and re.search(r"\.(md|cff|toml|yml)$", token)  # arquivo da raiz, sem barra
            if token.endswith("/") or raiz_md or ("/" in token and token.endswith(tuple(EXT))):
                yield i, "caminho", token, RAIZ


def referencias_quebradas(doc: Path):
    return [f"{doc.relative_to(RAIZ)}:{i}: {tipo} {alvo!r} não existe"
            for i, tipo, alvo, base in alvos_de(doc) if alvo and not (base / alvo).exists()]


def test_a_conferencia_acha_as_referencias_dos_docs_de_verdade():
    """Sem isto, um regex quebrado faria todos os outros testes passarem sem conferir nada."""
    total = sum(1 for d in DOCS for _ in alvos_de(d))
    assert total >= 40, f"só {total} referências conferidas: o extrator parou de enxergar os docs"


def test_documento_da_porta_de_entrada_existe():
    faltando = [d.name for d in DOCS[:5] if not d.exists()]
    assert not faltando, f"faltam: {faltando}"


@pytest.mark.parametrize("doc", DOCS, ids=lambda d: str(d.relative_to(RAIZ)))
def test_link_ou_caminho_citado_aponta_para_arquivo_que_nao_existe(doc):
    quebradas = referencias_quebradas(doc)
    assert not quebradas, "\n".join(quebradas)


def test_extrator_reprova_link_e_caminho_inexistentes_e_ignora_codigo_e_em_construcao(tmp_path):
    """O teste de fogo do próprio teste: o que é para falhar falha, o que é para ignorar passa."""
    doc = tmp_path / "x.md"
    doc.write_text(
        "[ruim](nao_existe.md) e `docs/nao_existe.md`\n\n"
        "```\n`docs/ignorado_no_bloco.md`\n```\n\n"
        "    `docs/ignorado_indentado.md`\n\n"
        "## Em construção\n\n`problems/ainda_nao.md` e [x](problems/ainda_nao.md)\n\n"
        "## Depois\n\n[ok](https://exemplo.org/a.md) `ledger/*.json` `a/<b>.py`\n",
        encoding="utf-8")
    achados = [(tipo, alvo) for _, tipo, alvo, _ in alvos_de(doc)]
    assert achados == [("link", "nao_existe.md"), ("caminho", "docs/nao_existe.md")]
