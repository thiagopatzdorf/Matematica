"""Ferramentas para a auditoria da base campeã de K_7(9,4) (e de qualquer base [9,3]_7 + trio).

Convenções (as mesmas do repo Matematica): H = [I_6 | A], linha j de A = 3 dígitos para as
colunas 6,7,8; síndrome s = H x com inteiro sum_j s_j 7^j (dígito j = coordenada j de F_7^6).
Tudo aqui é exato (inteiros mod 7), sem amostragem.
"""
from __future__ import annotations

import itertools
import numpy as np

Q, N, R, NR = 7, 9, 4, 6
NS = Q ** NR  # 117649 síndromes
POW = Q ** np.arange(NR)


def parse_A(s):
    return np.array([[int(c) for c in r] for r in s.split()], dtype=np.int64)


def H_of(A):
    return np.concatenate([np.eye(NR, dtype=np.int64), A], axis=1) % Q


def G_of(A):
    return np.concatenate([(-A.T) % Q, np.eye(3, dtype=np.int64)], axis=1)


def s2i(v):
    return int((np.asarray(v) % Q) @ POW)


def i2s(x):
    return np.array([(x // Q ** j) % Q for j in range(NR)], dtype=np.int64)


ALL_S = np.array([[(x // Q ** j) % Q for j in range(NR)] for x in range(NS)], dtype=np.int64)  # NS x 6


def add_tab(a, b):
    """soma de síndromes inteiras (vetorizado)."""
    return ((ALL_S[a] + ALL_S[b]) % Q) @ POW


def neg(a):
    return ((-ALL_S[a]) % Q) @ POW


def leader_weights(H):
    """peso mínimo da classe lateral de cada síndrome (BFS no grafo de Cayley com geradores a*h_j)."""
    dist = np.full(NS, 99, dtype=np.int64)
    dist[0] = 0
    gens = [s2i(a * H[:, j]) for j in range(N) for a in range(1, Q)]
    frontier = np.array([0])
    w = 0
    while frontier.size:
        w += 1
        nxt = []
        for g in gens:
            t = add_tab(frontier, np.full(frontier.size, g))
            t = t[dist[t] > w]
            dist[t] = w
            nxt.append(t)
        frontier = np.unique(np.concatenate(nxt))
    return dist


def ball_counts(H, r=R):
    """Nb[d] = #{e : wt(e) <= r, He = d} (cobertura de uma classe lateral por uma palavra)."""
    Nb = np.zeros(NS, dtype=np.int64)
    for w in range(r + 1):
        for supp in itertools.combinations(range(N), w):
            if w == 0:
                Nb[0] += 1
                continue
            vals = np.array(list(itertools.product(range(1, Q), repeat=w)), dtype=np.int64)  # m x w
            S = (vals @ H[:, list(supp)].T) % Q
            np.add.at(Nb, S @ POW, 1)
    return Nb


def orphans(Bmask, trio):
    """síndromes t com t - s fora de B para todo s do trio."""
    ok = np.ones(NS, dtype=bool)
    for s in trio:
        ok &= ~Bmask[add_tab(np.arange(NS), np.full(NS, int(neg(np.array([s]))[0])))]
    return np.nonzero(ok)[0]
