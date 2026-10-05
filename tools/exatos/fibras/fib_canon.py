#!/usr/bin/env python3
"""Completude da redução de `fibras/fib_encode.py` como algoritmo (generaliza k742/canonizar.py).

Recebe um código qualquer de Z_q^n com M palavras e fibras >= s_min, aplica só isometrias de
Hamming (S_q em cada coordenada, S_n nas coordenadas) e uma ordem das palavras, e devolve o
índice da instância (prefixo de k tipos) e as palavras na forma normal. Os testes conferem que
a atribuição lida da forma normal satisfaz todas as cláusulas da CNF da instância (menos as de
cobertura, quando o código não cobre). Logo: todas as instâncias UNSAT => não existe código.
"""
import itertools
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fib_encode as encode  # noqa: E402


def tipo_da_coord(cod, i, q):
    return tuple(sorted((Counter(c[i] for c in cod).get(a, 0) for a in range(q)), reverse=True))


def canonizar(cod, q, n, k, smin, usar_h=True, ordem="min"):
    M = len(cod)
    tipos = [tipo_da_coord(cod, i, q) for i in range(n)]
    # (a) coordenadas em ordem de chave_tipo (estável); as k primeiras definem a instância
    perm = sorted(range(n), key=lambda i: encode.chave_tipo(tipos[i], ordem))
    cod = [tuple(c[i] for i in perm) for c in cod]
    tipos = [tipos[i] for i in perm]
    prefixo = tuple(tipos[:k])
    _, ins = encode.instancias(q, n, M, k, smin, ordem=ordem)
    idx = ins.index(prefixo)
    ts = list(prefixo) + [None] * (n - k)
    # (b) coordenadas de tipo fixo: símbolo a passa a ter fibra ts[i][a] (decrescente)
    for i in range(k):
        cnt = Counter(c[i] for c in cod)
        ordem = sorted(range(q), key=lambda a: (-cnt.get(a, 0), a))
        ren = {a: r for r, a in enumerate(ordem)}
        cod = [tuple(ren[c[j]] if j == i else c[j] for j in range(n)) for c in cod]

    def classe(i, a, cnt):
        return ts[i][a] if ts[i] is not None else 0

    def livres_por_classe(i):
        out = {}
        for a in range(q):
            out.setdefault(ts[i][a] if ts[i] is not None else 0, []).append(a)
        return out

    # (c)+(d)+(e)+(h): blocos pela coordenada 0; coordenada 1 renomeada por primeira aparição
    # por bloco dentro da classe; blocos de mesmo tamanho reordenados pelo guloso do Lema 4
    # (a cada passo, o par bloco/rotulação admissível de menor vetor ordenado de rótulos da
    # coordenada 1; prova corrigida em REDTEAM_K764.md, seção 1.2).
    livres = livres_por_classe(1)
    ren1 = {}
    t0 = ts[0]

    def rotulos_se_agora(b):
        # menor vetor sobre as rotulações admissíveis por (e): dentro da classe, o símbolo novo
        # mais frequente no bloco leva o menor rótulo livre. Rotular na ordem do índice (como
        # era até o red team REDTEAM_K764.md, seção 1.1) viola (h) em ~1e-4 dos códigos.
        prox = {c: list(v) for c, v in livres.items()}
        pot = {}
        mult = Counter(c[1] for c in cod if c[0] == b)
        for a in sorted({c[1] for c in cod if c[0] == b and c[1] not in ren1}, key=lambda s: (-mult[s], s)):
            pot[a] = prox[classe(1, a, None)].pop(0)
        return sorted((ren1[c[1]] if c[1] in ren1 else pot[c[1]]) for c in cod if c[0] == b), pot

    ren0 = {}
    pos = 0
    while pos < q:
        grupo = [b for b in range(q) if t0[b] == t0[pos]]
        restantes = list(grupo)
        while restantes:
            b = min(restantes, key=lambda bb: (rotulos_se_agora(bb)[0] if usar_h else [], bb))
            if not usar_h:
                b = restantes[0]
            _, pot = rotulos_se_agora(b)
            for a, r in pot.items():
                ren1[a] = r
                livres[classe(1, a, None)].remove(r)
            ren0[b] = pos
            pos += 1
            restantes.remove(b)
    for a in range(q):
        if a not in ren1:
            ren1[a] = livres[classe(1, a, None)].pop(0)
    cod = [(ren0[c[0]], ren1[c[1]]) + tuple(c[2:]) for c in cod]
    cod.sort(key=lambda c: (c[0], c[1]))
    # (f) coordenadas >= 2: primeira aparição na ordem das palavras, por classe
    for i in range(2, n):
        livres = livres_por_classe(i)
        ren = {}
        for c in cod:
            if c[i] not in ren:
                ren[c[i]] = livres[classe(i, c[i], None)].pop(0)
        for a in range(q):
            if a not in ren:
                ren[a] = livres[classe(i, a, None)].pop(0)
        cod = [tuple(ren[c[j]] if j == i else c[j] for j in range(n)) for c in cod]
    # (g) ordena lexicograficamente cada grupo de colunas >= 2 de mesmo tipo
    i = 2
    while i < n:
        j = i
        while j + 1 < n and ts[j + 1] == ts[i]:
            j += 1
        cols = sorted(range(i, j + 1), key=lambda c: [w[c] for w in cod])
        ordem = list(range(i)) + cols + list(range(j + 1, n))
        cod = [tuple(w[c] for c in ordem) for w in cod]
        i = j + 1
    return idx, cod


def atribuicao(cnf, x, cod, q, n):
    val = {}
    for w, c in enumerate(cod):
        for i in range(1, n):
            for a in range(q):
                val[x[w][i][a]] = (c[i] == a)
    mudou = True
    while mudou:
        mudou = False
        for cl in cnf.cl:
            if any(val.get(abs(l)) == (l > 0) for l in cl if abs(l) in val):
                continue
            livres = [l for l in cl if abs(l) not in val]
            if len(livres) == 1:
                val[abs(livres[0])] = livres[0] > 0
                mudou = True
    return val


def violadas(cnf, val):
    return [cl for cl in cnf.cl if not any(val.get(abs(l), False) == (l > 0) for l in cl)]


def descobertos(cod, q, n):
    R = n - 2
    return sum(1 for w in itertools.product(range(q), repeat=n)
               if not any(sum(a != b for a, b in zip(w, c)) <= R for c in cod))
