#!/usr/bin/env python3
"""Fatia mínima para alfabeto binário: lista de instâncias por vetor de contagem de colunas.

É a redução de `tools/exatos/gaps2/fatia.py` (prova em docs/exatos/GAPS2_K362.md) com q = 2,
mas com outra enumeração das configurações K (s* pontos distintos de Z_2^m, m = n − 1), porque a
de `fatia.configuracoes` percorre multiconjuntos de colunas e calcula a forma canônica com s!
permutações em Python por multiconjunto, o que já leva horas em m = 11.

Representação: cada coluna de K, normalizada para o ponto 0 ter bit 0 (complementar a coluna é
uma isometria), é um padrão p em [0, 2^s) com o bit 0 apagado. Uma configuração a menos de
permutação de coordenadas é o vetor de contagem c (c_p = número de colunas com padrão p, soma m).
Duas configurações são isométricas se e só se os vetores diferem por uma permutação σ dos pontos
(que age nos padrões, com renormalização). Guardamos de cada órbita de S_s o vetor
lexicograficamente máximo, comparado em inteiros exatos. Os pontos precisam ser distintos: cada
par (i, k) é separado por alguma coluna presente. Isso dá exatamente uma configuração por classe
de isometria (conferido contra `fatia.configuracoes` em `tests/test_lp_bin.py`).

Instância (s*, K, t) com t = (M − s*,): no binário só há um bloco além da fatia 0, e
t_1 = M − s* ≥ s* porque s* ≤ ⌊M/2⌋. O filtro de contagem é o mesmo do GAPS2,
|U(K)| ≤ (M − s*)·V(n−1, R−1), e é invariante por isometria.

  python3 tools/exatos/lp_bin/fatia_bin.py --n 10 --R 3 --M 11 --listar i.json
"""
import argparse
import itertools
import json
from collections import Counter
from math import comb

import numpy as np


def vol(n, R):
    return sum(comb(n, i) for i in range(R + 1)) if R >= 0 else 0


def composicoes(m, P):
    """Todas as composições de m em P partes (int16)."""
    if P == 1:
        return np.array([[m]], dtype=np.int16)
    out = []
    for a in range(m, -1, -1):
        r = composicoes(m - a, P - 1)
        out.append(np.hstack([np.full((len(r), 1), a, np.int16), r]))
    return np.vstack(out)


def padroes(s):
    """Padrões normalizados: bit i = bit do ponto i na coluna; bit 0 sempre 0."""
    return [2 * k for k in range(1 << (s - 1))]


def _norm(p, s):
    return p ^ ((1 << s) - 1) if p & 1 else p


def tabelas_perm(s):
    pats = padroes(s)
    pos = {p: i for i, p in enumerate(pats)}
    tabs = [[pos[_norm(sum(((p >> i) & 1) << sig[i] for i in range(s)), s)] for p in pats]
            for sig in itertools.permutations(range(s))]
    return np.array(tabs), pats


def canonicos(m, s, lote=2_000_000):
    """Vetores de contagem, um por classe de isometria de s pontos distintos de Z_2^m."""
    tabs, pats = tabelas_perm(s)
    P = len(pats)
    w = 1
    while (m + 1) ** (w + 1) < 2 ** 62:
        w += 1
    blocos = [list(range(j, min(j + w, P))) for j in range(0, P, w)]
    pesos = [np.array([(m + 1) ** (len(b) - 1 - i) for i in range(len(b))], dtype=np.int64) for b in blocos]

    def chaves(X):
        return np.stack([X[:, b].astype(np.int64) @ pw for b, pw in zip(blocos, pesos)], 1)

    def maior(A, B):
        res, igual = np.zeros(len(A), bool), np.ones(len(A), bool)
        for j in range(A.shape[1]):
            res |= igual & (A[:, j] > B[:, j])
            igual &= A[:, j] == B[:, j]
        return res

    sep = [np.array([((p >> i) ^ (p >> k)) & 1 for p in pats], bool)
           for i in range(s) for k in range(i + 1, s)]
    todos = composicoes(m, P)
    out = []
    for ini in range(0, len(todos), lote):
        C = todos[ini:ini + lote]
        ok = np.ones(len(C), bool)
        for mask in sep:
            ok &= (C[:, mask] > 0).any(1)
        C = C[ok]
        chave = chaves(C)
        melhor = chave.copy()
        for t in tabs:
            Cp = np.zeros_like(C)
            Cp[:, t] = C
            k = chaves(Cp)
            mm = maior(k, melhor)
            melhor[mm] = k[mm]
        out.append(C[(chave == melhor).all(1)])
    return np.vstack(out), pats


def pontos(c, pats, s):
    """Os s pontos de Z_2^m: colunas na ordem dos padrões, repetidas c_p vezes."""
    cols = [p for p, k in zip(pats, c) for _ in range(int(k))]
    return [tuple((p >> i) & 1 for p in cols) for i in range(s)]


def descobertos(c, pats, s, R):
    """|U(K)| contado por órbitas (a_v = uns entre as colunas do padrão v)."""
    tipos = [(p, int(k)) for p, k in zip(pats, c) if k > 0]
    A = np.array(list(itertools.product(*[range(k + 1) for _, k in tipos])), dtype=np.int64)
    tam = np.ones(len(A), dtype=np.int64)
    D = np.zeros((len(A), s), dtype=np.int64)
    for j, (p, k) in enumerate(tipos):
        tam *= np.array([comb(k, a) for a in range(k + 1)], dtype=np.int64)[A[:, j]]
        for i in range(s):
            D[:, i] += (k - A[:, j]) if (p >> i) & 1 else A[:, j]
    return int(tam[D.min(1) > R].sum())


def instancias(n, R, M):
    """[(s, K, (M − s,))] na ordem: s crescente, K na ordem de `canonicos`."""
    out = []
    for s in range(0, M // 2 + 1):
        cap = (M - s) * vol(n - 1, R - 1)
        if s == 0:
            if (1 << (n - 1)) <= cap:
                out.append((0, (), (M,)))
            continue
        C, pats = canonicos(n - 1, s)
        for c in C:
            if descobertos(c, pats, s, R) <= cap:
                out.append((s, tuple(pontos(c, pats, s)), (M - s,)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("n", "R", "M"):
        ap.add_argument("--" + k, type=int, required=True)
    ap.add_argument("--listar", required=True, help="JSON no formato de rodar_pb.py --listar")
    a = ap.parse_args()
    ins = instancias(a.n, a.R, a.M)
    json.dump([[s, [list(k) for k in K], list(t)] for s, K, t in ins], open(a.listar, "w"))
    print(f"K_2({a.n},{a.R}) M={a.M}: {len(ins)} instâncias -> {a.listar}; por s*: {dict(Counter(i[0] for i in ins))}")


if __name__ == "__main__":
    main()
