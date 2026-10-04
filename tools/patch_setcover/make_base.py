#!/usr/bin/env python3
"""make_base.py -- separa base e remendo de um código do repo.

Uso: make_base.py data/structured/<nome>.json base.txt remendo.txt
A base é data/codes/<nome>.txt menos as `patch_words` do JSON estruturado (as classes
laterais); o remendo são as próprias `patch_words`. Confere |base| + |remendo| = M.
"""
import json
import os
import sys

js, out_base, out_patch = sys.argv[1:4]
d = json.load(open(js))
root = os.path.dirname(os.path.dirname(os.path.abspath(js)))
code = open(os.path.join(root, "codes", os.path.basename(js)[:-5] + ".txt")).read().split()
pw = list(d["patch_words"])
s = set(pw)
base = [w for w in code if w not in s]
assert len(base) + len(pw) == d["M"] == len(code), "base + remendo != M"
open(out_base, "w").write("\n".join(base) + "\n")
open(out_patch, "w").write("\n".join(pw) + "\n")
print(f"base {len(base)}  remendo {len(pw)}")
