#!/usr/bin/env python3
"""Busca witnesses explícitos pequenos para cotas superiores do ledger (gerador burro).

Para cada célula com q^n · M ≤ --limite cuja cota superior `best.ub = M` não sai só das regras
genéricas (tools/certificar/gerar.py --so-regras), roda o recozimento tools/exatos/sa_cover.c
por --segundos e, se achar código com M palavras, confere a cobertura em Python (avaliador exato,
independente do C) e grava tools/certificar/witnesses/K<q>_<n>_<R>_M<M>.txt (uma palavra por
linha; dígito k = coordenada k; q > 10 com dígitos separados por espaço).

O gerador pode ser burro: o juiz é o kernel do Lean (CoveringCerts.check) no gerar.py.

    python3 tools/certificar/buscar.py --limite 2000000 --segundos 10 --jobs 4
    python3 tools/certificar/buscar.py --importar DIR   # códigos q<Q>_n<N>_R<R>_M<M>*.txt já prontos
                                                        # (ex.: tools/exatos/particao_q42.py --gravar DIR)
"""
from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
WIT = RAIZ / "tools" / "certificar" / "witnesses"
sys.path.insert(0, str(RAIZ / "tools" / "certificar"))
import gerar  # noqa: E402


def ler(caminho: Path, q: int) -> list[list[int]]:
    out = []
    for linha in caminho.read_text().split("\n"):
        if linha.strip():
            out.append([int(x) for x in (linha.split() if q > 10 else linha.strip())])
    return out


def cobre(q: int, n: int, R: int, code: list[list[int]]) -> bool:
    """Avaliador exato: todo ponto de Z_q^n a distância ≤ R de alguma palavra."""
    if len({tuple(w) for w in code}) != len(code) or any(len(w) != n or max(w) >= q for w in code):
        return False
    cobertos = set()
    for w in code:
        for pos in itertools.combinations(range(n), R):
            for vals in itertools.product(range(q), repeat=R):
                x = list(w)
                for p, v in zip(pos, vals):
                    x[p] = v
                cobertos.add(tuple(x))
    return len(cobertos) == q ** n


def tentar(sa: Path, q, n, R, M, segundos, semente) -> bool:
    destino = WIT / f"K{q}_{n}_{R}_M{M}.txt"
    if destino.exists():
        return True
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "c.txt"
        try:
            subprocess.run([str(sa), str(q), str(n), str(R), str(M), str(segundos), str(semente), str(out)],
                           capture_output=True, timeout=segundos + 60)
        except subprocess.TimeoutExpired:
            return False
        if not out.exists():
            return False
        code = ler(out, q)
        if len(code) != M or not cobre(q, n, R, code):
            print(f"REPROVADO pelo avaliador: K{q}({n},{R}) M={M}", file=sys.stderr)
            return False
        destino.write_text(out.read_text())
        return True


def importar(d: Path) -> int:
    """Confere com o avaliador e copia códigos prontos (dígitos separados por espaço ou colados)."""
    ok = 0
    for p in sorted(d.glob("q*_n*_R*_M*.txt")):
        q, n, R, M = (int(x[1:]) for x in p.stem.split("_")[:4])
        code = [[int(x) for x in (l.split() if " " in l else l.strip())] for l in p.read_text().splitlines() if l.strip()]
        if len(code) != M or not cobre(q, n, R, code):
            print(f"REPROVADO pelo avaliador: {p.name}", file=sys.stderr)
            continue
        sep = " " if q > 10 else ""
        (WIT / f"K{q}_{n}_{R}_M{M}.txt").write_text("".join(sep.join(map(str, w)) + "\n" for w in code))
        ok += 1
    return ok


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--limite", type=int, default=2_000_000, help="teto de q^n · M")
    ap.add_argument("--segundos", type=int, default=10)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--semente", type=int, default=1)
    ap.add_argument("--importar", type=Path)
    a = ap.parse_args(argv)
    if a.importar:
        WIT.mkdir(parents=True, exist_ok=True)
        print(f"{importar(a.importar)} códigos importados e conferidos")
        return 0
    sa = RAIZ / "build" / "sa_cover"
    sa.parent.mkdir(exist_ok=True)
    subprocess.run(["cc", "-O2", "-o", str(sa), str(RAIZ / "tools/exatos/sa_cover.c"), "-lm"], check=True)
    WIT.mkdir(parents=True, exist_ok=True)
    cells = json.loads((RAIZ / "ledger" / "cells.json").read_text())["cells"]
    regras = gerar.fechar(cells, {})[0]
    alvos = [(c["q"], c["n"], c["R"], c["best"]["ub"]) for c in cells
             if c["space"] * c["best"]["ub"] <= a.limite and regras[(c["q"], c["n"], c["R"])] > c["best"]["ub"]]
    with ThreadPoolExecutor(a.jobs) as ex:
        ok = list(ex.map(lambda t: tentar(sa, *t, a.segundos, a.semente), alvos))
    print(f"{sum(ok)}/{len(alvos)} witnesses achados (q^n·M ≤ {a.limite})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
