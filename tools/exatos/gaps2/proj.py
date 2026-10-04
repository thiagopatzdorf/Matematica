#!/usr/bin/env python3
"""Redução de K_q(n,R) <= M a CNFs por perfil de fibras (generaliza `tools/exatos/k742`).

Cobertura por projeções: d(x,c) <= R  <=>  x e c concordam em algum conjunto S de n-R
coordenadas. Variável P[S,v] ("alguma palavra tem v nas coordenadas S"); a cobertura de x é a
cláusula OR_S P[S, x_S]. Só a direção P -> OR_k (palavra k casa v em S) é necessária para a
contrapositiva (UNSAT => não existe código), e é a única codificada.

Lema das fibras (contagem, prova em docs/exatos/GAPS2_K362.md): se F(j,a) tem s palavras,
os pontos x com x_j = a a distância > R (nas outras n-1 coordenadas) de todas as s palavras de
F só podem ser cobertos por palavras fora de F, a distância <= R-1 nas outras coordenadas.
Logo q^(n-1) - s*V(n-1,R) <= (M-s)*V(n-1,R-1); o menor s que passa é `fibra_minima`.

Perfil: o tipo (tamanhos de fibra, decrescente) de cada coordenada; a menos de permutar
coordenadas, um multiconjunto de n tipos. Quebra de simetria, como em k742: (a) coordenadas na
ordem do perfil; (b) símbolos em ordem decrescente de fibra; (c) palavras em blocos pelo
símbolo da coordenada 0; (d) dentro do bloco, coordenada 1 não decrescente; (e) coordenada 1:
precedência por bloco entre símbolos de mesma fibra; (f) coordenadas 2..n-1: precedência por
palavra entre símbolos de mesma fibra. Completude: `canon.py` (e os testes).
"""
import argparse
import itertools
import math
import sys
from collections import Counter
from math import comb


def vol(n, R, q):
    return sum(comb(n, i) * (q - 1) ** i for i in range(R + 1)) if R >= 0 else 0


def fibra_minima(q, n, R, M):
    """Menor s que a contagem do lema das fibras não exclui."""
    s = 0
    while s < M and q ** (n - 1) - s * vol(n - 1, R, q) > (M - s) * vol(n - 1, R - 1, q):
        s += 1
    return s


def tipos(q, M, smin):
    out = []

    def rec(resto, partes, maximo, pref):
        if partes == 0:
            if resto == 0:
                out.append(tuple(pref))
            return
        for v in range(min(maximo, resto - smin * (partes - 1)), smin - 1, -1):
            rec(resto - v, partes - 1, v, pref + [v])

    rec(M, q, M, [])
    return out


def simetria_residual(t):
    r = 1
    for c in Counter(t).values():
        r *= math.factorial(c)
    return r


def ordem_tipos(q, M, smin):
    return sorted(tipos(q, M, smin), key=lambda t: (simetria_residual(t), t))


def perfis(q, n, R, M, smin=None):
    if smin is None:
        smin = fibra_minima(q, n, R, M)
    return list(itertools.combinations_with_replacement(ordem_tipos(q, M, smin), n))


class CNF:
    def __init__(self):
        self.nv = 0
        self.cl = []
        self.defs = []  # (var, "and"|"or", literais): definições usadas por canon.atribuicao

    def var(self):
        self.nv += 1
        return self.nv

    def add(self, c):
        self.cl.append(list(c))

    def dimacs(self, comentarios=()):
        linhas = ["c " + s for s in comentarios]
        linhas.append(f"p cnf {self.nv} {len(self.cl)}")
        linhas += [" ".join(map(str, c)) + " 0" for c in self.cl]
        return "\n".join(linhas) + "\n"


def exatamente(cnf, xs, k):
    """sum(xs) == k (contador sequencial de Sinz com equivalências)."""
    n = len(xs)
    if k > n:
        cnf.add([])
        return
    r = [[cnf.var() for _ in range(k + 1)] for _ in range(n)]
    for i in range(n):
        for j in range(k + 1):
            v = r[i][j]
            if i == 0:
                if j == 0:
                    cnf.add([-v, xs[0]])
                    cnf.add([v, -xs[0]])
                else:
                    cnf.add([-v])
                continue
            prev = r[i - 1][j]
            cnf.add([-prev, v])
            if j == 0:
                cnf.add([-xs[i], v])
                cnf.add([-v, prev, xs[i]])
            else:
                pj = r[i - 1][j - 1]
                cnf.add([-pj, -xs[i], v])
                cnf.add([-v, prev, xs[i]])
                cnf.add([-v, prev, pj])
    if k > 0:
        cnf.add([r[n - 1][k - 1]])
    cnf.add([-r[n - 1][k]])


def blocos(t0):
    b, ini = [], 0
    for s in t0:
        b.append(range(ini, ini + s))
        ini += s
    return b


