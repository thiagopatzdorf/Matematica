#!/usr/bin/env python3
"""Modelo por projeções de pares para K_q(4,2) (CP-SAT, só booleanos).

x está a distância <= 2 de c sse c concorda com x em duas coordenadas i<j, ou seja, sse o par
(x_i, x_j) está na projeção P_ij do código. Então C cobre sse, para todo x em Z_q^4,
OR_{i<j} P_ij(x_i, x_j). (É a formulação de grafos de complemento das projeções do Florath
para K_8(4,2) = 23: x descoberto = 4-clique transversal nos complementos.)

Variáveis: y[c][i][s] (one-hot), P[ij][a][b], e P[ij][a][b] -> OR_c (y[c][i][a] AND y[c][j][b]).
Restrições derivadas (opcionais, cada uma com o lema que a justifica no docstring de main):
  --fibra F : cada símbolo aparece >= F vezes em cada coordenada.
Quebra de simetria sã: palavra 0 = 0000 e linhas em ordem lexicográfica e colunas em ordem
lexicográfica (double lex), como em cpsat_cover.py.

Uso: python3 tools/exatos/proj_q42.py --q 7 --M 18 --fibra 2 --tempo 600 --workers 4
"""
import argparse, itertools, json, time

from ortools.sat.python import cp_model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", type=int, required=True)
    ap.add_argument("--M", type=int, required=True)
    ap.add_argument("--fibra", type=int, default=0)
    ap.add_argument("--tempo", type=float, default=600)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--sem-simetria", action="store_true")
    ap.add_argument("--saida")
    a = ap.parse_args()
    q, M, n = a.q, a.M, 4
    m = cp_model.CpModel()
    y = [[[m.NewBoolVar("") for s in range(q)] for i in range(n)] for c in range(M)]
    for c in range(M):
        for i in range(n):
            m.AddExactlyOne(y[c][i])
    pares = list(itertools.combinations(range(n), 2))
    P = {}
    for (i, j) in pares:
        for av in range(q):
            for bv in range(q):
                p = m.NewBoolVar("")
                ws = []
                for c in range(M):
                    w = m.NewBoolVar("")
                    m.AddImplication(w, y[c][i][av])
                    m.AddImplication(w, y[c][j][bv])
                    m.AddBoolOr([y[c][i][av].Not(), y[c][j][bv].Not(), w])  # w <-> y and y
                    ws.append(w)
                m.AddBoolOr([p.Not()] + ws)
                for w in ws:
                    m.AddImplication(w, p)
                P[(i, j, av, bv)] = p
    for x in itertools.product(range(q), repeat=n):
        m.AddBoolOr([P[(i, j, x[i], x[j])] for (i, j) in pares])
    if a.fibra:
        for i in range(n):
            for v in range(q):
                m.Add(sum(y[c][i][v] for c in range(M)) >= a.fibra)
    if not a.sem_simetria:
        for i in range(n):
            m.Add(y[0][i][0] == 1)
        val = lambda c, i: sum(s * y[c][i][s] for s in range(1, q))
        rows = [sum(q ** (n - 1 - i) * val(c, i) for i in range(n)) for c in range(M)]
        for c in range(M - 1):
            m.Add(rows[c] <= rows[c + 1])
        if q ** (M - 1) < 2 ** 60:
            cols = [sum(q ** (M - 1 - c) * val(c, i) for c in range(1, M)) for i in range(n)]
            for i in range(n - 1):
                m.Add(cols[i] <= cols[i + 1])
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = a.tempo
    s.parameters.num_workers = a.workers
    t0 = time.time()
    st = s.Solve(m)
    res = dict(celula=f"K{q}(4,2)", M=M, modelo="projecoes", fibra=a.fibra, simetria=not a.sem_simetria,
               status=s.StatusName(st), tempo_s=round(s.WallTime(), 2), conflitos=s.NumConflicts(), workers=a.workers)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE) and a.saida:
        with open(a.saida, "w") as f:
            for c in range(M):
                f.write(" ".join(str(next(v for v in range(q) if s.Value(y[c][i][v]))) for i in range(n)) + "\n")
        res["saida"] = a.saida
    print(json.dumps(res, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
