#!/usr/bin/env python3
"""Auditoria da lista de classes [9,3]_7 não degeneradas (tarefas 1 e 2).

uso: verify_list.py <classes_sorted.jsonl> [<saida.json>]

1. reconstrói G a partir de "A" (H = [I6|A], G = [-A^T|I3]) e confere G H^T = 0;
   G sem coluna nula; colunas contêm referencial; multiconjunto das colunas == "pts"
   (traduzindo a numeração do base_search, reconstruída aqui só para essa conferência);
2. duplicatas: invariante forte (distribuição de pesos + perfil ponto×retas) e, para
   empates, equivalência projetiva por força bruta; além disso forma canônica do C;
3. fórmula de massa: soma |PGL(3,7)|/|Stab(S)| contra o número de 9-multiconjuntos
   de PG(2,7) com referencial, contado por fórmula e por busca em profundidade;
4. confronto com a enumeração independente de órbitas (pg2_orbits enum 9).
"""
import hashlib
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from math import comb

import audit_lib as L

M = 9
SAMPLE_PY = 300  # pares conferidos também em Python (~0,3 s cada)


def base_search_index():
    """Numeração do base_search (build_points): referencial padrão e1,e2,e3,(1,1,1)
    primeiro; depois os demais vetores normalizados em ordem lexicográfica."""
    frame = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)]
    rest = [p for p in L.POINTS if p not in frame]
    return {i: p for i, p in enumerate(frame + rest)}


def invariant(G, S):
    wd = L.weight_distribution(G)
    mult = Counter(S)
    line_cnt = [sum(mult[p] for p in Ln) for Ln in L.LINES]
    prof = sorted((mult[p], tuple(sorted(line_cnt[li] for li, Ln in enumerate(L.LINES) if p in Ln))) for p in mult)
    return (wd, tuple(sorted(line_cnt)), tuple(prof))


def equivalent_bruteforce(S1, S2):
    """Existe g em PGL(3,7) com g(S1) = S2 (multiconjuntos)? Fixa um referencial F0 de S1
    e testa todas as 4-uplas ordenadas de pontos distintos de S2 em posição geral."""
    s1 = sorted(set(S1))
    F0 = next(f for f in itertools.combinations(s1, 4) if L.general_position(f))
    target = Counter(S2)
    for F in itertools.permutations(sorted(set(S2)), 4):
        if not L.general_position(F):
            continue
        g = L.projectivity(F0, F)
        if Counter(L.apply(g, p) for p in S1) == target:
            return True
    return False


def stab_bruteforce(S):
    """|Stab(S)| em Python: nº de 4-uplas F de S com g(F0 -> F) levando S em S."""
    s = sorted(set(S))
    F0 = next(f for f in itertools.combinations(s, 4) if L.general_position(f))
    target = Counter(S)
    return sum(1 for F in itertools.permutations(s, 4)
               if L.general_position(F) and Counter(L.apply(L.projectivity(F0, F), p) for p in S) == target)


