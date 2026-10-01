#!/usr/bin/env python3
"""Gerador de ensaio (4a): parte a busca de root n m na profundidade d em pedaços.
uso: gen_demo.py n m d outdir prefix [agrupar=K]
Escreve <outdir>/<prefix>_Chunk_<k>.lean (cada um com até K teoremas `chkN n [] (l+1) s = true`)
e <outdir>/<prefix>_Top.lean com `chkN n [s_1..s_M] d (root n m) = true` e a montagem `Ref n (root n m)`.
Imprime estatísticas (nós por pedaço) em JSON.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sc_ref import run, root

n, m, d, out, pre = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5]
K = int(sys.argv[6]) if len(sys.argv) > 6 else 1
fr, st = [], [0]
assert run(n, root(n, m), d, fr, st)
sizes = []
for s in fr:
    c = [0]
    assert run(n, tuple(s), s[0] + 1, [], c)
    sizes.append(c[0])
groups = [list(range(i, min(i + K, len(fr)))) for i in range(0, len(fr), K)]
os.makedirs(out, exist_ok=True)
fn = "chkN %d" % n
for g, idx in enumerate(groups):
    with open(os.path.join(out, "%s_Chunk_%d.lean" % (pre, g)), "w") as f:
        f.write("import CoveringLean.SearchCore\nopen SC\n\nnamespace %s\n\n" % pre)
        for i in idx:
            l, cov, forb = fr[i]
            f.write("theorem c%d : %s [] %d ⟨%d, %d, %d⟩ = true := by decide +kernel\n" % (i, fn, l + 1, l, cov, forb))
        f.write("\nend %s\n" % pre)
with open(os.path.join(out, "%s_Top.lean" % pre), "w") as f:
    f.write("import CoveringLean.SearchSound\n")
    for g in range(len(groups)):
        f.write("import CoveringLean.%s_Chunk_%d\n" % (pre, g))
    f.write("open SC\n\nnamespace %s\n\n" % pre)
    f.write("/-- fronteira na profundidade %d, em ordem DFS -/\ndef S : List St := [\n" % d)
    f.write(",\n".join("  ⟨%d, %d, %d⟩" % tuple(s) for s in fr))
    f.write("]\n\ntheorem top : %s S %d (root %d %d) = true := by decide +kernel\n\n" % (fn, d, n, m))
    f.write("theorem ref : Ref %d (root %d %d) := by\n  refine chkN_sound %d S %d _ top ?_\n" % (n, n, m, n, d))
    f.write("  intro t ht\n  simp only [S, List.mem_cons, List.not_mem_nil, or_false] at ht\n")
    f.write("  rcases ht with " + " | ".join(["rfl"] * len(fr)) + "\n")
    for i in range(len(fr)):
        f.write("  · exact chkN_sound %d [] _ _ c%d (by simp)\n" % (n, i))
    f.write("\nend %s\n\n#print axioms %s.ref\n" % (pre, pre))
print(json.dumps({"root_nodes_to_depth": st[0], "frontier": len(fr), "files": len(groups),
                  "chunk_nodes_total": sum(sizes), "chunk_nodes_max": max(sizes) if sizes else 0}))
