#!/usr/bin/env python3
"""precompute.py -- P (2058 órfãs da base campeã) e pares (palavra, ponto de P) com cobertura >= 12."""
import itertools, numpy as np
POW = np.array([7**j for j in range(9)], dtype=np.int64)
A = np.array([[int(c) for c in r] for r in "666 065 652 643 621 615".split()])
H = np.hstack([np.eye(6, dtype=np.int64), A]); SP = np.array([7**i for i in range(6)])
allx = np.arange(7**9, dtype=np.int64)
V = np.stack([(allx // 7**j) % 7 for j in range(9)], 1).astype(np.int8)
syn = ((V.astype(np.int64) @ H.T) % 7) @ SP
P = np.flatnonzero(np.isin(syn, [19141, 37272, 63434, 75935, 89846, 111459])); assert len(P) == 2058
E = []
for w in range(5):
    for pos in itertools.combinations(range(9), w):
        for vals in itertools.product(range(1, 7), repeat=w):
            e = [0] * 9
            for p, v in zip(pos, vals): e[p] = v
            E.append(e)
E = np.array(E, dtype=np.int64)
covw = np.zeros(7**9, dtype=np.int64); PW = []; PP = []
for i, p in enumerate(P):
    b = ((V[p].astype(np.int64) + E) % 7) @ POW
    covw[b] += 1; PW.append(b.astype(np.int32)); PP.append(np.full(len(b), i, dtype=np.int32))
PW = np.concatenate(PW); PP = np.concatenate(PP); keep = covw[PW] >= 12
np.save("P.npy", P); np.save("pairs_w.npy", PW[keep]); np.save("pairs_p.npy", PP[keep]); np.save("covw.npy", covw.astype(np.int16))
print("ok", keep.sum())
