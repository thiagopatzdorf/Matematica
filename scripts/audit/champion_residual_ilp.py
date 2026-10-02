#!/usr/bin/env python3
"""Cota inferior VÁLIDA para o remendo da base campeã, por relaxação agregada.

Ideia: palavras de cobertura alta (tot >= THR) entram explicitamente (x_w binário); as demais
(cobertura <= c_low) são trocadas por um só inteiro y e por folgas z_p em [0,1]:
    min sum x_w + y   s.a.  sum_{w alta, w cobre p} x_w + z_p >= 1  (p em P),   sum_p z_p <= c_low * y.
Todo remendo verdadeiro dá uma solução viável (x = altas usadas, y = baixas usadas, z_p = 1 se p
só é coberto por baixas), então o ótimo (ou o dual bound do B&B) é cota inferior do remendo.
Quebra de simetria válida: se nenhuma palavra de cobertura 24 é usada, |W| >= 2058/19 > 108;
senão uma translação por C0 (preserva P e os tipos) leva uma delas para a = 000, então
sum_k x_{(sigma_k, a=0)} >= 1.

Uso: python3 champion_residual_ilp.py THR TEMPO_S [--lp]
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import scipy.sparse as sp
from scipy.optimize import Bounds, LinearConstraint, milp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import champion_lib as L  # noqa: E402
from champion_residual import offsets_by_syndrome, setup  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "data", "audit", "champion")
TRANS = np.array([[a % 7, (a // 7) % 7, a // 49] for a in range(343)])


def build(thr):
    A, H, Nb, O, cov = setup()
    tot = cov.sum(1)
    types = np.nonzero(tot >= thr)[0]
    c_low = int(tot[tot < thr].max())
    E, S = offsets_by_syndrome(H)
    st = np.searchsorted(S, np.arange(L.NS))
    en = np.searchsorted(S, np.arange(L.NS), side="right")
    rows, cols = [], []
    j = 0
    zero_cols = []
    for s in types:
        pats = []
        for i, t in enumerate(O):
            d = L.s2i(L.i2s(int(t)) - L.i2s(int(s)))
            off = E[st[d]:en[d], 6:9]
            pats.append((i, off))
        for a in range(343):
            if a == 0 and tot[s] == 24:
                zero_cols.append(j)
            for i, off in pats:
                b = (TRANS[a] + off) % 7
                idx = i * 343 + b[:, 0] + 7 * b[:, 1] + 49 * b[:, 2]
                rows.extend(idx.tolist())
                cols.extend([j] * len(idx))
            j += 1
    nx = j
    M = sp.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(2058, nx))
    M.data[:] = 1  # duplicatas viram 1
    return M, nx, c_low, zero_cols, types, tot


def main():
    thr = int(sys.argv[1])
    tlim = float(sys.argv[2])
    lp = "--lp" in sys.argv
    M, nx, c_low, zero_cols, types, tot = build(thr)
    P = 2058
    # variáveis: x (nx), z (P), y (1)
    n = nx + P + 1
    c = np.concatenate([np.ones(nx), np.zeros(P), [1.0]])
    A1 = sp.hstack([M, sp.identity(P), sp.csr_matrix((P, 1))])
    A2 = sp.hstack([sp.csr_matrix((1, nx)), sp.csr_matrix(np.ones((1, P))), sp.csr_matrix([[-float(c_low)]])])
    sb = np.zeros((1, n))
    sb[0, zero_cols] = 1
    A3 = sp.csr_matrix(sb)
    cons = [LinearConstraint(A1, 1, np.inf), LinearConstraint(A2, -np.inf, 0), LinearConstraint(A3, 1, np.inf)]
    integ = np.concatenate([np.ones(nx), np.zeros(P), [1]])
    if lp:
        integ = np.zeros(n)
    ub = np.concatenate([np.ones(nx + P), [np.inf]])
    t0 = time.time()
    res = milp(c, constraints=cons, integrality=integ, bounds=Bounds(0, ub),
               options={"time_limit": tlim, "disp": True, "mip_rel_gap": 0})
    out = {"thr": thr, "n_types": int(len(types)), "n_x": nx, "c_low": c_low, "lp_only": lp,
           "status": int(res.status), "message": res.message, "secs": time.time() - t0,
           "primal": None if res.x is None else float(res.fun),
           "dual_bound": getattr(res, "mip_dual_bound", None)}
    if res.x is not None:
        x = res.x
        out["n_high_used"] = int(round(x[:nx].sum()))
        out["y"] = float(x[-1])
    name = f"ilp_thr{thr}{'_lp' if lp else ''}.json"
    with open(os.path.join(OUT, name), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
