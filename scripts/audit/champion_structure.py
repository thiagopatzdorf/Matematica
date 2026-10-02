#!/usr/bin/env python3
"""Seção A da auditoria: estrutura do código C0 = [9,3]_7 da base campeã (e de outras bases).

Uso: python3 champion_structure.py  -> grava data/audit/champion/structure.json
Calcula, de forma exata: distribuição de pesos, pontos em PG(2,7) e retas, cônicas, estabilizador
em PGL(3,7) (força bruta sobre referenciais), grupo monomial induzido no espaço de síndromes,
grupo da base (fixa o conjunto das 3 síndromes, com translações), órbitas dos trios e das órfãs.
"""
from __future__ import annotations

import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audit_lib as AL  # noqa: E402
import champion_lib as L  # noqa: E402

Q = 7
OUT = os.path.join(HERE, "..", "..", "data", "audit", "champion")


def inv(a):
    return pow(int(a) % Q, Q - 2, Q)


def stab_pgl(cols):
    """Elementos g de PGL(3,7) com g(conjunto de pontos) = conjunto (pontos distintos assumidos).
    Devolve lista de (g, perm, lam): g col_j = lam_j col_perm[j]."""
    pts = [AL.point_index(c) for c in cols]
    assert len(set(pts)) == len(pts), "pontos repetidos"
    S = set(pts)
    frames = [f for f in itertools.permutations(range(len(pts)), 4)
              if AL.general_position([pts[i] for i in f])]
    f0 = frames[0]
    res, seen = [], set()
    for f in frames:
        g = AL.projectivity([pts[i] for i in f0], [pts[i] for i in f])
        if {AL.apply(g, p) for p in pts} != S:
            continue
        # normaliza g (1ª entrada não nula = 1) para deduplicar
        flat = [x for r in g for x in r]
        c = inv(next(x for x in flat if x % Q))
        key = tuple(x * c % Q for x in flat)
        if key in seen:
            continue
        seen.add(key)
        g = np.array(key).reshape(3, 3)
        perm, lam = [], []
        for j, cj in enumerate(cols):
            v = [int(x) for x in (g @ np.array(cj)) % Q]
            k = pts.index(AL.point_index(v))
            cc = np.array(cols[k])
            i0 = next(i for i in range(3) if cc[i])
            perm.append(k)
            lam.append(int(v[i0] * inv(cc[i0]) % Q))
        res.append((g, perm, lam))
    return res


def monomial_on_syndromes(H, perm, lam, mu=1):
    """Matriz 6x6 L com H M x = L H x, onde (M x)_{perm j} = mu * x_j / lam_j (preserva C0)."""
    n = H.shape[1]
    M = np.zeros((n, n), dtype=np.int64)
    for j in range(n):
        M[perm[j], j] = mu * inv(lam[j]) % Q
    HM = (H @ M) % Q
    Lm = HM[:, :6]  # base de síndromes = palavras unitárias e_0..e_5 (H=[I|A])
    # confere que vale para todas as colunas (i.e., C0 é preservado)
    assert np.array_equal((Lm @ H) % Q, HM), "M não preserva C0"
    return Lm


def apply_L(Lm, s):
    return L.s2i(Lm @ L.i2s(s))


def conics(pts_vec):
    """maior número de pontos do conjunto numa cônica não degenerada, e quantas atingem."""
    P = np.array(pts_vec)  # m x 3
    mons = np.stack([P[:, 0] ** 2, P[:, 1] ** 2, P[:, 2] ** 2, P[:, 0] * P[:, 1], P[:, 0] * P[:, 2], P[:, 1] * P[:, 2]], 1) % Q
    best, cnt = 0, {}
    for co in itertools.product(range(Q), repeat=6):
        nz = [x for x in co if x]
        if not nz or nz[0] != 1:
            continue
        a, b, c, d, e, f = co
        # matriz simétrica (2 invertível mod 7): [[2a,d,e],[d,2b,f],[e,f,2c]]
        Mx = [[2 * a, d, e], [d, 2 * b, f], [e, f, 2 * c]]
        if AL.det3(*Mx) == 0:
            continue
        k = int(((mons @ np.array(co)) % Q == 0).sum())
        cnt[k] = cnt.get(k, 0) + 1
        best = max(best, k)
    return best, cnt


