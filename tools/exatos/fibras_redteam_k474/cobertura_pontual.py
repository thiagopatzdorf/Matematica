#!/usr/bin/env python3
"""A cláusula de cobertura de cada ponto z da CNF REAL da instância (M, perfil) é satisfeita sse z é
coberto? Confere em tamanho real (K_4(6,3) M=11 e K_4(7,4) M=9), por propagação unitária:
  1. regenera a CNF (fib_encode.codificar, quebra=False) de uma instância sorteada;
  2. fixa as variáveis x de um código com aquele perfil (coordenada 0 = blocos);
  3. propaga: as P[T,v] são definidas por equivalência, então ficam determinadas;
  4. a cláusula do ponto z fica falsa sse nenhum dos P[T, z_T] é verdadeiro;
  5. compara o conjunto de pontos "descobertos segundo a CNF" com o conjunto "descobertos" pela
     definição d(z, c) <= R (força bruta com numpy, sem Lema 2').
Uso: python3 cobertura_pontual.py q n R M N SEMENTE
"""
import itertools
import math
import os
import random
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "fibras"))
sys.path.insert(0, AQUI)
import fib_encode as enc  # noqa: E402
import orbita_indep as o  # noqa: E402
from pysat.solvers import Solver  # noqa: E402


def melhorar(cod, q, n, R, rng, passos=300):
    """Subida de colina que preserva o perfil (troca símbolos entre palavras numa coluna): mais pontos cobertos
    deixam o teste mais discriminante do que um código aleatório (que cobre poucos pontos)."""
    P = np.array(list(itertools.product(range(q), repeat=n)), dtype=np.int8)

    def cob(c):
        m = np.zeros(len(P), dtype=bool)
        for w in c:
            m |= (P != np.array(w, dtype=np.int8)).sum(1) <= R
        return int(m.sum())

    atual = cob(cod)
    for _ in range(passos):
        i = rng.randrange(1, n)
        a, b = rng.sample(range(len(cod)), 2)
        if cod[a][i] == cod[b][i]:
            continue
        novo = [list(w) for w in cod]
        novo[a][i], novo[b][i] = novo[b][i], novo[a][i]
        novo = [tuple(w) for w in novo]
        v = cob(novo)
        if v >= atual:
            cod, atual = novo, v
    return cod, atual


def main():
    q, n, R, M, N, sem = map(int, sys.argv[1:7])
    t = n - R
    rng = random.Random(sem)
    smin = enc.fibra_minima(q, n, R, M)
    _, ins = enc.instancias(q, n, M, n, smin, ordem="max")
    pontos = list(itertools.product(range(q), repeat=n))
    Parr = np.array(pontos, dtype=np.int8)
    larg = math.comb(n, t)
    for r in range(N):
        pref = rng.choice(ins)
        cod = o.codigo_com_perfil(q, n, list(pref), rng)
        # forma de blocos: coordenada 0 por blocos (t0[a] palavras com símbolo a), símbolos por fibra decrescente
        # (codigo_com_perfil sorteia colunas com as fibras t[a] para o símbolo a, só falta ordenar por coord 0)
        cod.sort(key=lambda w: w[0])
        cod, cob_bf = melhorar(cod, q, n, R, rng)
        cod.sort(key=lambda w: w[0])
        cnf, x, sim0, ts = enc.codificar(q, n, M, pref, smin, quebra=False, R=R)
        assert [w[0] for w in cod] == sim0
        unit = [x[w][i][cod[w][i]] for w in range(M) for i in range(1, n)]
        nvx = max(x[w][i][a] for w in range(M) for i in range(1, n) for a in range(q))
        cover = [c for c in cnf.cl if len(c) == larg and all(l > nvx for l in c)]
        cover = cover[-len(pontos):]
        assert len(cover) == len(pontos)
        resto = [c for c in cnf.cl if not (len(c) == larg and all(l > nvx for l in c))]
        with Solver(name="glucose4", bootstrap_with=resto) as s:
            ok, impl = s.propagate(assumptions=unit)
            assert ok
            verdade = set(l for l in impl if l > 0)
        desc_cnf = {j for j, c in enumerate(cover) if not any(l in verdade for l in c)}
        cobertos = np.zeros(len(pontos), dtype=bool)
        for w in cod:
            cobertos |= (Parr != np.array(w, dtype=np.int8)).sum(1) <= R
        desc_bf = set(np.flatnonzero(~cobertos).tolist())
        print(f"perfil {' '.join(''.join(map(str, u)) for u in pref)}: pontos descobertos pela CNF = {len(desc_cnf)}, "
              f"pela definição = {len(desc_bf)}, coincidem = {desc_cnf == desc_bf}", flush=True)
        assert desc_cnf == desc_bf
        assert len(desc_bf) == len(pontos) - cob_bf


if __name__ == "__main__":
    main()
