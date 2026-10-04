#!/usr/bin/env python3
"""register.py -- registra um código base + remendo novo no formato do repo.

Uso: register.py data/structured/<código de origem>.json remendo.txt "<comando>" "<notas>"
Escreve data/codes/<novo>.txt (base na ordem do código de origem + remendo) e, se existir
data/attack/<origem>.json, data/attack/<novo>.json. O JSON de data/structured NÃO é escrito
aqui: ele é gerado por scripts/codes/build_structured.py (acrescente a proveniência lá e rode;
o teste test_code_format exige que o JSON versionado seja exatamente o gerado).
NÃO verifica: rode tools/verify/verify e scripts/attack/verify_bfs no .txt antes de commitar.
"""
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
sha = hashlib.sha256(("\n".join(sorted(words)) + "\n").encode()).hexdigest()
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
print(nn, M, sha)
print("falta: proveniência em scripts/codes/build_structured.py e regenerar data/structured/" + nn + ".json")
