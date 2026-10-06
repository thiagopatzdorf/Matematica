"""Raio de cobertura de segunda ordem R_2(C) de um código C ⊆ Z_q^n.

Definição (Elimelech–Schwartz, arXiv:2210.00531):

    R_2(C) = max_{(u1,u2) ∈ (Z_q^n)^2}  min_{(c1,c2) ∈ C×C}  |supp(u1−c1) ∪ supp(u2−c2)|.

Dois verificadores independentes:

* ``r2_bruto``: a definição ao pé da letra, em Python puro, com conjuntos de suporte.
  Lento (q^{2n}·|C|^2·n), serve de juiz para o outro.
* ``r2_rapido``: usa a isometria das colunas. A matriz 2×n (u1;u2) é um vetor de comprimento n
  sobre o alfabeto Z_q^2 (cada coluna vira um símbolo), e o 2-peso é exatamente o peso de Hamming
  desse vetor. Então R_2(C) é o raio de cobertura comum do código C⊗C = {colunas de (c1;c2)} em
  (Z_q^2)^n, calculado por busca em largura com várias fontes no grafo de Hamming H(n, q^2).

Um código é uma lista de tuplas (ou uma lista de inteiros na base q, com ``de_inteiros``).
"""
from __future__ import annotations

from itertools import product

import numpy as np


def de_inteiros(indices, q: int, n: int) -> list[tuple[int, ...]]:
    """Índice na base q (coordenada 0 é o dígito menos significativo) → tupla de comprimento n."""
    saida = []
    for x in indices:
        x = int(x)
        t = []
        for _ in range(n):
            t.append(x % q)
            x //= q
        saida.append(tuple(t))
    return saida


def para_inteiro(palavra, q: int) -> int:
    return sum(int(s) * q**i for i, s in enumerate(palavra))


def _suporte(u, c) -> set[int]:
    return {i for i, (a, b) in enumerate(zip(u, c)) if a != b}


def r2_bruto(codigo, q: int, n: int) -> int:
    """R_2 pela definição, sem atalho nenhum. Só para q^{2n}·|C|^2 pequeno."""
    codigo = [tuple(c) for c in codigo]
    if not codigo:
        raise ValueError("código vazio não tem raio de cobertura")
    pior = 0
    espaco = list(product(range(q), repeat=n))
    for u1 in espaco:
        for u2 in espaco:
            melhor = n
            for c1 in codigo:
                s1 = _suporte(u1, c1)
                for c2 in codigo:
                    melhor = min(melhor, len(s1 | _suporte(u2, c2)))
            pior = max(pior, melhor)
    return pior


def _indices_pares(codigo, q: int, n: int) -> np.ndarray:
    """Índices em (Z_q^2)^n das colunas de (c1;c2), para todo par ordenado (c1,c2) ∈ C×C."""
    Q = q * q
    arr = np.asarray([tuple(c) for c in codigo], dtype=np.int64).reshape(len(codigo), n)
    pesos = Q ** np.arange(n, dtype=np.int64)
    linha1 = (arr * q) @ pesos       # símbolo da coluna i = q·c1_i + c2_i
    linha2 = arr @ pesos
    return (linha1[:, None] + linha2[None, :]).ravel()


def cobertos_ate(codigo, q: int, n: int, r: int) -> np.ndarray:
    """Máscara booleana dos pontos de (Z_q^2)^n a distância ≤ r de C⊗C (r passos de BFS)."""
    Q = q * q
    alcancado = np.zeros(Q**n, dtype=bool)
    alcancado[_indices_pares(codigo, q, n)] = True
    for _ in range(r):
        novo = alcancado.copy()
        for i in range(n):
            # eixo do meio = coordenada i; um passo muda só essa coordenada para qualquer símbolo
            v = alcancado.reshape(Q ** (n - 1 - i), Q, Q**i)
            novo.reshape(Q ** (n - 1 - i), Q, Q**i)[:] |= v.any(axis=1, keepdims=True)
        alcancado = novo
    return alcancado


def r2_rapido(codigo, q: int, n: int) -> int:
    """R_2 pela isometria das colunas: raio de cobertura de C⊗C em H(n, q^2)."""
    if len(codigo) == 0:
        raise ValueError("código vazio não tem raio de cobertura")
    for r in range(n + 1):
        if cobertos_ate(codigo, q, n, r).all():
            return r
    raise AssertionError("inalcançável: raio n sempre cobre")


def r1_rapido(codigo, q: int, n: int) -> int:
    """Raio de cobertura comum R(C) em H(n, q), mesma BFS (para a cota R ≤ R_2 ≤ 2R)."""
    alcancado = np.zeros(q**n, dtype=bool)
    alcancado[[para_inteiro(c, q) for c in codigo]] = True
    r = 0
    while not alcancado.all():
        novo = alcancado.copy()
        for i in range(n):
            v = alcancado.reshape(q ** (n - 1 - i), q, q**i)
            novo.reshape(q ** (n - 1 - i), q, q**i)[:] |= v.any(axis=1, keepdims=True)
        alcancado = novo
        r += 1
    return r


def volume_bola(n: int, r: int, alfabeto: int) -> int:
    from math import comb
    return sum(comb(n, i) * (alfabeto - 1) ** i for i in range(r + 1))


def cota_esfera(q: int, n: int, r: int) -> int:
    """Menor M com M^2 · V ≥ q^{2n}, V = volume da bola de raio r em H(n, q^2)."""
    V = volume_bola(n, r, q * q)
    alvo = q ** (2 * n)
    M = 1
    while M * M * V < alvo:
        M += 1
    return M


def raiz_teto(x: int) -> int:
    from math import isqrt
    s = isqrt(x)
    return s if s * s == x else s + 1
