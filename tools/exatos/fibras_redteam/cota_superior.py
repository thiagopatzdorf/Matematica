"""Cota superior K_7(6,4) <= 14, conferida sem nada do repo: lê o código, confere que tem 14
palavras distintas em Z_7^6 e que toda palavra de Z_7^6 está a distância <= 4 de alguma.
Também conta, para cada ponto, quantas palavras o cobrem (mínimo tem de ser >= 1)."""
import itertools
import sys

import numpy as np


def ler(caminho):
    pal = [l.strip() for l in open(caminho) if l.strip() and not l.startswith("#")]
    return [tuple(int(ch) for ch in p) for p in pal]


def multiplicidade_de_cobertura(cod, q, n, R):
    pts = np.array(list(itertools.product(range(q), repeat=n)), dtype=np.int8)
    mult = np.zeros(len(pts), dtype=np.int32)
    for c in cod:
        d = (pts != np.array(c, dtype=np.int8)).sum(axis=1)
        mult += d <= R
    return pts, mult


def main(caminho, q=7, n=6, R=4):
    cod = ler(caminho)
    assert all(len(c) == n and all(0 <= a < q for a in c) for c in cod), "palavra fora de Z_q^n"
    assert len(set(cod)) == len(cod), "palavra repetida"
    pts, mult = multiplicidade_de_cobertura(cod, q, n, R)
    desc = int((mult == 0).sum())
    print(f"palavras={len(cod)} pontos={len(pts)} descobertos={desc} cobertura_min={mult.min()} max={mult.max()}")
    return len(cod), desc


if __name__ == "__main__":
    M, desc = main(sys.argv[1])
    sys.exit(0 if desc == 0 else 1)
