#!/usr/bin/env python3
"""O grupo de Hamming S_q wr S_n agindo em palavras de Z_q^n (docs/exatos/k362/K3_M15_GROUP_ACTION.md).

Um elemento é g = (perm, sims): perm é uma permutação de range(n) e sims[i] uma permutação de
range(q). A ação é (g·c)_i = sims[i][c[perm[i]]]: a coordenada i da imagem lê a coordenada
perm[i] da palavra e troca o símbolo por sims[i]. É a mesma convenção dos testes de
tools/exatos/gaps2 (`isometria_aleatoria`), para que as duas frentes falem do mesmo grupo.
"""
import itertools
import random


def aplica(g, c):
    perm, sims = g
    return tuple(sims[i][c[perm[i]]] for i in range(len(perm)))


def aplica_codigo(g, cod):
    return sorted(aplica(g, c) for c in cod)


def compoe(g, h):
    """g∘h: primeiro h, depois g. (g·(h·c))_i = gs[i][(h·c)[gp[i]]] = gs[i][hs[gp[i]][c[hp[gp[i]]]]]."""
    gp, gs = g
    hp, hs = h
    n = len(gp)
    return (tuple(hp[gp[i]] for i in range(n)),
            tuple(tuple(gs[i][hs[gp[i]][v]] for v in range(len(gs[i]))) for i in range(n)))


def inverso(g):
    perm, sims = g
    n, q = len(perm), len(sims[0])
    ip = [0] * n
    for i, p in enumerate(perm):
        ip[p] = i
    isims = [None] * n
    for i, p in enumerate(perm):
        inv = [0] * q
        for v, w in enumerate(sims[i]):
            inv[w] = v
        isims[p] = tuple(inv)
    return tuple(ip), tuple(isims)


def identidade(q, n):
    return tuple(range(n)), tuple(tuple(range(q)) for _ in range(n))


def aleatorio(q, n, rng=random):
    perm = list(range(n))
    rng.shuffle(perm)
    return tuple(perm), tuple(tuple(rng.sample(range(q), q)) for _ in range(n))


def todos(q, n):
    """Os q!^n · n! elementos (só para n pequeno: força bruta dos testes)."""
    for perm in itertools.permutations(range(n)):
        for sims in itertools.product(itertools.permutations(range(q)), repeat=n):
            yield perm, sims


def ordem(q, n):
    from math import factorial
    return factorial(q) ** n * factorial(n)
