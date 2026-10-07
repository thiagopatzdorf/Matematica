#!/usr/bin/env python3
"""Menor código de cobertura de Z_3^6 (raio 1) INVARIANTE por um grupo G prescrito, exato por PLI.

Por que: tabu_grupo.c (#104) busca heurística em órbitas; aqui o mesmo espaço de órbitas vai ao SCIP
e sai o ótimo G-invariante (ou cota inferior ao estourar o tempo). Se algum G der ≤ 72, é um código de
72. Geradores na convenção do tabu_grupo: "p0,..,p5[:a0,..,a5[:m0,..,m5]]" => y_i = m_i x_{p_i} + a_i.
Saída: uma linha JSON por grupo (ordem, nº de órbitas, ótimo/cota, status, segundos).
Anexo do diagnóstico docs/alvos/K3-6-1.md (2026-10-07); só medição, sem prova.
Uso: python3 grupo_exato.py [segundos_por_grupo=120] [processos=4]   (precisa de pyscipopt)
"""
import itertools, json, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed

q, n, R = 3, 6, 1
PTS = list(itertools.product(range(q), repeat=n))
IDX = {p: i for i, p in enumerate(PTS)}


def parse_gen(s):
    partes = s.split(":")
    p = list(map(int, partes[0].split(",")))
    a = list(map(int, partes[1].split(","))) if len(partes) > 1 else [0] * n
    m = list(map(int, partes[2].split(","))) if len(partes) > 2 else [1] * n
    return [IDX[tuple((m[i] * x[p[i]] + a[i]) % q for i in range(n))] for x in PTS]


def fecho(gens):
    ident = list(range(len(PTS)))
    G = {tuple(ident)}
    fila = [ident]
    while fila:
        g = fila.pop()
        for h in gens:
            gh = [h[g[i]] for i in range(len(PTS))]
            t = tuple(gh)
            if t not in G:
                G.add(t)
                fila.append(gh)
                if len(G) > 5000:
                    raise ValueError("grupo grande demais")
    return [list(g) for g in G]


def orbitas(G):
    oid = [-1] * len(PTS)
    orbs = []
    for i in range(len(PTS)):
        if oid[i] < 0:
            o = sorted({g[i] for g in G})
            for j in o:
                oid[j] = len(orbs)
            orbs.append(o)
    return oid, orbs


def bola(i):
    x = PTS[i]
    out = [i]
    for c in range(n):
        for s in range(q):
            if s != x[c]:
                out.append(IDX[x[:c] + (s,) + x[c + 1:]])
    return out


def resolver(nome, gens_s, tempo, teto=72):
    from pyscipopt import Model, quicksum
    t0 = time.time()
    try:
        G = fecho([parse_gen(s) for s in gens_s])
    except ValueError as e:
        return {"grupo": nome, "erro": str(e)}
    oid, orbs = orbitas(G)
    # cobertura: órbita i coberta sse alguma órbita escolhida j tem ponto na bola do representante de i
    cobre = [set(oid[k] for k in bola(o[0])) for o in orbs]
    m = Model(); m.hideOutput(); m.setParam("limits/time", tempo); m.setParam("parallel/maxnthreads", 1)
    x = [m.addVar(vtype="B") for _ in orbs]
    for i, c in enumerate(cobre):
        m.addCons(quicksum(x[j] for j in c) >= 1)
    m.setObjective(quicksum(len(orbs[j]) * x[j] for j in range(len(orbs))), "minimize")
    m.optimize()
    st = m.getStatus()
    reg = {"grupo": nome, "geradores": gens_s, "ordem": len(G), "orbitas": len(orbs),
           "tamanhos_orbita": sorted(set(len(o) for o in orbs)), "status": st, "seg": round(time.time() - t0, 1)}
    if st == "optimal":
        reg["otimo_invariante"] = int(round(m.getObjVal()))
    else:
        try:
            reg["cota_inferior"] = round(m.getDualbound(), 2)
            reg["melhor_achado"] = int(round(m.getPrimalbound())) if m.getNSols() else None
        except Exception:
            pass
    if st == "optimal" and reg["otimo_invariante"] <= teto:
        sol = m.getBestSol()
        cod = sorted(k for j in range(len(orbs)) if m.getSolVal(sol, x[j]) > 0.5 for k in orbs[j])
        with open(f"grupo_{nome}_M{len(cod)}.txt", "w") as f:
            for k in cod:
                f.write("".join(map(str, PTS[k])) + "\n")
        reg["arquivo"] = f"grupo_{nome}_M{len(cod)}.txt"
    return reg


