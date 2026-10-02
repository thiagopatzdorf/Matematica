#!/usr/bin/env python3
"""Classes de equivalência monomial de códigos [9,3]_7 DEGENERADOS (fora da varredura).

uso: degenerate.py <saida.jsonl> [<resumo.json>]

Código [9,3]_7 a menos de equivalência monomial  <->  (z colunas nulas, multiconjunto de
m = 9 - z pontos de PG(2,7) de posto 3) a menos de PGL(3,7). Degenerado = z >= 1, ou
z = 0 sem referencial. Tipos:
  (i)  z >= 1, parte não nula COM referencial (m >= 4): órbitas por pg2_orbits enum m;
  (i') z >= 1, parte não nula SEM referencial (posto 3): triângulo ou reta + ponto;
  (ii) z = 0, sem referencial (posto 3): triângulo ou reta + ponto (m = 9).
Sem referencial e posto 3 (classificação conferida por busca em profundidade no C):
  - triângulo: suporte = 3 pontos não colineares, multiplicidades (a,b,c) — a órbita é a
    partição {a,b,c} de m (as permutações dos vértices são projetividades);
  - reta + ponto: suporte ⊆ L ∪ {P}, P fora de L, >= 3 pontos em L. L e P são únicos;
    o estabilizador de (L,P) em PGL(3,q) é GL(2,q) e age em L como PGL(2,q) com núcleo
    de ordem q-1. Órbita <-> (mult(P) = j, órbita de PGL(2,7) do multiconjunto em L).
Cada contagem é conferida por fórmula de massa. Grava, para cada classe, a matriz
H = [I6|A] depois de permutar as coordenadas (equivalência monomial).
"""
import itertools
import json
import sys
from collections import Counter
from math import comb

import audit_lib as L

Q = L.Q
N = 9

# ---------- PG(1,q) e PGL(2,q) ----------
P1 = [p for p in itertools.product(range(Q), repeat=2) if L.normalize(p) == p]
P1IDX = {p: i for i, p in enumerate(P1)}
PGL2 = []
for a, b, c, d in itertools.product(range(Q), repeat=4):
    if (a * d - b * c) % Q == 0:
        continue
    M = (a, b, c, d)
    # representante normalizado (1ª entrada não nula = 1) para tirar escalares
    if L.normalize(M) == M:
        PGL2.append(M)
assert len(PGL2) == (Q * Q - 1) * (Q * Q - Q) // (Q - 1) == 336
ACT2 = [[P1IDX[L.normalize(((a * x + b * y), (c * x + d * y)))] for (x, y) in P1] for (a, b, c, d) in PGL2]


def pgl2_orbits(u):
    """Órbitas de PGL(2,q) nos u-multiconjuntos de PG(1,q) com suporte >= 3: [(canon, |stab|)]."""
    seen = {}
    for U in itertools.combinations_with_replacement(range(len(P1)), u):
        if len(set(U)) < 3:
            continue
        imgs = [tuple(sorted(act[x] for x in U)) for act in ACT2]
        can = min(imgs)
        if can not in seen:
            seen[can] = sum(1 for im in imgs if im == can)
    return list(seen.items())


def partitions3(m):
    return [(a, b, m - a - b) for a in range(1, m) for b in range(a, m) if m - a - b >= b]


