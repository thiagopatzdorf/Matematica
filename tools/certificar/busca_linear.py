#!/usr/bin/env python3
"""Acha códigos lineares `[n, k]_q` de raio R para as células cuja melhor cota é `q^k`, e grava o JSON.

A tabela do Kéri marca dezenas de cotas binárias como "linear code" (Graham–Sloane, 1985) sem dar o
código; `lineares.py` só tinha os que alguém escreveu à mão. Aqui o gerador é burro
(`busca_linear.c`: recozimento sobre as colunas de H = [A | I_r]) e o juiz é o de sempre: o avaliador
de síndromes em Python (`lineares.cobre_por_sindromes`) antes de gravar, e o kernel do Lean
(`Syn.lin_cert`) no lote. Código que não passa no avaliador não vira arquivo.

Alvos: células sem certificado no lote (`gerar.fechar` > `best.ub`) com `best.ub = q^k` e
`q^(n-k) ≤ --teto` (o kernel confere as `q^(n-k)` testemunhas do transversal; 28 561 já passou).

    python3 tools/certificar/busca_linear.py --listar                 # só os alvos
    python3 tools/certificar/busca_linear.py --segundos 60 --jobs 4   # busca e grava os achados
    python3 tools/certificar/busca_linear.py --importar achados.txt   # linhas "q n r R a1,..;a2,..;..."
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar  # noqa: E402
import lineares  # noqa: E402

FONTE_C = RAIZ / "tools" / "certificar" / "busca_linear.c"
BIN = RAIZ / "build" / "busca_linear"
TETO = 60_000


def _potencia(M: int, q: int) -> int | None:
    k, v = 0, 1
    while v < M:
        v, k = v * q, k + 1
    return k if v == M and k > 0 else None


def alvos(cells: list[dict], teto: int = TETO) -> list[tuple[int, int, int, int, str | None]]:
    """[(q, n, r, R, chave do Kéri)] das células ainda fora do lote com best.ub = q^k e q^r ≤ teto."""
    wits = {s: w for s, w in gerar.ler_witnesses().items() if s[0] ** s[1] * w[0] <= gerar.CUSTO_MAX}
    V, _a, _n = gerar.fechar(cells, wits, lineares.ler_lineares(), gerar.ler_externos())
    out = []
    for c in cells:
        q, n, R, M = c["q"], c["n"], c["R"], c["best"]["ub"]
        k = _potencia(M, q)
        if k is None or k >= n or V[(q, n, R)] <= M or q ** (n - k) > teto:
            continue
        chave = (c["published"]["sources"].get("keri_2011") or {}).get("ub_key")
        out.append((q, n, n - k, R, chave))
    return sorted(out, key=lambda t: (t[0] ** t[2], t))


def compilar() -> Path:
    BIN.parent.mkdir(exist_ok=True)
    subprocess.run(["cc", "-O2", "-o", str(BIN), str(FONTE_C), "-lm"], check=True)
    return BIN


def buscar(q: int, n: int, r: int, R: int, segundos: float, sementes=(1, 2, 3)) -> list[list[int]] | None:
    """Colunas de A (k vetores de Z_q^r) de um código que cobre, ou None."""
    for s in sementes:
        p = subprocess.run([str(BIN), str(q), str(n), str(r), str(R), str(segundos), str(s)],
                           capture_output=True, text=True)
        if p.returncode == 0:
            return [[int(x) for x in linha.split()] for linha in p.stdout.splitlines() if linha.strip()]
    return None


def gravar(q: int, n: int, R: int, A: list[list[int]], chave: str | None) -> Path:
    """Confere pelo avaliador de síndromes e grava tools/certificar/lineares/K<q>_<n>_<R>_M<q^k>.json."""
    r = len(A[0])
    unit = [[1 if t == i else 0 for t in range(r)] for i in range(r)]
    G = lineares._de_paridade(q, A + unit)
    if len(G) + r != n or not lineares.cobre_por_sindromes(q, n, R, G):
        raise ValueError(f"K{q}({n},{R}): o código proposto não cobre com raio {R}")
    p = lineares.LIN / f"K{q}_{n}_{R}_M{q ** len(G)}.json"
    linhas = ["{", f' "q": {q}, "n": {n}, "R": {R},',
              f' "construcao": "código linear [{n},{len(G)}]_{q} de raio {R} (busca local, tools/certificar/busca_linear.c)",',
              f' "chave_keri": {json.dumps(chave)},', ' "gerador": [']
    linhas += [f"  {json.dumps(g)}" + ("," if i < len(G) - 1 else "") for i, g in enumerate(G)]
    linhas += [" ]", "}"]
    p.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--teto", type=int, default=TETO, help="teto de q^r (testemunhas que o kernel confere)")
    ap.add_argument("--segundos", type=float, default=30, help="CPU por semente")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--importar", type=Path, help='linhas "q n r R c1;c2;..." (colunas de A, dígitos separados por espaço)')
    a = ap.parse_args(argv)
    cells = json.loads((RAIZ / "ledger" / "cells.json").read_text())["cells"]
    lista = alvos(cells, a.teto)
    chaves = {(q, n, R): ch for q, n, _r, R, ch in lista}
    if a.listar:
        for q, n, r, R, ch in lista:
            print(f"K{q}({n},{R}) ≤ {q}^{n - r}  (r = {r}, chave {ch})")
        return 0
    if a.importar:
        ok = 0
        for linha in a.importar.read_text().splitlines():
            if not linha.strip():
                continue
            q, n, _r, R, cols = linha.split(maxsplit=4)
            q, n, R = int(q), int(n), int(R)
            if (q, n, R) not in chaves:
                print(f"K{q}({n},{R}) não é alvo (já certificada ou cota diferente)", file=sys.stderr)
                continue
            A = [[int(x) for x in c.split()] for c in cols.split(";") if c.strip()]
            print(gravar(q, n, R, A, chaves[(q, n, R)]).relative_to(RAIZ))
            ok += 1
        print(f"{ok} códigos importados e conferidos")
        return 0
    compilar()

    def um(t):
        q, n, r, R, ch = t
        A = buscar(q, n, r, R, a.segundos)
        return gravar(q, n, R, A, ch) if A else None
    with ThreadPoolExecutor(a.jobs) as ex:
        feitos = [p for p in ex.map(um, lista) if p]
    for p in feitos:
        print(p.relative_to(RAIZ))
    print(f"{len(feitos)}/{len(lista)} códigos achados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
