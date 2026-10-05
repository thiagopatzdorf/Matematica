#!/usr/bin/env python3
"""Prepara os dados de uma refutação SEM a quebra (d)–(f) para os comandos `lratk_data`,
`lratk_steps` e `lratk_final` (CoveringLean/LratKData.lean), divididos em módulos.

    python3 tools/exatos/k742/lean/preparar_semquebra.py --perfil 55 \
        --saida CoveringLean/K742Sat/dados [--dicas-por-modulo 2000000] [--bloco 100]

Passos (determinísticos):
1. CNF por `encode.codificar(7, 18, perfil, quebra=False)` (`encode.py --sem-quebra`);
2. CaDiCaL 3.0.1 `--lrat --binary=false`;
3. `lrat-trim` 0.2.0 `-a` (apara e confere: `s VERIFIED`);
4. renumera as cláusulas derivadas para `n+1, n+2, …` (até a primeira cláusula vazia) e escreve,
   em `<saida>/s<perfil>/`:
   * `f.cnf`  : o DIMACS da CNF;
   * `c.txt`  : as cláusulas derivadas, uma por linha (literais DIMACS, sem o 0 final);
   * `h<m>.txt`: as dicas renumeradas dos passos do módulo `m` (primeira linha: `j0 k0`, o
     índice do primeiro bloco e a chave do primeiro passo);
   * `meta.txt`: `n K bloco nblocos nmodulos`.

Nada disso precisa de confiança: o kernel confere a CNF contra `K742Cnf.cnfSemQuebra` e cada
passo RUP. Imprime um JSON com os sha256 (da CNF, do LRAT aparado e de cada arquivo gerado).
Binários: variáveis CADICAL e LRAT_TRIM, ou no PATH.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
import encode  # noqa: E402


def sha(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--perfil", type=int, required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--dicas-por-modulo", type=int, default=2_000_000)
    ap.add_argument("--bloco", type=int, default=100)
    ap.add_argument("--manter-lrat", action="store_true")
    a = ap.parse_args()
    q, M = 7, 18
    d = os.path.join(a.saida, f"s{a.perfil:04d}")
    os.makedirs(d, exist_ok=True)
    ps = encode.perfis(q, M)
    cnf, _, _ = encode.codificar(q, M, ps[a.perfil], quebra=False)
    fcnf = os.path.join(d, "f.cnf")
    with open(fcnf, "w") as f:
        f.write(cnf.dimacs([f"K_{q}(4,2) M={M} perfil {a.perfil} sem quebra: {ps[a.perfil]}"]))
    cadical = os.environ.get("CADICAL", "cadical")
    trim = os.environ.get("LRAT_TRIM", "lrat-trim")
    orig = os.path.join(d, "orig.lrat")
    lrat = os.path.join(d, "trim.lrat")
    t0 = time.time()
    r = subprocess.run([cadical, "-q", fcnf, "--lrat", "--binary=false", orig], capture_output=True, text=True)
    if r.returncode != 20:
        sys.exit(f"CaDiCaL não deu UNSAT (rc={r.returncode})")
    t1 = time.time()
    r = subprocess.run([trim, "-a", fcnf, orig, lrat], capture_output=True, text=True)
    if "s VERIFIED" not in r.stdout:
        sys.exit("lrat-trim não conferiu a prova:\n" + r.stdout[-500:])
    os.remove(orig)
    t2 = time.time()
    # número de cláusulas da CNF
    n = 0
    with open(fcnf) as f:
        for ln in f:
            if ln and ln[0] not in "cp" and ln.strip():
                n += 1
    ren = {}
    k = n
    clauses = []
    hints = []
    vazio = False
    with open(lrat) as f:
        for ln in f:
            xs = ln.split()
            if len(xs) < 2 or xs[1] == "d":
                continue
            xs = list(map(int, xs))
            i0 = xs.index(0, 1)
            c = xs[1:i0]
            h = xs[i0 + 1:-1]
            if any(x < 0 for x in h):
                sys.exit("dica negativa (RAT)")
            k += 1
            ren[xs[0]] = k
            clauses.append(c)
            hints.append([x if x <= n else ren[x] for x in h])
            if not c:
                vazio = True
                break
    if not vazio:
        sys.exit("a prova não termina na cláusula vazia")
    if not a.manter_lrat:
        sha_lrat = sha(lrat)
        os.remove(lrat)
    else:
        sha_lrat = sha(lrat)
    K = k
    with open(os.path.join(d, "c.txt"), "w") as f:
        for c in clauses:
            f.write(" ".join(map(str, c)) + "\n")
    B = a.bloco
    nb = (len(hints) + B - 1) // B
    # módulos: blocos consecutivos até ~dicas-por-modulo dicas
    mods = []
    cur, acc = [], 0
    for j in range(nb):
        s = sum(len(h) for h in hints[j * B:(j + 1) * B])
        if cur and acc + s > a.dicas_por_modulo:
            mods.append(cur)
            cur, acc = [], 0
        cur.append(j)
        acc += s
    if cur:
        mods.append(cur)
    info = []
    for m, js in enumerate(mods):
        j0 = js[0]
        k0 = n + 1 + j0 * B
        passos = hints[j0 * B:(js[-1] + 1) * B]
        with open(os.path.join(d, f"h{m}.txt"), "w") as f:
            f.write(f"{j0} {k0}\n")
            for h in passos:
                f.write(" ".join(map(str, h)) + "\n")
        info.append({"modulo": m, "blocos": len(js), "j0": j0, "dicas": sum(len(h) for h in passos)})
    with open(os.path.join(d, "meta.txt"), "w") as f:
        f.write(f"{n} {K} {B} {nb} {len(mods)}\n")
    reg = {"q": q, "M": M, "perfil": a.perfil, "quebra": False,
           "tipos": ["".join(map(str, t)) for t in ps[a.perfil]],
           "n": n, "K": K, "passos": len(hints), "dicas": sum(map(len, hints)),
           "bloco": B, "nblocos": nb, "modulos": info,
           "sha256.cnf": sha(fcnf), "sha256.lrat_trim": sha_lrat,
           "sha256.arquivos": {fn: sha(os.path.join(d, fn)) for fn in sorted(os.listdir(d))},
           "cadical_s": round(t1 - t0, 1), "trim_s": round(t2 - t1, 1)}
    print(json.dumps(reg))


if __name__ == "__main__":
    main()
