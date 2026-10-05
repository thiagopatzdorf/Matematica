#!/usr/bin/env python3
"""Certificados de inviabilidade por programação linear para as instâncias da fatia mínima.

Cada instância (s*, K, t) de `tools/exatos/gaps2` (redução e prova de completude em
docs/exatos/GAPS2_K362.md) é o sistema 0-1 sobre z_c, c em Z_q^n:

  cobertura  sum_{d(c,x) <= R} z_c >= 1                 (uma linha por x)
  fibras     sum_{c_j = a} z_c >= s*                    (j = 1..n-1, a = 0..q-1)
  tamanho    sum_c z_c = M ;  blocos  sum_{c_0 = b} z_c = t_b   (b = 1..q-1)
  fatia 0    z_c fixo (1 se c = (0,k) com k em K, 0 nas outras palavras com c_0 = 0)

Certificado de Farkas (inteiro): y >= 0 nas linhas ">=", mu livre nas linhas "=". Com
g = y^T G + mu^T E, todo z em [lb, ub] que satisfaz o sistema tem
  y.h + mu.e <= g.z <= sum_c max(g_c lb_c, g_c ub_c).
Se y.h + mu.e > sum_c max(...), o sistema não tem solução nem fracionária. Quando a raiz não
basta, ramifica em z_c = 1 / z_c = 0 (vale porque z é 0-1) e certifica cada folha.
A conferência exata, sem numpy, está em `verificar.py`.
"""
import argparse
import gzip
import itertools
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, hstack, identity, vstack

ESCALAS = (1, 2, 3, 4, 5, 6, 8, 10, 12, 20, 30, 60, 100, 1000, 10**4, 10**5, 10**6, 10**8)


def sistema(q, n, R, M, s, K, t):
    P = np.array(list(itertools.product(range(q), repeat=n)))
    N = len(P)
    D = (P[:, None, :] != P[None, :, :]).sum(2)
    G = [(D <= R).astype(float)]
    h = [np.ones(N)]
    if s > 0:
        G.append(np.array([P[:, j] == a for j in range(1, n) for a in range(q)], float))
        h.append(np.full((n - 1) * q, float(s)))
    E = np.vstack([np.ones((1, N))] + [(P[:, 0] == b)[None].astype(float) for b in range(1, q)])
    e = np.array([M] + list(t), float)
    fixos = {(0,) + tuple(k) for k in K}
    lb, ub = np.zeros(N), np.ones(N)
    for i, p in enumerate(map(tuple, P)):
        if p[0] == 0:
            lb[i] = ub[i] = 1.0 if p in fixos else 0.0
    return np.vstack(G), np.concatenate(h), E, e, lb, ub


def _dual(G, h, E, e, lb, ub):
    """max y.h + mu.e - sum_c u_c, com u_c >= g_c ub_c, u_c >= g_c lb_c, sum y <= 1."""
    N, ng, ne = G.shape[1], len(h), len(e)
    GT = csr_matrix(np.hstack([G.T, E.T]))
    I = identity(N, format="csr")
    A = vstack([hstack([GT.multiply(ub[:, None]), -I]), hstack([GT.multiply(lb[:, None]), -I]),
                csr_matrix(np.r_[np.ones(ng), np.zeros(ne + N)][None])]).tocsr()
    b = np.r_[np.zeros(2 * N), 1.0]
    c = -np.r_[h, e, -np.ones(N)]
    r = linprog(c, A_ub=A, b_ub=b, bounds=[(0, None)] * ng + [(None, None)] * (ne + N), method="highs")
    return -r.fun, r.x[:ng], r.x[ng:ng + ne]


def folga_exata(G, h, E, e, lb, ub, y, mu):
    """Lado esquerdo menos direito do certificado, em inteiros (> 0 = inviável)."""
    if (y < 0).any():
        return -1  # y < 0 não é multiplicador válido de linha ">=" (erro real: piso de -1e-12)
    Gi, Ei = G.astype(np.int64), E.astype(np.int64)
    g = Gi.T @ y + Ei.T @ mu
    lhs = int(y @ h.astype(np.int64)) + int(mu @ e.astype(np.int64))
    return lhs - int(np.maximum(g * ub.astype(np.int64), g * lb.astype(np.int64)).sum())


def _inteiro(sis, lb, ub, y, mu):
    for esc in ESCALAS:
        yi = np.maximum(np.floor(y * esc + 1e-9), 0).astype(np.int64)
        mi = np.round(mu * esc).astype(np.int64)
        if folga_exata(*sis[:4], lb, ub, yi, mi) > 0:
            return yi, mi
    return None


def certificar(sis, lb=None, ub=None, fixos=(), prof=0, prof_max=12):
    """Lista de folhas [(fixos, y, mu)], ou None se achar solução inteira (ou desistir)."""
    lb = sis[4] if lb is None else lb
    ub = sis[5] if ub is None else ub
    v, y, mu = _dual(*sis[:4], lb, ub)
    if v > 1e-9:
        r = _inteiro(sis, lb, ub, y, mu)
        if r:
            return [(list(fixos), r[0], r[1])]
    G, h, E, e = sis[:4]
    p = linprog(np.zeros(G.shape[1]), A_ub=-G, b_ub=-h, A_eq=E, b_eq=e,
                bounds=list(zip(lb, ub)), method="highs")
    if p.status != 0 or prof >= prof_max:
        return None
    livres = np.where(lb < ub)[0]
    j = int(livres[np.argmin(np.abs(p.x[livres] - 0.5))])
    if abs(p.x[j] - 0.5) > 0.499:
        return None  # solução inteira: a instância é viável
    folhas = []
    for val in (1, 0):
        l2, u2 = lb.copy(), ub.copy()
        l2[j] = u2[j] = val
        sub = certificar(sis, l2, u2, fixos + ((j, val),), prof + 1, prof_max)
        if sub is None:
            return None
        folhas += sub
    return folhas


def _registro(args):
    q, n, R, M, i, (s, K, t) = args
    folhas = certificar(sistema(q, n, R, M, s, K, t))
    reg = {"inst": i, "s": s, "K": [list(k) for k in K], "t": list(t)}
    if folhas is None:
        reg["folhas"] = None
    else:
        reg["folhas"] = [{"fixos": f, "y": {str(k): int(v) for k, v in enumerate(y) if v},
                          "mu": [int(v) for v in mu]} for f, y, mu in folhas]
    return reg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("q", "n", "R", "M"):
        ap.add_argument("--" + k, type=int, required=True)
    ap.add_argument("--instancias", required=True, help="JSON de rodar_pb.py --listar")
    ap.add_argument("--saida", required=True, help=".jsonl.gz")
    ap.add_argument("-j", type=int, default=2)
    a = ap.parse_args()
    ins = json.load(open(a.instancias))
    tarefas = [(a.q, a.n, a.R, a.M, i, x) for i, x in enumerate(ins)]
    ruins = []
    with ProcessPoolExecutor(a.j) as ex, gzip.open(a.saida, "wt") as f:
        for reg in ex.map(_registro, tarefas, chunksize=8):
            f.write(json.dumps(reg, separators=(",", ":")) + "\n")
            if reg["folhas"] is None:
                ruins.append(reg["inst"])
                print("sem certificado:", reg["inst"], flush=True)
    print(f"{len(ins)} instâncias, {len(ins) - len(ruins)} certificadas, sem certificado: {ruins}")
    sys.exit(1 if ruins else 0)


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "gaps2"))
    main()
