#!/usr/bin/env python3
"""Completude da fatia mínima como algoritmo: leva qualquer código de K_q(n,R) com M palavras
distintas a uma instância de `fatia.instancias` por uma isometria de Hamming, e devolve o
código transformado (que deve satisfazer todas as restrições do OPB da instância, exceto
cobertura se o código não cobre). Usado pelos testes (tests/test_gaps2.py)."""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fatia  # noqa: E402


def normalizar(cod, q, n):
    cnt = {(j, a): sum(1 for c in cod if c[j] == a) for j in range(n) for a in range(q)}
    s = min(cnt.values())
    j, a = min(k for k, v in cnt.items() if v == s)
    # coordenada j -> 0; símbolo a -> 0; outros símbolos da coord 0 por bloco decrescente
    perm = [j] + [i for i in range(n) if i != j]
    cod = [tuple(c[i] for i in perm) for c in cod]
    outros = sorted((b for b in range(q) if b != a), key=lambda b: (-cnt[j, b], b))
    ren0 = {a: 0, **{b: r + 1 for r, b in enumerate(outros)}}
    cod = [(ren0[c[0]],) + c[1:] for c in cod]
    F = [c[1:] for c in cod if c[0] == 0]
    m = n - 1
    if s > 0:
        # acha a ordem dos pontos e a isometria que levam F à forma canônica
        melhor = None
        for pp in itertools.permutations(range(s)):
            cols = [fatia.rgs([F[p][i] for p in pp]) for i in range(m)]
            chave = tuple(sorted(cols))
            if melhor is None or chave < melhor[0]:
                melhor = (chave, pp, cols)
        chave, pp, cols = melhor
        ordem_coord = sorted(range(m), key=lambda i: cols[i])  # estável
        sims = []
        for i in range(m):
            ren = {}
            for p in pp:
                ren.setdefault(F[p][i], len(ren))
            livres = iter(v for v in range(q) if v not in ren.values())
            for v in range(q):
                if v not in ren:
                    ren[v] = next(livres)
            sims.append(ren)
        cod = [(c[0],) + tuple(sims[i][c[1 + i]] for i in ordem_coord) for c in cod]
        K = tuple(fatia.de_colunas(chave))
    else:
        K = ()
    t = tuple(sorted((sum(1 for c in cod if c[0] == b) for b in range(1, q)), reverse=True))
    return (s, K, t), cod


def restricoes_violadas(q, n, R, M, inst, cod):
    """Avalia as restrições do OPB de `fatia_pb` direto no código (sem solver)."""
    import fatia_pb
    txt, var = fatia_pb.opb(q, n, R, M, inst)
    z = {v: int(c in set(cod)) for c, v in var.items()}
    ruins = []
    for ln in txt.splitlines()[1:]:
        tok = ln.rstrip(" ;").split()
        op, rhs = tok[-2], int(tok[-1])
        lhs = sum(int(tok[k]) * z[int(tok[k + 1][1:])] for k in range(0, len(tok) - 2, 2))
        if not (lhs >= rhs if op == ">=" else lhs == rhs):
            ruins.append(ln)
    return ruins
