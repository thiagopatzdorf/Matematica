"""Busca heurística de códigos com R_2(C) ≤ r (cotas superiores).

Usa a formulação por projeções: para cada palavra u, a máscara F(u) marca os conjuntos S de
n−r coordenadas com u|_S ∈ proj_S(C). O par (u1,u2) está coberto se e só se F(u1) ∧ F(u2) ≠ 0.
O custo de um código é o número de pares não ordenados descobertos; custo 0 ⇔ R_2(C) ≤ r.

Nada aqui é prova: toda testemunha encontrada é reconferida por ``raio2.r2_rapido``
(e, quando cabe, por ``raio2.r2_bruto``) antes de entrar em ``dados/``.
"""
from __future__ import annotations

import math
import random
from itertools import combinations

import numpy as np


class Projecoes:
    """Contagens de proj_S(C) para todo S, e o custo de pares descobertos."""

    def __init__(self, q: int, n: int, r: int):
        self.q, self.n, self.r = q, n, r
        self.N = q**n
        self.conjuntos = list(combinations(range(n), n - r))
        digitos = np.array([[(c // q**i) % q for i in range(n)] for c in range(self.N)], dtype=np.int64)
        # padrao[s, c] = índice do padrão c|_S na base q
        self.padrao = np.stack([
            (digitos[:, list(S)] * (q ** np.arange(len(S), dtype=np.int64))).sum(axis=1)
            for S in self.conjuntos
        ])
        self.P = q ** (n - r)
        self.cont = np.zeros((len(self.conjuntos), self.P), dtype=np.int64)
        self.bits = np.array([1 << s for s in range(len(self.conjuntos))], dtype=object)
        self.usar_objeto = len(self.conjuntos) > 62

    def zerar(self):
        self.cont[:] = 0

    def mudar(self, c: int, delta: int):
        self.cont[np.arange(len(self.conjuntos)), self.padrao[:, c]] += delta

    def mascaras(self) -> np.ndarray:
        presente = np.take_along_axis(self.cont, self.padrao, axis=1) > 0  # (|S|, N)
        if self.usar_objeto:
            m = np.zeros(self.N, dtype=object)
            for s in range(len(self.conjuntos)):
                m = m + presente[s].astype(object) * (1 << s)
            return m
        pesos = (np.int64(1) << np.arange(len(self.conjuntos), dtype=np.int64))
        return (presente.astype(np.int64) * pesos[:, None]).sum(axis=0)

    def custo(self) -> int:
        m = self.mascaras()
        valores, contagem = np.unique(m, return_counts=True)
        if self.usar_objeto:
            valores = list(valores)
            total = 0
            for i, a in enumerate(valores):
                for j in range(i, len(valores)):
                    if a & valores[j] == 0:
                        total += contagem[i] * (contagem[i] + 1) // 2 if i == j else contagem[i] * contagem[j]
            return int(total)
        disjunto = (valores[:, None] & valores[None, :]) == 0
        prod = np.outer(contagem, contagem)
        # pares não ordenados com u1 ≠ u2 mais os pares u1 = u2 (máscara vazia)
        fora = (prod * disjunto).sum() - (contagem * np.diag(disjunto)).sum()
        return int(fora // 2 + (contagem * np.diag(disjunto)).sum())


def recozimento(q: int, n: int, r: int, M: int, passos: int = 20000, semente: int = 0,
                inicial: list[int] | None = None, temp0: float = 2.0):
    """Recozimento simulado com troca de uma palavra. Devolve o código (índices) ou None."""
    rng = random.Random(semente)
    pj = Projecoes(q, n, r)
    N = q**n
    codigo = list(inicial) if inicial else rng.sample(range(N), M)
    em = set(codigo)
    for c in codigo:
        pj.mudar(c, +1)
    atual = pj.custo()
    for t in range(passos):
        if atual == 0:
            return sorted(codigo)
        temp = temp0 * (1 - t / passos) + 1e-3
        i = rng.randrange(M)
        velho = codigo[i]
        novo = rng.randrange(N)
        if novo in em:
            continue
        pj.mudar(velho, -1)
        pj.mudar(novo, +1)
        cand = pj.custo()
        if cand <= atual or rng.random() < math.exp((atual - cand) / temp):
            codigo[i] = novo
            em.discard(velho)
            em.add(novo)
            atual = cand
        else:
            pj.mudar(novo, -1)
            pj.mudar(velho, +1)
    return sorted(codigo) if atual == 0 else None
