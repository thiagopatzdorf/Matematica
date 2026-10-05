#!/usr/bin/env python3
"""Red team K_3(6,2), M = 15: a lista de instâncias tem TODA órbita que passa no filtro?

1. Para cada s, gera `fatia.configuracoes(q, n-1, s)` SEM filtro e confere a contagem contra
   Burnside (`burnside.py`). Formas distintas + contagem igual = uma configuração por órbita.
2. Calcula |U(K)| de cada órbita por força bruta (sem `fatia.descobertos`) e separa as que passam
   no filtro de contagem |U| <= (M - s)·V(n-1, R-1).
3. Compara esse conjunto (por forma canônica) com as configurações da lista dada (JSON de
   `rodar_pb.py --listar`) e confere que cada configuração aparece com todos os blocos
   t_1 >= ... >= t_{q-1} >= s de soma M - s, sem sobra nem falta.
"""
import argparse
import itertools
import json
import os
import sys
from collections import defaultdict
from math import comb

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "gaps2"))
sys.path.insert(0, AQUI)
import burnside  # noqa: E402
import fatia  # noqa: E402


def n_U(q, m, R, K):
    return sum(1 for y in itertools.product(range(q), repeat=m)
               if min(sum(a != b for a, b in zip(y, k)) for k in K) > R)


def blocos(q, M, s):
    """Todas as tuplas não crescentes de q-1 inteiros >= s com soma M - s (força bruta)."""
    return sorted(t for t in itertools.product(range(s, M - s + 1), repeat=q - 1)
                  if sum(t) == M - s and all(t[i] >= t[i + 1] for i in range(len(t) - 1)))


def conferir(q, n, R, M, lista, ss=None):
    m = n - 1
    V = sum(comb(m, i) * (q - 1) ** i for i in range(R))  # V(m, R-1)
    ss = ss or list(range(0, M // q + 1))
    orb = burnside.orbitas(q, m, [s for s in ss if s > 0])
    por_s = defaultdict(lambda: defaultdict(set))
    for s, K, t in lista:
        por_s[s][fatia.forma([tuple(k) for k in K])].add(tuple(t))
    rel = {}
    for s in ss:
        cap = (M - s) * V
        if s == 0:
            esperado = {} if q ** m > cap else {(): None}
            total = 1
        else:
            cfgs = fatia.configuracoes(q, m, s)
            total = len(cfgs)
            assert total == orb[s], (s, total, orb[s])
            esperado = {fatia.forma(K): None for K in cfgs if n_U(q, m, R, K) <= cap}
        obtido = por_s.get(s, {})
        falta = set(esperado) - set(obtido)
        sobra = set(obtido) - set(esperado)
        bl = blocos(q, M, s)
        blocos_ruins = [f for f, ts in obtido.items() if sorted(ts) != bl]
        rel[s] = {"orbitas": total, "passam": len(esperado), "na_lista": len(obtido),
                  "faltam": len(falta), "sobram": len(sobra), "blocos_ruins": len(blocos_ruins)}
    n_inst = sum(len(ts) for d in por_s.values() for ts in d.values())
    return rel, n_inst


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k, v in (("q", 3), ("n", 6), ("R", 2), ("M", 15)):
        ap.add_argument("--" + k, type=int, default=v)
    ap.add_argument("--instancias", required=True)
    a = ap.parse_args()
    lista = json.load(open(a.instancias))
    rel, n_inst = conferir(a.q, a.n, a.R, a.M, lista)
    for s, r in rel.items():
        print(s, r, flush=True)
    ok = all(r["faltam"] == 0 and r["sobram"] == 0 and r["blocos_ruins"] == 0 for r in rel.values())
    ok = ok and n_inst == len(lista)
    print(f"{len(lista)} instâncias na lista, {n_inst} distintas -> {'COMPLETA' if ok else 'FALHOU'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
