#!/usr/bin/env python3
"""Os cubos cobrem TODO modelo da CNF? Enumera, com SAT, as projeções dos modelos da CNF (sem as cláusulas
de cobertura, que só podem tirar modelos) sobre a coordenada 1 e compara com a lista de cubos do
certificado. Toda atribuição da coordenada 1 que a CNF aceita tem de ser extensão de algum cubo gravado.

Uso: python3 cubos_cnf.py CERT.jsonl.xz q n R M [limite_perfis]
"""
import json
import lzma
import os
import sys
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "fibras"))
sys.path.insert(0, AQUI)
import fib_encode as enc  # noqa: E402
import orbita_indep as o  # noqa: E402
from pysat.solvers import Solver  # noqa: E402


def projetados(q, n, R, M, pref, smin):
    cnf, x, sim0, ts = enc.codificar(q, n, M, pref, smin, R=R)
    nvx = max(x[w][i][a] for w in range(M) for i in range(1, n) for a in range(q))
    o.tirar_cobertura(cnf, q, n, M, R, nvx)
    out = set()
    with Solver(name="cadical153", bootstrap_with=cnf.cl) as s:
        while s.solve():
            m = set(l for l in s.get_model() if l > 0)
            val = tuple(next(a for a in range(q) if x[w][1][a] in m) for w in range(M))
            out.add(val)
            s.add_clause([-x[w][1][val[w]] for w in range(M)])
    return out


def main():
    arq, q, n, R, M = sys.argv[1], *map(int, sys.argv[2:6])
    lim = int(sys.argv[6]) if len(sys.argv) > 6 else 10 ** 9
    regs = [json.loads(l) for l in lzma.open(arq, "rt")]
    cubos = defaultdict(list)
    for r in regs:
        if r.get("L"):
            cubos[(tuple(sorted(r["tipos"])), r["ordem"], r["inst"], r["L"])].append(r)
    for (perfil, ordem, inst, L), rs in list(sorted(cubos.items()))[:lim]:
        pref = tuple(tuple(int(c) for c in s) for s in rs[0]["tipos"])
        smin = rs[0]["smin"]
        P = projetados(q, n, R, M, pref, smin)
        grav = {tuple(int(c) for c in r["cubo"]) for r in rs}
        sem_cubo = [v for v in P if v[:L] not in grav]
        print(f"inst {inst} {ordem}: modelos projetados na coord 1 = {len(P)}, cubos gravados = {len(grav)}, "
              f"modelos fora de todo cubo = {len(sem_cubo)}", flush=True)
        assert not sem_cubo


if __name__ == "__main__":
    main()
