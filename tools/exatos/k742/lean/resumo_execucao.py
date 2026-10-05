#!/usr/bin/env python3
"""Resume o registro da execução das refutações (tools/exatos/k742/lean/execucao/).

    python3 tools/exatos/k742/lean/resumo_execucao.py

Lê `modulos*.jsonl` (uma linha por módulo compilado, de `vm/agendar.py`) e
`semquebra_M18.jsonl`, e imprime: módulos, CPU total, ms de CPU por dica, pico de RSS, parede do
primeiro ao último módulo, e os 5 perfis mais caros.
"""
import json
import os
import re
from collections import defaultdict
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(AQUI, "execucao")


def main():
    mods = {}
    for f in sorted(os.listdir(EX)):
        if f.startswith("modulos") and f.endswith(".jsonl"):
            for ln in open(os.path.join(EX, f)):
                e = json.loads(ln)
                if e["rc"] == 0:
                    mods[e["modulo"]] = e
    reg = {}
    for ln in open(os.path.join(AQUI, "semquebra_M18.jsonl")):
        e = json.loads(ln)
        reg[e["perfil"]] = e
    cpu = sum(e["cpu_s"] for e in mods.values())
    cpu_b = sum(e["cpu_s"] for m, e in mods.items() if re.search(r"\.B\d+$", m))
    dicas = sum(e["dicas"] for e in reg.values())
    fins = [datetime.strptime(e["fim"], "%Y-%m-%dT%H:%M:%SZ") for e in mods.values()]
    ini = min(f.timestamp() - e["parede_s"] for f, e in zip(fins, mods.values()))
    por = defaultdict(float)
    for m, e in mods.items():
        por[int(m.split(".")[2][1:])] += e["cpu_s"]
    print(f"módulos com rc 0: {len(mods)}")
    print(f"CPU total: {cpu / 3600:.1f} h (blocos B: {cpu_b / 3600:.1f} h)")
    print(f"dicas: {dicas / 1e6:.1f} M; CPU dos blocos por dica: {1000 * cpu_b / dicas:.3f} ms")
    print(f"pico de RSS de um módulo: {max(e['rss_gb'] for e in mods.values()):.2f} GB")
    for tipo in ("Data", "B", "Final"):
        xs = [e for m, e in mods.items() if re.search(rf"\.{tipo}\d*$", m)]
        if xs:
            print(f"  {tipo}: {len(xs)} módulos, RSS máx {max(e['rss_gb'] for e in xs):.2f} GB, "
                  f"parede máx {max(e['parede_s'] for e in xs) / 60:.1f} min")
    print(f"parede, do primeiro ao último módulo: {(max(f.timestamp() for f in fins) - ini) / 3600:.2f} h")
    print("perfis mais caros (CPU h):",
          ", ".join(f"{p}: {c / 3600:.1f}" for p, c in sorted(por.items(), key=lambda x: -x[1])[:5]))


if __name__ == "__main__":
    main()
