#!/usr/bin/env python3
"""Relatório de cobertura da certificação do ledger: quantas cotas em cada estado, por q.

Lê ledger/cells.json (campo `certification`, gerado por ledger/build.py) e escreve
ledger/COBERTURA.md. O arquivo commitado tem de bater com o gerado (teste
`test_cobertura_commitada_bate_com_a_gerada_do_ledger`).

    python3 ledger/cobertura.py              # reescreve ledger/COBERTURA.md
    python3 ledger/cobertura.py --stdout     # só imprime
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
# A escada vem do build.py: duas cópias da lista divergem (uma delas já ficou sem o degrau novo).
from build import ESTADOS  # noqa: E402

CURTO = {"CLAIMED": "C", "WITNESS_CHECKED": "W", "CERTIFICATE_VERIFIED": "V", "FORMALIZED": "F",
         "INDEPENDENTLY_REPRODUCED": "I"}
FORMAL = ESTADOS.index("FORMALIZED")


def contar(cells: list[dict]) -> dict:
    """{q: Counter} com as chaves ub:<estado>, lb:<estado>, exatas, exatas_formais, ub_lean_externo."""
    por_q: dict[int, Counter] = {}
    for c in cells:
        cert = c["certification"]
        k = por_q.setdefault(c["q"], Counter())
        k["celulas"] += 1
        k["ub:" + cert["ub"]["state"]] += 1
        if cert["lb"]:
            k["lb:" + cert["lb"]["state"]] += 1
        if cert["exact"]:
            k["exatas"] += 1
            if all(ESTADOS.index(cert[s]["state"]) >= FORMAL for s in ("ub", "lb")):
                k["exatas_formais"] += 1
            if all(ESTADOS.index(cert[s]["state"]) >= 1 for s in ("ub", "lb")):
                k["exatas_certificadas"] += 1
        if "formalizacao_externa" in cert["ub"]["provenance"]:
            k["ub_lean_externo"] += 1
    return por_q


def relatorio(ledger: dict) -> str:
    por_q = contar(ledger["cells"])
    total = sum(por_q.values(), Counter())
    linhas = [
        "# Cobertura da certificação do ledger",
        "",
        "A machine-checked ledger of covering-code upper bounds, with formally certified exact entries.",
        "",
        "Gerado por `ledger/cobertura.py` a partir de `ledger/cells.json`; não edite à mão.",
        "Estados (cumulativos, ver `ledger/README.md`): **C** = CLAIMED, **W** = WITNESS_CHECKED,",
        "**V** = CERTIFICATE_VERIFIED (só inferior), **F** = FORMALIZED, **I** = INDEPENDENTLY_REPRODUCED.",
        "As cotas inferiores são, quase todas, herdadas da literatura (CLAIMED).",
        "",
        f"Total: {total['celulas']} células; exatas (inferior = superior): {total['exatas']}; "
        f"exatas com as duas cotas certificadas aqui (W ou acima): {total['exatas_certificadas']}; "
        f"exatas com as duas cotas no Lean daqui: {total['exatas_formais']}.",
        "",
        "| lado | " + " | ".join(ESTADOS) + " |",
        "|---|" + "---:|" * len(ESTADOS),
    ]
    for lado in ("ub", "lb"):
        linhas.append(f"| {lado} | " + " | ".join(str(total[f'{lado}:{e}']) for e in ESTADOS) + " |")
    linhas += [
        "",
        f"Cotas superiores com prova Lean externa da mesma cota (Florath, commit fixado, não "
        f"reconstruída aqui, por isso não sobe o estado): {total['ub_lean_externo']}.",
        "",
        "## Por q",
        "",
        "| q | células | " + " | ".join(f"{lado} {CURTO[e]}" for lado in ("ub", "lb") for e in ESTADOS)
        + " | exatas | ub Lean externo |",
        "|---:|---:|" + "---:|" * (2 * len(ESTADOS)) + "---:|---:|",
    ]
    for q in sorted(por_q):
        k = por_q[q]
        cols = [k["celulas"]] + [k[f"{lado}:{e}"] for lado in ("ub", "lb") for e in ESTADOS]
        cols += [k["exatas"], k["ub_lean_externo"]]
        linhas.append(f"| {q} | " + " | ".join(str(x) for x in cols) + " |")
    acima = [c for c in ledger["cells"]
             if ESTADOS.index(c["certification"]["ub"]["state"]) > 0
             or (c["certification"]["lb"] and ESTADOS.index(c["certification"]["lb"]["state"]) > 0)]
    linhas += ["", "## Células acima de CLAIMED", "", "| célula | ub | estado ub | lb | estado lb | exata |",
               "|---|---:|---|---:|---|---|"]
    for c in acima:
        cert = c["certification"]
        lb = cert["lb"] or {"value": "—", "state": "—"}
        linhas.append(f"| {c['id']} | {cert['ub']['value']} | {cert['ub']['state']} | {lb['value']} | "
                      f"{lb['state']} | {'sim' if cert['exact'] else 'não'} |")
    return "\n".join(linhas) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", type=Path, default=AQUI / "cells.json")
    ap.add_argument("--saida", type=Path, default=AQUI / "COBERTURA.md")
    ap.add_argument("--stdout", action="store_true")
    a = ap.parse_args(argv)
    texto = relatorio(json.loads(a.ledger.read_text(encoding="utf-8")))
    if a.stdout:
        sys.stdout.write(texto)
    else:
        a.saida.write_text(texto, encoding="utf-8")
        print(f"{a.saida}: escrito")
    return 0


if __name__ == "__main__":
    sys.exit(main())