def lex_colunas(cnf, x, i, j, q, M):
    """(g) coluna i <=lex coluna j (símbolos lidos na ordem das palavras). e[k] = "colunas
    iguais nas palavras < k" é forçado a verdadeiro quando o prefixo é igual; sob e[k], o
    símbolo de i na palavra k não passa o de j. Todo par lex-ordenado satisfaz (e = prefixo
    igual), então nenhum código em forma normal é perdido."""
    e = None
    for k in range(M):
        for a in range(q):
            for b in range(a):
                cnf.add(([-e] if e else []) + [-x[k][i][a], -x[k][j][b]])
        if k == M - 1:
            break
        e2 = cnf.var()
        for a in range(q):
            cnf.add(([-e] if e else []) + [-x[k][i][a], -x[k][j][a], e2])
        e = e2


def codificar(q, n, R, M, perfil, quebra=True, colunas=True):
    """Devolve (cnf, x, sim0); x[k][i][a] para i = 1..n-1."""
    cnf = CNF()
    t = perfil
    bl = blocos(t[0])
    sim0 = [a for a in range(q) for _ in bl[a]]
    x = [[None] + [[cnf.var() for _ in range(q)] for _ in range(1, n)] for _ in range(M)]
    for k in range(M):
        for i in range(1, n):
            cnf.add(x[k][i])
            for a, b in itertools.combinations(range(q), 2):
                cnf.add([-x[k][i][a], -x[k][i][b]])
    for i in range(1, n):
        for a in range(q):
            exatamente(cnf, [x[k][i][a] for k in range(M)], t[i][a])
    m = n - R
    P = {}
    for S in itertools.combinations(range(n), m):
        for v in itertools.product(range(q), repeat=m):
            p = cnf.var()
            P[S, v] = p
            if S[0] == 0:
                ks, resto = bl[v[0]], list(zip(S[1:], v[1:]))
            else:
                ks, resto = range(M), list(zip(S, v))
            ys = []
            for k in ks:
                if len(resto) == 1:
                    i, a = resto[0]
                    ys.append(x[k][i][a])
                    continue
                y = cnf.var()
                for i, a in resto:
                    cnf.add([-y, x[k][i][a]])
                cnf.defs.append((y, "and", [x[k][i][a] for i, a in resto]))
                ys.append(y)
            cnf.add([-p] + ys)
            cnf.defs.append((p, "or", ys))
    subs = list(itertools.combinations(range(n), m))
    for w in itertools.product(range(q), repeat=n):
        cnf.add([P[S, tuple(w[i] for i in S)] for S in subs])
    if not quebra:
        return cnf, x, sim0
    for B in bl:  # (d)
        for k in list(B)[:-1]:
            for a in range(q):
                for b in range(a):
                    cnf.add([-x[k][1][a], -x[k + 1][1][b]])
    for a in range(q - 1):  # (e)
        if t[1][a] != t[1][a + 1]:
            continue
        for bi, B in enumerate(bl):
            antes = [x[kk][1][a] for bb in bl[: bi + 1] for kk in bb]
            for k in B:
                cnf.add([-x[k][1][a + 1]] + antes)
    for i in range(2, n):  # (f)
        for a in range(q - 1):
            if t[i][a] != t[i][a + 1]:
                continue
            for k in range(M):
                cnf.add([-x[k][i][a + 1]] + [x[kk][i][a] for kk in range(k)])
    if colunas:  # (g) coordenadas >= 2 de mesmo tipo: colunas em ordem lexicográfica
        for i in range(2, n):
            for j in range(i + 1, n):
                if t[i] == t[j] and all(t[i] != t[l] for l in range(i + 1, j)):
                    lex_colunas(cnf, x, i, j, q, M)
    return cnf, x, sim0


def decodificar(modelo, x, sim0, q, n, M):
    verdade = {l for l in modelo if l > 0}
    out = []
    for k in range(M):
        w = [sim0[k]] + [next(a for a in range(q) if x[k][i][a] in verdade) for i in range(1, n)]
        out.append(tuple(w))
    return out


def cobre(q, n, R, cod):
    for x in itertools.product(range(q), repeat=n):
        if not any(sum(a != b for a, b in zip(x, c)) <= R for c in cod):
            return False
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("q", "n", "R", "M"):
        ap.add_argument("--" + k, type=int, required=True)
    ap.add_argument("--smin", type=int)
    ap.add_argument("--perfil", type=int)
    ap.add_argument("--saida")
    a = ap.parse_args()
    smin = a.smin if a.smin is not None else fibra_minima(a.q, a.n, a.R, a.M)
    ps = perfis(a.q, a.n, a.R, a.M, smin)
    if a.perfil is None:
        print(f"K_{a.q}({a.n},{a.R}) M={a.M} s_min={smin} tipos={len(ordem_tipos(a.q, a.M, smin))} perfis={len(ps)}")
        return
    cnf, _, _ = codificar(a.q, a.n, a.R, a.M, ps[a.perfil])
    txt = cnf.dimacs([f"K_{a.q}({a.n},{a.R}) M={a.M} smin={smin} perfil {a.perfil}: {ps[a.perfil]}"])
    (open(a.saida, "w").write(txt) if a.saida else sys.stdout.write(txt))


if __name__ == "__main__":
    main()
