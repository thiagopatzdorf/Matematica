"""Biblioteca da auditoria de completude (Python puro, independente do base_search).

Geometria de PG(2,q) com q primo, aritmética de códigos e a ponte com o binário C
`pg2_orbits` (compilado sob demanda em scripts/audit/.build/).

Numeração de pontos DESTA auditoria: vetores normalizados (1ª coordenada não nula = 1)
em ordem lexicográfica de (x, y, z). A numeração do base_search é outra e só é
reconstruída em `base_search_index` para conferir o campo "pts".
"""
from __future__ import annotations

import itertools
import os
import subprocess
from math import comb

Q = 7
K = 3
HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, ".build")


def inv(a: int, q: int = Q) -> int:
    return pow(a, q - 2, q)


def normalize(v, q: int = Q):
    v = tuple(x % q for x in v)
    for x in v:
        if x:
            c = inv(x, q)
            return tuple(y * c % q for y in v)
    return None  # vetor nulo


POINTS = [p for p in itertools.product(range(Q), repeat=3) if normalize(p) == p]
assert len(POINTS) == Q * Q + Q + 1 == 57
IDX = {p: i for i, p in enumerate(POINTS)}


def point_index(v):
    n = normalize(v)
    return None if n is None else IDX[n]


def dot(u, v, q: int = Q) -> int:
    return sum(a * b for a, b in zip(u, v)) % q


# retas de PG(2,q): dual dos pontos; reta u = {p : u.p = 0}
LINES = [frozenset(i for i, p in enumerate(POINTS) if dot(u, p) == 0) for u in POINTS]
assert all(len(L) == Q + 1 for L in LINES)


def det3(a, b, c, q: int = Q) -> int:
    return (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0])) % q


def collinear(i, j, k) -> bool:
    return det3(POINTS[i], POINTS[j], POINTS[k]) == 0


def general_position(four) -> bool:
    return all(not collinear(*t) for t in itertools.combinations(four, 3))


def has_frame(support) -> bool:
    return any(general_position(f) for f in itertools.combinations(sorted(set(support)), 4))


def rank_of(support) -> int:
    s = sorted(set(support))
    if not s:
        return 0
    if len(s) == 1:
        return 1
    if any(not collinear(*t) for t in itertools.combinations(s, 3)):
        return 3
    return 2


# ---------- álgebra linear mod q (matrizes como listas de listas) ----------
def matmul(A, B, q: int = Q):
    return [[sum(A[i][t] * B[t][j] for t in range(len(B))) % q for j in range(len(B[0]))] for i in range(len(A))]


def transpose(A):
    return [list(r) for r in zip(*A)]


def mat_inv3(M, q: int = Q):
    """Inversa 3x3 por Gauss-Jordan; None se singular."""
    a = [list(M[i]) + [int(i == j) for j in range(3)] for i in range(3)]
    for c in range(3):
        p = next((i for i in range(c, 3) if a[i][c] % q), None)
        if p is None:
            return None
        a[c], a[p] = a[p], a[c]
        iv = inv(a[c][c] % q, q)
        a[c] = [x * iv % q for x in a[c]]
        for i in range(3):
            if i != c and a[i][c] % q:
                f = a[i][c]
                a[i] = [(x - f * y) % q for x, y in zip(a[i], a[c])]
    return [row[3:] for row in a]


def projectivity(src4, dst4):
    """Matriz g (3x3) com g(src_i) ~ dst_i para 4-uplas em posição geral (únicas a menos de escalar)."""
    def to_std(four):
        P = [[POINTS[four[c]][r] for c in range(3)] for r in range(3)]
        Pi = mat_inv3(P)
        lam = [sum(Pi[i][j] * POINTS[four[3]][j] for j in range(3)) % Q for i in range(3)]
        assert all(lam)
        return [[inv(lam[i]) * Pi[i][j] % Q for j in range(3)] for i in range(3)]
    N1 = to_std(src4)
    N2 = to_std(dst4)
    N2i = mat_inv3(N2)
    return matmul(N2i, N1)


def apply(g, i):
    v = POINTS[i]
    return point_index([sum(g[r][c] * v[c] for c in range(3)) for r in range(3)])


# ---------- códigos ----------
def parse_A(s: str):
    rows = s.split()
    return [[int(ch) for ch in r] for r in rows]


def G_from_A(A, q: int = Q):
    """H = [I_r | A]  =>  G = [-A^T | I_k] satisfaz G H^T = -A^T + A^T = 0."""
    r, k = len(A), len(A[0])
    return [[(-A[j][i]) % q for j in range(r)] + [int(i == t) for t in range(k)] for i in range(k)]


def H_from_A(A):
    r = len(A)
    return [[int(i == j) for j in range(r)] + list(A[i]) for i in range(r)]


def weight_distribution(G, q: int = Q):
    k, n = len(G), len(G[0])
    wd = [0] * (n + 1)
    for u in itertools.product(range(q), repeat=k):
        w = sum(1 for j in range(n) if sum(u[i] * G[i][j] for i in range(k)) % q)
        wd[w] += 1
    return tuple(wd)


