#!/usr/bin/env python3
"""Segundo verificador de códigos de cobertura, implementação independente de tools/verify/verify.c.

Algoritmo DIFERENTE do verify.c: não enumera bolas nem usa tabela de deslocamentos. Parte do indicador do código no
grid (Z_q)^n, dilata R vezes por "mudar no máximo uma coordenada" (qualquer-ao-longo-do-eixo + difusão) e confere se
o resultado é o grid inteiro. Só depende de numpy. Compartilha com o verify.c apenas a especificação do formato
(docs/code-format.md) e a ideia de cobrir por bolas de Hamming; o código e o método de cálculo são outros.

Uso: verify_cover_dilation.py [-q Q -n N -r R] [-m M] ARQUIVO|-                 (modo legado)
     verify_cover_dilation.py --q Q --n N --R R --M M ARQUIVO|-                   (modo explícito)
     Legado: sem -q/-n/-r (e sem -m), os parâmetros saem do nome q<Q>_n<N>_R<R>_M<M>.txt, como no verify.c.
     Explícito: os QUATRO parâmetros vêm da linha de comando; o nome do arquivo nunca é fonte, e se ele seguir o padrão e disser
     outra instância é contradição (exit 2): um witness renomeado para outra instância não passa. Não se mistura com -q/-n/-r/-m.
Códigos de saída (contrato com a campanha: `fail_exit_codes` = [1, 2]; qualquer outro não-zero é ERRO, não refutação):
     0 cobre e confere com os parâmetros; 1 há ponto descoberto com raio R;
     2 o conteúdo contradiz os parâmetros (comprimento != n, dígito >= q, duplicata, #palavras != M, nome != parâmetros explícitos);
     3 uso incorreto ou falha operacional (opção inválida, arquivo ilegível, grid grande demais, exceção inesperada).
Linha final no mesmo formato do verify.c.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys

import numpy as np


class _Parser(argparse.ArgumentParser):
    def error(self, message):  # argparse sairia com 2, que aqui significa "o witness contradiz os parâmetros": uso incorreto é 3
        print(f"ERRO DE USO: {message}", file=sys.stderr)
        sys.exit(3)


def main(argv: list[str]) -> int:
    ap = _Parser(allow_abbrev=False)
    ap.add_argument("-q", type=int)
    ap.add_argument("-n", type=int)
    ap.add_argument("-r", type=int)
    ap.add_argument("-m", type=int)
    for k in ("q", "n", "R", "M"):
        ap.add_argument("--" + k, dest="x_" + k, type=int)
    ap.add_argument("arquivo")
    a = ap.parse_args(argv)
    explicitos = {k: getattr(a, "x_" + k) for k in ("q", "n", "R", "M")}
    q, n, R = a.q, a.n, a.r
    nome = re.match(r"^q(\d+)_n(\d+)_R(\d+)_M(\d+)", os.path.basename(a.arquivo))
    if any(v is not None for v in explicitos.values()):
        if any(x is not None for x in (a.q, a.n, a.r, a.m)):
            print("ERRO DE USO: não misture -q/-n/-r/-m com --q/--n/--R/--M", file=sys.stderr)
            return 3
        if any(v is None or v < 0 for v in explicitos.values()):
            print("ERRO DE USO: modo explícito exige os quatro, não negativos: --q --n --R --M "
                  "(sem eles o nome do arquivo seria a fonte do enunciado)", file=sys.stderr)
            return 3
        q, n, R, a.m = explicitos["q"], explicitos["n"], explicitos["R"], explicitos["M"]
        if nome and tuple(int(x) for x in nome.groups()) != (q, n, R, a.m):
            print(f"erro: parâmetros explícitos (q={q} n={n} R={R} M={a.m}) contradizem o nome do arquivo {nome.groups()}", file=sys.stderr)
            return 2
    elif q is None or n is None or R is None:
        m = re.match(r"^q(\d+)_n(\d+)_R(\d+)_M(\d+)\.txt$", os.path.basename(a.arquivo))
        if not m:
            print("ERRO DE USO: sem -q/-n/-r e o nome do arquivo não é q<Q>_n<N>_R<R>_M<M>.txt", file=sys.stderr)
            return 3
        q, n, R = (int(x) for x in m.groups()[:3])
        if a.m is None:
            a.m = int(m.group(4))
    if q < 2 or n < 1 or R < 0:
        print("ERRO DE USO: parâmetros fora do suportado (q>=2, n>=1, R>=0)", file=sys.stderr)
        return 3
    explicito = any(v is not None for v in explicitos.values())
    try:
        fonte = sys.stdin if a.arquivo == "-" else open(a.arquivo, encoding="utf-8")
        palavras = [ln.strip() for ln in fonte if ln.strip()]
    except (OSError, UnicodeDecodeError) as e:
        print(f"ERRO DE USO: não consegui ler o arquivo: {e}", file=sys.stderr)
        return 3
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
        print("ERRO DE USO: grid grande demais para este verificador", file=sys.stderr)
        return 3
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
    print(f"q={q} n={n} R={R} M={len(palavras)} points={grid.size} uncovered={descobertos} sha256={sha} params={'explicit' if explicito else 'legacy'} verifier=dilation-numpy")
    return 0 if descobertos == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except BaseException as e:  # noqa: BLE001 - traceback sairia com 1, que significa "há ponto descoberto" (FAIL): crash tem de ser 3 (ERRO)
        print(f"ERRO DE USO: falha inesperada: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(3)