def grupos():
    I = "0,1,2,3,4,5"
    g = {}
    g["C6"] = ["1,2,3,4,5,0"]
    g["C5"] = ["1,2,3,4,0,5"]
    g["C4"] = ["1,2,3,0,4,5"]
    g["C3"] = ["1,2,0,3,4,5"]
    g["C3xC3"] = ["1,2,0,4,5,3"]
    g["C2"] = ["1,0,2,3,4,5"]
    g["C2^3"] = ["1,0,3,2,5,4"]
    g["C2xC2xC2sep"] = ["1,0,2,3,4,5", "0,1,3,2,4,5", "0,1,2,3,5,4"]
    g["S3coord"] = ["1,2,0,3,4,5", "1,0,2,3,4,5"]
    for k in range(1, 7):
        a = ",".join(["1"] * k + ["0"] * (6 - k))
        g[f"T1^{k}"] = [f"{I}:{a}"]
    for k in (1, 2, 3, 6):
        mm = ",".join(["2"] * k + ["1"] * (6 - k))
        g[f"N^{k}"] = [f"{I}:0,0,0,0,0,0:{mm}"]
    g["C6+T"] = ["1,2,3,4,5,0", f"{I}:1,1,1,1,1,1"]
    g["C3xC3+T"] = ["1,2,0,4,5,3", f"{I}:1,1,1,1,1,1"]
    g["C2^3+T"] = ["1,0,3,2,5,4", f"{I}:1,1,1,1,1,1"]
    g["C6+N"] = ["1,2,3,4,5,0", f"{I}:0,0,0,0,0,0:2,2,2,2,2,2"]
    g["C3+T111"] = ["1,2,0,3,4,5", f"{I}:1,1,1,0,0,0"]
    g["T+N"] = [f"{I}:1,1,1,1,1,1", f"{I}:0,0,0,0,0,0:2,2,2,2,2,2"]
    g["AGL-like"] = [f"{I}:1,1,1,1,1,1", "1,2,3,4,5,0", f"{I}:0,0,0,0,0,0:2,2,2,2,2,2"]
    g["C2+T110000"] = ["1,0,2,3,4,5", f"{I}:1,1,0,0,0,0"]
    g["C3^2sym"] = ["1,2,0,3,4,5", "0,1,2,4,5,3"]
    g["twist6"] = ["1,2,3,4,5,0:1,0,0,0,0,0"]           # shift com translação numa coordenada (ordem 18)
    g["twist3"] = ["1,2,0,3,4,5:1,0,0,0,0,0"]           # ordem 9
    g["swap+neg"] = ["1,0,2,3,4,5:0,0,0,0,0,0:2,2,1,1,1,1"]
    g["C2diag"] = ["1,0,3,2,5,4:1,1,1,1,1,1"]
    return g


if __name__ == "__main__":
    tempo = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    G = grupos()
    with ProcessPoolExecutor(procs) as ex, open("grupo_exato.jsonl", "a") as out:
        futs = {ex.submit(resolver, nome, gens, tempo): nome for nome, gens in G.items()}
        for f in as_completed(futs):
            r = f.result()
            out.write(json.dumps(r) + "\n"); out.flush()
            print(json.dumps(r), flush=True)
