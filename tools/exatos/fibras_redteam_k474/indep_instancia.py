#!/usr/bin/env python3
"""Instância de perfil escrita com `cobertura_indep` (sem fib_encode) e resolvida por kissat/CaDiCaL.

Estrutura do perfil: coordenada 0 = blocos (t0[a] palavras com símbolo a); coluna i com exatamente t_i[a]
palavras de símbolo a; cobertura "u concorda com x em >= n-R coordenadas" por contador sequencial próprio;
quebra de simetria: palavras dentro de cada bloco em ordem lexicográfica (<=). Nada de (d)-(h) do repo.
O perfil vem do registro do certificado (campo `tipos`, na ordem gravada).

Uso: python3 indep_instancia.py CERT.jsonl.xz q n R M INST ORDEM SOLVER_BIN TEMPO [CNF_SAIDA]
"""
import json
import lzma
import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import cobertura_indep as ci  # noqa: E402


def construir(q, n, R, M, tipos):
    f = ci.F()
    w = [[[f.var() for _ in range(q)] for _ in range(n)] for _ in range(M)]
    for u in range(M):
        for i in range(n):
            f.add(w[u][i])
            for a in range(q):
                for b in range(a):
                    f.add([-w[u][i][a], -w[u][i][b]])
    blocos = [a for a in range(q) for _ in range(tipos[0][a])]
    for u in range(M):
        f.add([w[u][0][blocos[u]]])
    for i in range(1, n):
        for a in range(q):
            ci.exatamente(f, [w[u][i][a] for u in range(M)], tipos[i][a])
    # palavras de um mesmo bloco em ordem lexicográfica (colunas 1..n-1)
    for u in range(M - 1):
        if blocos[u] == blocos[u + 1]:
            ci.lex_leq_ok(f, [w[u][i] for i in range(1, n)], [w[u + 1][i] for i in range(1, n)], q)
    t = n - R
    import itertools
    for x in itertools.product(range(q), repeat=n):
        ms = []
        for u in range(M):
            m = f.var()
            ci.pelo_menos_cond(f, m, [w[u][i][x[i]] for i in range(n)], t)
            ms.append(m)
        f.add(ms)
    return f


def dimacs(f, caminho):
    with open(caminho, "w") as fo:
        fo.write(f"p cnf {f.nv} {len(f.cl)}\n")
        for c in f.cl:
            fo.write(" ".join(map(str, c)) + " 0\n")


def main():
    arq, q, n, R, M, inst, ordem, solver, tempo = sys.argv[1], *map(int, sys.argv[2:6]), int(sys.argv[6]), *sys.argv[7:10]
    saida = sys.argv[10] if len(sys.argv) > 10 else f"/tmp/indep_{q}_{n}_{M}_{inst}_{ordem}.cnf"
    reg = next(json.loads(ln) for ln in lzma.open(arq, "rt")
               if (r := json.loads(ln)) and r["inst"] == inst and r["ordem"] == ordem)
    tipos = [tuple(int(c) for c in s) for s in reg["tipos"]]
    t0 = time.time()
    f = construir(q, n, R, M, tipos)
    dimacs(f, saida)
    t1 = time.time()
    try:
        r = subprocess.run([solver, "-q", f"--time={tempo}", saida], capture_output=True, text=True, timeout=int(tempo) + 120)
        rc = r.returncode
    except subprocess.TimeoutExpired:
        rc = -1
    veredito = {20: "UNSAT", 10: "SAT"}.get(rc, "INDEFINIDO")
    print(json.dumps({"inst": inst, "ordem": ordem, "tipos": reg["tipos"], "vars": f.nv, "clausulas": len(f.cl),
                      "gerar_s": round(t1 - t0, 1), "resolver_s": round(time.time() - t1, 1), "veredito": veredito}), flush=True)
    os.remove(saida)


if __name__ == "__main__":
    main()
