#!/usr/bin/env python3
"""Instâncias da "fatia mínima" (`fatia.py`) como problemas pseudo-booleanos (OPB).

Variáveis z_c, uma por ponto c de Z_q^n ("c é palavra do código"). Restrições:
  cobertura   para todo x: sum_{d(c,x) <= R} z_c >= 1
  tamanho     sum_c z_c = M  (palavras distintas: ver fatia.py)
  fatia 0     z_c = 1 para as s* palavras da configuração (com c_0 = 0), z_c = 0 para os
              demais c com c_0 = 0
  blocos      sum_{c_0 = b} z_c = t_b  (b = 1..q-1)
  fibras      sum_{c_j = a} z_c >= s*  para toda coordenada j >= 1 e símbolo a
Com indicadores de ponto, as cardinalidades são restrições lineares e o resolvedor de planos de
corte (RoundingSat) raciocina por contagem direto; a prova sai no formato VeriPB.
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fatia  # noqa: E402


def opb(q, n, R, M, inst):
    s, K, t = inst
    pts = list(itertools.product(range(q), repeat=n))
    var = {c: i + 1 for i, c in enumerate(pts)}
    cons = []  # (termos [(coef, var)], op, rhs)
    for x in pts:
        cons.append(([(1, var[c]) for c in pts if fatia.dist(c, x) <= R], ">=", 1))
    cons.append(([(1, var[c]) for c in pts], "=", M))
    fixos = {(0,) + tuple(k) for k in K}
    for c in pts:
        if c[0] == 0:
            cons.append(([(1, var[c])], "=", 1 if c in fixos else 0))
    for b, tb in enumerate(t, start=1):
        cons.append(([(1, var[c]) for c in pts if c[0] == b], "=", tb))
    if s > 0:
        for j in range(1, n):
            for a in range(q):
                cons.append(([(1, var[c]) for c in pts if c[j] == a], ">=", s))
    neq = sum(1 for c in cons if c[1] == "=")
    linhas = [f"* #variable= {len(pts)} #constraint= {len(cons)} #equal= {neq} intsize= 8"]
    for termos, op, rhs in cons:
        linhas.append(" ".join(f"+{a} x{v}" for a, v in termos) + f" {op} {rhs} ;")
    return "\n".join(linhas) + "\n", var


if __name__ == "__main__":
    q, n, R, M, i = map(int, sys.argv[1:6])
    ins = fatia.instancias(q, n, R, M)
    sys.stdout.write(opb(q, n, R, M, ins[i])[0])
