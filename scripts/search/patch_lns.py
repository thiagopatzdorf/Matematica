#!/usr/bin/env python3
"""patch_lns.py -- busca em vizinhança grande (LNS) com ILP exato para o remendo.

Uso: patch_lns.py base.json sol.json segundos semente prefixo [k=24] [tau=12]

Congela a base (classes laterais), parte de uma solução completa (palavras soltas, formato
do patch_opt) e repete: tira k palavras (todas as que cobrem a vizinhança de um ponto
sorteado do resíduo), e resolve EXATAMENTE (HiGHS via scipy.optimize.milp) a cobertura
mínima dos pontos que ficaram descobertos, usando como colunas todas as palavras com
>= tau pontos do resíduo que tocam esses pontos. Se o ótimo do subproblema for < k, a
solução encolhe; se for == k, aceita a troca (anda no platô). Cada melhoria grava
prefixo_M<M>.json (mesmo formato do patch_opt; verificar com expand.py + verify.py).

Requer numpy, scipy (>= 1.9) e highspy.
"""
import itertools
import json
import sys
import time

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csc_matrix


def main():
    base = json.load(open(sys.argv[1]))
    sol = json.load(open(sys.argv[2]))
    secs, seed, pref = float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    k = int(sys.argv[6]) if len(sys.argv) > 6 else 24
    tau = int(sys.argv[7]) if len(sys.argv) > 7 else 12
    rng = np.random.default_rng(seed)
    q, n, R = base["q"], base["n"], base["R"]
    A = [[int(c) for c in r] for r in base["A"].split()]
    r, kk = len(A), len(A[0])
    pw = q ** np.arange(n, dtype=np.int64)
    E = []
    for w in range(R + 1):
        for pos in itertools.combinations(range(n), w):
            for vals in itertools.product(range(1, q), repeat=w):
                e = [0] * n
                for p, v in zip(pos, vals):
                    e[p] = v
                E.append(e)
    E = np.array(E, dtype=np.int64)

    def digits(x):
        return (np.asarray(x, dtype=np.int64)[..., None] // pw) % q

    def ball(xint):
        return (((digits(xint) + E) % q) * pw).sum(1)

    # base
    C = [[(-sum(A[i][j] * u[j] for j in range(kk))) % q for i in range(r)] + list(u)
         for u in itertools.product(range(q), repeat=kk)]
    C = np.array(C, dtype=np.int64)
    basew = []
    for s in base["coset_syndromes"]:
        d = np.array([(s // q ** i) % q for i in range(r)] + [0] * kk)
        basew += list((((d + C) % q) * pw).sum(1))
    N = q ** n
    cov = np.zeros(N, dtype=bool)
    for w in basew:
        cov[ball(w)] = True
    resid = np.flatnonzero(~cov)
    P = len(resid)
    pidx = np.full(N, -1, dtype=np.int32)
    pidx[resid] = np.arange(P, dtype=np.int32)
    del cov
    cnt = np.zeros(N, dtype=np.uint16)
    balls_p = []
    for p in resid:
        b = ball(p)
        balls_p.append(b)
        cnt[b] += 1
    t0 = time.time()
    print(f"resíduo {P} pontos; cobertura máx {cnt.max()}", flush=True)
    # candidatos e listas ponto -> candidatos
    cand_words = np.flatnonzero(cnt >= tau)
    cid = np.full(N, -1, dtype=np.int32)
    cid[cand_words] = np.arange(len(cand_words), dtype=np.int32)
    p2c = [cid[b][cid[b] >= 0] for b in balls_p]
    del balls_p
    print(f"{len(cand_words)} candidatos (tau={tau}) em {time.time() - t0:.0f}s", flush=True)

    def cover_list(w):
        b = ball(w)
        x = pidx[b]
        return x[x >= 0]

    cur = [int(sum(int(c) * q ** i for i, c in enumerate(s))) for s in sol["words"]]
    pcov = np.zeros(P, dtype=np.int32)
    lists = {}
    for w in cur:
        lists[w] = cover_list(w)
        pcov[lists[w]] += 1
    assert (pcov > 0).all(), "solução inicial não cobre o resíduo"
    M0 = len(basew) + len(cur)
    print(f"início: M={M0}", flush=True)
    clist_cache = {}

    def cand_cover(c):
        if c not in clist_cache:
            clist_cache[c] = cover_list(int(cand_words[c]))
        return clist_cache[c]

    it = 0
    while time.time() - t0 < secs:
        it += 1
        p0 = rng.integers(P)
        # vizinhança: palavras que cobrem p0 e os pontos que elas cobrem, até k palavras
        near = [w for w in cur if p0 in set(lists[w].tolist())]
        pts = set()
        for w in near:
            pts.update(lists[w].tolist())
        ranked = sorted(cur, key=lambda w: -len(pts.intersection(lists[w].tolist())))
        rem = ranked[:k]
        for w in rem:
            pcov[lists[w]] -= 1
        U = np.flatnonzero(pcov == 0)
        if len(U) == 0:
            for w in rem:
                pcov[lists[w]] += 1
            continue
        allc = [p2c[u] for u in U]
        cols, inv = np.unique(np.concatenate(allc), return_inverse=True)
        rows = np.repeat(np.arange(len(U)), [len(x) for x in allc])
        cc = inv
        # colunas que tocam >= 2 pontos de U (as de 1 ponto são dominadas por qualquer
        # outra que cubra o mesmo ponto e mais algum; mantém se o ponto ficaria sem coluna)
        deg = np.bincount(cc, minlength=len(cols))
        keep = deg >= 2
        rows_keep = keep[cc]
        if np.all(np.bincount(rows[rows_keep], minlength=len(U)) > 0):
            newidx = np.cumsum(keep) - 1
            rows, cc, cols = rows[rows_keep], newidx[cc[rows_keep]], cols[keep]
        Am = csc_matrix((np.ones(len(rows)), (rows, cc)), shape=(len(U), len(cols)))
        t_ilp = time.time()
        res = milp(c=np.ones(len(cols)), constraints=LinearConstraint(Am, lb=1, ub=np.inf),
                   integrality=np.ones(len(cols)), bounds=Bounds(0, 1),
                   options={"time_limit": 20, "disp": False, "presolve": True})
        chosen = []
        if res.x is None or res.status not in (0, 1):
            for w in rem:
                pcov[lists[w]] += 1
            continue
        chosen = [int(cand_words[cols[j]]) for j in np.flatnonzero(res.x > 0.5)]
        if len(chosen) <= len(rem):
            cur = [w for w in cur if w not in set(rem)] + chosen
            for w in chosen:
                lists[w] = cover_list(w)
                pcov[lists[w]] += 1
            M = len(basew) + len(cur)
            assert (pcov > 0).all()
            if len(chosen) < len(rem):
                ws = ["".join(str((w // q ** i) % q) for i in range(n)) for w in cur]
                out = dict(q=q, n=n, R=R, M=M, A=base["A"], coset_syndromes=base["coset_syndromes"], words=ws)
                json.dump(out, open(f"{pref}_M{M}.json", "w"))
                print(f"it={it} MELHORA M={M} (|U|={len(U)}, cols={len(cols)}, {time.time() - t0:.0f}s)", flush=True)
        else:
            for w in rem:
                pcov[lists[w]] += 1
        print(f"it={it} M={len(basew) + len(cur)} t_ilp={time.time() - t_ilp:.1f} sub={len(chosen) if res.x is not None else -1}/{len(rem)} U={len(U)} cols={len(cols)} ({time.time() - t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
