#!/usr/bin/env python3
"""Classes laterais de um código linear q-ário: expandir em palavras e refinar (subir de nível).

Convenção (a do kit, scripts/search/kit.h): H tem r linhas de n dígitos; a síndrome de x é
H x, gravada como inteiro com o dígito i igual à linha i (base q). A classe lateral de
síndrome s é {x : H x = s}. H pode ser qualquer matriz de posto r (q primo): a expansão
resolve H x = s por eliminação gaussiana.

Subcomandos
  expand q n "H" sindromes.txt [remendo.txt] > codigo.txt
      Lista as palavras das classes laterais (uma por linha, dígito i = coordenada i) e,
      se dado, o remendo. Falha se houver palavra repetida.
  lift q n "H" sindromes.txt j > novo
      Refina para o subcódigo {x : x_j = 0} acrescentando a linha e_j a H. Cada classe
      lateral vira q classes do subcódigo (novo dígito r = x_j = 0..q-1). Imprime na
      1a linha H'="..." e depois as síndromes refinadas. POR QUE: uma base de t classes de
      [n,k] é a mesma base de t*q classes de [n,k-1]; nesse nível mais fino o coset_sa pode
      trocar classes uma a uma e fechar as órfãs com classes de custo q^(k-1), não q^k.
"""
from __future__ import annotations

import itertools
import sys


def parse_H(q: int, n: int, Hs: str) -> list[list[int]]:
    H = [[int(c) % q for c in h] for h in Hs.split()]
    if any(len(h) != n for h in H):
        raise SystemExit("linha de H com comprimento diferente de n")
    return H


def solver(q: int, n: int, H: list[list[int]]):
    """Devolve (pivots, livres, f) com f(s_digits, y) -> x tal que H x = s."""
    r = len(H)
    M = [row[:] + [1 if i == j else 0 for j in range(r)] for i, row in enumerate(H)]  # [H | I]
    pivots = []
    row = 0
    for col in range(n):
        p = next((i for i in range(row, r) if M[i][col]), None)
        if p is None:
            continue
        M[row], M[p] = M[p], M[row]
        inv = pow(M[row][col], q - 2, q)
        M[row] = [(v * inv) % q for v in M[row]]
        for i in range(r):
            if i != row and M[i][col]:
                f = M[i][col]
                M[i] = [(a - f * b) % q for a, b in zip(M[i], M[row])]
        pivots.append(col)
        row += 1
        if row == r:
            break
    if row != r:
        raise SystemExit("H não tem posto cheio")
    free = [c for c in range(n) if c not in pivots]
    E = [m[n:] for m in M]      # E H = forma reduzida
    Hr = [m[:n] for m in M]

    def f(sd: list[int], y: tuple[int, ...]) -> list[int]:
        es = [sum(E[i][l] * sd[l] for l in range(r)) % q for i in range(r)]
        x = [0] * n
        for c, v in zip(free, y):
            x[c] = v
        for i, pc in enumerate(pivots):
            x[pc] = (es[i] - sum(Hr[i][c] * x[c] for c in free)) % q
        return x

    return pivots, free, f


def expand(q: int, n: int, H: list[list[int]], syn: list[int]) -> list[str]:
    r = len(H)
    _, free, f = solver(q, n, H)
    out = []
    for s in syn:
        sd = [(s // q**i) % q for i in range(r)]
        for y in itertools.product(range(q), repeat=len(free)):
            x = f(sd, y)
            assert all(sum(H[i][j] * x[j] for j in range(n)) % q == sd[i] for i in range(r))
            out.append("".join(map(str, x)))
    return out


def main() -> None:
    if len(sys.argv) < 6:
        raise SystemExit(__doc__)
    cmd, q, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    H = parse_H(q, n, sys.argv[4])
    syn = [int(t) for t in open(sys.argv[5]).read().split()]
    if len(set(syn)) != len(syn):
        raise SystemExit("síndrome repetida")
    if cmd == "expand":
        words = expand(q, n, H, syn)
        if len(sys.argv) > 6:
            words += [w.strip() for w in open(sys.argv[6]) if w.strip()]
        if len(set(words)) != len(words):
            raise SystemExit("palavra repetida entre base e remendo")
        sys.stdout.write("\n".join(words) + "\n")
    elif cmd == "lift":
        j = int(sys.argv[6])
        r = len(H)
        H2 = H + [[1 if c == j else 0 for c in range(n)]]
        solver(q, n, H2)  # confere posto
        print('H="' + " ".join("".join(map(str, h)) for h in H2) + '"')
        for s in syn:
            for d in range(q):
                print(s + d * q**r)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
