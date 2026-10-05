#!/usr/bin/env python3
"""Conferência exata (só biblioteca padrão, inteiros) dos certificados de `certificar_lp.py`.

Reconstrói cada sistema a partir de (q, n, R, M, s*, K, t), sem reaproveitar código do gerador,
e confere para cada folha: y >= 0 inteiro, mu inteiro e

    sum_linhas y*rhs + sum mu*rhs  >  sum_c max(g_c lb_c, g_c ub_c),   g = y^T G + mu^T E.

Confere também que as folhas de cada instância formam uma árvore binária completa (ramos
z_c = 1 e z_c = 0) e que as instâncias certificadas são exatamente as da lista dada, na ordem.
Convenção de índices: o ponto c tem índice sum_i c_i q^(n-1-i) (ordem de itertools.product);
linha de cobertura x = índice de x; linha de fibra (j, a), j >= 1, = q^n + (j-1)q + a;
linhas de igualdade = [tamanho, bloco 1, ..., bloco q-1].
"""
import argparse
import gzip
import hashlib
import itertools
import json
import sys


def bolas(q, n, R):
    pts = list(itertools.product(range(q), repeat=n))
    return pts, [[i for i, y in enumerate(pts) if sum(a != b for a, b in zip(x, y)) <= R] for x in pts]


def arvore_completa(caminhos):
    if caminhos == [[]]:
        return True
    if not caminhos or any(not c for c in caminhos):
        return False
    var = caminhos[0][0][0]
    if any(c[0][0] != var for c in caminhos):
        return False
    lados = {v: [c[1:] for c in caminhos if c[0][1] == v] for v in (0, 1)}
    return all(arvore_completa(lados[v]) for v in (0, 1))


def folha_ok(q, n, M, s, K, t, pts, bola, folha):
    N = len(pts)
    fixo = {}
    Kset = {(0,) + tuple(k) for k in K}
    for i, p in enumerate(pts):
        if p[0] == 0:
            fixo[i] = 1 if p in Kset else 0
    for j, v in folha["fixos"]:
        if fixo.get(j, v) != v:
            return True  # ramo vazio: contradiz a fatia fixada, nada a provar
        fixo[j] = v
    y = {int(k): v for k, v in folha["y"].items()}
    mu = folha["mu"]
    if any(not isinstance(v, int) or v < 0 for v in y.values()) or len(mu) != q:
        return False
    if any(not isinstance(v, int) for v in mu) or any(k < 0 or k >= N + (n - 1) * q for k in y):
        return False
    if s == 0 and any(k >= N for k in y):
        return False
    g = [mu[0] + (mu[p[0]] if p[0] else 0) for p in pts]
    lhs = mu[0] * M + sum(m * tb for m, tb in zip(mu[1:], t))
    for k, v in y.items():
        if k < N:
            lhs += v
            for c in bola[k]:
                g[c] += v
        else:
            j, a = divmod(k - N, q)
            lhs += v * s
            for c, p in enumerate(pts):
                if p[j + 1] == a:
                    g[c] += v
    rhs = sum(g[c] * fixo[c] if c in fixo else max(g[c], 0) for c in range(N))
    return lhs > rhs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("q", "n", "R", "M"):
        ap.add_argument("--" + k, type=int, required=True)
    ap.add_argument("--instancias", required=True)
    ap.add_argument("--certificados", required=True)
    ap.add_argument("--sha256", help="sha256 esperado do JSON de instâncias")
    a = ap.parse_args()
    bruto = open(a.instancias, "rb").read()
    if a.sha256 and hashlib.sha256(bruto).hexdigest() != a.sha256:
        sys.exit("sha256 da lista de instâncias não confere")
    ins = json.loads(bruto)
    pts, bola = bolas(a.q, a.n, a.R)
    vistos, ruins, folhas = 0, [], 0
    for linha in gzip.open(a.certificados, "rt"):
        reg = json.loads(linha)
        i = reg["inst"]
        s, K, t = ins[i]
        if i != vistos or [reg["s"], reg["K"], reg["t"]] != [s, K, t] or not reg["folhas"]:
            ruins.append(i)
        elif not arvore_completa([f["fixos"] for f in reg["folhas"]]):
            ruins.append(i)
        elif not all(folha_ok(a.q, a.n, a.M, s, K, t, pts, bola, f) for f in reg["folhas"]):
            ruins.append(i)
        vistos += 1
        folhas += len(reg["folhas"] or [])
    ok = not ruins and vistos == len(ins)
    print(f"K_{a.q}({a.n},{a.R}) M={a.M}: {vistos} de {len(ins)} instâncias, {folhas} folhas, "
          f"recusadas {ruins[:20]}{'...' if len(ruins) > 20 else ''} -> {'TODAS INVIÁVEIS' if ok else 'FALHOU'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