def analyze(name, Astr, trios, extra_trios=(), orbit_sets=None):
    A = L.parse_A(Astr)
    H = L.H_of(A)
    G = L.G_of(A)
    rep = {"name": name, "A": Astr}
    wd = AL.weight_distribution(G.tolist())
    rep["weight_distribution"] = list(wd)
    rep["dmin"] = next(i for i in range(1, 10) if wd[i])
    rep["MDS_bound_n-k+1"] = 9 - 3 + 1
    cols = [tuple(int(x) for x in G[:, j]) for j in range(9)]
    pts = [AL.point_index(c) for c in cols]
    rep["points_PG27_auditlib_index"] = pts
    rep["repeated_points"] = len(pts) - len(set(pts))
    line_counts = [len(set(pts) & Lset) for Lset in AL.LINES]
    rep["line_incidence_histogram"] = {str(k): line_counts.count(k) for k in range(10) if line_counts.count(k)}
    rep["max_points_on_a_line"] = max(line_counts)
    rep["is_arc"] = max(line_counts) <= 2
    best, cnt = conics([AL.POINTS[p] for p in pts])
    rep["max_points_on_nondegenerate_conic"] = best
    rep["conic_hits_histogram"] = {str(k): v for k, v in sorted(cnt.items()) if k >= 4}
    rep.update(trisecant_details(cols, pts))
    # dual: [9,6] gerado por H
    rep["dual_weight_distribution"] = list(AL.weight_distribution(H.tolist()))
    # grupos
    st = stab_pgl(cols)
    rep["stab_PGL3_7"] = len(st)
    rep["monomial_aut_order"] = 6 * len(st)
    Ls = []
    for (g, perm, lam) in st:
        for mu in range(1, Q):
            Ls.append(monomial_on_syndromes(H, perm, lam, mu))
    rep["coordinate_permutations_in_aut"] = sorted({tuple(p) for (_, p, _) in st})[:50]
    rep["perm_group_on_coordinates_order"] = len({tuple(p) for (_, p, _) in st})
    # orbitas das coordenadas
    orb = []
    left = set(range(9))
    while left:
        j = min(left)
        o = {p[j] for (_, p, _) in st} | {j}
        o = {p[j] for (_, p, _) in st}
        orb.append(sorted(o))
        left -= o
    rep["coordinate_orbits"] = orb
    # tabelas de cobertura
    Nb = L.ball_counts(H)
    lw = L.leader_weights(H)
    rep["coset_leader_weight_hist"] = np.bincount(lw).tolist()
    rep["covering_radius_C0"] = int(lw.max())
    Bmask = Nb > 0
    rep["nBc"] = int((~Bmask).sum())
    rep["trios"] = []
    allt = list(trios) + list(extra_trios)
    for tr in allt:
        o = L.orphans(Bmask, tr)
        e = {"trio": list(tr), "n_orphans": int(len(o)), "orphans": o.tolist(),
             "orphan_leader_weights": lw[o].tolist()}
        # pesos das classes t - s para cada s do trio
        e["orphan_minus_s_weights"] = [[int(lw[L.add_tab(np.array([t]), L.neg(np.array([s])))[0]]) for s in tr] for t in o.tolist()]
        # estrutura afim: posto das diferenças
        if len(o) > 1:
            D = np.array([L.i2s(t) for t in o]) - L.i2s(o[0])
            e["affine_span_dim"] = int(rank_mod(D % Q))
            e["orphan_vectors"] = ["".join(map(str, L.i2s(t))) for t in o]
        # grupo da base: (Lm, c) com Lm S + c = S
        S = set(tr)
        gb = []
        for Lm in Ls:
            imgs = [apply_L(Lm, s) for s in tr]
            for s in tr:
                c = L.s2i(L.i2s(s) - L.i2s(imgs[0]))
                if {L.s2i(L.i2s(x) + L.i2s(c)) for x in imgs} == S:
                    gb.append((Lm, c))
        e["base_group_order_mod_C0_translations"] = len(gb)
        # ação nas órfãs
        oset = o.tolist()
        orbits, seen = [], set()
        for t in oset:
            if t in seen:
                continue
            ob = {L.s2i(Lm @ L.i2s(t) + L.i2s(c)) for (Lm, c) in gb}
            assert ob <= set(oset)
            orbits.append(sorted(ob))
            seen |= ob
        e["orphan_orbits_under_base_group"] = orbits
        # ação do grupo da base no trio (permutações induzidas)
        e["trio_perms_induced"] = sorted({tuple(tr.index(L.s2i(Lm @ L.i2s(s) + L.i2s(c))) for s in tr) for (Lm, c) in gb})
        rep["trios"].append(e)
        e["_gb"] = gb
    # relação entre trios pelo grupo afim (Ls x translações)
    rel = []
    for i, j in itertools.combinations(range(len(allt)), 2):
        Si, Sj = allt[i], set(allt[j])
        found = False
        for Lm in Ls:
            imgs = [apply_L(Lm, s) for s in Si]
            for s in Sj:
                c = L.s2i(L.i2s(s) - L.i2s(imgs[0]))
                if {L.s2i(L.i2s(x) + L.i2s(c)) for x in imgs} == Sj:
                    found = True
                    break
            if found:
                break
        rel.append({"pair": [i, j], "equivalent_under_Aut(C0)_and_translations": found})
    rep["trio_equivalences"] = rel
    if orbit_sets and rep["trios"]:
        gb = rep["trios"][0]["_gb"]
        rep["orbits_under_base_group_of_trio0"] = {}
        for nm, ss in orbit_sets.items():
            left, obs = set(ss), []
            while left:
                t0 = min(left)
                ob = {L.s2i(Lm @ L.i2s(t0) + L.i2s(c)) for (Lm, c) in gb}
                obs.append(sorted(ob))
                left -= ob
            rep["orbits_under_base_group_of_trio0"][nm] = obs
    # centro comum: média do trio, das órfãs e dos conjuntos extras
    if rep["trios"]:
        e0 = rep["trios"][0]
        def cen(ss):
            v = sum(L.i2s(x) for x in ss) * inv(len(ss)) % Q
            return "".join(map(str, v))
        rep["centroids"] = {"trio0": cen(e0["trio"]), "orphans0": cen(e0["orphans"])}
        for nm, ss in (orbit_sets or {}).items():
            rep["centroids"][nm] = cen(ss)
    for e in rep["trios"]:
        e.pop("_gb")
    return rep, H, Nb, lw


