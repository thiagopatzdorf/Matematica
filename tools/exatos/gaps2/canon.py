#!/usr/bin/env python3
"""Completude da redução de `proj.py` como algoritmo: leva qualquer código de K_q(n,R) com M
palavras (fibras >= smin) à forma normal da CNF do seu perfil, usando só isometrias de Hamming
(S_q em cada coordenada, S_n nas coordenadas) e uma ordem das palavras.

Passos (prova em docs/exatos/GAPS2_K362.md, seção "Completude"):
 (a) coordenadas na ordem do perfil (ordenação estável pela posição do tipo);
 (b) símbolos de cada coordenada em ordem decrescente de fibra;
 (c)-(e) blocos pela coordenada 0; coordenada 1 renomeada por primeira aparição por bloco
     dentro de cada classe de fibra; palavras ordenadas por (coord 0, coord 1), estável;
 (f) coordenadas >= 2 renomeadas por primeira aparição na ordem das palavras;
 (g) coordenadas >= 2 de mesmo tipo: colunas ordenadas lexicograficamente (a renomeação (f)
     de cada coluna só depende da ordem das palavras, que não muda).
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import proj  # noqa: E402


def tipo(cod, i, q):
    return tuple(sorted((Counter(c[i] for c in cod).get(a, 0) for a in range(q)), reverse=True))


def classes(t, q):
    livres = {}
    for a in range(q):
        livres.setdefault(t[a], []).append(a)
    return livres


def canonizar(cod, q, n, R, smin=None):
    M = len(cod)
    if smin is None:
        smin = proj.fibra_minima(q, n, R, M)
    ordem = {t: r for r, t in enumerate(proj.ordem_tipos(q, M, smin))}
    ts = [tipo(cod, i, q) for i in range(n)]
    perm = sorted(range(n), key=lambda i: ordem[ts[i]])
    cod = [tuple(c[i] for i in perm) for c in cod]
    perfil = tuple(ts[i] for i in perm)
    # (b)
    for i in range(n):
        cnt = Counter(c[i] for c in cod)
        ren = {a: r for r, a in enumerate(sorted(range(q), key=lambda a: (-cnt.get(a, 0), a)))}
        cod = [c[:i] + (ren[c[i]],) + c[i + 1:] for c in cod]
    # (c)-(e)
    livres = classes(perfil[1], q)
    ren1 = {}
    for b in range(q):
        for a in sorted({c[1] for c in cod if c[0] == b and c[1] not in ren1}):
            ren1[a] = livres[perfil[1][a]].pop(0)
    for a in range(q):
        if a not in ren1:
            ren1[a] = livres[perfil[1][a]].pop(0)
    cod = [(c[0], ren1[c[1]]) + c[2:] for c in cod]
    cod.sort(key=lambda c: (c[0], c[1]))
    # (f)
    for i in range(2, n):
        livres = classes(perfil[i], q)
        ren = {}
        for c in cod:
            if c[i] not in ren:
                ren[c[i]] = livres[perfil[i][c[i]]].pop(0)
        for a in range(q):
            if a not in ren:
                ren[a] = livres[perfil[i][a]].pop(0)
        cod = [c[:i] + (ren[c[i]],) + c[i + 1:] for c in cod]
    # (g)
    cols = [[c[i] for c in cod] for i in range(n)]
    i = 2
    while i < n:
        j = i
        while j + 1 < n and perfil[j + 1] == perfil[i]:
            j += 1
        cols[i:j + 1] = sorted(cols[i:j + 1])
        i = j + 1
    cod = [tuple(cols[i][k] for i in range(n)) for k in range(M)]
    return perfil, cod


def atribuicao(cnf, x, cod, q, n):
    val = {}
    for k, c in enumerate(cod):
        for i in range(1, n):
            for a in range(q):
                val[x[k][i][a]] = (c[i] == a)
    for v, op, lits in cnf.defs:
        vs = [val[abs(l)] == (l > 0) for l in lits]
        val[v] = all(vs) if op == "and" else any(vs)
    mudou = True
    while mudou:  # contadores e e[k] de (g): ficam determinados por propagação
        mudou = False
        for cl in cnf.cl:
            if any(val.get(abs(l)) == (l > 0) for l in cl if abs(l) in val):
                continue
            livres = [l for l in cl if abs(l) not in val]
            if len(livres) == 1:
                val[abs(livres[0])] = livres[0] > 0
                mudou = True
    for v in range(1, cnf.nv + 1):  # e[k] que nenhuma cláusula força: falso é seguro
        val.setdefault(v, False)
    return val


def violadas(cnf, val):
    return [cl for cl in cnf.cl if not any(val[abs(l)] == (l > 0) for l in cl)]
