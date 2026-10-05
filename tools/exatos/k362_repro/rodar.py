"""Roda todas as instâncias (s, K) de "existe código de K_q(n,R) com M palavras?".

    python3 rodar.py 3 6 2 15 --formato opb --bin DIR --saida registros.jsonl [--proc 2]

DIR contém roundingsat e veripb (opb) ou cadical e lrat-check (cnf). Uma linha JSON por instância:
s, K, |U|, sha256 da fórmula, veredito, tempos, resultado do verificador. Se a relaxação da fatia for
satisfazível, tenta a formulação completa; se esta também for, o modelo é guardado (candidato a código).
"""
import argparse
import json
import multiprocessing as mp
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import enumera  # noqa: E402
import sat  # noqa: E402


def instancias(q, n, R, M):
    """(s, K) para s = 0..floor(M/q) e K um representante por classe que passa no lema da fatia."""
    out = []
    for s in range(M // q + 1):
        if s == 0:
            if q ** (n - 1) <= M * enumera.volume(n - 1, R - 1, q):
                out.append((0, ()))
            continue
        out += [(s, K) for K in enumera.classes(q, n - 1, s) if enumera.passa_filtro(K, q, R, M)]
    return out


def uma(args):
    q, n, R, M, s, K, formato, binarios, tempo = args
    reg = {"s": s, "K": [list(k) for k in K]}
    for completa in (False, True):
        cob, nv, teto, fib = sat.restricoes(q, n, R, M, K, completa)
        texto = (sat.opb if formato == "opb" else sat.cnf)(cob, nv, teto, fib)
        r = sat.resolver(texto, formato, binarios, nv, tempo[completa])
        modelo = r.pop("modelo", None)
        reg["completa" if completa else "fatia"] = r
        reg["veredito"], reg["verificador"] = r["veredito"], r.get("verificador")
        if r["veredito"] != "SAT":
            break
    if reg["veredito"] == "SAT":  # candidato: conferir de forma independente do solver
        C = sat.codigo_do_modelo(q, n, K, modelo)
        reg["codigo"] = [list(c) for c in C]
        reg["codigo_confere"] = len(set(C)) <= M and sat.raio(q, n, C) <= R
    return reg


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("q", type=int)
    ap.add_argument("n", type=int)
    ap.add_argument("R", type=int)
    ap.add_argument("M", type=int)
    ap.add_argument("--formato", choices=["opb", "cnf"], default="opb")
    ap.add_argument("--bin", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--proc", type=int, default=2)
    ap.add_argument("--tempo", type=float, nargs=2, default=[3600, 3600], metavar=("FATIA", "COMPLETA"),
                    help="segundos por fórmula; estourado vira veredito TEMPO (instância em aberto)")
    ap.add_argument("--lista", help="JSON com uma lista de K: roda só essas instâncias")
    ap.add_argument("--parte", default="0/1", help="i/k: roda só as instâncias de índice = i mod k")
    a = ap.parse_args(argv)
    nomes = ["roundingsat", "veripb"] if a.formato == "opb" else ["cadical", "lrat-check"]
    binarios = {b: os.path.join(a.bin, b) for b in nomes}
    i, k = map(int, a.parte.split("/"))
    todas = instancias(a.q, a.n, a.R, a.M)
    if a.lista:
        pedidas = {json.dumps(K) for K in json.load(open(a.lista))}
        todas = [(s, K) for s, K in todas if json.dumps([list(x) for x in K]) in pedidas]
    feitas = set()
    if os.path.exists(a.saida):
        feitas = {json.dumps(json.loads(ln)["K"]) for ln in open(a.saida)}
    tarefas = [(a.q, a.n, a.R, a.M, s, K, a.formato, binarios, a.tempo) for j, (s, K) in enumerate(todas)
               if j % k == i and json.dumps([list(x) for x in K]) not in feitas]
    print("instancias", len(todas), "a rodar", len(tarefas), flush=True)
    resumo = {}
    with mp.Pool(a.proc) as pool, open(a.saida, "a") as f:
        for reg in pool.imap_unordered(uma, tarefas, chunksize=4):
            f.write(json.dumps(reg) + "\n")
            f.flush()
            chave = (reg["veredito"], reg.get("verificador"))
            resumo[chave] = resumo.get(chave, 0) + 1
            if reg["veredito"] != "UNSAT":
                print("ATENCAO", json.dumps(reg)[:300], flush=True)
    print("resumo", resumo, flush=True)
    return resumo


if __name__ == "__main__":
    main()
