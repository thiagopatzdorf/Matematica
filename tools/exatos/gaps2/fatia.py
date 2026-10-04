#!/usr/bin/env python3
"""Redução de K_q(n,R) <= M por "fatia mínima": CNFs pequenas, uma por configuração.

Seja C um código de raio R em Z_q^n com M palavras e s* o menor tamanho de fibra
F(j,a) = {c in C : c_j = a} sobre todas as coordenadas j e símbolos a. Escolha (j,a) com
|F(j,a)| = s*; leve j à coordenada 0 e a ao símbolo 0. A fatia {x : x_0 = 0} é coberta pelas
s* palavras de F (raio R nas outras n-1 coordenadas) e pelas M-s* restantes (raio R-1, pois já
diferem na coordenada 0). Logo:

  (contagem) |U| <= (M - s*) * V(n-1, R-1), onde U = pontos de Z_q^(n-1) a distância > R
  das projeções de F;

e as projeções de F formam uma configuração de s* pontos de Z_q^(n-1), que a menos de
isometria é uma das listadas por `configuracoes` (colunas = cadeias de crescimento restrito,
a menos de permutar coordenadas e pontos).

Instância (s*, configuração K, tamanhos dos outros blocos da coordenada 0): as s* primeiras
palavras são K com símbolo 0 na coordenada 0; as outras vêm em blocos pelo símbolo 1..q-1 da
coordenada 0, com tamanhos t_1 >= ... >= t_{q-1} >= s* (renomeie os símbolos), em ordem
lexicográfica estrita dentro de cada bloco (palavras distintas: um código com repetição tem um
subcódigo menor que também cobre, e pode-se completar com palavras novas). Toda fibra de toda
coordenada tem >= s* palavras. Cobertura pelas projeções em (n-R)-subconjuntos, como em
`proj.py`. Completude: `canon_fatia.py` e os testes.
"""
import argparse
import itertools
import sys
from collections import Counter

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from proj import CNF, vol  # noqa: E402


def dist(a, b):
    return sum(x != y for x, y in zip(a, b))


def rgs(col):
    ren = {}
    return tuple(ren.setdefault(v, len(ren)) for v in col)


def forma(pontos):
    """Forma canônica de um conjunto de pontos a menos de isometria de Hamming: mínimo, sobre
    as ordens dos pontos, do multiconjunto ordenado das colunas normalizadas (RGS)."""
    s, m = len(pontos), len(pontos[0])
    melhor = None
    for perm in itertools.permutations(range(s)):
        cols = tuple(sorted(rgs([pontos[p][i] for p in perm]) for i in range(m)))
        if melhor is None or cols < melhor:
            melhor = cols
    return melhor


def de_colunas(cols):
    s = len(cols[0])
    return [tuple(c[k] for c in cols) for k in range(s)]


def configuracoes(q, m, s, R=None, cap=None):
    """Representantes (um por classe de isometria) dos conjuntos de s pontos distintos de
    Z_q^m. Com R e cap, só os que deixam <= cap pontos a distância > R (filtro de contagem,
    aplicado antes da forma canônica, que é a parte cara)."""
    import numpy as np
    pats = [p for p in itertools.product(range(q), repeat=s)
            if all(p[i] <= max(p[:i], default=-1) + 1 for i in range(s))]
    X = np.array(list(itertools.product(range(q), repeat=m)))
    A = np.array([[[int(v != p[k]) for k in range(s)] for v in range(q)] for p in pats])
    vistos = set()
    out = []
    for combo in itertools.combinations_with_replacement(range(len(pats)), m):
        cols = [pats[c] for c in combo]
        pts = de_colunas(cols)
        if len(set(pts)) < s:
            continue
        if cap is not None:
            D = sum(A[c][X[:, i]] for i, c in enumerate(combo))
            if int((D.min(axis=1) > R).sum()) > cap:
                continue
        f = forma(pts)
        if f not in vistos:
            vistos.add(f)
            out.append(de_colunas(f))
    return out


def descobertos(q, m, R, pts):
    return [x for x in itertools.product(range(q), repeat=m) if all(dist(x, p) > R for p in pts)]


def blocos_restantes(q, M, s):
    """Tamanhos t_1 >= ... >= t_{q-1} >= s com soma M - s."""
    out = []

    def rec(resto, partes, maximo, pref):
        if partes == 0:
            if resto == 0:
                out.append(tuple(pref))
            return
        for v in range(min(maximo, resto - s * (partes - 1)), s - 1, -1):
            rec(resto - v, partes - 1, v, pref + [v])

    rec(M - s, q - 1, M - s, [])
    return out


