#!/usr/bin/env python3
"""Roda a instância independente (`indep_instancia.construir` + kissat) em um lote sorteado de perfis de um
registro. Uso: python3 indep_lote.py CERT.jsonl.xz q n R M N SEMENTE KISSAT TEMPO SAIDA.jsonl [TRAB]"""
import json
import lzma
import os
import random
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import indep_instancia as ii  # noqa: E402


def main():
    arq, q, n, R, M, N, sem = sys.argv[1], *map(int, sys.argv[2:8])
    kissat, tempo, saida = sys.argv[8], int(sys.argv[9]), sys.argv[10]
    trab = sys.argv[11] if len(sys.argv) > 11 else "/tmp"
    regs = [json.loads(ln) for ln in lzma.open(arq, "rt")]
    regs = [r for r in regs if not r.get("L")]
    amostra = random.Random(sem).sample(regs, min(N, len(regs)))
    cont = {}
    for r in amostra:
        tipos = [tuple(int(c) for c in s) for s in r["tipos"]]
        f = ii.construir(q, n, R, M, tipos)
        cnf = os.path.join(trab, f"lote_{q}_{n}_{M}_{r['inst']}.cnf")
        ii.dimacs(f, cnf)
        t = time.time()
        try:
            p = subprocess.run([kissat, "-q", f"--time={tempo}", cnf], capture_output=True, text=True, timeout=tempo + 60)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            rc = -1
        os.remove(cnf)
        v = {20: "UNSAT", 10: "SAT"}.get(rc, "INDEFINIDO")
        cont[v] = cont.get(v, 0) + 1
        with open(saida, "a") as fo:
            fo.write(json.dumps({"inst": r["inst"], "ordem": r["ordem"], "tipos": r["tipos"], "veredito": v,
                                 "resolver_s": round(time.time() - t, 1)}) + "\n")
    print(f"K_{q}({n},{R}) M={M}: {len(amostra)} perfis sorteados (semente {sem}) pela codificação independente: {cont}")


if __name__ == "__main__":
    main()
