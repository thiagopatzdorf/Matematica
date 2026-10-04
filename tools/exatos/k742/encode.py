#!/usr/bin/env python3
"""Redução de K_q(4,2) <= M a instâncias SAT por perfil de fibras (método do Florath, adaptado).

Ideia (Florath, arXiv:2606.09600, repo florath/covering-codes-lean @ bbed9a6, K_8(4,2) = 23):
1. Lema das fibras: se C cobre Z_q^4 com raio 2 e |C| = M, cada fibra F(j,a) = {c : c_j = a}
   tem |F(j,a)| >= s_min, onde s_min é o menor s com K_{q-s}(3,1) <= M - s
   (prova no README; `fibra_minima`).
2. Perfil: em cada coordenada, o vetor de tamanhos de fibra (ordenado, decrescente) é uma
   partição de M em q partes >= s_min (um "tipo"). A menos de permutar coordenadas, o código
   tem um multiconjunto de 4 tipos (um "perfil"). Uma CNF por perfil.
3. Cobertura pelas projeções de pares: x é coberto sse algum par (x_i, x_j), i<j, está na
   projeção P_ij(C) (concordar em 2 das 4 coordenadas = distância <= 2).

Quebra de simetria (cada passo é uma operação do grupo S_q wr S_4 ou uma permutação das
palavras; a prova de que todo código cai em alguma instância está no README):
  (a) coordenadas em ordem do perfil; (b) símbolos de cada coordenada em ordem decrescente de
  fibra; (c) palavras agrupadas em blocos pelo símbolo da coordenada 0 (a coordenada 0 vira
  constante); (d) dentro de cada bloco, coordenada 1 não decrescente; (e) coordenada 1: entre
  símbolos de mesma fibra, o primeiro bloco em que a aparece <= o de a+1; (f) coordenadas 2 e
  3: entre símbolos de mesma fibra, a primeira palavra com a vem antes da primeira com a+1.

Uso:
  python3 tools/exatos/k742/encode.py --q 7 --M 17 --listar
  python3 tools/exatos/k742/encode.py --q 7 --M 17 --perfil 0 --saida p0.cnf
"""
import argparse
import itertools
import math
import sys
from collections import Counter

N = 4
PARES = list(itertools.combinations(range(N), 2))


def k_v31(v):
    """K_v(3,1) = ceil(v^2/2) (Kalbfleisch–Stanton 1968; confere com o ledger para v <= 8)."""
    return (v * v + 1) // 2


