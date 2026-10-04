#!/usr/bin/env python3
"""Lista células K_q(n,R) do ledger com folga (melhor ub − melhor lb) ≤ N.

Melhor lb = máximo entre published.lb e todas as fontes (Kéri, Gijswijt–Polak,
Marosi SDP, Florath Lean, literatura pós-Kéri). Melhor ub = best.ub (inclui o nosso).
Uso: python3 tools/exatos/folgas.py [--max 3] [--json]
"""
import argparse, json, pathlib

RAIZ = pathlib.Path(__file__).resolve().parents[2]


def melhores(c):
    lbs = [(c["published"]["lb"]["value"], c["published"]["lb"]["source"])]
    for nome, s in (c["published"].get("sources") or {}).items():
        if s and isinstance(s.get("lb"), (int, float)):
            lbs.append((s["lb"], nome))
    lb = max(v for v, _ in lbs)
    fontes_lb = sorted({n for v, n in lbs if v == lb})
    ub = c["best"]["ub"]
    fontes_ub = [c["best"]["holder"]]
    if c["best"]["holder"] == "published":
        fontes_ub = [c["published"]["ub"]["source"]]
    return lb, fontes_lb, ub, fontes_ub


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=3)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    cells = json.loads((RAIZ / "ledger/cells.json").read_text())["cells"]
    exatas = abertas = 0
    out = []
    for c in cells:
        lb, flb, ub, fub = melhores(c)
        if lb > ub:
            raise SystemExit(f"inconsistente: {c['id']} lb={lb} ub={ub}")
        if lb == ub:
            exatas += 1
            continue
        abertas += 1
        if ub - lb <= a.max:
            out.append(dict(id=c["id"], q=c["q"], n=c["n"], R=c["R"], lb=lb, fontes_lb=flb,
                            ub=ub, fontes_ub=fub, folga=ub - lb, espaco=c["space"]))
    out.sort(key=lambda x: (x["folga"], x["espaco"]))
    if a.json:
        print(json.dumps(dict(exatas=exatas, abertas=abertas, celulas=out), indent=1, ensure_ascii=False))
    else:
        print(f"exatas={exatas} abertas={abertas} folga<= {a.max}: {len(out)}")
        for x in out:
            print(f"{x['id']:12s} {x['lb']:>5}-{x['ub']:<5} folga {x['folga']} espaço {x['espaco']:>9}  lb:{','.join(x['fontes_lb'])}  ub:{','.join(x['fontes_ub'])}")


if __name__ == "__main__":
    main()
