"""Amostragem de y-SIPs de K_3(v,1): sorteia sequências, resolve com CaDiCaL e mede o tempo.

    python3 amostra.py --v 6 --M 72 --p 22 --n 30 --tempo 600 --semente 1 --saida m72.jsonl
    python3 amostra.py --v 5 --M 26 --todas --lrat --saida k5.jsonl     # validação: todas, com prova

Uma linha JSON por sequência: y, status (UNSAT/SAT/TEMPO), segundos de solver, e, com --lrat,
o veredito do lrat-check. Variáveis de ambiente: CADICAL, LRAT_CHECK, SISTEMA (binários).
"""
from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import ysip  # noqa: E402


def binario(var: str, nome: str) -> str:
    p = os.environ.get(var) or shutil.which(nome)
    if not p:
        sys.exit(f"falta o binário {nome} (defina {var})")
    return p


def sistema_bin() -> str:
    """Compila sistema.c sob demanda (cache ao lado, fora do git)."""
    if os.environ.get("SISTEMA"):
        return os.environ["SISTEMA"]
    destino = os.path.join(tempfile.gettempdir(), "k361_sistema")
    fonte = os.path.join(AQUI, "sistema.c")
    if not os.path.exists(destino) or os.path.getmtime(destino) < os.path.getmtime(fonte):
        subprocess.run(["cc", "-O2", "-o", destino, fonte], check=True)
    return destino


def sequencias(v: int, M: int, p: int) -> list[list[int]]:
    out = subprocess.run([sistema_bin(), str(v), str(M), str(p), str(p)],
                         capture_output=True, text=True, check=True).stdout
    return [list(map(int, ln.split())) for ln in out.splitlines() if ln and not ln.startswith("#")]


def resolver_cpsat(v: int, y: list[int], p: int, tempo: int) -> dict:
    st, seg = ysip.cpsat(v, y, p, tempo)
    return {"v": v, "y": y, "p": p, "status": "TEMPO" if st == "DESCONHECIDO" else st,
            "seg": round(seg, 2), "motor": "cpsat"}


def resolver(v: int, y: list[int], p: int, tempo: int, lrat: bool, pasta: str) -> dict:
    nv, cls = ysip.cnf_sb(v, y, p)
    base = os.path.join(pasta, "_".join(map(str, y)))
    ysip.escrever_dimacs(base + ".cnf", nv, cls)
    cmd = [binario("CADICAL", "cadical"), "-q", "-t", str(tempo), base + ".cnf"]
    if lrat:
        cmd[2:2] = ["--lrat", "--binary=false"]  # lrat-check só lê LRAT em texto
        cmd.append(base + ".lrat")
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    seg = time.time() - t0
    st = {10: "SAT", 20: "UNSAT"}.get(r.returncode, "TEMPO")
    reg = {"v": v, "y": y, "p": p, "status": st, "seg": round(seg, 2), "vars": nv, "clausulas": len(cls)}
    if lrat and st == "UNSAT":
        t1 = time.time()
        c = subprocess.run([binario("LRAT_CHECK", "lrat-check"), base + ".cnf", base + ".lrat"],
                           capture_output=True, text=True)
        # "c NOT VERIFIED" também contém "VERIFIED": compara a linha inteira
        ok = any(ln.strip() in ("c VERIFIED", "s VERIFIED") for ln in c.stdout.splitlines())
        reg["lrat_check"] = "VERIFIED" if ok else "FALHOU: " + c.stdout[-200:]
        reg["lrat_seg"] = round(time.time() - t1, 2)
        reg["lrat_bytes"] = os.path.getsize(base + ".lrat")
    for ext in (".cnf", ".lrat"):
        if os.path.exists(base + ext):
            os.remove(base + ext)
    return reg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--v", type=int, default=6)
    ap.add_argument("--M", type=int, required=True)
    ap.add_argument("--p", type=int, default=0, help="cota de fibra (linhas, colunas e sufixo)")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--todas", action="store_true")
    ap.add_argument("--tempo", type=int, default=600)
    ap.add_argument("--semente", type=int, default=1)
    ap.add_argument("--lrat", action="store_true")
    ap.add_argument("--motor", choices=["cadical", "cpsat"], default="cadical")
    ap.add_argument("--procs", type=int, default=1)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    seqs = sequencias(a.v, a.M, a.p)
    print(f"{len(seqs)} sequências (v={a.v}, M={a.M}, p={a.p})", file=sys.stderr)
    alvo = seqs if a.todas else random.Random(a.semente).sample(seqs, min(a.n, len(seqs)))
    with tempfile.TemporaryDirectory() as pasta, open(a.saida, "a") as f, \
            ThreadPoolExecutor(a.procs) as ex:
        def um(y):
            if a.motor == "cpsat":
                return resolver_cpsat(a.v, y, a.p, a.tempo)
            return resolver(a.v, y, a.p, a.tempo, a.lrat, pasta)
        for reg in ex.map(um, alvo):
            reg["total_seqs"] = len(seqs)
            f.write(json.dumps(reg) + "\n")
            f.flush()
            print(json.dumps(reg), file=sys.stderr)


if __name__ == "__main__":
    main()
