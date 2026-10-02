#!/usr/bin/env python3
"""JSON covering-code/v1 -> lista de palavras na forma canônica (uma por linha, ordenada, LF final).

Uso:
    expand.py data/structured/q7_n9_R4_M1351.json            # imprime na saída padrão
    expand.py data/structured/q7_n9_R4_M1351.json -o x.txt   # grava em arquivo
    expand.py --no-check ...                                 # não confere canonical_sha256

Determinístico: a saída é função só do JSON. Por padrão falha (código 1) se o sha256 canônico da
expansão não for o declarado em `canonical_sha256`, se houver palavra repetida entre blocos ou se o
total não for M. Especificação em docs/code-format.md.
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import codefmt as cf  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("json")
    ap.add_argument("-o", "--out")
    ap.add_argument("--no-check", action="store_true", help="não confere canonical_sha256")
    a = ap.parse_args(argv)
    doc = cf.load(a.json)
    try:
        words = cf.expand(doc) if a.no_check else cf.check_doc(doc)
    except cf.FormatError as e:
        print(f"{a.json}: ERRO: {e}", file=sys.stderr)
        return 1
    text = cf.canonical_text(words)
    if a.out:
        with open(a.out, "w") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    print(f"{os.path.basename(a.json)}: {len(words)} palavras, sha256 canônico {cf.canonical_sha256(words)}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
