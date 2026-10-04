"""Avaliador `lean_honesty`: os .lean usam `sorry`, `native_decide` ou declaram `axiom` DE VERDADE?

Uma busca ingênua dá falso alarme: os arquivos dizem "sem `sorry`, sem `native_decide`" em comentários.
Por isso o texto passa antes por um léxico mínimo do Lean 4 que apaga comentários de linha (`--`),
de bloco aninhado (`/- -/`, inclusive `/-- -/` e `/-! -/`) e o conteúdo de strings, caracteres e
identificadores «entre aspas», preservando as quebras de linha (os números de linha continuam certos).
Só o que sobra é procurado.

Limite declarado: é análise de texto, não do elaborador. Macros que gerem `sorry`, ou um
`#print axioms` com axioma inesperado, só um `lake build` mostra.
"""
from __future__ import annotations

import re
from pathlib import Path

from .base import RAIZ, Avaliador, registrar, relativo

# `--` e `/-` abrem comentário; um `"` abre string; r#"..."# é string crua; 'x' é caractere; «x» é identificador.
_TOKEN = re.compile(r"""/-|-/|--[^\n]*|"(?:\\.|[^"\\])*"?|r(?P<h>\#*)"|'(?:\\(?:x[0-9a-fA-F]{2}|u\{?[0-9a-fA-F]+\}?|.)|[^\\'\n])'|«[^»\n]*»""",
                    re.S)
_ANTES_ID = re.compile(r"[A-Za-z0-9_'.!?]")  # `r"` / `'a'` só valem se não colam em identificador

_PROIBIDOS = [
    ("sorry", re.compile(r"\bsorryAx\b|\bsorry\b")),
    ("native_decide", re.compile(r"\bnative_decide\b|\bdecide\s*\+native\b|\bofReduceBool\b")),
    ("axiom", re.compile(r"(?m)^[ \t]*(?:@\[[^\]\n]*\][ \t]*)?(?:(?:private|protected|noncomputable|unsafe)[ \t]+)*axiom\b")),
]
_DECL = re.compile(r"(?m)^[ \t]*(?:@\[[^\]\n]*\][ \t]*)?(?:(?:private|protected|noncomputable|unsafe|partial)[ \t]+)*"
                   r"(?:theorem|lemma|def|abbrev|instance|axiom|opaque)[ \t]+([^\s:({\[]+)")
_NS = re.compile(r"(?m)^[ \t]*(?:(?:private|protected)[ \t]+)?(namespace|end|section)\b[ \t]*([^\s]*)")


def limpar_lean(texto: str) -> str:
    """Troca comentários e conteúdo de strings por espaços (mantém `\\n`), com o mesmo comprimento."""
    saida: list[str] = []
    pos = 0  # fim do que já foi copiado
    i = 0
    prof = 0
    ini = 0  # início do comentário de bloco corrente

    def branco(s: str) -> str:
        return re.sub(r"[^\n]", " ", s)

    while True:
        m = _TOKEN.search(texto, i)
        if not m:
            break
        t = m.group(0)
        cola = m.start() > 0 and _ANTES_ID.match(texto[m.start() - 1]) is not None
        if prof:
            if t == "/-":
                prof += 1
            elif t == "-/":
                prof -= 1
                if prof == 0:
                    saida.append(branco(texto[ini:m.end()]))
                    pos = m.end()
            i = m.end()
            continue
        if t == "/-":
            prof, ini = 1, m.start()
            saida.append(texto[pos:ini])
            i = m.end()
        elif t == "-/":  # fecho solto fora de comentário: é código
            i = m.end()
        elif t.startswith("--"):
            saida.append(texto[pos:m.start()] + branco(t))
            pos = i = m.end()
        elif t[0] == "r" and m.group("h") is not None:
            fim = '"' + m.group("h")
            k = texto.find(fim, m.end())
            k = len(texto) if k < 0 else k + len(fim)
            saida.append(texto[pos:m.start()] + branco(texto[m.start():k]))
            pos = i = k
        elif t[0] in "'" and cola:  # `x'` ou `h'a'`: apóstrofo de identificador, não caractere
            i = m.start() + 1
        else:  # string, caractere ou «ident»
            saida.append(texto[pos:m.start()] + t[0] + branco(t[1:-1]) + t[-1:] if len(t) > 1 else texto[pos:m.end()])
            pos = i = m.end()
    if prof:  # comentário de bloco sem fecho: tudo até o fim é comentário
        saida.append(branco(texto[ini:]))
        pos = len(texto)
    saida.append(texto[pos:])
    return "".join(saida)


