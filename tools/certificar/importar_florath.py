#!/usr/bin/env python3
"""Importa os códigos explícitos pequenos do banco Lean do Florath como witnesses.

Lê CoveringCodes/Database/Sources/SmallExplicitUpper/K_<q>_<n>_<R>.lean de um clone de
florath/covering-codes-lean (BSD-3-Clause, Copyright (c) 2026 Andreas Florath; commit fixado em
ledger/sources.json), extrai as palavras `![f3_2, f3_0, ...]`, confere a cobertura com o avaliador
exato do buscar.py e grava tools/certificar/witnesses/K<q>_<n>_<R>_M<M>.txt. Só dados (as
palavras dos códigos) são reaproveitados; a prova no nosso Lean é nossa (UB.of_go). O aviso de
licença vai em tools/certificar/witnesses/LICENSE-florath.

    python3 tools/certificar/importar_florath.py CAMINHO_DO_CLONE
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from buscar import WIT, cobre  # noqa: E402

VETOR = re.compile(r"!\[(f\d+_\d+(?:\s*,\s*f\d+_\d+)*)\]")


def main(argv=None) -> int:
    clone = Path((argv or sys.argv[1:])[0])
    WIT.mkdir(parents=True, exist_ok=True)
    ok = 0
    for f in sorted((clone / "CoveringCodes/Database/Sources/SmallExplicitUpper").glob("K_*.lean")):
        q, n, R = (int(x) for x in f.stem.split("_")[1:])
        palavras = [[int(t.split("_")[1]) for t in m.group(1).split(",")] for m in VETOR.finditer(f.read_text())]
        palavras = [list(p) for p in dict.fromkeys(tuple(p) for p in palavras)]
        if not palavras or not cobre(q, n, R, palavras):
            print(f"pulado {f.name}: sem lista de palavras ou não cobre", file=sys.stderr)
            continue
        sep = " " if q > 10 else ""
        (WIT / f"K{q}_{n}_{R}_M{len(palavras)}.txt").write_text(
            "".join(sep.join(str(d) for d in p) + "\n" for p in palavras))
        ok += 1
    print(f"{ok} códigos do Florath importados e conferidos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