def frameless_rank3_classes(m, livres):
    """Classes de m-multiconjuntos de posto 3 sem referencial, com conferência de massa."""
    classes = []
    for (a, b, c) in partitions3(m):
        pts = [L.IDX[(1, 0, 0)]] * a + [L.IDX[(0, 1, 0)]] * b + [L.IDX[(0, 0, 1)]] * c
        nsym = {1: 6, 2: 2, 3: 1}[len({a, b, c})]
        classes.append({"pts": pts, "sub": f"triangulo{a}+{b}+{c}", "stab": (Q - 1) ** 2 * nsym})
    # reta L = {z = 0}: (x,y) -> (x,y,0); ponto P = (0,0,1)
    for j in range(1, m - 2):
        for U, st2 in pgl2_orbits(m - j):
            pts = [L.IDX[(P1[x][0], P1[x][1], 0)] for x in U] + [L.IDX[(0, 0, 1)]] * j
            classes.append({"pts": pts, "sub": f"reta{m - j}+ponto{j}", "stab": (Q - 1) * st2})
    lhs = sum(L.ORDER_PGL3 // c["stab"] for c in classes)
    rhs = sum(livres[s][1] * comb(m - 1, s - 1) for s in range(1, m + 1))
    for c in classes:
        assert L.rank_of(c["pts"]) == 3 and not L.has_frame(c["pts"])
    return classes, lhs, rhs


def main():
    out = sys.argv[1]
    summ_path = sys.argv[2] if len(sys.argv) > 2 else None
    livres = L.c_livres(N)
    # conferência do PGL(2): massa por u
    pgl2_check = {}
    for u in range(3, N):
        orb = pgl2_orbits(u)
        lhs = sum(336 // s for _, s in orb)
        rhs = sum(comb(len(P1), s) * comb(u - 1, s - 1) for s in range(3, u + 1))
        pgl2_check[u] = {"orbitas": len(orb), "massa": lhs, "esperado": rhs, "ok": lhs == rhs}
    summary = {"pgl2_massa": pgl2_check, "por_tipo": {}, "massa": {}}
    records = []
    for z in range(0, N - 2):
        m = N - z
        # com referencial (só z >= 1; z = 0 é a lista auditada em verify_list.py)
        if z >= 1 and m >= 4:
            reps = L.c_enum(m)
            lhs = sum(L.ORDER_PGL3 // s for _, s in reps)
            fl = sum(sum(L.frameless_sets_formula(s)) * comb(m - 1, s - 1) for s in range(1, m + 1))
            rhs = comb(L.NPTS + m - 1, m) - fl
            summary["massa"][f"z={z},com_referencial"] = {"orbitas": len(reps), "massa": lhs, "esperado": rhs, "ok": lhs == rhs}
            summary["por_tipo"][f"(i) z={z} com_referencial"] = len(reps)
            for can, st in reps:
                records.append({"pts": list(can), "z": z, "tipo": f"z={z};nao_nulas={m};com_referencial", "stab": st})
        classes, lhs, rhs = frameless_rank3_classes(m, livres)
        key = f"(ii) z=0 sem_referencial" if z == 0 else f"(i) z={z} sem_referencial"
        summary["massa"][f"z={z},sem_referencial"] = {"orbitas": len(classes), "massa": lhs, "esperado": rhs, "ok": lhs == rhs}
        summary["por_tipo"][key] = len(classes)
        for c in classes:
            records.append({"pts": c["pts"], "z": z, "tipo": f"z={z};nao_nulas={m};sem_referencial;{c['sub']}", "stab": c["stab"]})

    # matriz de checagem sistemática e conferência de ida e volta
    with open(out, "w") as f:
        for r in records:
            cols = [L.POINTS[p] for p in r["pts"]] + [(0, 0, 0)] * r["z"]
            A, _ = L.systematic_A(cols)
            G = L.G_from_A(A)
            back = L.columns_as_points(G)
            assert back.count(None) == r["z"]
            nz = sorted(p for p in back if p is not None)
            if "com_referencial" in r["tipo"]:
                (can, _), = L.c_stab([nz], len(nz))
                assert list(can) == sorted(r["pts"]), (can, r)
            else:
                assert L.rank_of(nz) == 3 and not L.has_frame(nz)
                assert sorted(Counter(nz).values()) == sorted(Counter(r["pts"]).values())
            f.write(json.dumps({"A": L.A_string(A), "tipo": r["tipo"]}, ensure_ascii=False) + "\n")
    summary["total_degeneradas"] = len(records)
    summary["massa_ok"] = all(v["ok"] for v in summary["massa"].values()) and all(v["ok"] for v in pgl2_check.values())
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    if summ_path:
        with open(summ_path, "w") as f:
            json.dump(summary, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
