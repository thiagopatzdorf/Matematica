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
coordenada 0, com tamanhos t_1 >= ... >= t_{q-1} >= s* (renomeie os símbolos). As palavras
são distintas: com M <= q^n, um código com repetição pode trocar a cópia por uma palavra nova e
continua cobrindo. Toda fibra de toda coordenada tem >= s* palavras. A codificação está em
`fatia_pb.py`; a completude (todo código cai numa instância cujo OPB ele satisfaz), em
`canon_fatia.py` e nos testes. Prova escrita em docs/exatos/GAPS2_K362.md.
"""
import argparse
import itertools
from collections import Counter
from math import comb


def vol(n, R, q):
    """Volume da bola de Hamming de raio R em Z_q^n."""
    return sum(comb(n, i) * (q - 1) ** i for i in range(R + 1)) if R >= 0 else 0


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
