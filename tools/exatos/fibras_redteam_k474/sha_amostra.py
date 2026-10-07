#!/usr/bin/env python3
"""Regenera a CNF de registros sorteados do certificado e compara o sha256; confere também, em TODOS os
registros, que o campo `tipos` é a instância `inst` da lista do codificador na ordem gravada.

Uso: python3 sha_amostra.py CERT.jsonl.xz q n R M N_inteiros N_cubos SEMENTE
"""
import json
import lzma
import os
import random
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
FIB = os.path.join(AQUI, "..", "fibras")
sys.path.insert(0, FIB)
import fecha_perfis as fp  # noqa: E402
import fib_encode as enc  # noqa: E402


def main():
    arq, q, n, R, M, ni, nc, sem = sys.argv[1], *map(int, sys.argv[2:9])
    regs = [json.loads(l) for l in lzma.open(arq, "rt")]
    smin = enc.fibra_minima(q, n, R, M)
    listas = {o: enc.instancias(q, n, M, n, smin, ordem=o)[1] for o in ("min", "max")}
    ruim = 0
    for r in regs:
        pref = listas[r.get("ordem", "min")][r["inst"]]
        if ["".join(map(str, t)) for t in pref] != r["tipos"] or r["smin"] != smin or r["M"] != M or r["q"] != q \
                or r["n"] != n or r.get("R") != R or r["k"] != n:
            ruim += 1
    print(f"registros com `tipos`/`inst`/parâmetros incoerentes: {ruim} de {len(regs)}")
    assert ruim == 0
    rng = random.Random(sem)
    inteiros = [r for r in regs if not r.get("L")]
    cubos = [r for r in regs if r.get("L")]
    amostra = rng.sample(inteiros, ni) + rng.sample(cubos, nc)
    for r in amostra:
        t = time.time()
        h = fp.sha_cnf(q, n, M, n, smin, r, R)
        print(f"inst {r['inst']} {r.get('ordem')} {'cubo ' + str(r['cubo_idx']) if r.get('L') else 'inteiro'}: "
              f"{'IGUAL' if h == r['sha256.cnf'] else 'DIFERENTE'} ({time.time() - t:.1f}s) {h[:12]}")
        assert h == r["sha256.cnf"]


if __name__ == "__main__":
    main()