def columns_as_points(G):
    """Índices (desta auditoria) das colunas de G; None para coluna nula."""
    return [point_index([G[i][j] for i in range(len(G))]) for j in range(len(G[0]))]


def systematic_A(cols):
    """Dadas as colunas de G (vetores de F_q^3, podendo haver nulos), devolve (A, perm) com
    H = [I_6 | A] matriz de checagem do código obtido permutando as coordenadas por `perm`
    (as 3 últimas coordenadas viram um conjunto de informação). Permutar coordenadas é
    equivalência monomial, então não muda nada que seja invariante por ela."""
    n = len(cols)
    nz = [j for j in range(n) if normalize(cols[j]) is not None]
    for tri in itertools.combinations(nz, 3):
        if det3(*[cols[j] for j in tri]):
            break
    else:
        raise ValueError("posto < 3")
    perm = [j for j in range(n) if j not in tri] + list(tri)
    G = [[cols[perm[j]][i] % Q for j in range(n)] for i in range(3)]
    B = [[G[i][j] for j in range(n - 3, n)] for i in range(3)]
    Gp = matmul(mat_inv3(B), G)
    assert all(Gp[i][n - 3 + j] == int(i == j) for i in range(3) for j in range(3))
    A = [[(-Gp[j][i]) % Q for j in range(3)] for i in range(n - 3)]
    H = H_from_A(A)
    assert all(v == 0 for row in matmul(Gp, transpose(H)) for v in row)
    return A, perm


def A_string(A) -> str:
    return " ".join("".join(str(x) for x in row) for row in A)


# ---------- binário C ----------
def binary() -> str:
    os.makedirs(BUILD, exist_ok=True)
    exe = os.path.join(BUILD, "pg2_orbits")
    src = os.path.join(HERE, "pg2_orbits.c")
    if not os.path.exists(exe) or os.path.getmtime(exe) < os.path.getmtime(src):
        subprocess.run(["gcc", "-O3", "-march=native", "-o", exe, src], check=True)
    return exe


def c_stab(multisets, m):
    """Para cada multiconjunto (lista de m índices): (canon, |Stab|) via pg2_orbits stab."""
    inp = "\n".join(" ".join(map(str, s)) for s in multisets) + "\n"
    out = subprocess.run([binary(), "stab", str(Q), str(m)], input=inp, capture_output=True, text=True, check=True).stdout
    res = []
    for line in out.splitlines():
        if line.startswith("SEM_REFERENCIAL"):
            res.append((None, None))
            continue
        a, b = line.split("|")
        res.append((tuple(map(int, a.split())), int(b)))
    assert len(res) == len(multisets)
    return res


def c_equiv(pairs, m):
    """Para cada par (S1, S2): True se existe g em PGL(3,q) com g(S1) = S2 (força bruta em C)."""
    inp = "\n".join(" ".join(map(str, a)) + "\n" + " ".join(map(str, b)) for a, b in pairs) + "\n"
    out = subprocess.run([binary(), "equiv", str(Q), str(m)], input=inp, capture_output=True, text=True, check=True).stdout
    res = [int(x) for x in out.split()]
    assert len(res) == len(pairs) and all(x in (0, 1) for x in res)
    return [x == 1 for x in res]


def c_enum(m, nshard=4):
    """Representantes canônicos das órbitas de m-multiconjuntos com referencial."""
    procs = [subprocess.Popen([binary(), "enum", str(Q), str(m), str(s), str(nshard)], stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, text=True) for s in range(nshard)]
    reps = []
    for p in procs:
        out, _ = p.communicate()
        assert p.returncode == 0
        for line in out.splitlines():
            a, b = line.split("|")
            reps.append((tuple(map(int, a.split())), int(b)))
    return reps


def c_livres(smax):
    out = subprocess.run([binary(), "livres", str(Q), str(smax)], capture_output=True, text=True, check=True).stdout
    d = {}
    for line in out.split("\n"):
        if line.strip():
            s, a, b = map(int, line.split())
            d[s] = (a, b)
    return d


# ---------- contagens analíticas ----------
ORDER_PGL3 = (Q**3 - 1) * (Q**3 - Q) * (Q**3 - Q**2) // (Q - 1)
NPTS = Q * Q + Q + 1
LPTS = Q + 1


def frameless_sets_formula(s):
    """(contidos numa reta, posto 3) entre os CONJUNTOS de s pontos sem referencial.
    Classificação: sem 4 pontos em posição geral <=> contido em reta L, ou em L ∪ {P}."""
    if s == 1:
        line = NPTS
    else:
        line = NPTS * comb(LPTS, s)
    if s < 3:
        r3 = 0
    elif s == 3:
        r3 = comb(NPTS, 3) - NPTS * comb(LPTS, 3)          # triângulos
    else:
        r3 = NPTS * comb(LPTS, s - 1) * (NPTS - LPTS)      # reta (s-1 pontos) + ponto fora
    return line, r3


def multisets_with_support_size(m, s):
    """nº de m-multiconjuntos com suporte igual a um conjunto fixo de s elementos."""
    return comb(m - 1, s - 1)
