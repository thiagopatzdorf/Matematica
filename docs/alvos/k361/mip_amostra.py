#!/usr/bin/env python3
"""y-SIP de K_3(v,1) como PLI puro (HiGHS e SCIP), medido nas MESMAS sequências dos JSONL do
RoundingSat (tools/exatos/k361/medicoes, 2026-10-04) para comparação pareada, mais M = 64 e 66.

Por que: K361_VIABILIDADE.md recomendou "PLI com relaxação de PL" como o motor que faltou medir
(é o que LMT usaram; SAT/PB estouraram). Aqui só medição, sem prova — um UNSAT do SCIP/HiGHS não
é certificado. Uma linha JSON por (motor, M, y). Anexo do diagnóstico docs/alvos/K3-6-1.md.

Uso (na VM): python3 mip_amostra.py --k361 /opt/Matematica/tools/exatos/k361 --saida /var/tmp/saida
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

K361 = None


def _carregar(k361: str):
    global K361
    K361 = k361
    sys.path.insert(0, k361)


def resolver_highs(v, y, p, tempo):
    import highspy
    import ysip
    W = ysip.palavras(v)
    idx = {w: i for i, w in enumerate(W)}
    n = len(W)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("time_limit", float(tempo))
    h.setOptionValue("threads", 1)
    inf = highspy.kHighsInf
    for _ in range(n):
        h.addVar(0.0, 1.0)
    h.changeColsIntegrality(n, list(range(n)), [highspy.HighsVarType.kInteger] * n)

    def linha(cols, lo, hi):
        h.addRow(lo, hi, len(cols), cols, [1.0] * len(cols))
    for w in W:
        linha([idx[u] for u in ysip.bola(v, w)], 1.0, inf)
    for j in range(3):
        for k in range(3):
            b = float(y[3 * j + k])
            linha([idx[w] for w in W if w[0] == j and w[1] == k], b, b)
    if p > 0:
        for i in range(2, v):
            for a in range(3):
                linha([idx[w] for w in W if w[i] == a], float(p), inf)
    t0 = time.time()
    h.run()
    seg = time.time() - t0
    nome = h.modelStatusToString(h.getModelStatus())
    st = "UNSAT" if nome == "Infeasible" else "SAT" if nome == "Optimal" else "TEMPO" if "ime" in nome else nome
    info = h.getInfo()
    return st, seg, {"nos": int(info.mip_node_count), "status_bruto": nome}


def resolver_scip(v, y, p, tempo):
    import ysip
    st, seg, nos = ysip.scip(v, y, p, tempo)
    return st, seg, {"nos": int(nos)}


def uma(args):
    k361, motor, v, M, y, p, tempo, origem = args
    _carregar(k361)
    f = resolver_highs if motor == "highs" else resolver_scip
    try:
        st, seg, extra = f(v, y, p, tempo)
    except Exception as e:  # noqa: BLE001 — registro do erro vale mais que a quebra do lote
        st, seg, extra = "ERRO", 0.0, {"erro": repr(e)[:300]}
    return {"v": v, "M": M, "y": y, "p": p, "motor": motor, "status": st, "seg": round(seg, 2),
            "tempo_limite": tempo, "origem": origem, **extra}


def pareadas(k361):
    """(M, y, p) dos JSONL do RoundingSat em medicoes/ (comparação pareada)."""
    out = []
    for arq in sorted(glob.glob(os.path.join(k361, "medicoes", "rs_M*.jsonl"))):
        for ln in open(arq):
            if ln.strip():
                r = json.loads(ln)
                out.append((sum(r["y"]), r["y"], r["p"], os.path.basename(arq)))
    return out


def novas(k361, v, M, n, semente, pbase=18):
    import amostra
    seqs = amostra.sequencias(v, M, pbase)
    rnd = random.Random(semente)
    esc = seqs if n >= len(seqs) else rnd.sample(seqs, n)
    return [(M, y, amostra.cota_sufixo(y, pbase, "auto"), f"nova:s{semente}") for y in esc]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k361", default=os.environ.get("K361", "/opt/Matematica/tools/exatos/k361"))
    ap.add_argument("--saida", default=".")
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--tempo", type=int, default=900)
    ap.add_argument("--motores", default="highs,scip")
    ap.add_argument("--novas", default="64,66", help="M extras com 6 sequências novas cada")
    ap.add_argument("--so-controle", action="store_true")
    a = ap.parse_args()
    _carregar(a.k361)
    os.makedirs(a.saida, exist_ok=True)
    motores = a.motores.split(",")
    tarefas = []
    # controle: K_3(5,1) = 27, ∄26 — todas as sequências
    for (M, y, p, o) in novas(a.k361, 5, 26, 10**6, 0, pbase=0):
        for m in motores:
            tarefas.append((a.k361, m, 5, M, y, p, min(a.tempo, 600), "controle:" + o))
    if not a.so_controle:
        itens = pareadas(a.k361)
        for Mx in [int(t) for t in a.novas.split(",") if t]:
            itens += novas(a.k361, 6, Mx, 6, 7)
        itens.sort(key=lambda t: t[0])
        for (M, y, p, o) in itens:
            for m in motores:
                tarefas.append((a.k361, m, 6, M, y, p, a.tempo, o))
    print(f"{len(tarefas)} tarefas, {a.procs} processos, tempo {a.tempo}s", flush=True)
    arq = open(os.path.join(a.saida, "mip.jsonl"), "a")
    t0 = time.time()
    with ProcessPoolExecutor(a.procs) as ex:
        futs = [ex.submit(uma, t) for t in tarefas]
        for f in as_completed(futs):
            r = f.result()
            arq.write(json.dumps(r) + "\n")
            arq.flush()
            print(f"[{time.time()-t0:7.0f}s] {r['motor']:5s} M={r['M']} {r['status']:5s} {r['seg']:8.1f}s nos={r.get('nos')}", flush=True)
    arq.close()


if __name__ == "__main__":
    main()
