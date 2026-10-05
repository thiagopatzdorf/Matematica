"""Regenera, com o codificador auditado, a CNF de uma amostra aleatória de perfis de um JSONL do
rodar.py e compara o sha256 com o registrado (sem rodar solver). Prova que os certificados
correspondem ao codificador do commit auditado, não a uma versão anterior.

Uso: sha_amostra.py DIR_FIBRAS ARQ.jsonl tamanho semente"""
import hashlib
import json
import random
import sys

d, jsonl, tam, sem = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
sys.path.insert(0, d)
import fib_encode as enc  # noqa: E402

regs = [json.loads(l) for l in open(jsonl)]
amostra = random.Random(sem).sample(regs, min(tam, len(regs)))
ok = ruim = 0
for r in amostra:
    q, n, M, k, smin, i = r["q"], r["n"], r["M"], r["k"], r["smin"], r["inst"]
    _, ins = enc.instancias(q, n, M, k, smin)
    pref = ins[i]
    cnf, *_ = enc.codificar(q, n, M, pref, smin)
    rot = f"K_{q}({n},{n-2}) M={M} k={k} s_min={smin} inst {i}: {pref}"
    h = hashlib.sha256(cnf.dimacs([rot]).encode()).hexdigest()
    if h == r["sha256.cnf"] and ["".join(map(str, t)) for t in pref] == r["tipos"]:
        ok += 1
    else:
        ruim += 1
        print("DIVERGE", i, flush=True)
print(json.dumps({"arquivo": jsonl.rsplit("/", 1)[-1], "amostra": len(amostra), "sha_igual": ok, "diverge": ruim}))
