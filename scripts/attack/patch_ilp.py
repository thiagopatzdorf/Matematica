#!/usr/bin/env python3
"""Remendo ótimo (ou cota) por ILP: lê a saída do patch_dump e resolve a cobertura mínima.

POR QUE: com resíduo pequeno, o ILP diz o ótimo entre os candidatos (ou a cota do LP), o que
separa "o SA travou" de "não existe melhor com estes candidatos". HiGHS via scipy.milp.

Uso: patch_ilp.py sub.txt segundos saida_remendo.txt [--lp]
Imprime o status, o valor e a cota dual; grava as palavras escolhidas (uma por linha).
"""
import sys

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csc_matrix


def main():
    sub, secs, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    lp = "--lp" in sys.argv
    with open(sub) as f:
        npts, nc = map(int, f.readline().split())
        words, rows, cols = [], [], []
        for j, line in enumerate(f):
            t = line.split()
            words.append(t[0])
            k = int(t[1])
            rows.extend(int(x) for x in t[2:2 + k])
            cols.extend([j] * k)
    A = csc_matrix((np.ones(len(rows)), (rows, cols)), shape=(npts, len(words)))
    if (A.sum(axis=1) == 0).any():
        raise SystemExit("ponto sem candidato: baixe o tau")
    res = milp(c=np.ones(len(words)), constraints=LinearConstraint(A, lb=1, ub=np.inf),
               integrality=None if lp else np.ones(len(words)), bounds=Bounds(0, 1),
               options={"time_limit": secs, "disp": False})
    print("status", res.status, res.message)
    if res.x is None:
        return
    print("valor", res.fun, "cota_dual", getattr(res, "mip_dual_bound", None))
    if not lp:
        sel = [words[j] for j in np.flatnonzero(res.x > 0.5)]
        cov = A[:, np.flatnonzero(res.x > 0.5)].sum(axis=1)
        assert (cov >= 1).all()
        open(out, "w").write("\n".join(sel) + "\n")
        print("palavras", len(sel))


if __name__ == "__main__":
    main()
