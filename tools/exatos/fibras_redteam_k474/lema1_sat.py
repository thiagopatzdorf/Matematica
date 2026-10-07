#!/usr/bin/env python3
"""Lema 1 contra um solver exato, com K_v(m,r) calculado AQUI (nada de ledger).

Para (q,n,R,M) e cada s = 0..q-1: o lema exclui "fibra de tamanho s" quando K_{q-s}(n-1,R-1) > M-s.
O teste pergunta ao SAT (codificação independente `cobertura_indep`): existe multiconjunto de M palavras
que cobre Z_q^n com raio R e exatamente s palavras com símbolo 0 na coordenada 0?
  - se o lema exclui s, a resposta TEM de ser UNSAT (senão o lema é falso: contraexemplo);
  - se o lema não exclui, SAT ou UNSAT são ambos coerentes (o lema não é justo), mas registramos.
Valores de K_v(m,r) usados vêm de `exato(v, m, r)`: menor M com SAT, partindo da cota de esferas.

Uso: python3 lema1_sat.py q n R M [M ...]    (um processo por célula; imprime uma linha por s)
"""
import math
import sys
import time
from functools import lru_cache

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cobertura_indep as ci  # noqa: E402


def esfera(v, m, r):
    vol = sum(math.comb(m, k) * (v - 1) ** k for k in range(r + 1))
    return -(-v ** m // vol)


@lru_cache(None)
def exato(v, m, r, limite=2000):
    """K_v(m,r) exato por SAT crescente a partir da cota de esferas (só para instâncias pequenas)."""
    if v == 1 or r >= m:
        return 1
    if r == 0:
        return v ** m
    M = esfera(v, m, r)
    while True:
        f, w = ci.codificar(v, m, r, M)
        ok, mod = ci.resolver(f)
        if ok:
            assert ci.cobre(ci.decodificar(mod, w, v, m), v, m, r)
            return M
        M += 1


def consulta(q, n, R, M, s, solver="cadical153"):
    f, w = ci.codificar(q, n, R, M, prefixo_fibra={(0, 0): s})
    ok, mod = ci.resolver(f, solver=solver)
    if ok:
        cod = ci.decodificar(mod, w, q, n)
        assert ci.cobre(cod, q, n, R) and sum(1 for c in cod if c[0] == 0) == s
    return ok


def main():
    q, n, R = map(int, sys.argv[1:4])
    for M in map(int, sys.argv[4:]):
        for s in range(q):
            t = time.time()
            K = exato(q - s, n - 1, R - 1)
            exclui = K > M - s
            ok = consulta(q, n, R, M, s)
            veredito = "OK" if not (exclui and ok) else "LEMA FALSO"
            print(f"K_{q}({n},{R}) M={M} s={s}: K_{q - s}({n - 1},{R - 1}) = {K} {'>' if exclui else '<='} {M - s}: "
                  f"lema {'exclui' if exclui else 'permite'}; SAT existe código com fibra {s}? {ok} -> {veredito} ({time.time() - t:.0f}s)",
                  flush=True)
            if exclui and ok:
                sys.exit(1)


if __name__ == "__main__":
    main()
