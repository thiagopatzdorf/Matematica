#!/usr/bin/env python3
"""Lema das fibras para K_q(n, n-2) em geral, instâncias por prefixo de tipos e CNF.

Generaliza `tools/exatos/k742/encode.py` (só K_q(4,2)) para qualquer comprimento n com raio
R = n - 2: x é coberto por c sse concordam em >= 2 coordenadas, logo a cobertura vira uma
condição sobre as projeções de pares P_ij(C) (para cada x, algum par (x_i, x_j) está em P_ij).
A prova dos lemas está em `docs/exatos/FIBRAS_GERAL.md`.

Lema das fibras (geral, R <= n-2): uma fibra F(j,a) com s palavras força
K_{q-s}(n-1, R-1) <= M - s. A cota inferior de K_{q-s}(n-1, R-1) vem do ledger (melhor lb de
todas as fontes) ou de uma tabela de cotas passada explicitamente (`cotas`).

Instâncias: o tipo de uma coordenada é o vetor decrescente dos tamanhos das q fibras (uma
partição de M em q partes >= s_min). As coordenadas são ordenadas por tipo (ordem total
`chave_tipo`); a instância fixa os tipos das k primeiras coordenadas (t_0 <= ... <= t_{k-1})
e deixa as demais "livres" (cada símbolo com >= s_min palavras). k = n é o perfil completo
do k742; k < n troca número de instâncias por instâncias maiores (relaxação: correta, só menos
apertada).

Quebra de simetria (prova de completude em `canonizar.py` e no doc): (c) coordenada 0 em
blocos; (d) dentro do bloco, coordenada 1 não decrescente; (e) coordenada 1: precedência por
bloco entre símbolos da mesma classe; (f) coordenadas >= 2: precedência por palavra entre
símbolos da mesma classe. Classe = tamanho de fibra (coordenada de tipo fixo) ou todos os
símbolos (coordenada livre).

Uso:
  python3 tools/exatos/fibras/fib_encode.py --q 7 --n 5 --M 15 --listar
  python3 tools/exatos/fibras/fib_encode.py --q 7 --n 5 --M 15 --k 5 --inst 0 --saida i0.cnf
"""
import argparse
import itertools
import json
import math
import pathlib
import sys
from collections import Counter
from functools import lru_cache

RAIZ = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "tools" / "exatos"))