def instancias(q, n, R, M):
    """Lista de (s, configuração, blocos) que sobrevivem à contagem."""
    out = []
    for s in range(0, M // q + 1):
        cap = (M - s) * vol(n - 1, R - 1, q)
        cfgs = configuracoes(q, n - 1, s, R, cap) if s > 0 else [[]]
        for K in cfgs:
            if len(descobertos(q, n - 1, R, K)) > cap:
                continue
            for t in blocos_restantes(q, M, s):
                out.append((s, tuple(K), t))
    return out


def pelo_menos(cnf, xs, k):
    """sum(xs) >= k (contador sequencial, só a direção necessária)."""
    if k <= 0:
        return
    n = len(xs)
    if k > n:
        cnf.add([])
        return
    # r[i][j] -> pelo menos j+1 verdadeiros entre xs[0..i]
    r = [[cnf.var() for _ in range(k)] for _ in range(n)]
    for i in range(n):
        for j in range(k):
            v = r[i][j]
            if i == 0:
                if j == 0:
                    cnf.add([-v, xs[0]])
                else:
                    cnf.add([-v])
                continue
            if j == 0:
                cnf.add([-v, r[i - 1][0], xs[i]])
            else:
                cnf.add([-v, r[i - 1][j], xs[i]])
                cnf.add([-v, r[i - 1][j], r[i - 1][j - 1]])
    cnf.add([r[n - 1][k - 1]])


def lex_estrito(cnf, a, b, q):
    """a <lex b para palavras com literais one-hot a[i][v], b[i][v] (i = 0..L-1)."""
    L = len(a)
    e = None  # "iguais até aqui"
    for i in range(L):
        pre = [-e] if e else []
        for u in range(q):
            for v in range(u):
                cnf.add(pre + [-a[i][u], -b[i][v]])
        e2 = cnf.var()
        for u in range(q):
            cnf.add(pre + [-a[i][u], -b[i][u], e2])
        e = e2
    cnf.add([-e])  # não podem ser iguais em tudo


def codificar(q, n, R, M, inst):
    s, K, t = inst
    cnf = CNF()
    vt = cnf.var()  # constante verdadeira (palavras fixas usam vt / -vt)
    cnf.add([vt])
    sim0 = [0] * s + [b + 1 for b, tb in enumerate(t) for _ in range(tb)]
    x = []
    for k in range(M):
        linha = [None]
        for i in range(1, n):
            if k < s:
                linha.append([vt if K[k][i - 1] == a else -vt for a in range(q)])
            else:
                vs = [cnf.var() for _ in range(q)]
                cnf.add(vs)
                for a, b in itertools.combinations(range(q), 2):
                    cnf.add([-vs[a], -vs[b]])
                linha.append(vs)
        x.append(linha)
    for i in range(1, n):
        for a in range(q):
            pelo_menos(cnf, [x[k][i][a] for k in range(M)], s)
    ini = s
    for tb in t:
        for k in range(ini, ini + tb - 1):
            lex_estrito(cnf, x[k][1:], x[k + 1][1:], q)
        ini += tb
    m = n - R
    blocos = {}
    for k in range(M):
        blocos.setdefault(sim0[k], []).append(k)
    P = {}

    def proj(S, v):
        """Literal "alguma palavra casa v em S" (True se uma palavra fixa já casa)."""
        if (S, v) in P:
            return P[S, v]
        ks = blocos.get(v[0], []) if S[0] == 0 else range(M)
        resto = [(i, vi) for i, vi in zip(S, v) if i != 0]
        ys = []
        res = None
        for k in ks:
            lits = [x[k][i][vi] for i, vi in resto]
            if any(l == -vt for l in lits):
                continue
            lits = [l for l in lits if l != vt]
            if not lits:
                res = True
                break
            if len(lits) == 1:
                ys.append(lits[0])
                continue
            y = cnf.var()
            for l in lits:
                cnf.add([-y, l])
            cnf.defs.append((y, "and", lits))
            ys.append(y)
        if res is None:
            if not ys:
                res = False
            else:
                p = cnf.var()
                cnf.add([-p] + ys)
                cnf.defs.append((p, "or", ys))
                res = p
        P[S, v] = res
        return res

    subs = list(itertools.combinations(range(n), m))
    for w in itertools.product(range(q), repeat=n):
        lits = [proj(S, tuple(w[i] for i in S)) for S in subs]
        if any(l is True for l in lits):
            continue
        cnf.add([l for l in lits if l is not False])
    return cnf, x, sim0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("q", "n", "R", "M"):
        ap.add_argument("--" + k, type=int, required=True)
    a = ap.parse_args()
    ins = instancias(a.q, a.n, a.R, a.M)
    print(f"K_{a.q}({a.n},{a.R}) M={a.M}: {len(ins)} instâncias")
    print(Counter((i[0], i[2]) for i in ins))


if __name__ == "__main__":
    main()
