#!/usr/bin/env python3
"""Red team do Lema 1 (fibras): construção explícita da prova, sem importar nada de tools/exatos/fibras.

Lema 1: C ⊂ Z_q^n de raio R <= n-2 com M palavras (multiconjunto); F = {c : c_j = a}, s = |F| < q.
Então K_{q-s}(n-1, R-1) <= M - s.  Prova: A_i = {c_i : c in F}; S_i ⊂ Z_q \\ A_i com |S_i| = q - s;
B = {x : x_j = a, x_i in S_i}; phi_i = identidade em S_i e sigma_i fora; a imagem de C \\ F por phi
(sem a coordenada j) cobre prod S_i com raio R-1.

Este script aplica a construção a códigos de cobertura REAIS (e a multiconjuntos), com S_i e sigma_i
sorteados, e confere por força bruta que a imagem cobre. Falha (exit 1) se algum caso não cobre.

Uso: python3 lema1_construcao.py [semente] [codigos_por_celula]
"""
import itertools
import random
import sys

import numpy as np


def pontos(q, n):
    return np.array(list(itertools.product(range(q), repeat=n)), dtype=np.int8)


def descobertos(cod, q, n, R, P=None):
    """Pontos de Z_q^n a distância > R de todas as palavras (força bruta, numpy)."""
    P = pontos(q, n) if P is None else P
    cob = np.zeros(len(P), dtype=bool)
    for c in cod:
        cob |= (P != np.array(c, dtype=np.int8)).sum(1) <= R
    return int((~cob).sum())


def codigo_guloso(q, n, R, rng, extra=0):
    """Código que cobre (guloso aleatório), com `extra` palavras repetidas/aleatórias a mais."""
    P = pontos(q, n)
    desc = np.ones(len(P), dtype=bool)
    cod = []
    while desc.any():
        idx = np.flatnonzero(desc)
        cand = P[rng.sample(list(idx), min(30, len(idx)))]
        # candidatos: pontos descobertos mexidos em algumas coordenadas
        melhor, ganho = None, -1
        for c in cand:
            c = c.copy()
            for i in range(n):
                if rng.random() < 0.3:
                    c[i] = rng.randrange(q)
            g = int((desc & ((P != c).sum(1) <= R)).sum())
            if g > ganho:
                melhor, ganho = c, g
        cod.append(tuple(int(v) for v in melhor))
        desc &= ~((P != melhor).sum(1) <= R)
    # poda: tira palavras redundantes (o guloso deixa códigos grandes, com fibras >= q, onde o lema nada diz)
    ordem = list(range(len(cod)))
    rng.shuffle(ordem)
    for u in ordem:
        resto = [w for k, w in enumerate(cod) if k != u and w is not None]
        if descobertos(resto, q, n, R, P) == 0:
            cod[u] = None
    cod = [w for w in cod if w is not None]
    for _ in range(extra):
        cod.append(rng.choice(cod) if rng.random() < 0.5 else tuple(rng.randrange(q) for _ in range(n)))
    rng.shuffle(cod)
    return cod


def lema1(cod, q, n, R, j, a, rng, mutante=False):
    """Aplica a construção; devolve (s, imagem como lista de tuplas em Z_{q-s}^{n-1}) ou None se s >= q."""
    F = [c for c in cod if c[j] == a]
    s = len(F)
    if s >= q or s == 0 and mutante:
        return None
    resto = [i for i in range(n) if i != j]
    S, phi = {}, {}
    for i in resto:
        A = {c[i] for c in F}
        livres = [v for v in range(q) if v not in A]
        assert len(livres) >= q - s
        # mutante: S_i tirado de Z_q inteiro (ignora A_i): é o erro que a prova escrita impede
        Si = sorted(rng.sample(range(q) if mutante else livres, q - s))      # |S_i| = q-s, tirado de fora de A_i
        rot = {v: r for r, v in enumerate(Si)}      # S_i ≅ Z_{q-s}
        sig = rng.choice(Si)
        S[i] = Si
        phi[i] = {v: rot[v if v in rot else sig] for v in range(q)}
    img = [tuple(phi[i][c[i]] for i in resto) for c in cod if c[j] != a]
    return s, img


def principal(semente=2026, por_celula=6, mutante=False, celulas=None):
    rng = random.Random(semente)
    celulas = celulas or [(3, 4, 1), (3, 5, 2), (4, 4, 2), (3, 5, 1), (4, 5, 2), (3, 6, 3), (3, 6, 2), (4, 6, 3),
                          (4, 5, 1), (5, 5, 3), (4, 7, 4), (4, 7, 3)]
    total = falhas = 0
    for q, n, R in celulas:
        casos = soma_s = 0
        for rep in range(por_celula):
            cod = codigo_guloso(q, n, R, rng, extra=rng.choice([0, 0, 1, 3]))
            M = len(cod)
            for j in range(n):
                for a in range(q):
                    r = lema1(cod, q, n, R, j, a, rng, mutante)
                    if r is None:
                        continue
                    s, img = r
                    ok = len(img) <= M - s and descobertos(img, q - s, n - 1, R - 1) == 0 if R >= 1 else True
                    casos += 1
                    soma_s += s
                    total += 1
                    if not ok:
                        falhas += 1
                        print("FALHA", (q, n, R), "M", M, "j,a", j, a, "s", s, file=sys.stderr)
        print(f"K_{q}({n},{R}): {casos} fibras testadas (s médio {soma_s / max(casos, 1):.2f})")
    print(f"total {total} fibras, {falhas} falhas")
    return falhas


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(1 if principal(int(a[0]) if a else 2026, int(a[1]) if len(a) > 1 else 6) else 0)
