#!/usr/bin/env python3
"""Massa de testes de órbita: perfis sorteados (com codigo_com_perfil) contra a CNF com quebra=True.

  python3 orbita_massa.py Q N R M AMOSTRA SEMENTE [com_cobertura 0|1] [mutante]

Imprime uma linha por (código, ordem) com UNSAT; resumo no fim. Mutantes (trechos trocados no
fib_encode lido do disco) servem para medir o PODER do teste.
"""
import importlib.util
import os
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FIB = os.path.join(AQUI, "..", "fibras")
sys.path.insert(0, AQUI)
import orbita_indep as o  # noqa: E402

MUTANTES = {
    "h_ambos": ("lex_leq_listas(cnf, [x[w][1] for w in A], [x[w][1] for w in B], q)",
                "lex_leq_listas(cnf, [x[w][1] for w in A], [x[w][1] for w in B], q); "
                "lex_leq_listas(cnf, [x[w][1] for w in B], [x[w][1] for w in A], q)"),
    "e_sem_classe": ("        if c1[a] != c1[a + 1]:\n            continue\n        for bi, B in enumerate(bl):",
                     "        for bi, B in enumerate(bl):"),
    "f_sem_classe": ("            if ci[a] != ci[a + 1]:\n                continue\n            for w in range(M):",
                     "            for w in range(M):"),
    "g_tipos_diferentes": ("            if ts[i] == ts[i + 1]:\n                lex_leq(cnf, x, q, M, i, i + 1)",
                           "            lex_leq(cnf, x, q, M, i, i + 1)"),
    "d_sem_monotonia": ("                    cnf.add([-x[w][1][a], -x[w + 1][1][b]])",
                        "                    cnf.add([-x[w][1][a], -x[w + 1][1][b], x[w][1][a]]) if False else None"),
}


def carregar(mutante=None):
    src = open(os.path.join(FIB, "fib_encode.py")).read()
    if mutante:
        a, b = MUTANTES[mutante]
        assert a in src, f"mutante {mutante}: trecho não encontrado"
        src = src.replace(a, b)
    spec = importlib.util.spec_from_loader("fib_encode_m", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__file__ = os.path.join(FIB, "fib_encode.py")
    sys.modules["fib_encode_m"] = mod
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod


def main():
    a = sys.argv[1:]
    q, n, R, M, N, sem = map(int, a[:6])
    cob = bool(int(a[6])) if len(a) > 6 else False
    mut = a[7] if len(a) > 7 else None
    sys.path.insert(0, FIB)
    enc = carregar(mut)
    rng = random.Random(sem)
    smin = enc.fibra_minima(q, n, R, M)
    _, ins = enc.instancias(q, n, M, n, smin)
    unsat = total = 0
    for r in range(N):
        p = rng.choice(ins) if r % 2 == 0 else max(ins[: min(len(ins), 400)], key=lambda t: sum(enc.simetria_residual(u) for u in t) + rng.random())
        cod = o.codigo_com_perfil(q, n, list(p), rng)
        for ordem in ("min", "max"):
            ok = o.orbita_sat(enc, q, n, M, R, cod, ordem, com_cobertura=cob)
            total += 1
            if not ok:
                unsat += 1
                print("ORBITA_UNSAT", ordem, [''.join(map(str, t)) for t in p], cod, flush=True)
    print(f"q={q} n={n} R={R} M={M} smin={smin} mutante={mut} cobertura={cob}: {total} testes, {unsat} UNSAT")


if __name__ == "__main__":
    main()
