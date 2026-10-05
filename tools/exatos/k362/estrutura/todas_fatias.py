#!/usr/bin/env python3
"""Degraus que usam as fatias 1 e 2: o LP da instância inteira, escrito em Z_3^5.

Com K_0 = K (a fatia 0 fixa) e as palavras de fora em z_{b,y} (bloco b = 1, 2, projeção y),
0 <= z <= 1, o sistema da instância é, sem perda nenhuma:

  fatia 0, u ∈ U(K):           Σ_b Σ_{y ∈ B_1(u)} z_{b,y} >= 1
  fatia a ∈ {1,2}, v ∉ B_1(K):  Σ_{y ∈ B_2(v)} z_{a,y} + Σ_{y ∈ B_1(v)} z_{a',y} >= 1   (a' = 3 - a)
  fibras (i, c):               Σ_b Σ_{y_i = c} z_{b,y} >= s* - |K_{i,c}|
  blocos:                      Σ_y z_{b,y} = t_b

(os pontos (a, v) com d(v, K) <= 1 já são cobertos pela fatia 0). Cada linha tem uma CLASSE:
("0", d(u,K)) na fatia 0 e ("ab", d(v,K) + 1) nas fatias 1, 2 (a distância em Z_3^6 até a fibra F = fatia 0) (simétricas sob a troca de símbolos só
quando t_1 = t_2). `inviavel(..., classes)` resolve o LP só com as linhas das classes dadas mais
os blocos (e as fibras, se pedido), e devolve se é inviável, para medir de quais faixas de
distância à fatia o certificado precisa.
"""
import itertools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lemas import P5, _dist5, IDX  # noqa: E402


def linhas(K, s, t):
    D = _dist5()
    ks = [IDX[tuple(k)] for k in K]
    dK = D[:, ks].min(1)
    B1, B2 = (D <= 1).astype(float), (D <= 2).astype(float)
    rows, cls = [], []
    Z = np.zeros(243)
    for u in range(243):
        if dK[u] >= 3:
            rows.append(np.r_[B1[u], B1[u]]); cls.append(("0", int(dK[u])))
    for a in (1, 2):
        for v in range(243):
            if dK[v] >= 2:
                r = np.r_[B2[v], B1[v]] if a == 1 else np.r_[B1[v], B2[v]]
                rows.append(r); cls.append(("ab", int(dK[v]) + 1))
    fib, rhsf = [], []
    for i in range(5):
        for c in range(3):
            ind = np.array([p[i] == c for p in P5], float)
            fib.append(np.r_[ind, ind]); rhsf.append(s - sum(k[i] == c for k in K))
    E = np.array([np.r_[np.ones(243), Z], np.r_[Z, np.ones(243)]])
    return np.array(rows), cls, np.array(fib), np.array(rhsf, float), E, np.array(t, float)


def inviavel(K, s, t, classes=None, fibras=True, bounds01=True):
    from scipy.optimize import linprog
    G, cls, Fb, hf, E, e = linhas(K, s, t)
    sel = [i for i, c in enumerate(cls) if classes is None or c in classes]
    A = G[sel]
    h = np.ones(len(sel))
    if fibras:
        A = np.vstack([A, Fb]); h = np.r_[h, hf]
    r = linprog(np.zeros(486), A_ub=-A, b_ub=-h, A_eq=E, b_eq=e,
                bounds=(0, 1) if bounds01 else (0, None), method="highs")
    return r.status == 2


# ---------- lema do complemento da fibra, em Z_3^6 (degraus X, XB, XBF) ----------

P6 = list(itertools.product(range(3), repeat=6))


def regiao(K, quais="X"):
    """Pontos de Z_3^6 longe da fibra F = {(0, k)}: "X" = d(x, F) >= 3 (complemento de B_2(F)),
    "casca" = d(x, F) = 3, "fatia0" = X ∩ {x_0 = 0} (o U do lema da fatia)."""
    F = [(0,) + tuple(k) for k in K]
    out = []
    for x in P6:
        d = min(sum(a != b for a, b in zip(x, f)) for f in F)
        if d >= 3 and (quais == "X" or (quais == "casca" and d == 3) or (quais == "fatia0" and x[0] == 0)):
            out.append(x)
    return out


