#!/usr/bin/env python3
"""expand.py -- reconstrói a lista de palavras a partir do JSON de estrutura.

Uso: expand.py estrutura.json saida.txt

Formato (o que patch_opt grava; compatível com os p*.json da frente 2b):
  q, n            alfabeto e comprimento (q primo)
  A               H = [I_r | A], linhas separadas por espaço ("652 132 ...")
  coset_syndromes síndromes das classes laterais da base (inteiros, dígito i = linha i,
                  base q, little-endian); ou s1/s2 (base {0,s1,s2})
  lines           [[g, rep], ...]: retas rep + <g> (q palavras cada); ou gens/reps
                  (gens = "g1,g2,..." gera o subcódigo; cada rep vira rep + <gens>)
  words           palavras soltas
Escrito em Python puro, sem reaproveitar o C, para servir de conferência cruzada.
"""
import itertools
import json
import sys


def main():
    P = json.load(open(sys.argv[1]))
    q, n = P.get("q", 7), P.get("n", 9)
    A = [[int(c) for c in r] for r in P["A"].split()]
    r, k = len(A), len(A[0])
    assert r + k == n
    syn = P.get("coset_syndromes") or [0, P["s1"], P["s2"]]
    C = [tuple([(-sum(A[i][j] * u[j] for j in range(k))) % q for i in range(r)] + list(u))
         for u in itertools.product(range(q), repeat=k)]
    add = lambda a, b: tuple((x + y) % q for x, y in zip(a, b))
    out = []
    for s in syn:
        d = tuple([(s // q ** i) % q for i in range(r)] + [0] * k)
        out += [add(d, c) for c in C]
    Cs = set(C)

    def span(gens):
        D = [(0,) * n]
        for g in gens:
            D = [add(x, tuple(c * gi % q for gi in g)) for x in D for c in range(q)]
        return D

    lines = P.get("lines")
    if lines:
        for g, rep in lines:
            gv = tuple(map(int, g))
            assert gv in Cs, "direção fora do código"
            out += [add(tuple(map(int, rep)), x) for x in span([gv])]
    elif P.get("reps"):
        gens = [tuple(map(int, g)) for g in P["gens"].split(",")]
        D = span(gens)
        for rep in P["reps"]:
            out += [add(tuple(map(int, rep)), x) for x in D]
    out += [tuple(map(int, w)) for w in P.get("words", [])]
    s = ["".join(map(str, w)) for w in out]
    open(sys.argv[2], "w").write("\n".join(s) + "\n")
    print(f"{len(s)} palavras, {len(set(s))} distintas")


if __name__ == "__main__":
    main()
