"""Amostra estratificada dos registros de K_7(5,3) M = 16 para regenerar LRAT (k753_lrat.py) e
para a codificação independente (indep_perfil.py).

Estratos: um perfil aleatório por tipo da coordenada 0 em cada ordem presente (min e max), os
K de maior tempo de solver, os K de maior prova, e A aleatórios; mais, de cada perfil fechado
por cubos, C cubos aleatórios. Semente fixa. Imprime um registro JSON por linha.

Uso: k753_amostra.py semente K A C INTEIROS.jsonl [CUBOS.jsonl ...]"""
import json
import random
import sys
from collections import defaultdict

sem, K, A, C = map(int, sys.argv[1:5])
rng = random.Random(sem)
regs = [json.loads(l) for l in open(sys.argv[5])]
cubos = defaultdict(dict)
for arq in sys.argv[6:]:
    for ln in open(arq, errors="replace"):
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if r.get("L") and r["resultado"] == "UNSAT" and r.get("lrat_check") == "VERIFIED":
            cubos[r["inst"]][r["cubo_idx"]] = r
escolhidos = {}
estr = defaultdict(list)
for r in regs:
    estr[(r.get("ordem", "min"), r["tipos"][0])].append(r)
for chave in sorted(estr):
    r = rng.choice(estr[chave])
    escolhidos[(r.get("ordem", "min"), r["inst"])] = dict(r, estrato=f"coord0 {chave[0]} {chave[1]}")
for campo in ("tempo_solver_s", "bytes.lrat"):
    for r in sorted(regs, key=lambda r: -r.get(campo, 0))[:K]:
        escolhidos.setdefault((r.get("ordem", "min"), r["inst"]), dict(r, estrato=f"maior {campo}"))
for r in rng.sample(regs, A):
    escolhidos.setdefault((r.get("ordem", "min"), r["inst"]), dict(r, estrato="aleatorio"))
for r in escolhidos.values():
    print(json.dumps(r, ensure_ascii=False))
for inst in sorted(cubos):
    for ci in sorted(rng.sample(sorted(cubos[inst]), min(C, len(cubos[inst])))):
        print(json.dumps(dict(cubos[inst][ci], estrato=f"cubo de {inst}"), ensure_ascii=False))
