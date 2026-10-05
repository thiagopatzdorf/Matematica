#!/usr/bin/env python3
"""Resíduo do censo: as instâncias que nenhum degrau da fatia 0 (P1, T, F) mata, levadas aos
degraus das fatias 1 e 2 (`todas_fatias.py`), na ordem X (complemento de B_2(F)), XB (com os
blocos t) e XBF (com as fibras), cada um com certificado conferido em inteiros. O que sobrar é
testado no LP da instância inteira (`inviavel`), só como diagnóstico (sem certificado aqui: o
certificado de Farkas dessas instâncias já está em contagem/dados).

  python3 tools/exatos/k362/estrutura/residuo.py --censo censo_K.jsonl --saida residuo.jsonl
"""
import argparse
import gzip
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import todas_fatias as tf  # noqa: E402
from censo import DADOS, degrau_que_mata  # noqa: E402

DEGRAUS = (("X", {}), ("XB", {"blocos": True}), ("XBF", {"blocos": True, "fibras": True}))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--censo", required=True)
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    ins = {M: json.loads(gzip.open(os.path.join(DADOS, f"K3_6_2_M{M}_instancias.json.gz")).read())
           for M in (15, 16)}
    feitos = set()
    if os.path.exists(a.saida):
        feitos = {(r["M"], r["inst"]) for r in map(json.loads, open(a.saida))}
    with open(a.saida, "a") as out:
        for ln in open(a.censo):
            r = json.loads(ln)
            for m, idx in r["inst"].items():
                M = int(m)
                if degrau_que_mata(r, M):
                    continue
                for i in idx:
                    if (M, i) in feitos:
                        continue
                    s, K, t = ins[M][i]
                    reg = {"M": M, "inst": i, "k": r["k"], "s": s, "t": t, "mata": None}
                    for nome, kw in DEGRAUS:
                        v, cert = tf.cert_complemento(K, t, M, **kw)
                        reg["folga_" + nome] = round(v, 6)
                        if cert is not None:
                            reg["mata"] = nome
                            break
                    if reg["mata"] is None:
                        reg["lp_inteiro_inviavel"] = tf.inviavel(K, s, t)
                    out.write(json.dumps(reg, separators=(",", ":")) + "\n")
                    out.flush()


if __name__ == "__main__":
    main()
