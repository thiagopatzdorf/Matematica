#!/usr/bin/env python3
"""Expande uma base de classes laterais (+ remendo) numa lista de palavras.

Base: H = [I_r | A] (r linhas de n dígitos, como o argumento H= do coset_sa/hsearch) e uma
lista de síndromes (inteiros; dígito i = linha i de H, base q -- a convenção do kit). A classe
lateral de síndrome s é {x : H x = s}; com H sistemática, x = (s - A y, y) para y em F_q^k.

Saída: uma palavra por linha (dígito i = coordenada i), sem duplicatas, na ordem: classes
laterais, depois o remendo (palavras já no formato de texto). Falha se o remendo repetir uma
palavra da base ou se H não for sistemática.

Uso:
  expand_cosets.py q n "H" sindromes.txt [remendo.txt] > codigo.txt
"""
from __future__ import annotations

import itertools
import sys


def expand(q: int, n: int, H: list[str], syn: list[int]) -> list[str]:
    r = len(H)
    k = n - r
    rows = [[int(c) for c in h] for h in H]
    for i in range(r):
        for j in range(r):
            if rows[i][j] != (1 if i == j else 0):
                raise SystemExit("H precisa ser sistemática [I_r | A]")
    A = [row[r:] for row in rows]
    out = []
    for s in syn:
        sd = [(s // q**i) % q for i in range(r)]
        for y in itertools.product(range(q), repeat=k):
            x = [(sd[i] - sum(A[i][l] * y[l] for l in range(k))) % q for i in range(r)] + list(y)
            out.append("".join(map(str, x)))
    return out


def main() -> None:
    if len(sys.argv) < 5:
        raise SystemExit(__doc__)
    q, n = int(sys.argv[1]), int(sys.argv[2])
    H = sys.argv[3].split()
    syn = [int(t) for t in open(sys.argv[4]).read().split()]
    if len(set(syn)) != len(syn):
        raise SystemExit("síndrome repetida")
    words = expand(q, n, H, syn)
    if len(sys.argv) > 5:
        patch = [w.strip() for w in open(sys.argv[5]) if w.strip()]
        words += patch
    if len(set(words)) != len(words):
        raise SystemExit("palavra repetida entre base e remendo")
    sys.stdout.write("\n".join(words) + "\n")


if __name__ == "__main__":
    main()
