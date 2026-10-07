#!/usr/bin/env python3
"""Codificador de cobertura escrito do zero (não importa nada de tools/exatos/fibras nem de k742).

Variáveis: w[u][i][a] = "a palavra u tem símbolo a na coordenada i" (one-hot em TODAS as coordenadas).
Cobertura (Lema 2' redito à mão): x é coberto por u sse u concorda com x em >= t = n - R coordenadas.
Aqui NÃO há projeção por t-uplas: para cada (x, u) uma variável m[x][u] com m -> "pelo menos t das n
igualdades w[u][i][x_i] valem", feito com um contador sequencial próprio (só o sentido necessário
para satisfatibilidade: m -> cardinalidade), e uma cláusula OU_u m[x][u] por ponto x.
Quebras de simetria mínimas e óbvias: palavras em ordem lexicográfica (multiconjunto: <=), nada mais,
a não ser que o chamador peça. Resolve com pysat (Cadical153) se houver.
"""
import itertools


class F:
    def __init__(self):
        self.nv = 0
        self.cl = []

    def var(self):
        self.nv += 1
        return self.nv

    def add(self, c):
        self.cl.append(list(c))


def pelo_menos(f, lits, k):
    """sum(lits) >= k, contador sequencial de Sinz só no sentido '>=': s[i][j] -> (>= j+1 entre as i+1 primeiras)."""
    n = len(lits)
    if k <= 0:
        return
    if k > n:
        f.add([])
        return
    # r[i][j]: dentre lits[0..i], pelo menos j+1 verdadeiros (r -> condição). Implicações r[i][j] -> r[i-1][j] v (r[i-1][j-1] ^ lit)
    r = [[f.var() for _ in range(k)] for _ in range(n)]
    f.add([r[n - 1][k - 1]])
    for i in range(n):
        for j in range(k):
            v = r[i][j]
            if i == 0:
                if j == 0:
                    f.add([-v, lits[0]])
                else:
                    f.add([-v])
                continue
            if j == 0:
                f.add([-v, r[i - 1][0], lits[i]])
            else:
                f.add([-v, r[i - 1][j], r[i - 1][j - 1]])
                f.add([-v, r[i - 1][j], lits[i]])


def codificar(q, n, R, M, ordem_lex=True, prefixo_fibra=None):
    """CNF 'existe multiconjunto de M palavras de Z_q^n que cobre com raio R'.
    prefixo_fibra: dict (i, a) -> s  =  exatamente s palavras com símbolo a na coordenada i."""
    t = n - R
    f = F()
    w = [[[f.var() for _ in range(q)] for _ in range(n)] for _ in range(M)]
    for u in range(M):
        for i in range(n):
            f.add(w[u][i])
            for a, b in itertools.combinations(range(q), 2):
                f.add([-w[u][i][a], -w[u][i][b]])
    if prefixo_fibra:
        for (i, a), s in prefixo_fibra.items():
            col = [w[u][i][a] for u in range(M)]
            exatamente(f, col, s)
    for x in itertools.product(range(q), repeat=n):
        ms = []
        for u in range(M):
            m = f.var()
            pelo_menos_cond(f, m, [w[u][i][x[i]] for i in range(n)], t)
            ms.append(m)
        f.add(ms)
    if ordem_lex:
        for u in range(M - 1):
            lex_leq_ok(f, [w[u][i] for i in range(n)], [w[u + 1][i] for i in range(n)], q)
    return f, w


def pelo_menos_cond(f, m, lits, k):
    """m -> sum(lits) >= k."""
    n = len(lits)
    if k <= 0:
        return
    if k > n:
        f.add([-m])
        return
    r = [[f.var() for _ in range(k)] for _ in range(n)]
    f.add([-m, r[n - 1][k - 1]])
    for i in range(n):
        for j in range(k):
            v = r[i][j]
            if i == 0:
                f.add([-v, lits[0]] if j == 0 else [-v])
                continue
            if j == 0:
                f.add([-v, r[i - 1][0], lits[i]])
            else:
                f.add([-v, r[i - 1][j], r[i - 1][j - 1]])
                f.add([-v, r[i - 1][j], lits[i]])


def exatamente(f, lits, s):
    """sum(lits) == s: >= s por contador e <= s como >= (n-s) das negações."""
    pelo_menos(f, lits, s)
    pelo_menos(f, [-l for l in lits], len(lits) - s)


def lex_leq_ok(f, A, B, q):
    """A <=lex B (listas de one-hots), com variável de igualdade DEFINIDA nos dois sentidos."""
    eq_ant = None
    for r in range(len(A)):
        pre = [-eq_ant] if eq_ant else []
        for a in range(q):
            for b in range(a):
                f.add(pre + [-A[r][a], -B[r][b]])
        if r == len(A) - 1:
            return
        e = f.var()
        # e <-> (eq_ant e A[r]==B[r])
        iguais = []
        for a in range(q):
            y = f.var()                   # y <-> A[r][a] e B[r][a]
            f.add([-y, A[r][a]])
            f.add([-y, B[r][a]])
            f.add([y, -A[r][a], -B[r][a]])
            iguais.append(y)
        # e <-> eq_ant e OR(iguais)
        f.add([-e] + iguais)
        if eq_ant:
            f.add([-e, eq_ant])
            for y in iguais:
                f.add([-y, -eq_ant, e])
        else:
            for y in iguais:
                f.add([-y, e])
        eq_ant = e


def decodificar(modelo, w, q, n):
    pos = {l for l in modelo if l > 0}
    return [tuple(next(a for a in range(q) if w[u][i][a] in pos) for i in range(n)) for u in range(len(w))]


def resolver(f, assumptions=(), solver="cadical153"):
    from pysat.solvers import Solver
    with Solver(name=solver, bootstrap_with=f.cl) as s:
        ok = s.solve(assumptions=list(assumptions))
        return (ok, s.get_model() if ok else None)


def cobre(cod, q, n, R):
    """Predicado de cobertura por força bruta pela definição de distância (sem Lema 2')."""
    for x in itertools.product(range(q), repeat=n):
        if not any(sum(a != b for a, b in zip(x, c)) <= R for c in cod):
            return False
    return True
