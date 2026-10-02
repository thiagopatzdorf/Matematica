#!/usr/bin/env python3
"""Seção B da auditoria: o remendo (residual) da base campeã de K_7(9,4), formulado de forma exata.

P = união das 6 classes laterais órfãs (6*343 = 2058 palavras). Fato usado em tudo: a quantidade
de pontos da classe lateral t cobertos por uma palavra w depende só da síndrome sigma = Hw:
|Ball(w,4) ∩ (classe t)| = Nb[t - sigma], Nb[d] = #{e : wt(e)<=4, He=d}. Assim as 7^9 bolas
caem em 117649 tipos (um por síndrome), cada tipo com 343 translações por C0.

Grava data/audit/champion/residual.json. Sem amostragem: as contagens são exaustivas.
"""
from __future__ import annotations

import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import champion_lib as L  # noqa: E402

Q = 7
OUT = os.path.join(HERE, "..", "..", "data", "audit", "champion")
ASTR = "666 065 652 643 621 615"
TRIO = (0, 4191, 7708)
P1137 = "/home/user/Matematica/data/structured/q7_n9_R4_M1137.json"


def setup():
    A = L.parse_A(ASTR)
    H = L.H_of(A)
    Nb = L.ball_counts(H)
    O = L.orphans(Nb > 0, TRIO)
    # cov[sigma, i] = pontos da órfã O[i] cobertos por uma palavra de síndrome sigma
    sig = np.arange(L.NS)
    cov = np.stack([Nb[L.add_tab(np.full(L.NS, int(t)), L.neg(sig))] for t in O], axis=1)
    return A, H, Nb, O, cov


def word_syndrome(H, w):
    return L.s2i(H @ np.array([int(c) for c in w]))


def main():
    os.makedirs(OUT, exist_ok=True)
    A, H, Nb, O, cov = setup()
    rep = {"A": ASTR, "trio": list(TRIO), "orphan_syndromes": O.tolist(), "P_size": int(343 * len(O))}
    tot = cov.sum(1)
    cmax = int(tot.max())
    rep["max_points_of_P_in_one_ball"] = cmax
    rep["hist_ball_coverage_by_syndrome_type"] = {str(k): int((tot == k).sum()) for k in range(cmax + 1) if (tot == k).sum()}
    rep["words_with_coverage_k"] = {k: 343 * v for k, v in rep["hist_ball_coverage_by_syndrome_type"].items()}
    supp = (cov > 0).sum(1)
    rep["hist_number_of_orphan_cosets_touched"] = {str(k): int((supp == k).sum()) * 343 for k in range(7)}
    rep["max_coverage_single_orphan_coset"] = int(cov.max())
    rep["per_orphan_max"] = cov.max(0).tolist()
    rep["words_touching_each_orphan_coset"] = [int((cov[:, i] > 0).sum()) * 343 for i in range(len(O))]
    rep["words_touching_exactly_one_orphan_coset"] = int((supp == 1).sum()) * 343
    rep["hist_types_by_coverage_of_orphan0"] = np.bincount(cov[:, 0]).tolist()
    # perfis de cobertura dos tipos máximos
    best = np.nonzero(tot == cmax)[0]
    prof = {}
    for s in best:
        k = tuple(sorted(cov[s].tolist(), reverse=True))
        prof[str(k)] = prof.get(str(k), 0) + 1
    rep["profiles_of_max_coverage_types"] = prof
    rep["max_coverage_types"] = best.tolist()
    from champion_structure import rank_mod
    V = [L.i2s(int(x)) for x in best]
    rep["max_coverage_types_affine_span_dim"] = int(rank_mod([(v - V[0]) % Q for v in V[1:]]))
    rep["max_coverage_types_centroid"] = "".join(map(str, (sum(V) * pow(len(V), Q - 2, Q)) % Q))
    rep["max_coverage_types_touching_all_6"] = int(((tot == cmax) & (supp == 6)).sum())
    # perfis por número de classes tocadas: cobertura máxima conjunta
    rep["max_total_given_touched"] = {str(k): int(tot[supp == k].max()) if (supp == k).any() else 0 for k in range(7)}
    # cotas
    P = 343 * len(O)
    rep["LB_trivial"] = int(-(-P // cmax))
    # LP: por simetria (translações por C0 e o grupo da base, transitivo nas 6 órfãs; ver structure.json)
    # o dual u_p = 1/cmax é viável (toda bola tem <= cmax pontos de P) e o primal simetrizado de uma
    # bola de cobertura máxima atinge P/cmax. Confere numericamente com o LP agregado de 6 linhas.
    from scipy.optimize import linprog
    cand = np.nonzero(tot > 0)[0]
    res = linprog(np.ones(len(cand)), A_ub=-cov[cand].T.astype(float), b_ub=-343.0 * np.ones(len(O)),
                  bounds=(0, None), method="highs")
    rep["LP_aggregated_value"] = float(res.fun)
    rep["LP_exact_value"] = f"{P}/{cmax} = {P / cmax}"
    rep["LP_dual_certificate"] = f"u_p = 1/{cmax} para todo p em P; viabilidade = max_sigma sum_t Nb[t-sigma] = {cmax}"
    # melhor solução conhecida (remendo do 1137)
    d = json.load(open(P1137))
    W = d["patch_words"]
    rep["UB_patch_size"] = len(W)
    # confere que o remendo cobre P inteiro (ponto a ponto)
    covered = verify_patch(H, Nb, O, W)
    rep["UB_patch_covers_P"] = covered
    ws = [word_syndrome(H, w) for w in W]
    rep["UB_patch_coverage_hist"] = {str(k): int(v) for k, v in zip(*np.unique(tot[ws], return_counts=True))}
    rep["UB_patch_sum_of_coverage"] = int(tot[ws].sum())
    rep["UB_patch_excess_multiplicity"] = int(tot[ws].sum()) - P
    rep["gap_UB_minus_LB"] = len(W) - rep["LB_trivial"]
    with open(os.path.join(OUT, "residual.json"), "w") as f:
        json.dump(rep, f, indent=1)
    print(json.dumps(rep, indent=1))


def offsets_by_syndrome(H):
    """dict d -> array (m,3) com e[6:9] de cada e de peso <= 4 e He = d."""
    es = []
    for w in range(5):
        for supp in itertools.combinations(range(9), w):
            for vals in itertools.product(range(1, Q), repeat=w):
                e = [0] * 9
                for j, v in zip(supp, vals):
                    e[j] = v
                es.append(e)
    E = np.array(es, dtype=np.int64)
    S = ((E @ H.T) % Q) @ L.POW
    order = np.argsort(S, kind="stable")
    return E[order], S[order]


def coset_point_index(x):
    """índice do ponto x (9 dígitos) dentro da sua classe: as 3 coordenadas de informação."""
    return int(x[6] + 7 * x[7] + 49 * x[8])


def verify_patch(H, Nb, O, W):
    E, S = offsets_by_syndrome(H)
    starts = np.searchsorted(S, np.arange(L.NS))
    ends = np.searchsorted(S, np.arange(L.NS), side="right")
    pos = {int(t): i for i, t in enumerate(O)}
    hit = np.zeros((len(O), 343), dtype=bool)
    for w in W:
        x = np.array([int(c) for c in w])
        for t, i in pos.items():
            dd = L.s2i(L.i2s(t) - H @ x)
            blk = E[starts[dd]:ends[dd]]
            pts = (x[None, :] + blk) % Q
            hit[i, pts[:, 6] + 7 * pts[:, 7] + 49 * pts[:, 8]] = True
    return bool(hit.all())


if __name__ == "__main__":
    main()
