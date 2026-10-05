#!/usr/bin/env python3
"""Escada de lemas para as instâncias da fatia mínima de K_3(6,2) (M = 15 e 16).

Notação. Uma instância é (s*, K, t): K são as s* projeções em Z_3^5 da fatia 0 (as palavras com
c_0 = 0), t = (t_1, t_2) os tamanhos dos outros blocos. U(K) = pontos de Z_3^5 a distância >= 3
de K. As M - s* palavras fora da fatia 0 já diferem de (0, u) na coordenada 0, então só cobrem
(0, u) se a projeção delas está a distância <= 1 de u (lema da fatia). Os degraus, do mais legível
ao mais forte, e cada um com certificado conferido em inteiros por `confere_*`:

  P1  empacotamento: P ⊂ U com distâncias >= 3 e |P| > M - s* (casa dos pombos);
  Pm  m-empacotamento: P ⊂ U com toda bola de raio 1 contendo <= m pontos de P e |P| > m(M - s*);
  T   lema da fatia LP: pesos inteiros w >= 0 em U com w(B_1(y)) <= W para todo y e Σw > W(M - s*);
  F   T com as fibras: pesos w em U, f_{i,b} >= 0 e λ com w(B_1(y)) + Σ_i f_{i,y_i} <= λ para todo
      y e Σw + Σ f_{i,b}(s* - |K_{i,b}|) > λ(M - s*).

Os degraus que restam (as fatias 1 e 2) estão em `todas_fatias.py`.
"""
import itertools
from functools import lru_cache

import numpy as np

P5 = list(itertools.product(range(3), repeat=5))
IDX = {p: i for i, p in enumerate(P5)}


def dist(a, b):
    return sum(x != y for x, y in zip(a, b))


@lru_cache(None)
def _dist5():
    A = np.array(P5)
    return (A[:, None, :] != A[None, :, :]).sum(2)


def U_de(K):
    D = _dist5()
    ks = [IDX[tuple(k)] for k in K]
    return [i for i in range(243) if D[i, ks].min() >= 3]


def bolas1(U):
    """Matriz (243 x |U|): linha y = indicador de B_1(y) ∩ U."""
    D = _dist5()
    return (D[:, U] <= 1).astype(float)


# ---------- conferências exatas (só inteiros, sem numpy) ----------

def confere_empacotamento(K, M, P, m=1):
    """P ⊂ U(K), toda bola de raio 1 de Z_3^5 contém <= m pontos de P e |P| > m(M - s*)."""
    s = len(K)
    P = [tuple(p) for p in P]
    if len(set(P)) != len(P):
        return False
    if any(min(dist(p, k) for k in K) < 3 for p in P):
        return False
    if any(sum(dist(y, p) <= 1 for p in P) > m for y in P5):
        return False
    return len(P) > m * (M - s)


def confere_fatia(K, M, w):
    """w: dict ponto->inteiro >= 0 em U(K). W = max bola; vale se Σw > W(M - s*)."""
    s = len(K)
    if any(v < 0 or not isinstance(v, int) for v in w.values()):
        return False
    if any(min(dist(p, k) for k in K) < 3 for p in w):
        return False
    W = max(sum(v for p, v in w.items() if dist(y, p) <= 1) for y in P5)
    return sum(w.values()) > W * (M - s)


def confere_fibras(K, M, w, f, lam):
    """w em U(K); f[(i,b)] >= 0 para i = 0..4 (coordenadas 1..5 do código); λ inteiro."""
    s = len(K)
    if any(v < 0 for v in w.values()) or any(v < 0 for v in f.values()):
        return False
    if any(min(dist(p, k) for k in K) < 3 for p in w):
        return False
    for y in P5:
        if sum(v for p, v in w.items() if dist(y, p) <= 1) + sum(f.get((i, y[i]), 0) for i in range(5)) > lam:
            return False
    falta = {(i, b): s - sum(k[i] == b for k in K) for i in range(5) for b in range(3)}
    return sum(w.values()) + sum(v * falta[ib] for ib, v in f.items()) > lam * (M - s)


# ---------- busca (HiGHS em ponto flutuante; o veredito é sempre o da conferência) ----------

def m_empacotamento(K, M, m=1, tempo=20, alvo=None):
    """Maior P ⊂ U com <= m pontos por bola (MILP). Com `alvo`, só procura |P| >= alvo
    (viabilidade, bem mais rápido). Devolve (|P|, P, decidido?)."""
    from scipy.optimize import milp, LinearConstraint, Bounds
    U = U_de(K)
    if not U:
        return 0, [], True
    A = bolas1(U)
    cons = [LinearConstraint(A, -np.inf, m)]
    obj = -np.ones(len(U))
    if alvo is not None:
        cons.append(LinearConstraint(np.ones((1, len(U))), alvo, np.inf))
        obj = np.zeros(len(U))
    r = milp(obj, constraints=cons, integrality=np.ones(len(U)),
             bounds=Bounds(0, 1), options={"time_limit": tempo})
    if r.x is None:
        return 0, [], False
    P = [P5[U[i]] for i in range(len(U)) if r.x[i] > 0.5]
    return len(P), P, r.status == 0


