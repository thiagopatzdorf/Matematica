#!/usr/bin/env python3
"""Propaga cotas inferiores pelo lema das fibras (docs/exatos/FIBRAS_GERAL.md, Lema 1).

Lema 1 com s = |F(j,a)| < q: K_{q-s}(n-1, R-1) <= M - s (s = 0 vale também: nenhuma palavra tem a na
coordenada j, e o resto é um código de raio R-1 em Z_q^{n-1} com M palavras). Numa coordenada as q
fibras somam M, então a menor tem s <= M // q. Logo, para R >= 1 e n >= 2,

    existe código com M palavras  =>  existe s em [0, M // q] com lb(K_{q-s}(n-1, R-1)) <= M - s.

O script lê as cotas inferiores publicadas do ledger (só leitura), aplica correções dadas na linha de
comando (ex.: 7,6,4=14 do PR #56) e itera até o ponto fixo, imprimindo as células que sobem.
Não escreve no ledger: o resultado é hipótese de trabalho até alguém revisar e registrar.

Uso: propaga_fibras.py [q,n,R=lb ...]
"""
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[3]


def carregar():
    cells = json.load(open(RAIZ / "ledger" / "cells.json"))["cells"]
    lb, ub = {}, {}
    for c in cells:
        t = (c["q"], c["n"], c["R"])
        v = (c.get("published") or {}).get("lb") or {}
        if v.get("value") is not None:
            lb[t] = v["value"]
        if c.get("best", {}).get("ub") is not None:
            ub[t] = c["best"]["ub"]
    return lb, ub


def cota(lb, q, n, R):
    if R <= 0:
        return q ** n  # raio 0: o código é o espaço todo
    if R >= n:
        return 1
    return lb.get((q, n, R), 1)


def propagar(lb, ub):
    base = dict(lb)
    mudou = True
    while mudou:
        mudou = False
        for (q, n, R) in list(lb):
            if R < 1 or n < 2:
                continue
            M = lb[(q, n, R)]
            while True:
                ok = any(cota(lb, q - s, n - 1, R - 1) <= M - s for s in range(0, min(M // q, q - 1) + 1))
                if ok:
                    break
                M += 1
            if M > lb[(q, n, R)]:
                lb[(q, n, R)] = M
                mudou = True
    return {t: (base[t], lb[t], ub.get(t)) for t in lb if lb[t] > base[t]}


def main(argv):
    lb, ub = carregar()
    for a in argv[1:]:
        t, v = a.split("=")
        q, n, R = map(int, t.split(","))
        lb[(q, n, R)] = max(lb.get((q, n, R), 1), int(v))
        print(f"correção: K_{q}({n},{R}) >= {v}")
    for (q, n, R), (antes, depois, u) in sorted(propagar(lb, ub).items()):
        print(f"K_{q}({n},{R}): lb {antes} -> {depois}  (ub {u})")


if __name__ == "__main__":
    main(sys.argv)
