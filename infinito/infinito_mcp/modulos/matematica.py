"""Módulo matemática: o ledger de cotas, os códigos e o verificador oficial do repo.

Tudo aqui é leitura ou verificação barata e exata (o avaliador da casa), então não gasta
crédito. O que prova algo é o verificador em C e o kernel do Lean, nunca a resposta do modelo.

Fonte: o próprio repo (`INF_REPO`; na imagem, `/app/repo`). Nada é copiado para outro lugar,
então ledger e certificados que mudam no repo mudam aqui no próximo deploy.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

NOME = "matematica"
DOCS = {  # allowlist: o agente lê estes, não caminhos arbitrários
    "readme": "README.md", "estado_da_arte": "STATE_OF_ART.md", "validacao": "VALIDATION.md",
    "reproduzir_1137": "REPRODUCE_1137.md", "ledger": "ledger/README.md", "formato_de_codigo": "docs/code-format.md",
    "revisao_lean": "LEAN_REVIEW.md", "red_team_lean": "LEAN_RED_TEAM.md",
}
_CELULA = re.compile(r"^K(\d+)\((\d+),(\d+)\)$")
_ARQ_CODIGO = re.compile(r"^q\d+_n\d+_R\d+_M\d+\.(txt|json)$")


def _repo(env: dict) -> Path:
    return Path(env.get("INF_REPO") or Path(__file__).resolve().parents[3])


def _celulas(repo: Path) -> list[dict]:
    return json.loads((repo / "ledger" / "cells.json").read_text(encoding="utf-8"))["cells"]


def parse_celula(texto: str) -> str:
    """'K7(9,4)', '7,9,4' ou '7 9 4' -> 'K7(9,4)'. Recusa o que não é uma célula."""
    t = texto.strip().upper().replace(" ", "")
    m = _CELULA.match(t) or re.match(r"^(\d+),(\d+),(\d+)$", t) or re.match(r"^(\d+)/(\d+)/(\d+)$", t)
    if not m:
        raise ValueError(f"célula inválida: {texto!r} (use K7(9,4) ou q,n,R)")
    q, n, r = m.groups()
    return f"K{int(q)}({int(n)},{int(r)})"


def registrar(ctx) -> None:
    tool, repo = ctx.tool, _repo(ctx.env)
    if str(repo / "ledger") not in sys.path:
        sys.path.insert(0, str(repo / "ledger"))

    @tool
    def celula(id: str) -> dict:  # noqa: A002 - o nome que o agente vê
        """Uma célula K_q(n,R) do ledger: cotas publicadas (com fonte), a nossa, e o estado
        (`ours_lean` > `ours_computational` > `published`). Aceita 'K7(9,4)' ou '7,9,4'."""
        try:
            alvo = parse_celula(id)
        except ValueError as e:
            return {"ok": False, "erro": str(e)}
        for c in _celulas(repo):
            if c["id"] == alvo:
                return {"ok": True, "celula": c}
        return {"ok": False, "erro": f"{alvo} não está no ledger (1145 células, q de 2 a 21)"}

    @tool
    def alvos(limite: int = 20, max_espaco: float = 1e9, incluir_fechadas: bool = False) -> dict:
        """Células ranqueadas por onde há mais chance de melhorar: ninguém atacou desde 2011 primeiro,
        depois maior razão ub/lb, depois menor espaço (q^n). Cada linha traz a justificativa."""
        import targets  # ledger/targets.py do repo
        r = targets.ranquear(_celulas(repo), max_espaco=max_espaco, incluir_fechadas=incluir_fechadas)
        return {"ok": True, "total": len(r), "alvos": r[: max(1, min(limite, 200))]}

    @tool
    def nossos_resultados() -> dict:
        """Só as células em que temos código (computacional) ou teorema (Lean), com o estado de cada uma."""
        saida = [{"id": c["id"], "status": c["status"], "ours_lean": c.get("ours_lean"),
                  "ours_computational": c.get("ours_computational"), "best": c.get("best")}
                 for c in _celulas(repo) if c.get("ours_lean") or c.get("ours_computational")]
        return {"ok": True, "total": len(saida), "celulas": saida}

    @tool
    def codigos() -> dict:
        """Arquivos de código em `data/codes/` (q<Q>_n<N>_R<R>_M<M>) e se têm descrição estruturada."""
        pasta, est = repo / "data" / "codes", repo / "data" / "structured"
        nomes = sorted(p.name for p in pasta.glob("*.txt"))
        return {"ok": True, "codigos": [{"arquivo": n, "estruturado": (est / (n[:-4] + ".json")).exists()} for n in nomes]}

    @tool
    def verificar_codigo(arquivo: str, tempo_limite_s: int = 120) -> dict:
        """Roda o verificador oficial em C num código de `data/codes/`: palavras distintas, M certo, todo
        ponto do espaço a distância ≤ R de alguma palavra. Devolve o sha256 canônico. Grátis, exato."""
        if not _ARQ_CODIGO.match(arquivo) or not arquivo.endswith(".txt"):
            return {"ok": False, "erro": "arquivo tem de ser data/codes/q<Q>_n<N>_R<R>_M<M>.txt"}
        alvo = repo / "data" / "codes" / arquivo
        if not alvo.exists():
            return {"ok": False, "erro": f"{arquivo} não existe (veja `codigos`)"}
        binario = Path(ctx.env.get("INF_VERIFY_BIN") or repo / "tools" / "verify" / "verify")
        if not binario.exists():
            return {"ok": False, "erro": "verificador não compilado nesta instalação (INF_VERIFY_BIN)"}
        try:
            p = subprocess.run([str(binario), str(alvo)], capture_output=True, text=True,
                               timeout=max(5, min(tempo_limite_s, 600)))
        except subprocess.TimeoutExpired:
            return {"ok": False, "erro": f"verificador passou de {tempo_limite_s}s"}
        veredito = {0: "cobre", 1: "NÃO cobre: há pontos descobertos", 2: "formato inválido"}.get(p.returncode, "erro")
        return {"ok": p.returncode == 0, "veredito": veredito, "codigo_de_saida": p.returncode,
                "saida": (p.stdout + p.stderr).strip()[-2000:]}

    @tool
    def documento(nome: str) -> dict:
        """Lê um documento do repo: readme, estado_da_arte, validacao, reproduzir_1137, ledger,
        formato_de_codigo, revisao_lean, red_team_lean."""
        arq = DOCS.get(nome)
        if not arq:
            return {"ok": False, "erro": f"nome inválido; use um de: {', '.join(sorted(DOCS))}"}
        p = repo / arq
        if not p.exists():
            return {"ok": False, "erro": f"{arq} não existe neste deploy"}
        texto = p.read_text(encoding="utf-8")
        return {"ok": True, "arquivo": arq, "bytes": len(texto.encode()), "texto": texto[:60_000],
                "truncado": len(texto) > 60_000}
