#!/usr/bin/env python3
"""Detector de contradição: as cotas do ledger (com os valores novos K_4(7,4) = 10, K_4(6,3) >= 12) respeitam
as desigualdades elementares entre células? Para cada relação K_A <= K_B, tem de valer lb(A) <= ub(B).

  (1) K_q(n,R)   <= K_q(n+1,R)       (furar uma coordenada não aumenta o raio)
  (2) K_q(n+1,R+1) <= K_q(n,R)       (anexar uma coordenada livre)
  (3) K_q(n+1,R) <= q * K_q(n,R)     (produto com Z_q)
  (4) K_q(n,R+1) <= K_q(n,R)         (raio maior)
  (5) K_q(n,R)   <= K_{q+1}(n,R)     (colapsar o símbolo extra)
Uso: python3 consistencia_ledger.py [ledger/cells.json]   (sai com 1 se achar contradição)
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]


def carregar(caminho=None):
    cells = json.loads(Path(caminho or RAIZ / "ledger" / "cells.json").read_text())["cells"]
    return {(c["q"], c["n"], c["R"]): (c["certification"]["lb"]["value"], c["certification"]["ub"]["value"]) for c in cells}


def contradicoes(L):
    ruins = []
    for (q, n, R), (lb, ub) in L.items():
        pares = [("(1)", (q, n, R), (q, n + 1, R), 1), ("(2)", (q, n + 1, R + 1), (q, n, R), 1),
                 ("(3)", (q, n + 1, R), (q, n, R), q), ("(4)", (q, n, R + 1), (q, n, R), 1),
                 ("(5)", (q, n, R), (q + 1, n, R), 1)]
        for nome, A, B, fator in pares:
            if A in L and B in L:
                # nome: K_A <= fator * K_B  =>  lb(A) <= fator * ub(B)
                if L[A][0] > fator * L[B][1]:
                    ruins.append((nome, A, L[A], B, L[B], fator))
    return ruins


def main():
    L = carregar(sys.argv[1] if len(sys.argv) > 1 else None)
    ruins = contradicoes(L)
    comparadas = 0
    for (q, n, R) in L:
        for A, B in (((q, n, R), (q, n + 1, R)), ((q, n + 1, R + 1), (q, n, R)), ((q, n + 1, R), (q, n, R)),
                     ((q, n, R + 1), (q, n, R)), ((q, n, R), (q + 1, n, R))):
            comparadas += (A in L and B in L)
    print(f"{len(L)} células, {comparadas} comparações; contradições: {len(ruins)}")
    for r in ruins:
        print("CONTRADIÇÃO", r)
    sys.exit(1 if ruins else 0)


if __name__ == "__main__":
    main()
