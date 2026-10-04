"""Amostragem de y-SIPs de K_3(v,1): sorteia sequências, resolve e mede o tempo.

    python3 amostra.py --v 6 --M 72 --p 22 --n 30 --tempo 600 --semente 1 --saida m72.jsonl
    python3 amostra.py --v 5 --M 26 --todas --lrat --saida k5.jsonl     # validação: todas, com prova

Uma linha JSON por sequência: y, status (UNSAT/SAT/TEMPO), segundos de solver, e, com --lrat,
o veredito do lrat-check. Motores: cadical (LRAT), kissat, roundingsat (log VeriPB com --lrat).
Variáveis de ambiente: CADICAL, KISSAT, ROUNDINGSAT, LRAT_CHECK, SISTEMA (binários).
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


def cota_sufixo(y: list[int], p: int, modo: str) -> int:
    """Cota de fibra das coordenadas 2..v-1 no y-SIP.

    "igual": a mesma p do sistema (como LMT, que usa p = 20 ou 22 vindas de computação).
    "auto": max(menor linha, menor coluna). Vale sem computação nenhuma: escolha a coordenada
    0 como a que tem a menor fibra do código e a 1 como a de menor fibra entre as outras cinco;
    então toda fibra das coordenadas 2..v-1 tem pelo menos a menor fibra da coordenada 1, e o
    grupo de ordem 72 só permuta/transpõe linhas e colunas (ver README).
    """
    if modo == "igual":
        return p
    linhas = [sum(y[3 * j:3 * j + 3]) for j in range(3)]
    colunas = [y[k] + y[3 + k] + y[6 + k] for k in range(3)]
    return max(p, max(min(linhas), min(colunas)))


def resolver_rs(v: int, y: list[int], p: int, tempo: int, pasta: str, prova: bool) -> dict:
    """RoundingSat (planos de corte): contagens como restrições lineares nativas.

    Com ``prova``, grava o log VeriPB e guarda tamanho (a conferência é do VeriPB, fora daqui).
    """
    base = os.path.join(pasta, "rs_" + "_".join(map(str, y)))
    with open(base + ".opb", "w") as f:
        f.write(ysip.opb(v, y, p))
    cmd = [binario("ROUNDINGSAT", "roundingsat"), f"--time-limit={tempo}", base + ".opb"]
    if prova:
        cmd.insert(1, f"--proof-log={base}.proof")
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    seg = time.time() - t0
    linhas = r.stdout.splitlines()
    st = "UNSAT" if "s UNSATISFIABLE" in linhas else "SAT" if "s SATISFIABLE" in linhas else "TEMPO"
    reg = {"v": v, "y": y, "p": p, "motor": "roundingsat", "status": st, "seg": round(seg, 2)}
    for ln in linhas:
        if ln.startswith("c conflicts "):
            reg["conflitos"] = int(ln.split()[2])
    for ext in (".opb", ".proof", ".formula"):
        if os.path.exists(base + ext):
            if ext == ".proof":
                reg["prova_bytes"] = os.path.getsize(base + ext)
            os.remove(base + ext)
    return reg


def resolver(v: int, y: list[int], p: int, tempo: int, lrat: bool, pasta: str,
             motor: str = "cadical") -> dict:
    nv, cls = ysip.cnf_sb(v, y, p)
    base = os.path.join(pasta, "_".join(map(str, y)))
    ysip.escrever_dimacs(base + ".cnf", nv, cls)
    cmd = [binario("CADICAL", "cadical"), "-q", "-t", str(tempo), base + ".cnf"]
    if motor == "kissat":  # segunda opinião, sem prova
        cmd = [binario("KISSAT", "kissat"), "-q", f"--time={tempo}", base + ".cnf"]
    elif lrat:
        cmd[2:2] = ["--lrat", "--binary=false"]  # lrat-check só lê LRAT em texto
        cmd.append(base + ".lrat")
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    seg = time.time() - t0
    st = {10: "SAT", 20: "UNSAT"}.get(r.returncode, "TEMPO")
    reg = {"v": v, "y": y, "p": p, "motor": motor, "status": st, "seg": round(seg, 2), "vars": nv, "clausulas": len(cls)}
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
    ap.add_argument("--sufixo", choices=["auto", "igual"], default="auto")
    ap.add_argument("--motor", choices=["cadical", "kissat", "roundingsat"], default="cadical")
    ap.add_argument("--procs", type=int, default=1)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    seqs = sequencias(a.v, a.M, a.p)
    print(f"{len(seqs)} sequências (v={a.v}, M={a.M}, p={a.p})", file=sys.stderr)
    alvo = seqs if a.todas else random.Random(a.semente).sample(seqs, min(a.n, len(seqs)))
    with tempfile.TemporaryDirectory() as pasta, open(a.saida, "a") as f, \
            ThreadPoolExecutor(a.procs) as ex:
        def um(y):
            ps = cota_sufixo(y, a.p, a.sufixo)
            if a.motor == "roundingsat":
                return resolver_rs(a.v, y, ps, a.tempo, pasta, a.lrat)
            return resolver(a.v, y, ps, a.tempo, a.lrat, pasta, a.motor)
        for reg in ex.map(um, alvo):
            reg["total_seqs"] = len(seqs)
            f.write(json.dumps(reg) + "\n")
            f.flush()
            print(json.dumps(reg), file=sys.stderr)


if __name__ == "__main__":
    main()