def _cross(a, b):
    return AL.normalize((a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]))


def trisecant_details(cols, pts):
    """retas com 3 pontos (como coordenadas), concorrência, e forma normal no triângulo quando
    as trissecantes formam um triângulo cobrindo os 9 pontos."""
    tl = [Ls for Ls in AL.LINES if len(set(pts) & Ls) == 3]
    tris = [sorted(pts.index(p) for p in set(pts) & Ls) for Ls in tl]
    out = {"trisecants_as_coordinate_triples": tris}
    if len(tl) < 3:
        return out
    common = set.intersection(*[set(x) for x in tl])
    out["trisecants_concurrent"] = bool(common)
    covers = sorted(sum(tris, [])) == list(range(9))
    out["trisecants_partition_the_9_points"] = covers
    if len(tl) == 3 and not common and covers:
        sides = [_cross(cols[t[0]], cols[t[1]]) for t in tris]
        V = [_cross(sides[1], sides[2]), _cross(sides[2], sides[0]), _cross(sides[0], sides[1])]
        out["triangle_vertices_in_set"] = any(AL.point_index(v) in pts for v in V)
        Pm = [[V[c][r] for c in range(3)] for r in range(3)]
        Pi = AL.mat_inv3(Pm)
        nf = []
        for t in tris:
            nf.append([list(AL.normalize([sum(Pi[r][k] * cols[j][k] for k in range(3)) for r in range(3)])) for j in t])
        out["triangle_normal_form_points_per_side"] = nf
    return out


def rank_mod(M):
    M = [list(map(int, r)) for r in M]
    r = 0
    rows, cols = len(M), len(M[0])
    for c in range(cols):
        p = next((i for i in range(r, rows) if M[i][c] % Q), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        iv = inv(M[r][c])
        M[r] = [x * iv % Q for x in M[r]]
        for i in range(rows):
            if i != r and M[i][c] % Q:
                f = M[i][c]
                M[i] = [(x - f * y) % Q for x, y in zip(M[i], M[r])]
        r += 1
    return r


def main():
    os.makedirs(OUT, exist_ok=True)
    reps = []
    r1, *_ = analyze("champion_1137", "666 065 652 643 621 615",
                     [(0, 4191, 7708), (0, 20875, 59538), (0, 21613, 64832)],
                     orbit_sets={"cov24_types": [5960, 11892, 13654, 32373, 49666, 51578, 83916, 93522, 104890]})
    reps.append(r1)
    r2, *_ = analyze("old_base_1285", "652 132 256 141 231 402", [(0, 98305, 38951)])
    reps.append(r2)
    # 2ª classe pela contagem nBc (classes_sorted.jsonl linha 2): sem trio com <= 20 órfãs (exactT2, T=20)
    r3, *_ = analyze("class2_nBc10548", "666 066 651 642 634 623", [])
    reps.append(r3)
    # referência: triângulo com 3 pontos por lado em classes de mu3 = {1,2,4}.
    # c em 3*mu3 = forma normal medida da campeã; c em mu3 = configuração de Hesse (12 retas).
    mu = [1, 2, 4]
    ref = {}
    for nm, cs in (("twisted_triangle_c_in_3mu3", [3, 5, 6]), ("hesse_triangle_c_in_mu3", mu)):
        cols = [(1, a, 0) for a in mu] + [(0, 1, b) for b in (3, 5, 6)] + [(1, 0, c) for c in cs]
        pts = [AL.point_index(c) for c in cols]
        ref[nm] = {"trisecants": sum(1 for Ls in AL.LINES if len(set(pts) & Ls) == 3),
                   "stab_PGL3_7": len(stab_pgl(cols)),
                   "weight_distribution": list(AL.weight_distribution([[c[i] for c in cols] for i in range(3)]))}
    reps.append({"name": "reference_triangle_configurations", **ref})
    print(ref)
    with open(os.path.join(OUT, "structure.json"), "w") as f:
        json.dump(reps, f, indent=1)
    for r in reps:
        if "trios" not in r:
            continue
        print(json.dumps({k: v for k, v in r.items() if k not in ("trios", "coordinate_permutations_in_aut")}))
        for t in r["trios"]:
            print(json.dumps({k: v for k, v in t.items() if k not in ("orphans",)}))
        print(r["trio_equivalences"])


if __name__ == "__main__":
    main()
