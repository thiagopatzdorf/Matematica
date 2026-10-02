#!/usr/bin/env python3
"""Gerador guloso mínimo, padrão do record_loop para células PEQUENAS.

Não é para bater recorde: serve para o loop ter um gerador determinístico
que roda em segundos em q^n pequeno (o teste usa K_2(4,1)). A cada passo
escolhe, entre as palavras ainda descobertas, a que cobre mais descobertas;
empate desfeito pela ordem lexicográfica embaralhada com a semente.

Uso: gen_greedy.py q n R saida.txt [--seed S]
"""
from __future__ import annotations

import argparse
import itertools
import random
import sys
from pathlib import Path


def bola(w, q, R):
    n = len(w)
    out = {w}
    fronteira = {w}
    for _ in range(R):
        prox = set()
        for v in fronteira:
            for j in range(n):
                for s in range(q):
                    if s != v[j]:
                        u = v[:j] + (s,) + v[j + 1:]
                        if u not in out:
                            prox.add(u)
        out |= prox
        fronteira = prox
    return out


def guloso(q: int, n: int, R: int, seed: int = 0) -> list[tuple[int, ...]]:
    if q**n > 200_000:
        raise SystemExit(f"gen_greedy é só para células pequenas (q^n = {q**n})")
    todas = list(itertools.product(range(q), repeat=n))
    random.Random(seed).shuffle(todas)
    bolas = {w: bola(w, q, R) for w in todas}
    descobertas = set(todas)
    codigo = []
    while descobertas:
        w = max(todas, key=lambda v: len(bolas[v] & descobertas))
        codigo.append(w)
        descobertas -= bolas[w]
    return codigo


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("q", type=int)
    ap.add_argument("n", type=int)
    ap.add_argument("R", type=int)
    ap.add_argument("saida", type=Path)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    cod = guloso(a.q, a.n, a.R, a.seed)
    sep = "" if a.q <= 10 else " "
    a.saida.write_text("\n".join(sep.join(str(x) for x in w) for w in sorted(cod)) + "\n")
    print(f"{len(cod)} palavras -> {a.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
