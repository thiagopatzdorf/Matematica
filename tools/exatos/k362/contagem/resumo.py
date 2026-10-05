#!/usr/bin/env python3
"""Resumo de uma rodada de `certificar_lp.py`: por (s*, blocos), quantas instâncias, quantas
fecham na raiz do LP, quantas folhas no total, e a lista das que pediram ramificação (ou ficaram
sem certificado) com s*, |U(K)| e blocos. Só biblioteca padrão; não confere nada (isso é do
`verificar.py`), apenas classifica.

  python3 tools/exatos/k362/contagem/resumo.py --q 3 --n 6 --R 2 \
      --certificados tools/exatos/k362/contagem/dados/K3_6_2_M16_certificados.jsonl.gz
"""
import argparse
import gzip
import itertools
import json
from collections import defaultdict


def n_descobertos(q, m, R, K):
    """|U(K)|: pontos de Z_q^m a distância > R de todo ponto de K."""
    return sum(1 for x in itertools.product(range(q), repeat=m)
               if all(sum(a != b for a, b in zip(x, k)) > R for k in K))


def resumir(q, n, R, regs):
    tab = defaultdict(lambda: [0, 0, 0])  # (s, t) -> [instâncias, mortas na raiz, folhas]
    duras = []
    for r in regs:
        chave = (r["s"], tuple(r["t"]))
        nf = len(r["folhas"]) if r["folhas"] else 0
        tab[chave][0] += 1
        tab[chave][1] += nf == 1
        tab[chave][2] += nf
        if nf != 1:
            duras.append({"inst": r["inst"], "s": r["s"], "t": r["t"], "folhas": nf or None,
                          "U": n_descobertos(q, n - 1, R, [tuple(k) for k in r["K"]])})
    return dict(tab), duras


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("q", "n", "R"):
        ap.add_argument("--" + k, type=int, required=True)
    ap.add_argument("--certificados", required=True)
    a = ap.parse_args()
    regs = [json.loads(ln) for ln in gzip.open(a.certificados, "rt")]
    tab, duras = resumir(a.q, a.n, a.R, regs)
    print("s*  blocos    instâncias  raiz  folhas")
    for (s, t), (ni, raiz, nf) in sorted(tab.items()):
        print(f"{s:2d}  {str(t):9s} {ni:10d} {raiz:5d} {nf:7d}")
    print(f"total: {sum(v[0] for v in tab.values())} instâncias, "
          f"{sum(v[1] for v in tab.values())} na raiz, {sum(v[2] for v in tab.values())} folhas")
    for d in duras:
        print(json.dumps(d))


if __name__ == "__main__":
    main()
