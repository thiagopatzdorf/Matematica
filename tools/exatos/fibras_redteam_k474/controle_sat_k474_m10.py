#!/usr/bin/env python3
"""Controle de SAT em tamanho real: o código de 10 palavras de K_4(7,4) (data/codes/q4_n7_R4_M10.txt, que
cobre) tem de ser aceito pela CNF COMPLETA (cobertura por triplas + quebras (a)-(h)) da instância do seu
perfil, na órbita de isometrias, nas duas ordens. Se der UNSAT, a CNF ou as quebras perdem códigos que cobrem.

Uso: python3 controle_sat_k474_m10.py [arquivo_do_codigo]
"""
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "fibras"))
sys.path.insert(0, AQUI)
import fib_encode as enc  # noqa: E402
import lema1_construcao as lc  # noqa: E402
import orbita_indep as o  # noqa: E402


def main():
    arq = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "..", "..", "..", "data", "codes", "q4_n7_R4_M10.txt")
    cod = [tuple(int(c) for c in ln.strip()) for ln in open(arq) if ln.strip()]
    q, n, R, M = 4, 7, 4, len(cod)
    assert lc.descobertos(cod, q, n, R) == 0
    print("tipos das colunas:", [o.tipo(cod, i, q) for i in range(n)], "smin ledger:", enc.fibra_minima(q, n, R, M))
    ok_tudo = True
    for ordem in ("min", "max"):
        t = time.time()
        ok = o.orbita_sat(enc, q, n, M, R, cod, ordem, com_cobertura=True)
        print(f"ordem {ordem}: CNF completa (com cobertura) na órbita do código real: {'SAT' if ok else 'UNSAT'} ({time.time() - t:.0f}s)", flush=True)
        ok_tudo &= ok
    sys.exit(0 if ok_tudo else 1)


if __name__ == "__main__":
    main()
