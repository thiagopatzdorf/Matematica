#!/usr/bin/env python3
"""Completude das quebras de simetria (a)-(h) por SAT, sem canonizador e sem importar o fib_canon.

Para um código C qualquer (cubra ou não), a CNF da instância de C (fib_encode.codificar com
quebra=True) restrita à ÓRBITA de C tem de ser satisfatível, onde a órbita é feita pelo grupo
completo: permutação das palavras P (M x M), das coordenadas Q (n x n) e dos símbolos S[i'] de
cada coordenada de destino (q x q). A imagem x é definida só por implicações Z & S -> x, e o
solver procura (P, Q, S) tal que x satisfaça a CNF. UNSAT = a CNF perde o código C (e,
se C cobre, perde uma solução de verdade).

Escrito do zero para esta revisão (o `orbita_fibras.py` do red team anterior não é usado).
Uso como biblioteca: orbita_sat(enc, q, n, M, R, cod, ordem, com_cobertura) -> True/False.
"""
import itertools
from collections import Counter


def tipo(cod, i, q):
    c = Counter(w[i] for w in cod)
    return tuple(sorted((c.get(a, 0) for a in range(q)), reverse=True))


def instancia_do_codigo(enc, cod, q, n, M, R, ordem, k=None):
    k = n if k is None else k
    tipos = sorted((tipo(cod, i, q) for i in range(n)), key=lambda t: enc.chave_tipo(t, ordem))
    smin = min(min(t) for t in tipos)
    _, ins = enc.instancias(q, n, M, k, smin, ordem=ordem)
    pref = tuple(tipos[:k])
    return smin, ins.index(pref), pref


def tirar_cobertura(cnf, q, n, M, R, nvx):
    """Remove as cláusulas de cobertura (só literais positivos de largura C(n, n-R), sobre variáveis
    auxiliares > as do x); as definições das P ficam. Para código que cobre isso não muda o veredito."""
    import math
    larg = math.comb(n, n - R)
    cnf.cl = [c for c in cnf.cl if not (len(c) == larg and all(l > 0 and l > nvx for l in c))]


def orbita_sat(enc, q, n, M, R, cod, ordem="min", com_cobertura=True, k=None, solver="cadical153"):
    from pysat.solvers import Solver
    k = n if k is None else k
    smin, idx, pref = instancia_do_codigo(enc, cod, q, n, M, R, ordem, k)
    cnf, x, sim0, ts = enc.codificar(q, n, M, pref, smin, R=R)
    nvx = max(x[w][i][a] for w in range(M) for i in range(1, n) for a in range(q))
    if not com_cobertura:
        tirar_cobertura(cnf, q, n, M, R, nvx)
    cl = [list(c) for c in cnf.cl]
    nv = [cnf.nv]

    def nova():
        nv[0] += 1
        return nv[0]

    def perm(N):
        m = [[nova() for _ in range(N)] for _ in range(N)]
        for r in range(N):
            cl.append(m[r][:])
            for a, b in itertools.combinations(range(N), 2):
                cl.append([-m[r][a], -m[r][b]])
        for c in range(N):
            col = [m[r][c] for r in range(N)]
            cl.append(col)
            for a, b in itertools.combinations(range(N), 2):
                cl.append([-col[a], -col[b]])
        return m

    P = perm(M)                        # P[w'][w]
    Q = perm(n)                        # Q[i'][i]
    S = [perm(q) for _ in range(n)]    # S[i'][a'][a]
    for wp in range(M):
        for ip in range(n):
            for w in range(M):
                for i in range(n):
                    z = nova()
                    cl.append([-P[wp][w], -Q[ip][i], z])      # z >= P & Q
                    c = cod[w][i]
                    for ap in range(q):
                        if ip == 0:
                            if sim0[wp] != ap:
                                cl.append([-z, -S[0][ap][c]])
                        else:
                            cl.append([-z, -S[ip][ap][c], x[wp][ip][ap]])
    with Solver(name=solver, bootstrap_with=cl) as s:
        return s.solve()


def codigo_com_perfil(q, n, tipos, rng):
    """Código aleatório cujas colunas têm exatamente as fibras de `tipos` (uma coluna por tipo, em ordem
    aleatória das palavras). Pode não cobrir; é o pior caso para empates de (g) e (h)."""
    M = sum(tipos[0])
    cols = []
    for t in tipos:
        col = [a for a in range(q) for _ in range(t[a])]
        rng.shuffle(col)
        cols.append(col)
    cod = [tuple(cols[i][w] for i in range(n)) for w in range(M)]
    return cod


def embaralhar(cod, q, n, rng):
    perm = list(range(n))
    rng.shuffle(perm)
    sims = [rng.sample(range(q), q) for _ in range(n)]
    out = [tuple(sims[i][c[perm[i]]] for i in range(n)) for c in cod]
    rng.shuffle(out)
    return out