def main():
    path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    raw = open(path, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    rows = [json.loads(x) for x in raw.decode().splitlines() if x.strip()]
    rep = {"arquivo": path, "sha256": sha, "linhas": len(rows)}
    bs = base_search_index()

    multisets, invs, problems = [], [], Counter()
    for r in rows:
        A = L.parse_A(r["A"])
        assert len(A) == 6 and all(len(x) == 3 for x in A)
        G = L.G_from_A(A)
        H = L.H_from_A(A)
        if any(v for row in L.matmul(G, L.transpose(H)) for v in row):
            problems["GHt!=0"] += 1
        cols = L.columns_as_points(G)
        if any(c is None for c in cols):
            problems["coluna_nula"] += 1
            continue
        if not L.has_frame(cols):
            problems["sem_referencial"] += 1
        pts_mine = sorted(L.IDX[bs[p]] for p in r["pts"])
        if pts_mine != sorted(cols):
            problems["pts!=colunas(A)"] += 1
        multisets.append(sorted(cols))
        invs.append(invariant(G, cols))
    rep["problemas_por_linha"] = dict(problems)

    # duplicatas por invariante + força bruta
    groups = defaultdict(list)
    for i, v in enumerate(invs):
        groups[v].append(i)
    collide = [g for g in groups.values() if len(g) > 1]
    pairs = sum(comb(len(g), 2) for g in collide)
    allpairs = [(a, b) for g in collide for a, b in itertools.combinations(g, 2)]
    eq = L.c_equiv([(multisets[a], multisets[b]) for a, b in allpairs], M)
    dup_pairs = [p for p, e in zip(allpairs, eq) if e]
    # conferência cruzada do C pela força bruta em Python (amostra fixa + todo par que o C acusar)
    rng = random.Random(20261002)
    sample = rng.sample(range(len(allpairs)), min(SAMPLE_PY, len(allpairs)))
    sample = sorted(set(sample) | {i for i, e in enumerate(eq) if e})
    py_disagree = sum(1 for i in sample if equivalent_bruteforce(*[multisets[x] for x in allpairs[i]]) != eq[i])
    # controle positivo: imagem projetiva aleatória de 50 linhas TEM de dar equivalente (C e Python)
    ctrl = []
    for i in rng.sample(range(len(multisets)), 50):
        S = multisets[i]
        while True:
            g = [[rng.randrange(L.Q) for _ in range(3)] for _ in range(3)]
            if L.mat_inv3(g):
                break
        ctrl.append((S, sorted(L.apply(g, p) for p in S)))
    ctrl_ok = all(L.c_equiv(ctrl, M)) and all(equivalent_bruteforce(a, b) for a, b in ctrl[:10])
    rep["invariantes_distintos"] = len(groups)
    rep["grupos_com_empate"] = len(collide)
    rep["pares_testados_forca_bruta"] = pairs
    rep["pares_equivalentes"] = len(dup_pairs)
    rep["amostra_python_pares"] = len(sample)
    rep["amostra_python_divergencias_com_C"] = py_disagree
    rep["controle_positivo_50_imagens_aleatorias_ok"] = ctrl_ok

    # forma canônica + estabilizador (C)
    cs = L.c_stab(multisets, M)
    canons = [c for c, _ in cs]
    stabs = [s for _, s in cs]
    assert all(c is not None for c in canons)
    rep["formas_canonicas_distintas"] = len(set(canons))
    rep["dist_estabilizador"] = dict(sorted(Counter(stabs).items()))
    for s in stabs:
        assert L.ORDER_PGL3 % s == 0, s
    lhs = sum(L.ORDER_PGL3 // s for s in stabs)
    # conferência do estabilizador do C em Python: os 10 maiores + 20 sorteados
    chk = sorted(range(len(stabs)), key=lambda i: -stabs[i])[:10] + random.Random(7).sample(range(len(stabs)), 20)
    rep["stab_python_conferidos"] = len(chk)
    rep["stab_python_divergencias"] = sum(1 for i in chk if stab_bruteforce(multisets[i]) != stabs[i])

    # lado direito: 9-multiconjuntos com referencial
    total = comb(L.NPTS + M - 1, M)
    fl_formula = sum(sum(L.frameless_sets_formula(s)) * L.multisets_with_support_size(M, s) for s in range(1, M + 1))
    livres = L.c_livres(M)
    fl_dfs = sum((a + b) * L.multisets_with_support_size(M, s) for s, (a, b) in livres.items())
    sets_ok = all(livres[s] == L.frameless_sets_formula(s) for s in range(1, M + 1))
    rep.update({
        "ordem_PGL3": L.ORDER_PGL3,
        "C(65,9)": total,
        "sem_referencial_formula": fl_formula,
        "sem_referencial_busca": fl_dfs,
        "conjuntos_livres_formula==busca": sets_ok,
        "lado_direito": total - fl_formula,
        "lado_esquerdo": lhs,
        "massa_bate": lhs == total - fl_formula and fl_formula == fl_dfs,
    })

    # enumeração independente de órbitas
    reps = L.c_enum(M)
    enum_set = {c for c, _ in reps}
    rep["enum_independente_orbitas"] = len(reps)
    rep["enum_independente==lista"] = enum_set == set(canons)
    rep["enum_independente_massa"] = sum(L.ORDER_PGL3 // s for _, s in reps)

    print(json.dumps(rep, indent=1, ensure_ascii=False))
    if out_path:
        with open(out_path, "w") as f:
            json.dump(rep, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
