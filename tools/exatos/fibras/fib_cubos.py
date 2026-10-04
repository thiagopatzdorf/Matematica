#!/usr/bin/env python3
"""Cubos (cube-and-conquer) para uma instância de fib_encode: divide pela coordenada 1.

Um cubo fixa o símbolo da coordenada 1 das L primeiras palavras. A lista é a de TODOS os
prefixos de comprimento L de atribuições da coordenada 1 que satisfazem as cláusulas da CNF que
só falam da coordenada 1: uma palavra por símbolo, fibra (exata se o tipo é fixo, >= s_min se
livre), (d) não decrescente dentro do bloco e (e) precedência por bloco dentro da classe. Toda
atribuição que satisfaz a CNF inteira satisfaz essas cláusulas, logo tem o prefixo de algum
cubo: a instância é UNSAT sse todos os cubos são UNSAT (CNF + cláusulas unitárias do cubo).
`tests/test_fibras.py` confere a enumeração contra força bruta em casos pequenos.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fib_encode as enc  # noqa: E402


def atribuicoes_coord1(q, M, t0, t1, smin, L=None):
    """Prefixos (comprimento L, padrão M) de atribuições válidas da coordenada 1."""
    L = M if L is None else L
    bl = enc.blocos(t0)
    blk = [b for b, B in enumerate(bl) for _ in B]
    cls = enc.classes(q, t1)
    alvo = t1
    cnt = [0] * q
    pal = []
    out = set()

    def falta_minima():
        # palavras ainda necessárias para completar as fibras
        if alvo is None:
            return sum(max(0, smin - c) for c in cnt)
        return sum(alvo[a] - cnt[a] for a in range(q))

    def rec(w):
        if M - w < falta_minima():
            return
        if w == L:
            if L < M or (alvo is None and all(c >= smin for c in cnt)) or \
                    (alvo is not None and all(cnt[a] == alvo[a] for a in range(q))):
                if L == M or completa(w):
                    out.add(tuple(pal))
            return
        lo = pal[-1] if w > 0 and blk[w - 1] == blk[w] else 0
        for a in range(lo, q):
            if alvo is not None and cnt[a] >= alvo[a]:
                continue
            if a > 0 and cls[a - 1] == cls[a] and cnt[a - 1] == 0:
                continue
            cnt[a] += 1
            pal.append(a)
            rec(w + 1)
            cnt[a] -= 1
            pal.pop()

    def completa(w):
        # existe extensão até M? (busca em profundidade com o mesmo critério)
        achou = [False]

        def ext(v):
            if achou[0] or M - v < falta_minima():
                return
            if v == M:
                ok = all(c >= smin for c in cnt) if alvo is None else all(cnt[a] == alvo[a] for a in range(q))
                achou[0] = achou[0] or ok
                return
            lo = pal[-1] if v > 0 and blk[v - 1] == blk[v] else 0
            for a in range(lo, q):
                if alvo is not None and cnt[a] >= alvo[a]:
                    continue
                if a > 0 and cls[a - 1] == cls[a] and cnt[a - 1] == 0:
                    continue
                cnt[a] += 1
                pal.append(a)
                ext(v + 1)
                cnt[a] -= 1
                pal.pop()
                if achou[0]:
                    return

        ext(w)
        return achou[0]

    rec(0)
    return sorted(out)


def unitarias(x, cubo):
    return [[x[w][1][a]] for w, a in enumerate(cubo)]
