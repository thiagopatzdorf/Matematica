#!/usr/bin/env python3
"""Gera os dados que `lratk_refute` lê: CNF de um perfil (encode.py) + prova LRAT aparada.

    python3 tools/exatos/k742/lean/gerar_dados.py --q 7 --M 18 --perfil 64 \
        --saida CoveringLean/K742Sat/dados

Passos (todos determinísticos; os sha256 conferem com `manifesto.json`):
1. CNF por `encode.py` (o sha256 confere com o JSONL de `tools/exatos/k742/certificados/`);
2. CaDiCaL 3.0.1 (`c607304`) `--lrat --binary=false`;
3. `lrat-trim` 0.2.0 (`b30f400`, github.com/arminbiere/lrat-trim) `-a`: apara a prova (passos e
   dicas não usados) e a confere de novo (`s VERIFIED`);
4. remove as linhas de deleção (o `lratk_refute` as ignora).

O LRAT original é apagado; fica só o aparado (≈ 50% do texto, 41% dos passos em média nos 70
perfis de M = 18). Binários: variáveis CADICAL e LRAT_TRIM, ou no PATH.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

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
    ap.add_argument("--q", type=int, required=True)
    ap.add_argument("--M", type=int, required=True)
    ap.add_argument("--perfil", type=int, required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    os.makedirs(a.saida, exist_ok=True)
    base = os.path.join(a.saida, f"K{a.q}_4_2_M{a.M}_p{a.perfil:04d}")
    ps = encode.perfis(a.q, a.M)
    cnf, _, _ = encode.codificar(a.q, a.M, ps[a.perfil])
    with open(base + ".cnf", "w") as f:
        f.write(cnf.dimacs([f"K_{a.q}(4,2) M={a.M} perfil {a.perfil}: {ps[a.perfil]}"]))
    cadical = os.environ.get("CADICAL", "cadical")
    trim = os.environ.get("LRAT_TRIM", "lrat-trim")
    r = subprocess.run([cadical, "-q", base + ".cnf", "--lrat", "--binary=false", base + ".orig.lrat"],
                       capture_output=True, text=True)
    if r.returncode != 20:
        sys.exit(f"CaDiCaL não deu UNSAT (rc={r.returncode})")
    r = subprocess.run([trim, "-a", base + ".cnf", base + ".orig.lrat", base + ".lrat"],
                       capture_output=True, text=True)
    if "s VERIFIED" not in r.stdout:
        sys.exit("lrat-trim não conferiu a prova:\n" + r.stdout[-500:])
    os.remove(base + ".orig.lrat")
    # As linhas de deleção não servem ao `lratk_refute` (o banco nunca apaga): fora.
    with open(base + ".lrat") as f:
        linhas = [ln for ln in f if ln.split(" ", 2)[1:2] != ["d"]]
    with open(base + ".lrat", "w") as f:
        f.writelines(linhas)
    reg = {"q": a.q, "M": a.M, "perfil": a.perfil, "tipos": ["".join(map(str, t)) for t in ps[a.perfil]],
           "sha256.cnf": sha(base + ".cnf"), "bytes.lrat": os.path.getsize(base + ".lrat"),
           "sha256.lrat": sha(base + ".lrat")}
    man = os.path.join(AQUI, "manifesto.json")
    esperado = {}
    if os.path.exists(man):
        esperado = {(e["q"], e["M"], e["perfil"]): e for e in json.load(open(man))}
    e = esperado.get((a.q, a.M, a.perfil))
    if e and (e["sha256.cnf"] != reg["sha256.cnf"] or e["sha256.lrat"] != reg["sha256.lrat"]):
        sys.exit(f"sha256 diferente do manifesto: {reg} vs {e}")
    print(json.dumps(reg))


if __name__ == "__main__":
    main()
