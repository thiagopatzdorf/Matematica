"""Teste de completude por SAT para a CNF de `tools/exatos/fibras/fib_encode.py`, sem usar
`fib_canon.py`: para um código C, a CNF do perfil de C restrita à órbita de C sob
(S_q em cada coordenada) x (S_n nas coordenadas compatíveis com o perfil) x (reordenação das
palavras) tem de ser SAT. Se for UNSAT para algum C, a quebra de simetria perde C.

O codificador testado é carregado de um diretório dado (`FIBRAS_DIR` ou argumento), para poder
apontar para o commit auditado e para mutantes.
"""
import importlib.util
import itertools
import os
from collections import Counter

from pysat.solvers import Solver


def carregar_encode(diretorio, fonte=None, nome="fib_encode_auditado"):
    """Carrega fib_encode.py de `diretorio` (ou o texto `fonte`, para mutantes)."""
    caminho = os.path.join(diretorio, "fib_encode.py")
    if fonte is None:
        fonte = open(caminho).read()
    spec = importlib.util.spec_from_loader(nome, loader=None, origin=caminho)
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = caminho
    exec(compile(fonte, caminho, "exec"), mod.__dict__)
    return mod


def tipo(C, i, q):
    return tuple(sorted((Counter(c[i] for c in C).get(a, 0) for a in range(q)), reverse=True))


def eo(lits):
    return [list(lits)] + [[-a, -b] for a, b in itertools.combinations(lits, 2)]


def orbita_sat(enc, C, q, n, k=None, cobertura=True, ordem="min", smin=None, solver="cadical195",
               quebra_kw=None):
    """True sse algum elemento da órbita de C satisfaz a CNF (enc.codificar) do perfil de C."""
    k = n if k is None else k
    M = len(C)
    ts = [tipo(C, i, q) for i in range(n)]
    if smin is None:
        smin = min(min(t) for t in ts)
    ordenados = sorted(ts, key=lambda t: enc.chave_tipo(t, ordem))
    prefixo = tuple(ordenados[:k])
    alvo = list(prefixo) + [None] * (n - k)
    cnf, x, sim0, _ = enc.codificar(q, n, M, prefixo, smin, **(quebra_kw or {}))
    cl = list(cnf.cl)
    if not cobertura:
        n0 = len(enc.codificar(q, n, M, prefixo, smin, quebra=False)[0].cl)
        ini = n0 - q ** n
        cl = cl[:ini] + cl[n0:]
    top = cnf.nv

    def nv():
        nonlocal top
        top += 1
        return top

    extra = []
    pi = [[nv() for _ in range(M)] for _ in range(M)]          # palavra w da CNF <- palavra u de C
    Q = [[nv() for _ in range(n)] for _ in range(n)]           # coordenada i da CNF <- coord j de C
    sg = [[[nv() for _ in range(q)] for _ in range(q)] for _ in range(n)]  # símbolo de C na coord j
    for w in range(M):
        extra += eo(pi[w])
    for u in range(M):
        extra += eo([pi[w][u] for w in range(M)])
    for i in range(n):
        extra += eo(Q[i])
        extra += eo([Q[j][i] for j in range(n)])
        for j in range(n):
            # coordenadas de tipo fixo só recebem coordenada de C com o mesmo tipo; livres, as que
            # sobram (o tipo delas vem depois do prefixo na ordem total, que é o que (a) exige)
            if alvo[i] is not None and ts[j] != alvo[i]:
                extra.append([-Q[i][j]])
            if alvo[i] is None and enc.chave_tipo(ts[j], ordem) < enc.chave_tipo(prefixo[-1], ordem):
                extra.append([-Q[i][j]])
    for j in range(n):
        for a in range(q):
            extra += eo(sg[j][a])
        for b in range(q):
            extra += eo([sg[j][a][b] for a in range(q)])
    for w in range(M):
        for u in range(M):
            for j in range(n):
                extra.append([-pi[w][u], -Q[0][j], sg[j][C[u][j]][sim0[w]]])
                for i in range(1, n):
                    for b in range(q):
                        extra.append([-pi[w][u], -Q[i][j], -sg[j][C[u][j]][b], x[w][i][b]])
    with Solver(name=solver, bootstrap_with=cl + extra) as s:
        return s.solve()
