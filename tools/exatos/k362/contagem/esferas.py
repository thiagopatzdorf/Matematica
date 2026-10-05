#!/usr/bin/env python3
"""Contagem dupla e LPs agregados para K_q(n,R) (frente matemática de K_3(6,2), M = 15).

  intersecoes  |B_R(c) ∩ B_R(c')| em função de d(c,c')
  capacidades  a_r(d) = |S_r(z) ∩ B_R(c)| com d(z,c) = d (a "tabela radial")
  lp_local     LP/ILP sobre N(v) = #pontos x com vetor local v = (A_0(x),...,A_n(x)),
               A_i(x) = #palavras a distância i de x; restrições: contagem, cascas
               (sum_d a_r(d) v_d >= |S_r|), identidades de pares
               sum_x A_i A_j = M sum_k a_k p^k_ij, Delsarte (MacWilliams >= 0) e, se
               `balanceado`, sum_i i v_i = n M (q-1)/q em todo x (lema do perfil equilibrado)
  ramos_raval  LP de cobertura residual dos 38 ramos de 3 centros (Raval, Zenodo 22510341)
"""
import itertools
import sys
from math import comb

import numpy as np
from scipy.optimize import linprog


def p_inter(q, n):
    """p[k][i][j] = #x com d(x,c) = i e d(x,c') = j, quando d(c,c') = k."""
    P = np.zeros((n + 1, n + 1, n + 1), dtype=np.int64)
    for k in range(n + 1):
        u = [1] * k + [0] * (n - k)
        for x in itertools.product(range(q), repeat=n):
            P[k, sum(a != 0 for a in x), sum(a != b for a, b in zip(x, u))] += 1
    return P


def intersecoes(q, n, R):
    P = p_inter(q, n)
    return [int(P[k, :R + 1, :R + 1].sum()) for k in range(n + 1)]


def capacidades(q, n, R):
    P = p_inter(q, n)
    return [[int(P[d, r, :R + 1].sum()) for d in range(n + 1)] for r in range(n + 1)]


def kraw(q, n, m, k):
    return sum((-1) ** s * (q - 1) ** (m - s) * comb(k, s) * comb(n - k, m - s) for s in range(m + 1))


def _vetores(M, caps):
    if len(caps) == 1:
        if M <= caps[0]:
            yield (M,)
        return
    for a in range(min(M, caps[0]) + 1):
        for r in _vetores(M - a, caps[1:]):
            yield (a,) + r


def lp_local(q, n, R, M, cascas=True, pares=True, delsarte=True, balanceado=False, inteiro=False):
    """True se o LP (ou ILP em N(v)) é viável. Ilimitado nunca: é só viabilidade."""
    K = [comb(n, i) * (q - 1) ** i for i in range(n + 1)]
    T = capacidades(q, n, R)
    V = [v for v in _vetores(M, [1] + K[1:]) if sum(v[:R + 1]) >= 1]
    if cascas:
        V = [v for v in V if all(sum(v[d] * T[r][d] for d in range(n + 1)) >= K[r] for r in range(n + 1))]
    if balanceado:
        V = [v for v in V if q * sum(i * x for i, x in enumerate(v)) == n * M * (q - 1)]
    if not V:
        return False
    P, Va, nv = p_inter(q, n), np.array(V, float), len(V)
    linhas, rhs = [], []

    def lin(coef_v, coef_a, b):
        linhas.append(np.r_[coef_v, coef_a])
        rhs.append(b)
    lin(np.ones(nv), np.zeros(n), q ** n)
    if pares:
        for i in range(n + 1):
            for j in range(i, n + 1):
                lin(Va[:, i] * Va[:, j], [-M * P[k, i, j] for k in range(1, n + 1)], M * P[0, i, j])
    else:
        for i in range(n + 1):
            lin(Va[:, i], np.zeros(n), M * K[i])
    cw = (Va[:, 0] == 1).astype(float)
    lin(cw, np.zeros(n), M)
    for k in range(1, n + 1):
        lin(cw * Va[:, k], -M * np.eye(n)[k - 1], 0)
    lin(np.zeros(nv), np.ones(n), M - 1)
    Aub = [np.r_[np.zeros(nv), [-kraw(q, n, m, k) for k in range(1, n + 1)]] for m in range(1, n + 1)]
    bub = [kraw(q, n, m, 0) for m in range(1, n + 1)]
    r = linprog(np.zeros(nv + n), A_ub=np.array(Aub) if delsarte else None, b_ub=bub if delsarte else None,
                A_eq=np.array(linhas), b_eq=rhs, bounds=(0, None), method="highs",
                integrality=[1] * nv + [0] * n if inteiro else None)
    return r.status == 0


def ramos_raval(M=15):
    """[(d, órbita, representante, |H|, |U|, valor do LP residual)] para os 38 ramos."""
    W = list(itertools.product(range(3), repeat=6))
    A = np.array(W)
    D, WT, idx = (A[:, None, :] != A[None, :, :]).sum(2), (A != 0).sum(1), {w: i for i, w in enumerate(W)}
    out = []
    for d in (5, 6):
        anc = (1,) * d + (0,) * (6 - d)
        g = {}
        for w in W:
            if w != (0,) * 6 and w != anc and sum(x != 0 for x in w) <= 4:
                s = w[:d]
                g.setdefault((s.count(0), s.count(1), s.count(2), sum(x != 0 for x in w[d:])), []).append(w)
        orb = sorted((min(m), m) for m in g.values())
        for k, (rep, _) in enumerate(orb):
            proib = {idx[x] for _, m in orb[:k] for x in m}
            F = [idx[(0,) * 6], idx[anc], idx[rep]]
            H = np.where(D[:, F].min(1) > 2)[0]
            U = [c for c in range(729) if WT[c] <= d and c not in F and c not in proib]
            r = linprog(np.ones(len(U)), A_ub=-(D[np.ix_(H, U)] <= 2).astype(float), b_ub=-np.ones(len(H)),
                        bounds=(0, None), method="highs")
            out.append((d, k, "".join(map(str, rep)), len(H), len(U), r.fun))
    return out


if __name__ == "__main__":
    print("interseções K3(6,2):", intersecoes(3, 6, 2))
    print("capacidades:", capacidades(3, 6, 2))
    for M in range(10, 16):
        print(M, {nome: lp_local(3, 6, 2, M, **kw) for nome, kw in
                  [("cascas", dict(pares=False, delsarte=False)), ("+delsarte", dict(pares=False)), ("+pares", {})]})
    print("M=15 equilibrado, ILP:", lp_local(3, 6, 2, 15, balanceado=True, inteiro=True))
    if "--ramos" in sys.argv:
        for r in ramos_raval():
            print(*r[:5], round(r[5], 4), "morre (M=15)" if r[5] > 12 + 1e-9 else "")
