"""Regenera, com o codificador auditado, a CNF de N registros aleatórios de um JSONL de
K_7(5,3) M = 16 (inteiros; respeita `ordem`) e compara o sha256 com o registrado, sem solver.

Uso: k753_sha.py DIR_FIBRAS ARQ.jsonl N semente"""
import hashlib
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from k753_lrat import cnf_do_registro  # noqa: E402

d, jsonl, N, sem = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
sys.path.insert(0, d)
import fib_cubos  # noqa: E402
import fib_encode as enc  # noqa: E402

regs = [json.loads(l) for l in open(jsonl)]
amostra = random.Random(sem).sample(regs, min(N, len(regs)))
ok, ruins = 0, []
for r in amostra:
    if hashlib.sha256(cnf_do_registro(enc, fib_cubos, r).encode()).hexdigest() == r["sha256.cnf"]:
        ok += 1
    else:
        ruins.append((r.get("ordem", "min"), r["inst"]))
ordens = {o: sum(1 for r in amostra if r.get("ordem", "min") == o) for o in ("min", "max")}
print(json.dumps({"arquivo": os.path.basename(jsonl), "amostra": len(amostra), "por_ordem": ordens,
                  "sha_igual": ok, "diverge": len(ruins), "divergentes": ruins[:20]}))
