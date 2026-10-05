"""Códigos de cobertura reais de células pequenas da família K_q(n, n-2), achados pela
codificação independente por perfil (`indep_perfil.py`), para servir de entrada aos testes de
completude. Percorre perfis (em ordem aleatória, fibras >= smin) e, em cada perfil SAT, tira até
`por_perfil` códigos distintos bloqueando cada um. Todo código gravado é conferido por força bruta.

Uso: gerar_codigos.py q n M smin quantos por_perfil semente saida.txt [segundos_max]
(saída: códigos separados por linha em branco)"""
import itertools
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import indep_perfil  # noqa: E402
import perfis_indep  # noqa: E402
from pysat.solvers import Solver  # noqa: E402


def cobre(C, q, n, R):
    return all(any(sum(a != b for a, b in zip(p, c)) <= R for c in C) for p in itertools.product(range(q), repeat=n))


def achar(q, n, M, smin, quantos, por_perfil, semente, segundos=600):
    rng = random.Random(semente)
    perfis = sorted(perfis_indep.perfis(q, n, M, smin))
    rng.shuffle(perfis)
    out, t0 = [], time.time()
    for p in perfis:
        if len(out) >= quantos or time.time() - t0 > segundos:
            break
        f, X = indep_perfil.codificar(q, n, M, list(p))
        with Solver(name="cadical195", bootstrap_with=f.cl) as s:
            for _ in range(por_perfil):
                if not s.solve():
                    break
                C = indep_perfil.decodificar(s.get_model(), X, q, n, M)
                assert cobre(C, q, n, n - 2)
                out.append(C)
                s.add_clause([-X[w][i][C[w][i]] for w in range(M) for i in range(n)])
    return out


if __name__ == "__main__":
    q, n, M, smin, quantos, por_perfil, semente = map(int, sys.argv[1:8])
    segundos = int(sys.argv[9]) if len(sys.argv) > 9 else 600
    cods = achar(q, n, M, smin, quantos, por_perfil, semente, segundos)
    with open(sys.argv[8], "w") as fh:
        for C in cods:
            fh.write("\n".join("".join(map(str, c)) for c in C) + "\n\n")
    print(f"K_{q}({n},{n-2}) M={M}: {len(cods)} códigos")
