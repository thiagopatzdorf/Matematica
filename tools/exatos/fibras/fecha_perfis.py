#!/usr/bin/env python3
"""Confere se um conjunto de JSONL do rodar.py cobre TODOS os perfis de K_q(n, n-2) com M palavras.

Um perfil (multiconjunto de n tipos) conta como fechado se aparece com resultado UNSAT e
`lrat_check` VERIFIED, em qualquer ordem (min/max), ou se TODOS os seus cubos (mesmo L e mesma
ordem) aparecem assim. Também confere que o sha256 de cada CNF bate com o que o codificador gera
hoje, numa amostra (`--amostra-sha N`), e lista o que falta. Sai com código 1 se faltar perfil
ou se houver SAT / INDEFINIDO sem fechamento.

Uso (aceita .jsonl e .jsonl.xz):
  python3 tools/exatos/fibras/fecha_perfis.py --q 7 --n 5 --M 16 tools/exatos/fibras/certificados/K7_5_3_M16.parte-*.jsonl.xz
"""
import argparse
import hashlib
import json
import lzma
import os
import random
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fib_cubos  # noqa: E402
import fib_encode as enc  # noqa: E402


def chave(tipos):
    return tuple(sorted(tipos))


def sha_cnf(q, n, M, k, smin, r):
    ordem = r.get("ordem", "min")
    sem = r.get("sem", "")
    _, ins = enc.instancias(q, n, M, k, smin, ordem=ordem)
    pref = ins[r["inst"]]
    cnf, x, _, ts = enc.codificar(q, n, M, pref, smin, lex="g" not in sem, blocos_h="h" not in sem)
    rot = f"K_{q}({n},{n-2}) M={M} k={k} s_min={smin} inst {r['inst']}: {pref}" + (f" sem ({sem})" if sem else "")
    if r.get("L"):
        cubo = fib_cubos.atribuicoes_coord1(q, M, ts[0], ts[1], smin, r["L"], blocos_h="h" not in sem)[r["cubo_idx"]]
        for u in fib_cubos.unitarias(x, cubo):
            cnf.add(u)
        rot += f" cubo L={r['L']} #{r['cubo_idx']}: {cubo}"
    return hashlib.sha256(cnf.dimacs([rot]).encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--q", type=int, required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--M", type=int, required=True)
    ap.add_argument("--amostra-sha", type=int, default=0)
    ap.add_argument("arquivos", nargs="+")
    a = ap.parse_args()
    k = a.n
    smin = enc.fibra_minima(a.q, a.n, a.n - 2, a.M)
    _, ins = enc.instancias(a.q, a.n, a.M, k, smin)
    todos = {chave("".join(map(str, t)) for t in p) for p in ins}
    fechados = set()
    cubos = defaultdict(set)   # (perfil, ordem, L, inst) -> cubos fechados
    ruins = []
    regs = []
    tempo = tempo_check = bytes_lrat = 0.0
    for arq in a.arquivos:
        # .xz lido direto: o registro de K_7(5,3) M=16 vai em partes comprimidas < 5 MB
        for ln in (lzma.open(arq, "rt") if arq.endswith(".xz") else open(arq)):
            r = json.loads(ln)
            if (r["q"], r["n"], r["M"]) != (a.q, a.n, a.M) or r.get("sem"):
                continue
            ok = r["resultado"] == "UNSAT" and r.get("lrat_check") == "VERIFIED"
            if r["resultado"] == "SAT":
                ruins.append(r)
            if not ok:
                continue
            regs.append(r)
            tempo += r["tempo_solver_s"]
            tempo_check += r.get("tempo_check_s", 0)
            bytes_lrat += r.get("bytes.lrat", 0)
            if r.get("L"):
                cubos[(chave(r["tipos"]), r.get("ordem", "min"), r["L"], r["inst"])].add(r["cubo_idx"])
            else:
                fechados.add(chave(r["tipos"]))
    for (perfil, ordem, L, inst), feitos in cubos.items():
        _, insx = enc.instancias(a.q, a.n, a.M, k, smin, ordem=ordem)
        ts = insx[inst]
        n_c = len(fib_cubos.atribuicoes_coord1(a.q, a.M, ts[0], ts[1], smin, L))
        if feitos >= set(range(n_c)):
            fechados.add(perfil)
    falta = todos - fechados
    print(f"K_{a.q}({a.n},{a.n-2}) M={a.M}: {len(todos)} perfis, {len(fechados & todos)} fechados "
          f"(UNSAT + LRAT conferido), {len(falta)} faltando, {len(ruins)} SAT")
    print(f"soma solver {tempo:.0f} s, soma lrat-check {tempo_check:.0f} s, LRAT {bytes_lrat / 1e9:.1f} GB")
    if a.amostra_sha:
        rng = random.Random(0)
        amostra = rng.sample(regs, min(a.amostra_sha, len(regs)))
        bate = sum(sha_cnf(a.q, a.n, a.M, k, smin, r) == r["sha256.cnf"] for r in amostra)
        print(f"sha256 das CNFs regeneradas: {bate}/{len(amostra)} batem")
        if bate != len(amostra):
            sys.exit(1)
    for p in sorted(falta)[:20]:
        print("falta:", " | ".join(p))
    for r in ruins[:5]:
        print("SAT:", r["tipos"], r.get("codigo"), r.get("cobre"))
    sys.exit(1 if falta or ruins else 0)


if __name__ == "__main__":
    main()
