"""Poder dos testes: quebras de simetria ERRADAS plantadas no fib_encode.py auditado. Para cada
mutante, conta em quantos códigos aleatórios a órbita por SAT fica UNSAT (mutante pego) e em
quantos a forma normal corrigida deixa de satisfazer a CNF. O controle (texto sem mudança) tem de
dar 0 nos dois.

Uso: mutantes.py DIR_FIBRAS q n M smin N semente"""
import json
import os
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import canon_corrigido  # noqa: E402
import orbita_fibras  # noqa: E402
from checar_cnf import Checador  # noqa: E402
from completude import codigo_aleatorio  # noqa: E402

MUTANTES = {
    "controle": ("", ""),
    # (h) entre blocos consecutivos de tamanhos DIFERENTES também
    "h_entre_tamanhos": ("if ts[0][b] == ts[0][b + 1] and ts[0][b] > 0:\n                A, B = list(bl[b]), list(bl[b + 1])",
                         "if ts[0][b] > 0 and ts[0][b + 1] > 0:\n                A, B = list(bl[b]), list(bl[b + 1]); "
                         "L = min(len(A), len(B)); A, B = A[:L], B[:L]"),
    # (h) estrita: também bloco b+1 <=lex bloco b (força igualdade)
    "h_nos_dois_sentidos": ("lex_leq_listas(cnf, [x[w][1] for w in A], [x[w][1] for w in B], q)",
                            "lex_leq_listas(cnf, [x[w][1] for w in A], [x[w][1] for w in B], q); "
                            "lex_leq_listas(cnf, [x[w][1] for w in B], [x[w][1] for w in A], q)"),
    # (h) na coordenada 2 em vez da 1 (a coordenada 2 não está ordenada dentro do bloco)
    "h_na_coordenada_2": ("lex_leq_listas(cnf, [x[w][1] for w in A], [x[w][1] for w in B], q)",
                          "lex_leq_listas(cnf, [x[w][2] for w in A], [x[w][2] for w in B], q)"),
    # (g) entre colunas de tipos diferentes
    "g_tipos_diferentes": ("            if ts[i] == ts[i + 1]:\n                lex_leq(", "            if True:\n                lex_leq("),
    # (g) incluindo a coluna 1
    "g_inclui_coluna_1": ("for i in range(2, n - 1):\n            if ts[i] == ts[i + 1]:",
                          "for i in range(1, n - 1):\n            if ts[i] == ts[i + 1]:"),
    # (e) sem respeitar a classe
    "e_ignora_classe": ("        if c1[a] != c1[a + 1]:\n            continue\n", ""),
    # (f) sem respeitar a classe
    "f_ignora_classe": ("            if ci[a] != ci[a + 1]:\n                continue\n            for w in range(M):",
                        "            for w in range(M):"),
}


def main():
    d, q, n, M, smin, N, semente = sys.argv[1], *map(int, sys.argv[2:8])
    fonte = open(os.path.join(d, "fib_encode.py")).read()
    sys.path.insert(0, d)
    for nome, (a, b) in MUTANTES.items():
        assert a in fonte, nome
        enc = orbita_fibras.carregar_encode(d, fonte.replace(a, b, 1) if a else fonte, "m_" + nome)
        rng = random.Random(semente)
        chk = Checador(enc, q, n, M, smin)
        orb = corr = 0
        for _ in range(N):
            C = codigo_aleatorio(q, n, M, smin, rng)
            if not orbita_fibras.orbita_sat(enc, C, q, n, cobertura=False, smin=smin):
                orb += 1
            pref, norm = canon_corrigido.canonizar(C, q, n)
            if not chk.satisfaz(pref, norm, False):
                corr += 1
        print(json.dumps({"mutante": nome, "q": q, "n": n, "M": M, "codigos": N,
                          "orbita_unsat": orb, "forma_normal_viola": corr}), flush=True)


if __name__ == "__main__":
    main()
