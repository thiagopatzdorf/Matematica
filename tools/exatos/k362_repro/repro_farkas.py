"""Certificado de Farkas para o LP de uma instância (ou ramo) e verificador exato em Fraction.

Sistema: linhas a.x >= b (coeficientes inteiros), 0 <= x <= 1. Se existem y >= 0 com
y.b > sum_j max(0, (A^T y)_j), o sistema não tem solução nem fracionária: para x viável,
y.b <= y.A x <= sum_j max(0, (A^T y)_j) x_j <= sum_j max(0, (A^T y)_j).
O gerador usa o HiGHS (scipy); o verificador (`confere`) só usa inteiros e Fraction.
Mesmo TIPO de certificado do PR #60, com código, enumeração e verificador próprios.
"""
from fractions import Fraction

import numpy as np


def linhas(cob, nv, teto, fib, blocos=()):
    """Linhas (lista de (índices, coeficiente comum), rhs) a partir de repro_sat.restricoes:
    cobertura >= 1, -sum <= ... (tamanho), fibras >= k e, opcionalmente, blocos exatos (= t)."""
    L = [(c, 1, 1) for c in cob]
    L.append((list(range(1, nv + 1)), -1, -teto))
    L += [(lits, 1, k) for lits, k in fib]
    for lits, t in blocos:
        L += [(lits, 1, t), (lits, -1, -t)]
    return L


def gerar(L, nv):
    """Resolve max y.b - 1.u s.a. A^T y - u <= 0, y.b - 1.u <= 1, y, u >= 0. Devolve y (floats) ou None."""
    from scipy.optimize import linprog
    from scipy.sparse import lil_matrix
    m = len(L)
    A = lil_matrix((nv + 1, m + nv))
    for i, (idx, a, _) in enumerate(L):
        for v in idx:
            A[v - 1, i] = a
    for j in range(nv):
        A[j, m + j] = -1
    b = np.array([r for _, _, r in L], dtype=float)
    A[nv, :m] = b
    A[nv, m:] = -1
    rhs = np.zeros(nv + 1)
    rhs[nv] = 1
    c = np.concatenate([-b, np.ones(nv)])
    res = linprog(c, A_ub=A.tocsr(), b_ub=rhs, bounds=(0, None), method="highs")
    if res.status != 0 or -res.fun < 0.5:
        return None
    return res.x[:m]


def racionalizar(y, den=10 ** 6):
    return [Fraction(max(v, 0.0)).limit_denominator(den) for v in y]


def confere(L, nv, y):
    """Verificador exato: devolve a folga y.b - sum max(0, (A^T y)_j); > 0 prova inviabilidade."""
    if len(y) != len(L) or any(v < 0 for v in y):
        return Fraction(-1)
    col = [Fraction(0)] * (nv + 1)
    yb = Fraction(0)
    for (idx, a, r), v in zip(L, y):
        if v:
            yb += v * r
            for j in idx:
                col[j] += v * a
    return yb - sum(c for c in col[1:] if c > 0)

