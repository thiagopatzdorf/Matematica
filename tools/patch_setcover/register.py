#!/usr/bin/env python3
"""register.py -- registra um código base + remendo novo no formato do repo.

Uso: register.py data/structured/<código de origem>.json remendo.txt "<comando>" "<notas>"
Escreve data/codes/<novo>.txt, data/structured/<novo>.json (mesma base linear, patch_words
novas, canonical_sha256) e, se existir data/attack/<origem>.json, data/attack/<novo>.json.
NÃO verifica: rode tools/verify/verify e scripts/attack/verify_bfs no .txt antes de commitar.
"""
import copy
import datetime
import hashlib
import json
import os
import sys

src, patch, cmd, notes = sys.argv[1:5]
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(src))))
old = json.load(open(src))
name = os.path.basename(src)[:-5]
code = open(os.path.join(root, "data", "codes", name + ".txt")).read().split()
pw_old = set(old["patch_words"])
base = [w for w in code if w not in pw_old]
new = open(patch).read().split()
assert len(set(new)) == len(new) and not set(new) & set(base), "remendo repetido ou dentro da base"
words = base + new
M = len(words)
nn = f"q{old['q']}_n{old['n']}_R{old['R']}_M{M}"
open(os.path.join(root, "data", "codes", nn + ".txt"), "w").write("\n".join(words) + "\n")
d = copy.deepcopy(old)
d["M"] = M
d["patch_words"] = new
d["canonical_sha256"] = hashlib.sha256(("\n".join(sorted(words)) + "\n").encode()).hexdigest()
d["provenance"] = {"generator": "tools/patch_setcover (patch_inst + rwls): mesma base de " + name + ", remendo novo",
                   "commit": None, "seed": None, "command": cmd, "date": datetime.date.today().isoformat(),
                   "agent": "James.V1", "repo_commit": None, "notes": notes}
json.dump(d, open(os.path.join(root, "data", "structured", nn + ".json"), "w"), ensure_ascii=False, indent=1)
open(os.path.join(root, "data", "structured", nn + ".json"), "a").write("\n")
ap = os.path.join(root, "data", "attack", name + ".json")
if os.path.exists(ap):
    a = json.load(open(ap))
    a["M"] = M
    a["patch_words"] = new
    if "patch_size" in a:
        a["patch_size"] = len(new)
    a["origem"] = f"remendo de {len(new)} por tools/patch_setcover sobre a base de {name}: {cmd}"
    a["verificacao"] = notes
    json.dump(a, open(os.path.join(root, "data", "attack", nn + ".json"), "w"), ensure_ascii=False, indent=1)
    open(os.path.join(root, "data", "attack", nn + ".json"), "a").write("\n")
print(nn, M, d["canonical_sha256"])
