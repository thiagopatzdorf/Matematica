"""Resumo de uma amostra (JSONL de amostra.py) e extrapolação do custo total.

    python3 resumo.py out/rs_M72.jsonl --tarifa 0.0181

Tempo por subproblema: mediana, p90, máximo. Extrapolação: N_sequências x média, com intervalo
bootstrap de 90 % (percentis 5 e 95 da média reamostrada). Subproblema que estourou o tempo
("TEMPO") entra com o tempo-limite: a média e o total viram COTA INFERIOR, e o resumo diz isso.
Tarifa em US$ por vCPU-hora (padrão: c2d-highmem-8 spot em southamerica-east1, US$ 0,1448/h
para 8 vCPU, tabela do lote-gcp.py de 2026-10-02).
"""
from __future__ import annotations

import argparse
import json
import random
import statistics

TARIFA_PADRAO = 0.1448 / 8


def percentil(xs: list[float], q: float) -> float:
    s = sorted(xs)
    if not s:
        return float("nan")
    k = (len(s) - 1) * q
    i = int(k)
    return s[i] if i + 1 >= len(s) else s[i] + (s[i + 1] - s[i]) * (k - i)


def resumir(regs: list[dict], tarifa: float = TARIFA_PADRAO, reamostras: int = 2000,
            semente: int = 1) -> dict:
    t = [r["seg"] for r in regs]
    n_total = regs[0]["total_seqs"]
    censurados = sum(1 for r in regs if r["status"] == "TEMPO")
    rng = random.Random(semente)
    medias = sorted(statistics.fmean(rng.choices(t, k=len(t))) for _ in range(reamostras))
    media = statistics.fmean(t)

    def cpu_h(m: float) -> float:
        return m * n_total / 3600

    return {
        "amostra": len(t), "sequencias": n_total, "censurados": censurados,
        "status": {s: sum(1 for r in regs if r["status"] == s) for s in {r["status"] for r in regs}},
        "mediana_s": round(statistics.median(t), 1), "p90_s": round(percentil(t, 0.9), 1),
        "max_s": round(max(t), 1), "media_s": round(media, 1),
        "total_cpu_h": round(cpu_h(media), 1),
        "intervalo_cpu_h": [round(cpu_h(medias[int(0.05 * reamostras)]), 1),
                            round(cpu_h(medias[int(0.95 * reamostras) - 1]), 1)],
        "total_usd": round(cpu_h(media) * tarifa, 2),
        "cota_inferior": censurados > 0,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", nargs="+")
    ap.add_argument("--tarifa", type=float, default=TARIFA_PADRAO, help="US$ por vCPU-hora")
    a = ap.parse_args()
    for arq in a.jsonl:
        regs = [json.loads(ln) for ln in open(arq) if ln.strip()]
        print(arq, json.dumps(resumir(regs, a.tarifa), ensure_ascii=False))


if __name__ == "__main__":
    main()
