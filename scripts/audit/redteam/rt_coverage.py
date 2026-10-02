#!/usr/bin/env python3
"""Red team, ataques 1 e 2: cobertura e integridade dos arquivos da varredura.

Uso: rt_coverage.py <dir_varredura> <prefixo_shard> [ledger]
  ex.: rt_coverage.py ~/state/maestro/fz fz ledger_final.jsonl
       rt_coverage.py ~/state/maestro/fzdeg fzd ledger_deg.jsonl
Lê A de dentro de cada c_L.out e compara com a linha L de classes_sorted.jsonl.
Só leitura. Imprime cada anomalia e um resumo final.
"""
import glob, hashlib, json, os, re, sys
from collections import defaultdict

d, pref = sys.argv[1], sys.argv[2]
ledger = sys.argv[3] if len(sys.argv) > 3 else None
classes = [json.loads(l) for l in open(os.path.join(d, "classes_sorted.jsonl"))]
N = len(classes)
files = defaultdict(list)
for f in glob.glob(os.path.join(d, pref + "-0*", "c_*.out")):
    L = int(re.search(r"c_(\d+)\.out$", f).group(1))
    files[L].append(f)
prob = []
def P(*a):
    prob.append(" ".join(map(str, a)))
expected = set(range(1, N + 1))
miss = sorted(expected - set(files)); extra = sorted(set(files) - expected)
if miss: P("FALTANDO", len(miss), miss[:20])
if extra: P("EXTRA", extra[:20])
mins = {}
shardmis = 0
sha = {}
for L, fl in sorted(files.items()):
    if L > N: continue
    contents = {open(f, "rb").read() for f in fl}
    if len(fl) > 1: P("DUPLICADO", L, fl, "conteudos distintos" if len(contents) > 1 else "iguais")
    for f in fl:
        raw = open(f, "rb").read(); sha[L] = hashlib.sha256(raw).hexdigest()
        lines = raw.decode().strip().splitlines()
        if not lines: P("VAZIO", f); continue
        try: j = json.loads(lines[-1])
        except Exception: P("ULTIMA_LINHA_NAO_JSON", f, lines[-1][:80]); continue
        exp_shard = f"{pref}-0{(L-1)%3+1}"
        if os.path.basename(os.path.dirname(f)) != exp_shard: shardmis += 1
        c = classes[L - 1]
        if j.get("A") != c["A"]: P("A_DIFERE", L, f, j.get("A"), c["A"])
        if "nBc" in c and j.get("nBc") != c["nBc"]: P("NBC_DIFERE", L, j.get("nBc"), c["nBc"])
        if j.get("exact") is not True: P("SEM_EXACT", L, f)
        if (j.get("q"), j.get("n"), j.get("R"), j.get("t"), j.get("T")) != (7, 9, 4, 3, 8): P("PARAM", L, j)
        trios = [l for l in lines[:-1] if l.startswith("TRIO")]
        other = [l for l in lines[:-1] if not l.startswith("TRIO")]
        if other: P("LINHA_ESTRANHA", L, other[:2])
        orf = [int(re.search(r"orphans=(\d+)", l).group(1)) for l in trios]
        if any(o > 8 for o in orf): P("TRIO_ACIMA_T", L)
        if trios and j["orphans"] != min(orf): P("MIN_INCONSISTENTE", L, j["orphans"], min(orf))
        if not trios and j["orphans"] != -1: P("ORFAS_SEM_TRIO", L, j["orphans"])
        if trios:
            cs = j["coset_syndromes"]
            # o trio reportado deve estar entre as linhas TRIO
            if not any(f"s1={cs[1]} s2={cs[2]}" in l or f"s1={cs[2]} s2={cs[1]}" in l for l in trios):
                P("TRIO_REPORTADO_AUSENTE", L, cs)
        mins[L] = j["orphans"]
if ledger:
    for l in open(os.path.join(d, ledger)):
        e = json.loads(l); L = e["L"]
        if e.get("sha256_file") and sha.get(L) != e["sha256_file"]: P("LEDGER_SHA", L)
        if e.get("orphans") != mins.get(L): P("LEDGER_ORFAS", L, e.get("orphans"), mins.get(L))
for p in prob: print(p)
hit = {L: o for L, o in mins.items() if o != -1}
print(f"RESUMO N={N} arquivos_L={len(files)} problemas={len(prob)} fora_do_shard_esperado={shardmis}")
print("classes com orfas<=8:", {L: (o, classes[L-1]['A']) for L, o in hit.items()})
