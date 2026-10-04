#!/usr/bin/env python3
"""Recorta as fontes do ledger para um subconjunto pequeno de células.

Gera tests/fixtures/fontes/ (layout coldcase/<caminho> e florath/<caminho>)
a partir de um diretório com os dois repositórios inteiros (ou do cache do
build.py), para os testes rodarem sem rede. Rode de novo quando trocar o
commit fixado em ledger/sources.json.

    python3 tests/fixtures/recortar_fontes.py DIR_COM_coldcase_E_florath
"""
import csv
import io
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CELULAS = {
    # as nossas
    (7, 9, 4), (7, 8, 3), (5, 10, 4), (5, 9, 3), (5, 7, 2), (5, 9, 4), (4, 10, 4), (5, 9, 5), (2, 6, 1),
    (5, 10, 5), (5, 11, 4),   # v0.6 (7,10,4 já está na linha de baixo)
    # alvo pequeno do loop, Wu–Chen (pós-Kéri), intocada, recorde/cerco/varredura/ataque/SDP do Marosi
    (2, 4, 1), (2, 12, 1), (7, 10, 4), (6, 10, 4), (5, 11, 5), (10, 9, 5), (10, 8, 4), (6, 7, 3), (6, 9, 3), (3, 6, 1),
}


def main(origem: Path) -> None:
    sources = json.loads((AQUI.parents[1] / "ledger" / "sources.json").read_text())
    destino = AQUI / "fontes"
    for repo, spec in sources.items():
        if not isinstance(spec, dict) or "arquivos" not in spec:
            continue
        for nome, caminho in spec["arquivos"].items():
            src = origem / repo / caminho
            out = destino / repo / caminho
            out.parent.mkdir(parents=True, exist_ok=True)
            if caminho.endswith(".csv"):
                rows = list(csv.DictReader(src.open(encoding="utf-8")))
                buf = io.StringIO()
                w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), lineterminator="\n")
                w.writeheader()
                for r in rows:
                    if (int(r["q"]), int(r["n"]), int(r["r"])) in CELULAS:
                        w.writerow(r)
                out.write_text(buf.getvalue(), encoding="utf-8")
                continue
            d = json.loads(src.read_text(encoding="utf-8"))
            dentro = lambda e: (e["q"], e["n"], e["R"]) in CELULAS  # noqa: E731
            if nome == "bounds":
                d["entries"] = [e for e in d["entries"] if dentro(e)]
                d["keys"] = []
                d["lower_bound_updates_2025"] = []
            elif nome == "sweep_state":
                d = {k: v for k, v in d.items() if tuple(int(x) for x in k.split(",")) in CELULAS}
            else:
                d = [e for e in d if dentro(e)]
                if nome == "marosi_lb":
                    d = [{k: v for k, v in e.items() if not k.startswith("sdp_value_")} for e in d]
            out.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"fixture em {destino}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
