#!/usr/bin/env python3
"""Gera paper/numeros.tex: as contagens do ledger que o paper cita, como macros do LaTeX.

Por que existe: o paper repetia à mão os números do ledger ("547 of the 1145", "the other 598") e
ficou para trás quando o ledger subiu para 642 (PRs #95 e #98). Agora o main.tex só usa macros
(`\\NumUBKernel`, `\\NumCelulas`, ...) definidas em paper/numeros.tex, que sai daqui, e o teste
`tests/test_paper_numeros.py` falha se o arquivo commitado divergir do ledger ou se o main.tex voltar
a digitar uma dessas contagens.

Fonte única: `ledger/cells.json`, contado por `ledger/cobertura.py::contar` (a mesma função que gera o
`ledger/COBERTURA.md`; duas contagens da mesma coisa divergem). Determinístico: mesma entrada, mesmos
bytes (sem data de geração, ordem fixa).

    python3 tools/paper/numeros.py              # reescreve paper/numeros.tex e a frase do .zenodo.json
    python3 tools/paper/numeros.py --checar     # sai 1 se algum dos dois estiver desatualizado
    python3 tools/paper/numeros.py --stdout     # só imprime o numeros.tex
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "ledger"))
from build import ESTADOS  # noqa: E402
from cobertura import contar  # noqa: E402

KERNEL = ("FORMALIZED", "INDEPENDENTLY_REPRODUCED")  # estados em que a cota é teorema do kernel do Lean
SAIDA = RAIZ / "paper" / "numeros.tex"
ZENODO = RAIZ / ".zenodo.json"
FRASE_ZENODO = re.compile(r"\d+ of the \d+ upper bounds are theorems of the Lean kernel")
MACRO = re.compile(r"^\\newcommand\{\\([A-Za-z]+)\}\{(.*)\}$", re.M)  # o valor pode ter chaves ($K_{2}$)


def ler_ledger(raiz: Path = RAIZ) -> dict:
    return json.loads((raiz / "ledger" / "cells.json").read_text(encoding="utf-8"))


def _celula_tex(c: dict) -> str:
    return f"$K_{{{c['q']}}}({c['n']},{c['R']})$"


def _lista(cells: list[dict]) -> str:
    nomes = [_celula_tex(c) for c in sorted(cells, key=lambda c: (c["q"], c["n"], c["R"]))]
    if len(nomes) <= 1:
        return "".join(nomes)
    return ", ".join(nomes[:-1]) + " and " + nomes[-1]


def numeros(ledger: dict) -> dict[str, str]:
    """{nome da macro: valor em LaTeX}, na ordem em que vão para o arquivo."""
    cells = ledger["cells"]
    t = sum(contar(cells).values(), Counter())
    ub = {e: t[f"ub:{e}"] for e in ESTADOS}
    lb = {e: t[f"lb:{e}"] for e in ESTADOS}
    kernel = sum(ub[e] for e in KERNEL)
    exatas_lean = [c for c in cells if c["certification"]["exact"]
                   and all(c["certification"][s]["state"] in KERNEL for s in ("ub", "lb"))]
    lb_verificada = [c for c in cells if c["certification"]["lb"]
                     and c["certification"]["lb"]["state"] == "CERTIFICATE_VERIFIED"]
    qs = sorted({c["q"] for c in cells})
    return {
        "NumCelulas": str(t["celulas"]),
        "NumQMin": str(qs[0]),
        "NumQMax": str(qs[-1]),
        "NumExatas": str(t["exatas"]),
        "NumUBKernel": str(kernel),
        "NumUBFormalizada": str(ub["FORMALIZED"]),
        "NumUBReproduzida": str(ub["INDEPENDENTLY_REPRODUCED"]),
        "NumUBWitness": str(ub["WITNESS_CHECKED"]),
        "NumUBClaimed": str(ub["CLAIMED"]),
        "NumUBForaDoKernel": str(t["celulas"] - kernel),
        "NumUBLeanExterno": str(t["ub_lean_externo"]),
        "NumLBClaimed": str(lb["CLAIMED"]),
        "NumLBVerificada": str(lb["CERTIFICATE_VERIFIED"]),
        "NumLBKernel": str(sum(lb[e] for e in KERNEL)),
        "NumExatasCertificadas": str(t["exatas_certificadas"]),
        "NumExatasLean": str(len(exatas_lean)),
        "ExatasLeanLista": _lista(exatas_lean),
        "LBVerificadaLista": _lista(lb_verificada),
    }


def gerar(ledger: dict | None = None) -> str:
    ledger = ledger if ledger is not None else ler_ledger()
    linhas = [
        "% Gerado por tools/paper/numeros.py a partir de ledger/cells.json; NÃO edite à mão.",
        "% Se o ledger mudou: python3 tools/paper/numeros.py (teste: tests/test_paper_numeros.py).",
    ]
    linhas += [f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in numeros(ledger).items()]
    return "\n".join(linhas) + "\n"


def macros(numeros_tex: str) -> dict[str, str]:
    return dict(MACRO.findall(numeros_tex))


def expandir(tex: str, numeros_tex: str) -> str:
    """O main.tex com as macros de numeros.tex substituídas pelo valor (para quem confere o texto).

    `\\NumX{}` e `\\NumX` seguido de algo que não é letra viram o valor; uma macro desconhecida fica como está.
    """
    tabela = macros(numeros_tex)

    def troca(m: re.Match) -> str:
        return tabela.get(m.group(1), m.group(0))

    return re.sub(r"\\([A-Za-z]+)(?:\{\})?(?![A-Za-z])", troca, tex)


def frase_zenodo(ledger: dict) -> str:
    n = numeros(ledger)
    return f"{n['NumUBKernel']} of the {n['NumCelulas']} upper bounds are theorems of the Lean kernel"


def zenodo_atualizado(texto: str, ledger: dict) -> str:
    z = json.loads(texto)
    z["description"] = FRASE_ZENODO.sub(frase_zenodo(ledger), z["description"])
    return json.dumps(z, ensure_ascii=False, indent=2) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--checar", action="store_true", help="sai 1 se paper/numeros.tex ou .zenodo.json divergirem")
    ap.add_argument("--stdout", action="store_true", help="só imprime o numeros.tex")
    a = ap.parse_args(argv)
    ledger = ler_ledger()
    novo = gerar(ledger)
    if a.stdout:
        sys.stdout.write(novo)
        return 0
    z_atual = ZENODO.read_text(encoding="utf-8")
    z_novo = zenodo_atualizado(z_atual, ledger)
    atual = SAIDA.read_text(encoding="utf-8") if SAIDA.is_file() else ""
    if a.checar:
        ruins = [p.name for p, x, y in ((SAIDA, atual, novo), (ZENODO, z_atual, z_novo)) if x != y]
        if ruins:
            print("desatualizado: " + ", ".join(ruins) + " (rode python3 tools/paper/numeros.py)", file=sys.stderr)
            return 1
        return 0
    SAIDA.write_text(novo, encoding="utf-8")
    if z_novo != z_atual:
        ZENODO.write_text(z_novo, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
