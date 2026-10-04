#!/usr/bin/env python3
"""Leva qualquer código de K_q(4,2) com M palavras à forma normal da redução (prova construtiva).

Este é o argumento de completude do README escrito como algoritmo: recebe um código C
(qualquer, com fibras >= s_min), aplica só operações do grupo S_q wr S_4 e uma ordem das
palavras, e devolve (índice do perfil, atribuição das variáveis x). Os testes conferem que a
atribuição satisfaz TODAS as cláusulas da CNF do perfil, exceto as de cobertura quando C não
cobre. Logo, se a CNF de todo perfil é UNSAT, não existe código de cobertura com M palavras.
"""
import itertools
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import encode  # noqa: E402

N = encode.N


def tipo_da_coord(cod, i, q):
    return tuple(sorted(Counter(c[i] for c in cod).get(a, 0) for a in range(q))[::-1])


def canonizar(cod, q):
    """cod: lista de tuplas. Devolve (perfil_idx, palavras normalizadas em ordem)."""
    M = len(cod)
    ps = encode.perfis(q, M)
    ordem_tipo = {t: r for r, t in enumerate(sorted(
        {t for p in ps for t in p}, key=lambda t: (encode.simetria_residual(t), t)))}
    tipos = [tipo_da_coord(cod, i, q) for i in range(N)]
    # (a) permuta coordenadas para o perfil ficar na ordem canônica (ordenação estável)
    perm = sorted(range(N), key=lambda i: ordem_tipo[tipos[i]])
    cod = [tuple(c[i] for i in perm) for c in cod]
    perfil = tuple(tipos[i] for i in perm)
    idx = ps.index(perfil)
    # (b) renomeia símbolos: fibra decrescente (empates por ora arbitrários: rótulo original)
    for i in range(N):
        cnt = Counter(c[i] for c in cod)
        ordem = sorted(range(q), key=lambda a: (-cnt.get(a, 0), a))
        ren = {a: r for r, a in enumerate(ordem)}
        cod = [tuple(ren[c[j]] if j == i else c[j] for j in range(N)) for c in cod]
    # (c)+(d)+(e): blocos pela coord 0; coord 1 renomeada por primeira aparição por bloco
    # dentro de cada classe de fibra, com os símbolos novos do bloco em ordem arbitrária
    # (aqui: rótulo atual) e depois ordenados dentro do bloco.
    t1 = perfil[1]
    classes1 = {}
    for a in range(q):
        classes1.setdefault(t1[a], []).append(a)  # rótulos de cada classe, crescentes
    livres = {s: list(v) for s, v in classes1.items()}
    ren1 = {}
    for b in range(q):
        novos = sorted({c[1] for c in cod if c[0] == b and c[1] not in ren1})
        for a in novos:
            ren1[a] = livres[t1[a]].pop(0)
    for a in range(q):
        if a not in ren1:  # não acontece com fibras >= 1
            ren1[a] = livres[t1[a]].pop(0)
    cod = [(c[0], ren1[c[1]], c[2], c[3]) for c in cod]
    cod.sort(key=lambda c: (c[0], c[1]))  # estável: empates mantêm a ordem
    # (f) coords 2 e 3: renomeia por primeira aparição na ordem das palavras, por classe
    for i in (2, 3):
        ti = perfil[i]
        livres = {}
        for a in range(q):
            livres.setdefault(ti[a], []).append(a)
        ren = {}
        for c in cod:
            if c[i] not in ren:
                ren[c[i]] = livres[ti[c[i]]].pop(0)
        for a in range(q):
            if a not in ren:
                ren[a] = livres[ti[a]].pop(0)
        cod = [tuple(ren[c[j]] if j == i else c[j] for j in range(N)) for c in cod]
    return idx, cod


def atribuicao(cnf, x, cod, q):
    """Completa a atribuição de todas as variáveis da CNF a partir das palavras normalizadas,
    propagando as definições (contadores, y, P) por unidade."""
    val = {}
    for k, c in enumerate(cod):
        for i in range(1, N):
            for a in range(q):
                val[x[k][i][a]] = (c[i] == a)
    # propagação até ponto fixo: toda variável auxiliar é definida funcionalmente
    mudou = True
    while mudou:
        mudou = False
        for cl in cnf.cl:
            livres = [l for l in cl if abs(l) not in val]
            if any(val.get(abs(l)) == (l > 0) for l in cl if abs(l) in val):
                continue
            if len(livres) == 1:
                l = livres[0]
                val[abs(l)] = l > 0
                mudou = True
    return val


def clausulas_violadas(cnf, val):
    ruins = []
    for cl in cnf.cl:
        if not any(val.get(abs(l), False) == (l > 0) for l in cl):
            ruins.append(cl)
    return ruins


def cobre(cod, q):
    for w in itertools.product(range(q), repeat=N):
        if not any(sum(a != b for a, b in zip(w, c)) <= 2 for c in cod):
            return False
    return True
