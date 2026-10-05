#!/usr/bin/env python3
"""Censo dos subconjuntos "fatia 0" sobre a lista inteira de instâncias da fatia mínima.

Para cada instância, roda o RoundingSat em dois subconjuntos LITERAIS das linhas do OPB dela
(se um subconjunto é inviável, a instância é inviável, e a prova do subconjunto confere no
VeriPB contra ele):

  A  fixações da fatia 0 + cobertura dos pontos com x_0 = 0 + tamanho + blocos
     (é o lema da projeção: U(K) não cabe em M - s* bolas de raio 1 de Z_3^5)
  B  A + fibras (as bolas têm contagem de símbolo prescrita por coordenada)

Instância que sobrevive aos dois precisa da fórmula inteira.

  ROUNDINGSAT=... [VERIPB=...] python3 censo_projecao.py --instancias i15.json \
      --saida censo.jsonl [--so 0-99] [--tempo-b 60]
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import autopsia as au  # noqa: E402

COB0 = {k for k, c in enumerate(au.PTS) if c[0] == 0}  # linhas de cobertura da fatia 0
BASE = set(range(729, 975))  # tamanho, 243 fixações, 2 blocos (q = 3)


def subconjuntos(txt):
    n = len(txt.splitlines()) - 1
    a = COB0 | BASE
    return {"A": a, "B": a | set(range(975, n))}


def roda(sub, tempo, rs, vp):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "s.opb")
        open(p, "w").write(sub)
        cmd = [rs, p, "--print-sol=0", f"--time-limit={tempo}"] + \
            ([f"--proof-log={d}/s"] if vp else [])
        t0 = time.time()
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        dt = round(time.time() - t0, 3)
        st = [ln[2:].strip() for ln in out.splitlines() if ln.startswith("s ")]
        st = st[0] if st else "UNKNOWN"
        ver = None
        if vp and st == "UNSATISFIABLE":
            prova = next(os.path.join(d, f) for f in os.listdir(d) if f.startswith("s") and f != "s.opb")
            c = subprocess.run([vp, p, prova], capture_output=True, text=True).stdout
            ver = "s VERIFIED UNSATISFIABLE" in c
    return st, dt, ver


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--instancias", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--so", default="")
    ap.add_argument("--tempo-b", type=int, default=60)
    a = ap.parse_args()
    rs, vp = os.environ["ROUNDINGSAT"], os.environ.get("VERIPB")
    lista = json.load(open(a.instancias))
    idxs = range(len(lista))
    if a.so:
        idxs = [i for p in a.so.split(",") for i in
                range(int(p.partition("-")[0]), int(p.partition("-")[2] or p.partition("-")[0]) + 1)]
    feitos = {json.loads(ln)["idx"] for ln in open(a.saida)} if os.path.exists(a.saida) else set()
    with open(a.saida, "a") as f:
        for i in idxs:
            if i in feitos:
                continue
            inst = au.instancia(lista, i)
            txt, h = au.opb(inst)
            reg = {"idx": i, "s": inst[0], "sha256_opb": h}
            for nome, linhas in subconjuntos(txt).items():
                st, dt, ver = roda(au.opb_subconjunto(txt, linhas), 600 if nome == "A" else a.tempo_b,
                                   rs, vp)
                reg[nome] = [st, dt] + ([ver] if ver is not None else [])
                if st == "UNSATISFIABLE":
                    break
            f.write(json.dumps(reg) + "\n")
            f.flush()


if __name__ == "__main__":
    main()
