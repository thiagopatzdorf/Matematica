#!/usr/bin/env python3
"""Medição (não é prova): fração de configurações K sorteadas que o LP reduzido mata na raiz.

Para células cuja lista completa não cabe (s* grande), sorteia K com s pontos distintos de
Z_2^(n−1), descarta os que falham no filtro de contagem do GAPS2 e roda só o LP reduzido de
`certificar_bin.py` na raiz. A amostra é uniforme em conjuntos rotulados, não em classes de
isometria, então a fração é uma indicação da força do LP, não uma estimativa da lista.

  python3 tools/exatos/lp_bin/amostra_bin.py --n 11 --R 3 --M 15 --s 7 --k 50 --semente 1
"""
import argparse
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import certificar_bin as cb  # noqa: E402
import fatia_bin as fb  # noqa: E402


def descobertos(E, K, R):
    import numpy as np
    m = E.n - 1
    pts = np.arange(1 << m)
    pop = np.array([bin(i).count("1") for i in range(1 << m)])
    Ki = [cb.ponto(k, m) for k in K]
    d = np.min([pop[pts ^ k] for k in Ki], axis=0)
    return int((d > R).sum())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("n", "R", "M", "s", "k", "semente"):
        ap.add_argument("--" + k, type=int, required=True)
    a = ap.parse_args()
    rng = random.Random(a.semente)
    E = cb.Espaco(a.n, a.R)
    m = a.n - 1
    cap = (a.M - a.s) * fb.vol(m, a.R - 1)
    mortas = vivas = filtro = 0
    t0 = time.time()
    while mortas + vivas < a.k:
        K = [tuple(int(b) for b in format(x, f"0{m}b")) for x in rng.sample(range(1 << m), a.s)]
        if descobertos(E, K, a.R) > cap:
            filtro += 1
            continue
        folhas, _ = cb.certificar(E, a.M, a.s, K, [a.M - a.s], ramos=False)
        if folhas:
            mortas += 1
        else:
            vivas += 1
    print(f"K_2({a.n},{a.R}) M={a.M} s*={a.s}: {mortas}/{a.k} mortas na raiz, {vivas} vivas, "
          f"{filtro} sorteios cortados pelo filtro, {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
