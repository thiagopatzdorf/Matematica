#!/usr/bin/env python3
"""Roda todas as instâncias (perfis) de K_q(4,2) com M palavras e, se pedido, confere as provas.

Para cada perfil: gera a CNF (`encode.py`), roda o solver e registra uma linha JSON com o
resultado. Com `--prova`, o CaDiCaL escreve uma prova LRAT (`--lrat`) e ela é conferida por
dois verificadores independentes: `lrat-check` (drat-trim) e o verificador em Python deste
diretório (`lrat.py`, opcional com `--lrat-py`, lento). Instância SAT: o código é decodificado,
gravado e conferido em todo Z_q^4 aqui mesmo (o verificador oficial roda à parte).

Variáveis de ambiente: CADICAL, KISSAT, LRAT_CHECK (caminhos dos binários).

Uso:
  python3 tools/exatos/k742/rodar.py --q 7 --M 17 --dir saida/ [--prova] [--perfis 0-14] [-j 4]
"""
import argparse
import gzip
import hashlib
import itertools
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import proj  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))


def binario(var, nome):
    p = os.environ.get(var) or shutil.which(nome)
    if not p:
        raise SystemExit(f"{nome} não encontrado (defina {var})")
    return p


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def uma(args):
    q, n, R, M, smin, idx, d, prova, solver, tempo, descartar = args
    perfil = proj.perfis(q, n, R, M, smin)[idx]
    cnf, x, sim0 = proj.codificar(q, n, R, M, perfil)
    base = os.path.join(d, f"K{q}_{n}_{R}_M{M}_p{idx:06d}")
    with open(base + ".cnf", "w") as f:
        f.write(cnf.dimacs([f"K_{q}({n},{R}) M={M} smin={smin} perfil {idx}: {perfil}"]))
    reg = {"q": q, "n": n, "R": R, "M": M, "smin": smin, "perfil": idx, "tipos": ["".join(map(str, t)) for t in perfil],
           "vars": cnf.nv, "clausulas": len(cnf.cl)}
    t0 = time.time()
    if solver == "kissat" and not prova:
        cmd = [binario("KISSAT", "kissat"), "-q", f"--time={tempo}", base + ".cnf"]
    else:
        cmd = [binario("CADICAL", "cadical"), "-q", "-t", str(tempo), base + ".cnf"]
        if prova:
            cmd += ["--lrat", "--binary=false", base + ".lrat"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    reg["tempo_solver_s"] = round(time.time() - t0, 3)
    reg["rc"] = r.returncode
    if r.returncode == 20:
        reg["resultado"] = "UNSAT"
        if prova:
            t1 = time.time()
            c = subprocess.run([binario("LRAT_CHECK", "lrat-check"), base + ".cnf", base + ".lrat"],
                               capture_output=True, text=True)
            ok = "c VERIFIED" in c.stdout or "s VERIFIED" in c.stdout
            reg["lrat_check"] = "VERIFIED" if ok else ("FALHOU: " + c.stdout[-300:])
            reg["tempo_check_s"] = round(time.time() - t1, 3)
            for ext in (".cnf", ".lrat"):
                reg["bytes" + ext] = os.path.getsize(base + ext)
                reg["sha256" + ext] = sha(base + ext)
                if descartar:
                    os.remove(base + ext)
                    continue
                with open(base + ext, "rb") as fi, gzip.open(base + ext + ".gz", "wb", 6) as fo:
                    shutil.copyfileobj(fi, fo)
                os.remove(base + ext)
        else:
            os.remove(base + ".cnf")
    elif r.returncode == 10:
        reg["resultado"] = "SAT"
        modelo = [int(t) for ln in r.stdout.splitlines() if ln.startswith("v ")
                  for t in ln[2:].split()]
        palavras = ["".join(map(str, w)) for w in proj.decodificar(modelo, x, sim0, q, n, M)]
        reg["codigo"] = palavras
        reg["cobre"] = proj.cobre(q, n, R, [tuple(map(int, w)) for w in palavras])
        with open(base + ".codigo.txt", "w") as f:
            f.write("\n".join(palavras) + "\n")
        os.remove(base + ".cnf")
    else:
        reg["resultado"] = "INDEFINIDO"
    return reg


def intervalo(s, n):
    if not s:
        return list(range(n))
    out = []
    for parte in s.split(","):
        a, _, b = parte.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return [i for i in out if i < n]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--q", type=int, required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--R", type=int, required=True)
    ap.add_argument("--M", type=int, required=True)
    ap.add_argument("--smin", type=int)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--perfis", default="")
    ap.add_argument("--prova", action="store_true")
    ap.add_argument("--descartar", action="store_true",
                    help="confere a prova e apaga CNF/LRAT (guarda só tamanho e sha256)")
    ap.add_argument("--solver", default="cadical", choices=["cadical", "kissat"])
    ap.add_argument("--tempo", type=int, default=100000)
    ap.add_argument("-j", type=int, default=os.cpu_count())
    a = ap.parse_args()
    os.makedirs(a.dir, exist_ok=True)
    smin = a.smin if a.smin is not None else proj.fibra_minima(a.q, a.n, a.R, a.M)
    total = len(proj.perfis(a.q, a.n, a.R, a.M, smin))
    idxs = intervalo(a.perfis, total)
    log = os.path.join(a.dir, f"K{a.q}_{a.n}_{a.R}_M{a.M}.jsonl")
    feitos = set()
    if os.path.exists(log):
        for ln in open(log):
            feitos.add(json.loads(ln)["perfil"])
    tarefas = [(a.q, a.n, a.R, a.M, smin, i, a.dir, a.prova, a.solver, a.tempo, a.descartar) for i in idxs if i not in feitos]
    print(f"K_{a.q}({a.n},{a.R}) M={a.M} smin={smin}: {total} perfis, {len(tarefas)} a rodar", flush=True)
    cont = {}
    with ProcessPoolExecutor(a.j) as ex, open(log, "a") as f:
        for reg in ex.map(uma, tarefas):
            f.write(json.dumps(reg) + "\n")
            f.flush()
            cont[reg["resultado"]] = cont.get(reg["resultado"], 0) + 1
            extra = reg.get("lrat_check", "") or ("cobre=" + str(reg.get("cobre", "")))
            print(f"p{reg['perfil']} {reg['resultado']} {reg['tempo_solver_s']}s {extra}", flush=True)
    print("resumo:", cont)


if __name__ == "__main__":
    main()