def cota_elementar_31(v):
    """Cota inferior de K_v(3,1) só com argumentos elementares (README, "Lema 0"): o máximo
    entre a cota de esferas e o menor M que o lema das fibras em comprimento 3 não exclui
    (fibra s exige (v-s)^2 <= M-s; v fibras somam M)."""
    esferas = -(-v ** 3 // (1 + 3 * (v - 1)))
    M = 1
    while True:
        s = next((s for s in range(v + 1) if (v - s) ** 2 <= M - s), None)
        if s is not None and v * s <= M:
            return max(esferas, M)
        M += 1


def fibra_minima(q, M):
    """Menor s tal que uma fibra de tamanho s não está excluída pelo lema das fibras."""
    s = 0
    while s < q and k_v31(q - s) > M - s:
        s += 1
    return s


def tipos(q, M, smin):
    """Partições de M em exatamente q partes >= smin, como tuplas decrescentes."""
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
    """Ordem do grupo de símbolos que preserva o vetor de fibras t (produto de fatoriais)."""
    r = 1
    for c in Counter(t).values():
        r *= math.factorial(c)
    return r


def perfis(q, M):
    """Multiconjuntos de 4 tipos; a coordenada 0 recebe o tipo de menor simetria residual."""
    smin = fibra_minima(q, M)
    ts = sorted(tipos(q, M, smin), key=lambda t: (simetria_residual(t), t))
    return list(itertools.combinations_with_replacement(ts, N))


class CNF:
    def __init__(self):
        self.nv = 0
        self.cl = []

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
    """sum(xs) == k por contador sequencial completo (Sinz), com equivalências."""
    n = len(xs)
    if k > n:
        cnf.add([])
        return
    # r[i][j] <-> pelo menos j+1 dos xs[0..i] são verdadeiros, j = 0..k
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
    """Intervalos de índices de palavras por símbolo da coordenada 0."""
    b, ini = [], 0
    for s in t0:
        b.append(range(ini, ini + s))
        ini += s
    return b


def codificar(q, M, perfil, quebra=True):
    """Devolve (cnf, x) onde x[k][i][a] (i = 1..3) é o literal 'palavra k tem a na coord i'."""
    cnf = CNF()
    t = perfil
    bl = blocos(t[0])
    sim0 = [a for a in range(q) for _ in bl[a]]  # símbolo da coord 0 de cada palavra
    x = [[None] + [[cnf.var() for _ in range(q)] for _ in range(1, N)] for _ in range(M)]
    for k in range(M):
        for i in range(1, N):
            cnf.add(x[k][i])
            for a, b in itertools.combinations(range(q), 2):
                cnf.add([-x[k][i][a], -x[k][i][b]])
    for i in range(1, N):
        for a in range(q):
            exatamente(cnf, [x[k][i][a] for k in range(M)], t[i][a])
    # projeções de pares, exatas: P <-> OR_k (x_kia AND x_kjb)
    P = {}
    for (i, j) in PARES:
        for a in range(q):
            for b in range(q):
                p = cnf.var()
                P[i, j, a, b] = p
                if i == 0:
                    lits = [x[k][j][b] for k in bl[a]]
                    cnf.add([-p] + lits)
                    for l in lits:
                        cnf.add([-l, p])
                else:
                    ys = []
                    for k in range(M):
                        y = cnf.var()
                        cnf.add([-y, x[k][i][a]])
                        cnf.add([-y, x[k][j][b]])
                        cnf.add([y, -x[k][i][a], -x[k][j][b]])
                        cnf.add([-y, p])
                        ys.append(y)
                    cnf.add([-p] + ys)
    for w in itertools.product(range(q), repeat=N):
        cnf.add([P[i, j, w[i], w[j]] for (i, j) in PARES])
    if not quebra:  # só (a)-(c): controle para conferir que (d)-(f) não mudam o resultado
        return cnf, x, sim0
    # (d) dentro do bloco, coord 1 não decrescente
    for B in bl:
        for k in list(B)[:-1]:
            for a in range(q):
                for b in range(a):
                    cnf.add([-x[k][1][a], -x[k + 1][1][b]])
    # (e) coord 1: precedência por bloco entre símbolos de mesma fibra
    for a in range(q - 1):
        if t[1][a] != t[1][a + 1]:
            continue
        for bi, B in enumerate(bl):
            antes = [x[kk][1][a] for bb in bl[: bi + 1] for kk in bb]
            for k in B:
                cnf.add([-x[k][1][a + 1]] + antes)
    # (f) coords 2 e 3: precedência por palavra entre símbolos de mesma fibra
    for i in (2, 3):
        for a in range(q - 1):
            if t[i][a] != t[i][a + 1]:
                continue
            for k in range(M):
                cnf.add([-x[k][i][a + 1]] + [x[kk][i][a] for kk in range(k)])
    return cnf, x, sim0


def decodificar(modelo, x, sim0, q, M):
    verdade = {abs(l) for l in modelo if l > 0}
    palavras = []
    for k in range(M):
        w = [sim0[k]]
        for i in range(1, N):
            w.append(next(a for a in range(q) if x[k][i][a] in verdade))
        palavras.append("".join(map(str, w)))
    return palavras


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--q", type=int, required=True)
    ap.add_argument("--M", type=int, required=True)
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--perfil", type=int)
    ap.add_argument("--saida")
    ap.add_argument("--sem-quebra", action="store_true", help="omite (d)-(f) (controle)")
    a = ap.parse_args()
    ps = perfis(a.q, a.M)
    if a.listar or a.perfil is None:
        print(f"q={a.q} M={a.M} s_min={fibra_minima(a.q, a.M)} perfis={len(ps)}")
        for i, p in enumerate(ps):
            print(i, " | ".join("".join(map(str, t)) for t in p))
        return
    cnf, _, _ = codificar(a.q, a.M, ps[a.perfil], quebra=not a.sem_quebra)
    txt = cnf.dimacs([f"K_{a.q}(4,2) M={a.M} perfil {a.perfil}: {ps[a.perfil]}"])
    if a.saida:
        open(a.saida, "w").write(txt)
    else:
        sys.stdout.write(txt)


if __name__ == "__main__":
    main()
