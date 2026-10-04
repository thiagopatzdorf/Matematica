#!/usr/bin/env python3
"""Existe código q-ário de comprimento n, raio R e M palavras?  Modelo CP-SAT (OR-Tools).

Uso:
  python3 tools/exatos/cpsat_cover.py --q 2 --n 10 --R 3 --M 11 --tempo 600 --workers 4

Saída: uma linha JSON com status (OPTIMAL/FEASIBLE = achou código; INFEASIBLE = prova de
inexistência *dentro do CP-SAT*, sem certificado independente), tempo e tamanho do modelo.
Se achar, grava o código (formato de data/codes) em --saida.

Modelo: y[c][i][s] = 1 sse a palavra c tem o símbolo s na coordenada i (one-hot; binário usa
um booleano só). Para cada ponto x do espaço, z[x][c] -> (concordâncias de c com x) >= n-R, e
OR_c z[x][c].

Quebra de simetria (escolhida para ser *sã*: toda classe de equivalência tem representante que
satisfaz as restrições):
  * translação: o código pode ser transladado para conter 0, então a palavra 0 é a toda-zero;
  * linhas em ordem lexicográfica e colunas em ordem lexicográfica ("double lex"): permutar
    linhas e colunas de uma matriz sempre leva a uma matriz com as duas ordens (Flener et al.
    2002), e a linha toda-zero continua sendo a menor e a primeira.
  * opcional (--valprec, só q > 2): em cada coluna, entre os símbolos não nulos, o primeiro
    aparecimento de s vem antes do de s+1. NÃO é provado compatível com o double lex: só use
    para medir crescimento, nunca como prova (marcado na saída).
O que fica de fora: permutações de símbolos que não fixam 0 combinadas com a ordem das linhas.
"""
import argparse, itertools, json, sys, time

from ortools.sat.python import cp_model


def modelo(q, n, R, M, simetria=True, valprec=False, fibra=0):
    m = cp_model.CpModel()
    if q == 2:
        y = [[m.NewBoolVar(f"y{c}_{i}") for i in range(n)] for c in range(M)]
        def agree(c, i, s):
            return y[c][i] if s == 1 else y[c][i].Not()
        def val(c, i):
            return y[c][i]
    else:
        y = [[[m.NewBoolVar(f"y{c}_{i}_{s}") for s in range(q)] for i in range(n)] for c in range(M)]
        for c in range(M):
            for i in range(n):
                m.AddExactlyOne(y[c][i])
        def agree(c, i, s):
            return y[c][i][s]
        def val(c, i):
            return sum(s * y[c][i][s] for s in range(1, q))
    if fibra and q > 2:  # cada símbolo aparece >= fibra vezes em cada coordenada (lema provado fora)
        for i in range(n):
            for v in range(q):
                m.Add(sum(y[c][i][v] for c in range(M)) >= fibra)
    nz = 0
    for x in itertools.product(range(q), repeat=n):
        zs = []
        for c in range(M):
            z = m.NewBoolVar("")
            m.Add(sum(agree(c, i, x[i]) for i in range(n)) >= n - R).OnlyEnforceIf(z)
            zs.append(z)
            nz += 1
        m.AddBoolOr(zs)
    if simetria:
        for i in range(n):  # palavra 0 = toda-zero
            if q == 2:
                m.Add(y[0][i] == 0)
            else:
                m.Add(y[0][i][0] == 1)
        if q ** n < 2 ** 50:  # linhas em ordem lexicográfica (inteiro com a coluna 0 mais significativa)
            rows = [sum(q ** (n - 1 - i) * val(c, i) for i in range(n)) for c in range(M)]
            for c in range(M - 1):
                m.Add(rows[c] <= rows[c + 1])
        if q ** (M - 1) < 2 ** 50:  # colunas em ordem lexicográfica (a linha 0 é constante)
            cols = [sum(q ** (M - 1 - c) * val(c, i) for c in range(1, M)) for i in range(n)]
            for i in range(n - 1):
                m.Add(cols[i] <= cols[i + 1])
        if valprec and q > 2:
            # first[i][s] = primeira linha em que s aparece na coluna i (M se não aparece)
            for i in range(n):
                firsts = []
                for s in range(1, q):
                    f = m.NewIntVar(1, M, "")
                    for c in range(1, M):
                        # se y[c][i][s] então f <= c
                        m.Add(f <= c).OnlyEnforceIf(y[c][i][s])
                    # f é atingido: se f == c (< M) então y[c][i][s]
                    for c in range(1, M):
                        b = m.NewBoolVar("")
                        m.Add(f == c).OnlyEnforceIf(b)
                        m.Add(f != c).OnlyEnforceIf(b.Not())
                        m.AddImplication(b, y[c][i][s])
                    firsts.append(f)
                for a, b in zip(firsts, firsts[1:]):
                    m.Add(a <= b)
    return m, y, nz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", type=int, required=True)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--R", type=int, required=True)
    ap.add_argument("--M", type=int, required=True)
    ap.add_argument("--tempo", type=float, default=600)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--sem-simetria", action="store_true")
    ap.add_argument("--valprec", action="store_true")
    ap.add_argument("--fibra", type=int, default=0,
                    help="mínimo de palavras por (coordenada, símbolo); só use com o lema que o justifica")
    ap.add_argument("--semente", type=int, default=0)
    ap.add_argument("--saida")
    a = ap.parse_args()
    t0 = time.time()
    m, y, nz = modelo(a.q, a.n, a.R, a.M, not a.sem_simetria, a.valprec, a.fibra)
    tm = time.time() - t0
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = a.tempo
    s.parameters.num_workers = a.workers
    s.parameters.random_seed = a.semente
    st = s.Solve(m)
    res = dict(celula=f"K{a.q}({a.n},{a.R})", M=a.M, status=s.StatusName(st), tempo_s=round(s.WallTime(), 2),
               tempo_modelo_s=round(tm, 2), z=nz, workers=a.workers, simetria=not a.sem_simetria,
               valprec_nao_provado=a.valprec, fibra=a.fibra, conflitos=s.NumConflicts(), ramos=s.NumBranches())
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        words = []
        for c in range(a.M):
            if a.q == 2:
                d = [int(s.Value(y[c][i])) for i in range(a.n)]
            else:
                d = [next(v for v in range(a.q) if s.Value(y[c][i][v])) for i in range(a.n)]
            words.append("".join(str(v) for v in d) if a.q <= 10 else " ".join(map(str, d)))
        if a.saida:
            open(a.saida, "w").write("\n".join(words) + "\n")
            res["saida"] = a.saida
    print(json.dumps(res, ensure_ascii=False))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
