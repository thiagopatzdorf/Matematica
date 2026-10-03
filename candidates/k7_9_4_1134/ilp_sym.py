#!/usr/bin/env python3
"""ilp_sym.py -- remendo mínimo da base campeã com simetria imposta: invariância por um subgrupo G
de translações por palavras de C0 (G = reta ou plano de F_7^3 no espaço das mensagens m).
Variáveis = órbitas de palavras (cobertura >= T), restrições = órbitas de pontos de P.
Uso: ilp_sym.py T {line|plane} idx tempo_s"""
import sys, itertools, time, json
import numpy as np, highspy
Q, N = 7, 9; POW = np.array([Q**j for j in range(N)], dtype=np.int64)
A = np.array([[int(c) for c in r] for r in "666 065 652 643 621 615".split()])
ORPH = None
def enc(v): return (np.asarray(v) % Q) @ POW
def dec(i): return np.array([(i // Q**j) % Q for j in range(N)])
H = np.hstack([np.eye(6, dtype=int), A])
def cw(m): m = np.array(m); return np.concatenate([(-A @ m) % Q, m])
# subespaços de F_7^3 (representantes normalizados)
def norm(v):
    v = [x % Q for x in v]; i = next(k for k, x in enumerate(v) if x); inv = pow(v[i], -1, Q); return tuple((x * inv) % Q for x in v)
pts = sorted({norm(v) for v in itertools.product(range(Q), repeat=3) if any(v)})   # 57 pontos = retas
def plane_basis(nrm):  # plano = {m : nrm.m = 0}
    B = [v for v in itertools.product(range(Q), repeat=3) if any(v) and sum(a*b for a, b in zip(v, nrm)) % Q == 0]
    b1 = B[0]; b2 = next(v for v in B if norm(v) != norm(b1)); return [b1, b2]
T, kind, idx, tlim = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
gens = [pts[idx]] if kind == "line" else plane_basis(pts[idx])
G = [enc(sum((c * cw(g) for c, g in zip(cs, gens)), np.zeros(N, int))) for cs in itertools.product(range(Q), repeat=len(gens))]
Gv = np.array([dec(g) for g in G])                     # vetores de translação
# P e cobertura
P = np.load("P.npy"); pairs_w = np.load("pairs_w.npy"); pairs_p = np.load("pairs_p.npy"); covw = np.load("covw.npy")
def orbit_min(idxs):
    V = np.stack([(idxs // Q**j) % Q for j in range(N)], 1)
    best = idxs.copy()
    for g in Gv[1:]:
        best = np.minimum(best, ((V + g) % Q) @ POW)
    return best
sel = covw[pairs_w] >= T
pw_, pp_ = pairs_w[sel], pairs_p[sel]
wo = orbit_min(pw_); po = orbit_min(P)[pp_]          # órbita da palavra, órbita do ponto
# restrição por órbita de ponto: escolhe o representante = o próprio min; conta pares (orbita_w, rep_p)
rep_mask = P[pp_] == po                               # só linhas do representante de cada órbita de ponto
wo, po = wo[rep_mask], po[rep_mask]
uw, wi = np.unique(wo, return_inverse=True); up, pi = np.unique(po, return_inverse=True)
key = wi.astype(np.int64) * len(up) + pi; uk, cnt = np.unique(key, return_counts=True)
cols, rows = uk // len(up), uk % len(up)
osize = len(G)
h = highspy.Highs(); h.setOptionValue("output_flag", False); h.setOptionValue("time_limit", tlim)
inf = highspy.kHighsInf
nv = len(uw)
h.addVars(nv, np.zeros(nv), np.ones(nv) * 3)
h.changeColsCost(nv, np.arange(nv, dtype=np.int32), np.ones(nv) * osize)
h.changeColsIntegrality(nv, np.arange(nv, dtype=np.int32), np.array([highspy.HighsVarType.kInteger] * nv))
order = np.argsort(rows, kind="stable"); r_s, c_s, v_s = rows[order], cols[order], cnt[order]
starts = np.searchsorted(r_s, np.arange(len(up)))
h.addRows(len(up), np.ones(len(up)), np.full(len(up), inf), len(r_s), starts.astype(np.int32), c_s.astype(np.int32), v_s.astype(float))
t0 = time.time(); h.run()
info = h.getInfo(); st = h.modelStatusToString(h.getModelStatus())
obj = info.objective_function_value; db = info.mip_dual_bound
out = {"kind": kind, "idx": idx, "gens": gens, "orbit": osize, "T": T, "vars": nv, "rows": len(up), "status": st, "obj": obj, "dual_bound": db, "secs": round(time.time() - t0, 1)}
if h.getInfo().primal_solution_status == 2:
    x = np.round(h.getSolution().col_value).astype(int)
    words = []
    for j in np.flatnonzero(x):
        base = dec(uw[j])
        for _ in range(x[j]):
            words += [enc((base + g) % Q) for g in Gv]
    words = sorted(set(int(w) for w in words))
    out["patch_size"] = len(words)
    open(f"sym_{kind}{idx}_T{T}_{len(words)}.txt", "w").write("".join("".join(str(d) for d in dec(w)) + "\n" for w in words))
print(json.dumps(out), flush=True)
