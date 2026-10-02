#!/usr/bin/env python3
"""Segundo verificador de códigos de cobertura, implementação independente de tools/verify/verify.c.

Algoritmo DIFERENTE do verify.c: não enumera bolas nem usa tabela de deslocamentos. Parte do indicador do código no
grid (Z_q)^n, dilata R vezes por "mudar no máximo uma coordenada" (qualquer-ao-longo-do-eixo + difusão) e confere se
o resultado é o grid inteiro. Só depende de numpy. Compartilha com o verify.c apenas a especificação do formato
(docs/code-format.md) e a ideia de cobrir por bolas de Hamming; o código e o método de cálculo são outros.

Uso: verify_cover_dilation.py [-q Q -n N -r R] [-m M] ARQUIVO|-
     Sem -q/-n/-r (e sem -m), os parâmetros saem do nome q<Q>_n<N>_R<R>_M<M>.txt, como no verify.c.
Saída: 0 cobre; 1 há ponto descoberto; 2 entrada inválida. Linha final no mesmo formato do verify.c.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys

import numpy as np


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", type=int)
    ap.add_argument("-n", type=int)
    ap.add_argument("-r", type=int)
    ap.add_argument("-m", type=int)
    ap.add_argument("arquivo")
    a = ap.parse_args(argv)
    q, n, R = a.q, a.n, a.r
    if q is None or n is None or R is None:
        m = re.match(r"^q(\d+)_n(\d+)_R(\d+)_M(\d+)\.txt$", os.path.basename(a.arquivo))
        if not m:
            print("erro: sem -q/-n/-r e o nome do arquivo não é q<Q>_n<N>_R<R>_M<M>.txt", file=sys.stderr)
            return 2
        q, n, R = (int(x) for x in m.groups()[:3])
        if a.m is None:
            a.m = int(m.group(4))
    fonte = sys.stdin if a.arquivo == "-" else open(a.arquivo, encoding="utf-8")
    palavras = [ln.strip() for ln in fonte if ln.strip()]
    for w in palavras:
        if len(w) != n:
            print(f"erro: comprimento {len(w)} != {n}: {w!r}", file=sys.stderr)
            return 2
        if any((not ch.isdigit()) or int(ch) >= q for ch in w):
            print(f"erro: dígito >= q em {w!r}", file=sys.stderr)
            return 2
    if len(set(palavras)) != len(palavras):
        print("erro: palavra duplicada", file=sys.stderr)
        return 2
    if a.m is not None and len(palavras) != a.m:
        print(f"erro: {len(palavras)} palavras, esperado {a.m}", file=sys.stderr)
        return 2
    if q ** n > 1 << 31:
        print("erro: grid grande demais para este verificador", file=sys.stderr)
        return 2
    # índice little-endian w = sum s[k] q^k; o grid em ordem C tem o eixo 0 como dígito mais significativo
    pesos = np.array([q ** k for k in range(n)], dtype=np.int64)
    dig = np.array([[int(ch) for ch in w] for w in palavras], dtype=np.int64).reshape(len(palavras), n)
    grid = np.zeros(q ** n, dtype=bool)
    grid[dig @ pesos] = True
    grid = grid.reshape((q,) * n)
    for _ in range(R):
        novo = grid.copy()
        for eixo in range(n):
            novo |= np.broadcast_to(grid.any(axis=eixo, keepdims=True), grid.shape)
        grid = novo
    descobertos = int(grid.size - np.count_nonzero(grid))
    sha = hashlib.sha256(("\n".join(sorted(palavras)) + "\n").encode()).hexdigest()
    print(f"q={q} n={n} R={R} M={len(palavras)} points={grid.size} uncovered={descobertos} sha256={sha} verifier=dilation-numpy")
    return 0 if descobertos == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