def declaracoes(limpo: str) -> set[str]:
    """Nomes completos (com `namespace`) das declarações do texto já limpo."""
    nomes: set[str] = set()
    pilha: list[tuple[str, str]] = []  # (tipo, nome)
    eventos = sorted([(m.start(), "ns", m) for m in _NS.finditer(limpo)] +
                     [(m.start(), "decl", m) for m in _DECL.finditer(limpo)], key=lambda e: e[0])
    for _, tipo, m in eventos:
        if tipo == "decl":
            nome = m.group(1)
            prefixo = ".".join(n for k, n in pilha if k == "namespace" and n)
            nomes.add(f"{prefixo}.{nome}" if prefixo else nome)
            continue
        kw, nome = m.group(1), m.group(2)
        if kw == "end":
            if pilha:
                pilha.pop()
        else:
            pilha.append((kw, nome if kw == "namespace" else ""))
    return nomes


def arquivos_lean(alvo: Path) -> list[Path]:
    return [alvo] if alvo.is_file() else sorted(alvo.rglob("*.lean"))


def _linha(texto: str, pos: int) -> int:
    return texto.count("\n", 0, pos) + 1


@registrar
class LeanHonesty(Avaliador):
    id = "lean_honesty"
    versao = "1"
    descricao = "uso REAL de sorry/native_decide/axiom em CoveringLean/**/*.lean (ignora comentários e strings)"
    alvo_padrao = str(RAIZ / "CoveringLean")

    def avaliar(self, alvo, **opcoes):
        alvo = Path(alvo)
        repro = f"python3 -m evaluators {self.id} {relativo(alvo)} --json"
        if not alvo.exists():
            return self.falha_de_ambiente(f"alvo não existe: {alvo}", "alvo_ausente", comando_reproducao=repro)
        arquivos = arquivos_lean(alvo)
        if not arquivos:
            return self.falha_de_ambiente(f"nenhum .lean em {alvo}", "alvo_vazio", comando_reproducao=repro)
        achados: list[dict] = []
        ignoradas = {nome: {"ocorrencias": 0, "arquivos": 0} for nome, _ in _PROIBIDOS}
        for arq in arquivos:
            bruto = arq.read_text(encoding="utf-8", errors="replace")
            limpo = limpar_lean(bruto)
            for nome, rx in _PROIBIDOS:
                reais = list(rx.finditer(limpo))
                for m in reais:
                    achados.append({"arquivo": relativo(arq), "linha": _linha(limpo, m.start()), "tipo": nome,
                                    "trecho": bruto.splitlines()[_linha(limpo, m.start()) - 1].strip()[:160]})
                total = len(rx.findall(bruto))
                if total > len(reais):
                    ignoradas[nome]["ocorrencias"] += total - len(reais)
                    ignoradas[nome]["arquivos"] += 1
        evid = {"arquivos_varridos": len(arquivos), "achados": achados[:200], "n_achados": len(achados),
                "mencoes_so_em_comentario_ou_string": ignoradas}
        if achados:
            tipos = sorted({a["tipo"] for a in achados})
            v = f"{len(achados)} uso(s) real(is) de {', '.join(tipos)}; primeiro em {achados[0]['arquivo']}:{achados[0]['linha']}"
            return self.resultado(False, v, evidencia=evid, comando_reproducao=repro)
        return self.resultado(True, f"limpo: {len(arquivos)} arquivos sem sorry, native_decide nem axiom (fora de comentários)",
                              evidencia=evid, comando_reproducao=repro)
