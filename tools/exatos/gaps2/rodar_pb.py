#!/usr/bin/env python3
"""Roda as instâncias da fatia mínima (`fatia.py`) como PB no RoundingSat, com prova VeriPB.

Para cada instância: gera o OPB (`fatia_pb.py`), roda `roundingsat --proof-log`, confere a
prova com `veripb` e grava uma linha JSON (resultado, tempos, sha256 do OPB e da prova).
Instância SAT: o código é lido, conferido em todo Z_q^n e gravado (contraexemplo!).

  # 1) lista de instâncias (precisa de numpy; pode rodar noutra máquina)
  python3 tools/exatos/gaps2/rodar_pb.py --q 3 --n 6 --R 2 --M 15 --listar inst.json
  # 2) roda (só stdlib + binários)
  ROUNDINGSAT=... VERIPB=... python3 tools/exatos/gaps2/rodar_pb.py --q 3 --n 6 --R 2 --M 15 \
      --instancias inst.json --dir saida -j 8 [--descartar]
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


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def binario(var, nome):
    p = os.environ.get(var) or shutil.which(nome)
    if not p:
        raise SystemExit(f"{nome} não encontrado (defina {var})")
    return p


def uma(args):
    import fatia_pb
    q, n, R, M, idx, inst, d, tempo, descartar = args
    inst = (inst[0], tuple(tuple(k) for k in inst[1]), tuple(inst[2]))
    txt, var = fatia_pb.opb(q, n, R, M, inst)
    base = os.path.join(d, f"K{q}_{n}_{R}_M{M}_i{idx:06d}")
    with open(base + ".opb", "w") as f:
        f.write(txt)
    reg = {"q": q, "n": n, "R": R, "M": M, "inst": idx, "s": inst[0], "blocos": list(inst[2]),
           "config": ["".join(map(str, k)) for k in inst[1]]}
    t0 = time.time()
    r = subprocess.run(["timeout", str(tempo), binario("ROUNDINGSAT", "roundingsat"), base + ".opb",
                        f"--proof-log={base}", "--print-sol=1"], capture_output=True, text=True)
    reg["tempo_solver_s"] = round(time.time() - t0, 3)
    st = [ln[2:].strip() for ln in r.stdout.splitlines() if ln.startswith("s ")]
    reg["resultado"] = st[0] if st else "INDEFINIDO"
    prova = base + ".pbp"
    if os.path.exists(base) and not os.path.exists(prova):
        os.replace(base, prova)
    if reg["resultado"] == "UNSATISFIABLE":
        t1 = time.time()
        c = subprocess.run([binario("VERIPB", "veripb"), base + ".opb", prova],
                           capture_output=True, text=True)
        ok = "s VERIFIED UNSATISFIABLE" in c.stdout
        reg["veripb"] = "VERIFIED" if ok else "FALHOU: " + (c.stdout + c.stderr)[-300:]
        reg["tempo_check_s"] = round(time.time() - t1, 3)
        for ext, p in ((".opb", base + ".opb"), (".pbp", prova)):
            reg["bytes" + ext] = os.path.getsize(p)
            reg["sha256" + ext] = sha(p)
            if descartar:
                os.remove(p)
            else:
                with open(p, "rb") as fi, gzip.open(p + ".gz", "wb", 6) as fo:
                    shutil.copyfileobj(fi, fo)
                os.remove(p)
    else:
        if reg["resultado"] == "SATISFIABLE":
            inv = {v: c for c, v in var.items()}
            vs = [int(t[1:]) for ln in r.stdout.splitlines() if ln.startswith("v ")
                  for t in ln[2:].split() if t.startswith("x")]
            cod = [inv[v] for v in vs]
            reg["codigo"] = ["".join(map(str, c)) for c in cod]
            reg["cobre"] = all(any(sum(a != b for a, b in zip(x, c)) <= R for c in cod)
                               for x in itertools.product(range(q), repeat=n))
        for p in (base + ".opb", prova):
            if os.path.exists(p):
                os.remove(p)
    return reg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("q", "n", "R", "M"):
        ap.add_argument("--" + k, type=int, required=True)
    ap.add_argument("--listar")
    ap.add_argument("--instancias")
    ap.add_argument("--dir")
    ap.add_argument("--so", default="", help="índices a rodar, ex.: 0-99,150")
    ap.add_argument("--tempo", type=int, default=100000)
    ap.add_argument("--descartar", action="store_true")
    ap.add_argument("-j", type=int, default=os.cpu_count())
    a = ap.parse_args()
    if a.listar:
        import fatia
        ins = fatia.instancias(a.q, a.n, a.R, a.M)
        json.dump([[s, [list(k) for k in K], list(t)] for s, K, t in ins], open(a.listar, "w"))
        print(f"{len(ins)} instâncias -> {a.listar}")
        return
    ins = json.load(open(a.instancias))
    idxs = list(range(len(ins)))
    if a.so:
        idxs = []
        for parte in a.so.split(","):
            x, _, y = parte.partition("-")
            idxs += list(range(int(x), int(y or x) + 1))
    os.makedirs(a.dir, exist_ok=True)
    log = os.path.join(a.dir, f"K{a.q}_{a.n}_{a.R}_M{a.M}.jsonl")
    feitos = set()
    if os.path.exists(log):
        feitos = {json.loads(ln)["inst"] for ln in open(log)}
    tarefas = [(a.q, a.n, a.R, a.M, i, ins[i], a.dir, a.tempo, a.descartar)
               for i in idxs if i not in feitos]
    print(f"{len(ins)} instâncias, {len(tarefas)} a rodar", flush=True)
    cont = {}
    with ProcessPoolExecutor(a.j) as ex, open(log, "a") as f:
        for reg in ex.map(uma, tarefas, chunksize=1):
            f.write(json.dumps(reg) + "\n")
            f.flush()
            chave = reg["resultado"] + ("/" + reg["veripb"][:8] if "veripb" in reg else "")
            cont[chave] = cont.get(chave, 0) + 1
            print(reg["inst"], chave, reg["tempo_solver_s"], flush=True)
    print("resumo:", cont)


if __name__ == "__main__":
    main()