def confere_complemento(K, t, M, w, f=None, blocos=False):
    """Conferência exata (inteiros) do lema do complemento. w: dict ponto de Z_3^6 -> inteiro >= 0,
    só em pontos a distância >= 3 de F; f: dict (i, b) -> inteiro >= 0, i = 1..5 (coordenada do
    código). Valor de uma palavra c de fora (c_0 != 0): w(B_2(c)) + Σ_i f[(i, c_i)]. Sem blocos,
    vale se Σw + Σ f·(s - |F_{i,b}|) > (M - s)·max valor; com blocos, > Σ_b t_b·max_{c_0 = b} valor."""
    s = len(K)
    f = f or {}
    F = [(0,) + tuple(k) for k in K]
    d = lambda a, b: sum(x != y for x, y in zip(a, b))  # noqa: E731
    if any(not isinstance(v, int) or v < 0 for v in list(w.values()) + list(f.values())):
        return False
    if any(min(d(x, g) for g in F) < 3 for x in w) or any(not 1 <= i <= 5 for i, _ in f):
        return False
    lam = {1: None, 2: None}
    for c in P6:
        if c[0] == 0:
            continue
        val = sum(v for x, v in w.items() if d(x, c) <= 2) + sum(f.get((i, c[i]), 0) for i in range(1, 6))
        lam[c[0]] = val if lam[c[0]] is None else max(lam[c[0]], val)
    falta = sum(v * (s - sum(k[i - 1] == b for k in K)) for (i, b), v in f.items())
    lhs = sum(w.values()) + falta
    rhs = t[0] * lam[1] + t[1] * lam[2] if blocos else (M - s) * max(lam.values())
    return lhs > rhs


ESC = (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 60, 120, 240, 1000, 10**4, 10**6)


def lp_complemento(K, t, M, quais="X", blocos=False, fibras=False):
    """Dual do LP do degrau, em ponto flutuante: (folga normalizada, w, f). Folga > 0 = mata."""
    from scipy.optimize import linprog
    s = len(K)
    X = regiao(K, quais)
    Xa = np.array(X)
    out = [c for c in P6 if c[0] != 0]
    Oa = np.array(out)
    B = ((Oa[:, None, :] != Xa[None, :, :]).sum(2) <= 2).astype(float)  # out x X
    nX, nf = len(X), (15 if fibras else 0)
    Fm = np.zeros((len(out), nf))
    falta = np.zeros(nf)
    if fibras:
        for r, c in enumerate(out):
            for i in range(1, 6):
                Fm[r, 3 * (i - 1) + c[i]] = 1
        falta = np.array([s - sum(k[i - 1] == b for k in K) for i in range(1, 6) for b in range(3)], float)
    nl = 2 if blocos else 1
    L = np.zeros((len(out), nl))
    for r, c in enumerate(out):
        L[r, (c[0] - 1) if blocos else 0] = -1
    A = np.hstack([B, Fm, L])
    A = np.vstack([A, np.r_[np.ones(nX), np.zeros(nf + nl)][None]])
    b = np.r_[np.zeros(len(out)), 1.0]
    custo = np.array(t, float) if blocos else np.array([M - s], float)
    c = -np.r_[np.ones(nX), falta, -custo]
    r = linprog(c, A_ub=A, b_ub=b, bounds=[(0, None)] * (nX + nf) + [(None, None)] * nl, method="highs")
    return -r.fun, dict(zip(X, r.x[:nX])), {(1 + j // 3, j % 3): r.x[nX + j] for j in range(nf)}


def cert_complemento(K, t, M, quais="X", blocos=False, fibras=False):
    v, w, f = lp_complemento(K, t, M, quais, blocos, fibras)
    if v <= 1e-9:
        return v, None
    for e in ESC:
        wi = {x: int(np.floor(a * e + 1e-9)) for x, a in w.items()}
        wi = {x: a for x, a in wi.items() if a}
        fi = {k: int(np.floor(a * e + 1e-9)) for k, a in f.items()}
        fi = {k: a for k, a in fi.items() if a}
        if wi and confere_complemento(K, t, M, wi, fi, blocos):
            return v, (wi, fi)
    return v, None
