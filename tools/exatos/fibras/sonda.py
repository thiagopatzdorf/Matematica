#!/usr/bin/env python3
"""Sonda de existência: procura um código de K_q(n, n-2) com M palavras num perfil escolhido.

O `rodar.py` percorre perfis por índice para provar inexistência. Para achar um código basta
um perfil bom (em geral o mais equilibrado, que o índice não alcança barato quando T é grande):
aqui o prefixo de tipos é dado direto. A CNF é a mesma do `fib_encode.codificar` (as quebras
de simetria só restringem, então SAT continua sendo um código de verdade), e o código achado é
decodificado e conferido em todo Z_q^n (CaDiCaL por padrão: em K_7(6,4), M = 14, achou o código em
18 s onde o kissat passou de 300 s). UNSAT de sonda não prova nada (sem LRAT e perfil
escolhido a dedo): só SAT + cobertura conferida vale.

Uso (tipos separados por ';', partes de um tipo por ','):
  python3 tools/exatos/fibras/sonda.py --q 7 --n 6 --M 14 --tipos "2,2,2,2,2,2,2" --dir s/
  python3 tools/exatos/fibras/sonda.py --q 16 --n 4 --M 86 --equilibrado 2 --dir s/ --tempo 1200
"""
import argparse
import json
import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import fib_encode as enc  # noqa: E402
from rodar import binario, cobre  # noqa: E402


def equilibrado(q, M):
    """Tipo com as fibras mais parecidas possível: M = q·b + r, r fibras de b+1."""
    b, r = divmod(M, q)
    return tuple([b + 1] * r + [b] * (q - r))


def sondar(q, n, M, prefixo, d, solver="cadical", tempo=600):
    smin = min(min(t) for t in prefixo)
    for t in prefixo:
        assert len(t) == q and sum(t) == M and list(t) == sorted(t, reverse=True), t
    cnf, x, sim0, _ = enc.codificar(q, n, M, tuple(prefixo), smin)
    os.makedirs(d, exist_ok=True)
    nome = "_".join("".join(map(str, t)) if max(t) < 10 else "-".join(map(str, t)) for t in prefixo)
    base = os.path.join(d, f"sonda_K{q}_{n}_{n-2}_M{M}_{nome}")
    with open(base + ".cnf", "w") as f:
        f.write(cnf.dimacs([f"sonda K_{q}({n},{n-2}) M={M} prefixo {prefixo}"]))
    if solver == "kissat":
        cmd = [binario("KISSAT", "kissat"), "-q", f"--time={tempo}", base + ".cnf"]
    else:
        cmd = [binario("CADICAL", "cadical"), "-q", "-t", str(tempo), base + ".cnf"]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    reg = {"q": q, "n": n, "M": M, "prefixo": [list(t) for t in prefixo], "solver": solver,
           "tempo_solver_s": round(time.time() - t0, 3), "rc": r.returncode}
    os.remove(base + ".cnf")
    if r.returncode == 10:
        modelo = [int(v) for ln in r.stdout.splitlines() if ln.startswith("v ") for v in ln[2:].split()]
        pal = enc.decodificar(modelo, x, sim0, q, n, M)
        reg["resultado"] = "SAT"
        reg["codigo"] = ["".join(map(str, w)) if q <= 10 else " ".join(map(str, w)) for w in pal]
        reg["cobre"] = cobre(q, n, pal)
        with open(base + ".codigo.txt", "w") as f:
            f.write("\n".join(reg["codigo"]) + "\n")
    else:
        reg["resultado"] = "UNSAT_NA_SONDA" if r.returncode == 20 else "INDEFINIDO"
    return reg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--q", type=int, required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--M", type=int, required=True)
    ap.add_argument("--tipos", default="", help="prefixo: tipos separados por ';'")
    ap.add_argument("--equilibrado", type=int, default=0, help="prefixo de k cópias do tipo equilibrado")
    ap.add_argument("--dir", required=True)
    ap.add_argument("--solver", default="cadical", choices=["kissat", "cadical"])
    ap.add_argument("--tempo", type=int, default=600)
    a = ap.parse_args()
    if a.tipos:
        prefixo = [tuple(int(v) for v in t.split(",")) for t in a.tipos.split(";")]
    else:
        prefixo = [equilibrado(a.q, a.M)] * max(1, a.equilibrado)
    print(json.dumps(sondar(a.q, a.n, a.M, prefixo, a.dir, a.solver, a.tempo)), flush=True)


if __name__ == "__main__":
    main()
