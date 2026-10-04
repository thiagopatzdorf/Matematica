#!/usr/bin/env python3
"""Ranqueia células K_q(n,R) como alvo de busca de cota superior.

Critérios, nesta ordem (lidos de ledger/cells.json):

1. só células ABERTAS (melhor inferior publicada < melhor superior conhecida)
   cujo espaço q^n cabe na verificação barata (padrão: q^n <= 1e9);
2. camada: 0 = ninguém atacou desde 2011 (sem registro/alvo/cerco do Marosi
   nos attack_*.json, sweep_targets.json e cov_sweep_state.json, superior
   ainda a do Kéri, e não é nossa); 1 = o Marosi atacou e não melhorou;
   2 = já melhorada depois de 2011 (Marosi, Florath ou nós);
3. dentro da camada, gap relativo superior/inferior (ub/lb) decrescente;
   desempate pelo espaço menor (verificação mais barata).

Uso:
    python3 ledger/targets.py                 # top 15, tabela
    python3 ledger/targets.py --top 30 --json
    python3 ledger/targets.py --max-espaco 1e8
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent

CAMADA_TXT = {
    0: "ninguém atacou desde 2011",
    1: "Marosi atacou, sem melhora",
    2: "já melhorada depois de 2011",
}


def melhor_ub(c: dict) -> int | None:
    if c.get("best"):
        return c["best"]["ub"]
    return c["published"]["ub"]["value"] if c["published"]["ub"] else None


def camada(c: dict) -> int:
    nosso = bool(c.get("ours_lean") or c.get("ours_computational"))
    if c.get("ub_improved_since_2011") or nosso:
        return 2
    if c["marosi_attacked"]["ub"]:
        return 1
    return 0


def justificar(c: dict, cam: int, ub: int, lb: int) -> str:
    fonte_ub = "nossa" if c.get("best", {}) and c["best"]["holder"] != "published" else \
        c["published"]["ub"]["source"]
    partes = [
        CAMADA_TXT[cam],
        f"ub/lb = {ub}/{lb} = {ub / lb:.2f}",
        f"q^n = {c['space']:.2e}",
        f"ub de {fonte_ub} (chave Kéri '{c['published']['sources']['keri_2011'].get('ub_key') or '-'}')",
        f"lb de {c['published']['lb']['source']}",
    ]
    if c["marosi_attacked"]["evidence"]:
        partes.append("evidência Marosi: " + ", ".join(sorted(set(
            e.split(":")[0] for e in c["marosi_attacked"]["evidence"]))))
    return "; ".join(partes)


def ranquear(cells: list[dict], max_espaco: float = 1e9, incluir_fechadas: bool = False) -> list[dict]:
    out = []
    for c in cells:
        lb = c["published"]["lb"]["value"] if c["published"]["lb"] else None
        cert_lb = (c.get("certification") or {}).get("lb")
        if cert_lb:  # inclui as nossas inferiores (K7(4,2) = 19 sai da lista de alvos)
            lb = max(lb or 0, cert_lb["value"])
        ub = melhor_ub(c)
        if lb is None or ub is None or lb <= 0:
            continue
        if not incluir_fechadas and lb >= ub:
            continue
        if c["space"] > max_espaco:
            continue
        cam = camada(c)
        out.append({
            "id": c["id"], "q": c["q"], "n": c["n"], "R": c["R"],
            "lb": lb, "ub": ub, "ratio": ub / lb, "space": c["space"],
            "camada": cam, "justificativa": justificar(c, cam, ub, lb),
        })
    out.sort(key=lambda t: (t["camada"], -t["ratio"], t["space"], t["q"], t["n"], t["R"]))
    for i, t in enumerate(out, 1):
        t["rank"] = i
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", type=Path, default=AQUI / "cells.json")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--max-espaco", type=float, default=1e9)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    cells = json.loads(a.ledger.read_text(encoding="utf-8"))["cells"]
    alvos = ranquear(cells, a.max_espaco)[: a.top]
    if a.json:
        print(json.dumps(alvos, ensure_ascii=False, indent=1))
        return 0
    print(f"{'#':>3} {'célula':<11} {'lb':>6} {'ub':>6} {'ub/lb':>6} {'q^n':>9} cam  justificativa")
    for t in alvos:
        print(f"{t['rank']:>3} {t['id']:<11} {t['lb']:>6} {t['ub']:>6} {t['ratio']:>6.2f} "
              f"{t['space']:>9.2e} {t['camada']:>3}  {t['justificativa']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