def _k742():
    # reuso do k742 sem colidir com o nome de módulo `encode` (os testes carregam os dois)
    import importlib.util
    spec = importlib.util.spec_from_file_location("k742_encode", RAIZ / "tools/exatos/k742/encode.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_K = _k742()
CNF, exatamente = _K.CNF, _K.exatamente


@lru_cache(None)
def cotas_ledger():
    import folgas
    cells = json.loads((RAIZ / "ledger" / "cells.json").read_text())["cells"]
    return {(c["q"], c["n"], c["R"]): folgas.melhores(c)[0] for c in cells}


def cota_inferior(v, n, R, cotas=None):
    """Cota inferior de K_v(n,R) válida (casos triviais + ledger/tabela)."""
    if v <= 1 or R >= n:
        return 1
    if R < 0:
        raise ValueError("raio negativo")
    if R == 0:
        return v ** n
    tab = cotas if cotas is not None else cotas_ledger()
    if (v, n, R) in tab:
        return tab[(v, n, R)]
    if n == 3 and R == 1:  # Kalbfleisch–Stanton, K_v(3,1) = ceil(v^2/2)
        return (v * v + 1) // 2
    raise KeyError(f"sem cota para K_{v}({n},{R})")


def fibra_minima(q, n, R, M, cotas=None):
    """Menor s que o lema das fibras não exclui: K_{q-s}(n-1,R-1) <= M - s."""
    assert R <= n - 2, "o lema exige R <= n-2"
    s = 0
    while s < q and cota_inferior(q - s, n - 1, R - 1, cotas) > M - s:
        s += 1
    return s


def tipos(q, M, smin):
    """Partições de M em exatamente q partes >= smin (tuplas decrescentes)."""
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


def chave_tipo(t):
    """Ordem total dos tipos: menor simetria residual primeiro (a coordenada 0 é a que mais
    quebra simetria), depois lexicográfica. A mesma do k742."""
    return (simetria_residual(t), t)


def instancias(q, n, M, k, smin=None, cotas=None, R=None):
    """Multiconjuntos ordenados de k tipos (t_0 <= ... <= t_{k-1} em chave_tipo)."""
    R = n - 2 if R is None else R
    if smin is None:
        smin = fibra_minima(q, n, R, M, cotas)
    ts = sorted(tipos(q, M, smin), key=chave_tipo)
    return smin, list(itertools.combinations_with_replacement(ts, k))


def contar_instancias(q, n, M, k, smin):
    """Número de instâncias sem listar: C(T + k - 1, k), T = número de tipos."""
    E = M - q * smin
    if E < 0:
        return 0, 0

    @lru_cache(None)
    def p(m, partes, maior):
        if m == 0:
            return 1
        if partes == 0:
            return 0
        return sum(p(m - x, partes - 1, x) for x in range(1, min(maior, m) + 1))

    T = p(E, q, E)
    return T, math.comb(T + k - 1, k)


def pelo_menos(cnf, xs, k):
    """sum(xs) >= k (contador sequencial com equivalências, só o limite inferior)."""
    if k <= 0:
        return
    n = len(xs)
    if k > n:
        cnf.add([])
        return
    r = [[cnf.var() for _ in range(k)] for _ in range(n)]
    for i in range(n):
        for j in range(k):
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
    cnf.add([r[n - 1][k - 1]])


def blocos(t0):
    b, ini = [], 0
    for s in t0:
        b.append(range(ini, ini + s))
        ini += s
    return b


def classes(q, t):
    """Rótulo de classe de cada símbolo: tamanho da fibra (tipo fixo) ou 0 (livre)."""
    return [0] * q if t is None else list(t)


def codificar(q, n, M, prefixo, smin, quebra=True, lex=True):
    """CNF da instância. prefixo = tipos das coordenadas 0..k-1 (k >= 1); as outras são
    livres com fibras >= smin. Devolve (cnf, x, sim0, ts) com x[k][i][a] (i >= 1)."""
    k = len(prefixo)
    assert 1 <= k <= n
    ts = list(prefixo) + [None] * (n - k)
    cnf = CNF()
    bl = blocos(ts[0])
    sim0 = [a for a in range(q) for _ in bl[a]]
    x = [[None] + [[cnf.var() for _ in range(q)] for _ in range(1, n)] for _ in range(M)]
    for w in range(M):
        for i in range(1, n):
            cnf.add(x[w][i])
            for a, b in itertools.combinations(range(q), 2):
                cnf.add([-x[w][i][a], -x[w][i][b]])
    for i in range(1, n):
        for a in range(q):
            col = [x[w][i][a] for w in range(M)]
            if ts[i] is not None:
                exatamente(cnf, col, ts[i][a])
            else:
                pelo_menos(cnf, col, smin)
    P = {}
    for (i, j) in itertools.combinations(range(n), 2):
        for a in range(q):
            for b in range(q):
                p = cnf.var()
                P[i, j, a, b] = p
                if i == 0:
                    lits = [x[w][j][b] for w in bl[a]]
                    cnf.add([-p] + lits)
                    for l in lits:
                        cnf.add([-l, p])
                else:
                    ys = []
                    for w in range(M):
                        y = cnf.var()
                        cnf.add([-y, x[w][i][a]])
                        cnf.add([-y, x[w][j][b]])
                        cnf.add([y, -x[w][i][a], -x[w][j][b]])
                        cnf.add([-y, p])
                        ys.append(y)
                    cnf.add([-p] + ys)
    pares = list(itertools.combinations(range(n), 2))
    for v in itertools.product(range(q), repeat=n):
        cnf.add([P[i, j, v[i], v[j]] for (i, j) in pares])
    if not quebra:
        return cnf, x, sim0, ts
    # (d) dentro do bloco, coordenada 1 não decrescente
    for B in bl:
        for w in list(B)[:-1]:
            for a in range(q):
                for b in range(a):
                    cnf.add([-x[w][1][a], -x[w + 1][1][b]])
    # (e) coordenada 1: precedência por bloco entre símbolos da mesma classe
    c1 = classes(q, ts[1])
    for a in range(q - 1):
        if c1[a] != c1[a + 1]:
            continue
        for bi, B in enumerate(bl):
            antes = [x[ww][1][a] for bb in bl[: bi + 1] for ww in bb]
            for w in B:
                cnf.add([-x[w][1][a + 1]] + antes)
    # (f) coordenadas >= 2: precedência por palavra entre símbolos da mesma classe
    for i in range(2, n):
        ci = classes(q, ts[i])
        for a in range(q - 1):
            if ci[a] != ci[a + 1]:
                continue
            for w in range(M):
                cnf.add([-x[w][i][a + 1]] + [x[ww][i][a] for ww in range(w)])
    # (g) colunas >= 2 de mesmo tipo (ou ambas livres), consecutivas: ordem lexicográfica
    # (a forma normal relabela cada coluna só pelo seu conteúdo, então permutá-las é livre)
    if lex:
        for i in range(2, n - 1):
            if ts[i] == ts[i + 1]:
                lex_leq(cnf, x, q, M, i, i + 1)
    return cnf, x, sim0, ts


def lex_leq(cnf, x, q, M, i, j):
    """coluna i <=lex coluna j (sobre as palavras em ordem), e_w <-> prefixos iguais até w."""
    ant = None
    for w in range(M):
        for a in range(q):
            for b in range(a):
                cnf.add(([-ant] if ant else []) + [-x[w][i][a], -x[w][j][b]])
        if w == M - 1:
            break
        e = cnf.var()
        if ant:
            cnf.add([-e, ant])
        for a in range(q):
            cnf.add([-e, -x[w][i][a], x[w][j][a]])
            cnf.add([-e, x[w][i][a], -x[w][j][a]])
            cnf.add(([-ant] if ant else []) + [-x[w][i][a], -x[w][j][a], e])
        ant = e


def decodificar(modelo, x, sim0, q, n, M):
    verdade = {l for l in modelo if l > 0}
    out = []
    for w in range(M):
        pal = [sim0[w]]
        for i in range(1, n):
            pal.append(next(a for a in range(q) if x[w][i][a] in verdade))
        out.append(tuple(pal))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--q", type=int, required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--M", type=int, required=True)
    ap.add_argument("--k", type=int, help="coordenadas com tipo fixo (padrão: n)")
    ap.add_argument("--smin", type=int, help="força s_min (validação com lema enfraquecido)")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--inst", type=int)
    ap.add_argument("--saida")
    a = ap.parse_args()
    k = a.k or a.n
    smin = a.smin if a.smin is not None else fibra_minima(a.q, a.n, a.n - 2, a.M)
    T, N = contar_instancias(a.q, a.n, a.M, k, smin)
    print(f"K_{a.q}({a.n},{a.n-2}) M={a.M} s_min={smin} tipos={T} instâncias(k={k})={N}",
          file=sys.stderr)
    if a.inst is None:
        if a.listar and N <= 10000:
            _, ins = instancias(a.q, a.n, a.M, k, smin)
            for i, p in enumerate(ins):
                print(i, " | ".join("".join(map(str, t)) for t in p))
        return
    _, ins = instancias(a.q, a.n, a.M, k, smin)
    cnf, *_ = codificar(a.q, a.n, a.M, ins[a.inst], smin)
    txt = cnf.dimacs([f"K_{a.q}({a.n},{a.n-2}) M={a.M} k={k} s_min={smin} inst {a.inst}: {ins[a.inst]}"])
    if a.saida:
        open(a.saida, "w").write(txt)
    else:
        sys.stdout.write(txt)


if __name__ == "__main__":
    main()