def tau(K):
    """τ*(U): max Σw, w(B_1(y)∩U) <= 1. Devolve (valor, w float por ponto)."""
    from scipy.optimize import linprog
    U = U_de(K)
    if not U:
        return 0.0, {}
    A = bolas1(U)
    r = linprog(-np.ones(len(U)), A_ub=A, b_ub=np.ones(243), bounds=(0, None), method="highs")
    return -r.fun, {P5[U[i]]: r.x[i] for i in range(len(U)) if r.x[i] > 1e-12}


ESC = (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 60, 120, 1000, 10**4, 10**6)


def cert_fatia(K, M, v_w=None):
    """Certificado inteiro do degrau T (ou None). A busca da escala é em numpy; o veredito é
    `confere_fatia`, só com inteiros."""
    v, w = tau(K) if v_w is None else v_w
    if v <= M - len(K) + 1e-9:
        return v, None
    pts = list(w)
    A = (_dist5()[:, [IDX[p] for p in pts]] <= 1).astype(np.int64)
    x = np.array([w[p] for p in pts])
    for e in ESC:
        wi = np.floor(x * e + 1e-9).astype(np.int64)
        if wi.sum() > (A @ wi).max() * (M - len(K)):
            c = {p: int(a) for p, a in zip(pts, wi) if a}
            if confere_fatia(K, M, c):
                return v, c
    return v, None


def guloso(K, m=1, tentativas=200, semente=0):
    """m-empacotamento guloso aleatório em U (cota inferior). Devolve a maior lista achada."""
    U = U_de(K)
    if not U:
        return []
    A = bolas1(U).astype(np.int64)  # 243 x |U|
    viz = [np.nonzero(A[:, j])[0] for j in range(len(U))]
    rng = np.random.default_rng(semente)
    melhor = []
    for _ in range(tentativas):
        carga = np.zeros(243, np.int64)
        esc = []
        for j in rng.permutation(len(U)):
            if (carga[viz[j]] < m).all():
                carga[viz[j]] += 1
                esc.append(j)
        if len(esc) > len(melhor):
            melhor = esc
    return [P5[U[j]] for j in melhor]


def lp_fibras(K, M):
    """LP F (dual): max Σw + Σ f·falta - λ(M-s) com w(B_1(y)) + Σ f_{i,y_i} <= λ, Σw <= 1 (escala)."""
    from scipy.optimize import linprog
    s = len(K)
    U = U_de(K)
    nU = len(U)
    A1 = bolas1(U)
    Fy = np.zeros((243, 15))
    for y, p in enumerate(P5):
        for i in range(5):
            Fy[y, 3 * i + p[i]] = 1
    falta = np.array([s - sum(k[i] == b for k in K) for i in range(5) for b in range(3)], float)
    # variáveis: w (nU), f (15), λ (livre)
    c = -np.r_[np.ones(nU), falta, -(M - s)]
    A = np.hstack([A1, Fy, -np.ones((243, 1))])
    A = np.vstack([A, np.r_[np.ones(nU), np.zeros(16)][None]])
    b = np.r_[np.zeros(243), 1.0]
    r = linprog(c, A_ub=A, b_ub=b, bounds=[(0, None)] * (nU + 15) + [(None, None)], method="highs")
    return -r.fun, r.x[:nU], r.x[nU:nU + 15], r.x[-1], U


def cert_fibras(K, M):
    v, w, f, lam, U = lp_fibras(K, M)
    if v <= 1e-9:
        return v, None
    for e in ESC:
        wi = {P5[U[i]]: int(np.floor(x * e + 1e-9)) for i, x in enumerate(w)}
        wi = {p: x for p, x in wi.items() if x}
        fi = {(i // 3, i % 3): int(np.floor(x * e + 1e-9)) for i, x in enumerate(f)}
        fi = {k: x for k, x in fi.items() if x}
        # λ exato: o maior valor de centro com os pesos inteiros
        lam_i = max(sum(x for p, x in wi.items() if dist(y, p) <= 1) + sum(fi.get((i, y[i]), 0) for i in range(5))
                    for y in P5)
        if confere_fibras(K, M, wi, fi, lam_i):
            return v, (wi, fi, lam_i)
    return v, None
