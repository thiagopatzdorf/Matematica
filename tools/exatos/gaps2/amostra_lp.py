"""Amostra configurações K (s pontos de Z_q^(n-1)) que passam no filtro da fatia
|U| <= (M - s) V(n-1, R-1), por busca local aleatória, e roda o LP de `certificar_lp.py` em
cada instância (s, K, t). Não é uma lista de representantes e não prova nada.

AVISO (medido em 2026-10-05, docs/exatos/LP_FATIA_TERNARIO.md): esta amostra NÃO estima a fração
de instâncias que o LP mata. O LP mata K aleatórios também com M acima de valores em que existe
código (K_3(5,1) com M = 27: 5 de 6; K_3(6,1) com M = 75, 78; K_3(7,2) com M = 36..42). As
instâncias que importam são as raras, de K estruturado; use só como controle negativo (se o LP
não mata nem K aleatório, a via morreu).

  python3 tools/exatos/gaps2/amostra_lp.py q n R M s nK semente [prof_max] [alvo_U]
"""
import itertools
import json
import os
import random
import sys
import time

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "k362", "contagem"))
sys.path.insert(0, AQUI)
import certificar_lp as cl  # noqa
import fatia  # noqa


def amostra_K(q, m, R, s, cap, rng, tent=20000, alvo=None):
    P = np.array(list(itertools.product(range(q), repeat=m)))
    N = len(P)
    B = np.zeros((N, N), bool)
    for i in range(N):
        B[i] = (P != P[i]).sum(1) <= R
    for _ in range(50):
        K = rng.sample(range(N), s)
        cnt = B[K].sum(0)
        unc = int((cnt == 0).sum())
        it = 0
        meta = cap if alvo is None else rng.randint(alvo, cap)
        while unc > meta and it < tent * 5:
            it += 1
            i = rng.randrange(s)
            j = rng.randrange(N)
            if j in K:
                continue
            c2 = cnt - B[K[i]] + B[j]
            u2 = int((c2 == 0).sum())
            if u2 <= unc or rng.random() < 0.02:
                K[i] = j; cnt = c2; unc = u2
        if unc <= meta:
            return [tuple(int(v) for v in P[k]) for k in K], unc
    return None, None


def main():
    q, n, R, M, s, nK, seed = map(int, sys.argv[1:8])
    prof = int(sys.argv[8]) if len(sys.argv) > 8 else 6
    alvo = int(sys.argv[9]) if len(sys.argv) > 9 else None
    rng = random.Random(seed)
    cap = (M - s) * fatia.vol(n - 1, R - 1, q)
    blocos = fatia.blocos_restantes(q, M, s)
    res = []
    for k in range(nK):
        K, unc = amostra_K(q, n - 1, R, s, cap, rng, alvo=alvo)
        if K is None:
            print("sem K", flush=True); continue
        t = rng.choice(blocos)
        t0 = time.time()
        sis = cl.sistema(q, n, R, M, s, K, t)
        v, _, _ = cl._dual(*sis)
        f = cl.certificar(sis, prof_max=prof)
        r = {"s": s, "U": unc, "t": list(t), "dual": round(float(v), 5),
             "folhas": None if f is None else len(f), "seg": round(time.time() - t0, 2)}
        res.append(r)
        print(json.dumps(r), flush=True)
    ok = sum(r["folhas"] is not None for r in res)
    raiz = sum(r["folhas"] == 1 for r in res)
    print(f"RESUMO q{q} n{n} R{R} M{M} s{s}: {len(res)} amostras, {ok} certificadas, {raiz} na raiz, cap={cap}")


if __name__ == "__main__":
    main()
