#!/usr/bin/env python3
"""Conferência exata (só biblioteca padrão, inteiros) dos certificados binários de `certificar_bin.py`.

Escrito do zero, sem importar o gerador nem `verificar.py`. Reconstrói, para cada instância
(s*, K, t) da lista, o sistema 0-1 sobre z_c, c em Z_2^n (índice de c = Σ c_i 2^(n−1−i)):

  cobertura  Σ_{d(c,x) <= R} z_c >= 1             linha x            (0 <= x < 2^n)
  fibras     Σ_{c_j = a} z_c >= s*                linha 2^n + 2(j−1) + a, j = 1..n−1
  igualdades [Σ z_c = M, Σ_{c_0 = 1} z_c = t_1]   multiplicadores mu (livres)
  fatia 0    z_c = 1 se c = (0, k) com k em K, z_c = 0 nas outras palavras com c_0 = 0

Cada folha tem `ramos`: linhas extras [S, "ge", r] = Σ_{c∈S} z_c >= r ou [S, "le", r] =
Σ_{c∈S} z_c <= r, com multiplicadores yr >= 0, ou `fixos` [[c, v], ...] (z_c = v). As folhas
de uma instância têm de formar uma árvore completa: em cada nó, os dois filhos são
(S, "le", r) e (S, "ge", r + 1) para o mesmo S (exaustivo porque Σ_S z_c é inteiro), ou
z_c = 1 / z_c = 0. Para cada folha confere, em inteiros,

  Σ y·rhs + Σ yr·rhs + Σ mu·rhs  >  Σ_c max(g_c lb_c, g_c ub_c),

com g o vetor de coeficientes da combinação; com isso a folha não tem solução nem fracionária.

  python3 tools/exatos/lp_bin/verificar_bin.py --n 10 --R 3 --M 11 --instancias i.json \\
      --certificados c.jsonl.gz --sha256 <sha256 da lista>
"""
import argparse
import gzip
import hashlib
import json
import sys


def no_da_folha(f):
    """Lista de decisões da folha, cada uma normalizada para (chave do nó, lado)."""
    out = []
    for c, v in f.get("fixos", []):
        out.append((("var", c), v))
    for S, sent, r in f.get("ramos", []):
        k = r if sent == "le" else r - 1
        out.append((("soma", tuple(sorted(S)), k), 0 if sent == "le" else 1))
    return out


def arvore(caminhos):
    if caminhos == [[]]:
        return True
    if not caminhos or any(not c for c in caminhos):
        return False
    no = caminhos[0][0][0]
    if any(c[0][0] != no for c in caminhos):
        return False
    lados = {v: [c[1:] for c in caminhos if c[0][1] == v] for v in (0, 1)}
    return all(arvore(lados[v]) for v in (0, 1))


def folha_ok(n, R, M, s, K, t, f):
    N = 1 << n
    lb, ub = [0] * N, [1] * N
    Kset = set()
    for k in K:
        v = 0
        for b in k:
            v = 2 * v + int(b)
        Kset.add(v)
    for c in range(N >> 1):  # c_0 = 0
        lb[c] = ub[c] = 1 if c in Kset else 0
    for c, v in f.get("fixos", []):
        if lb[c] == ub[c] and lb[c] != v:
            return True  # ramo vazio
        lb[c] = ub[c] = v
    y = {int(k): v for k, v in f["y"].items()}
    mu, yr, ramos = f["mu"], f.get("yr", []), f.get("ramos", [])
    if len(mu) != 2 or not all(isinstance(v, int) for v in mu):
        return False
    if len(yr) != len(ramos) or any(not isinstance(v, int) or v < 0 for v in yr):
        return False
    if any(not isinstance(v, int) or v < 0 or k < 0 or k >= N + 2 * (n - 1) for k, v in y.items()):
        return False
    if s == 0 and any(k >= N for k in y):
        return False
    g = [mu[0] + (mu[1] if c >> (n - 1) else 0) for c in range(N)]
    lhs = mu[0] * M + mu[1] * t[0]
    for k, v in y.items():
        if not v:
            continue
        if k < N:
            lhs += v
            for c in range(N):
                if bin(c ^ k).count("1") <= R:
                    g[c] += v
        else:
            j, a = divmod(k - N, 2)
            lhs += v * s
            sh = n - 2 - j  # coordenada j + 1
            for c in range(N):
                if (c >> sh) & 1 == a:
                    g[c] += v
    for (S, sent, r), v in zip(ramos, yr):
        if sent not in ("ge", "le") or len(set(S)) != len(S) or any(not 0 <= c < N for c in S):
            return False
        sg = 1 if sent == "ge" else -1
        lhs += v * sg * r
        for c in S:
            g[c] += v * sg
    rhs = sum(max(g[c] * lb[c], g[c] * ub[c]) for c in range(N))
    return lhs > rhs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("n", "R", "M"):
        ap.add_argument("--" + k, type=int, required=True)
    ap.add_argument("--instancias", required=True)
    ap.add_argument("--certificados", required=True)
    ap.add_argument("--sha256", required=True, help="sha256 esperado da lista (a lista é parte da prova)")
    a = ap.parse_args()
    bruto = open(a.instancias, "rb").read()
    if hashlib.sha256(bruto).hexdigest() != a.sha256.strip().lower():
        sys.exit("sha256 da lista de instâncias não confere")
    ins = json.loads(bruto)
    vistos, ruins, folhas = 0, [], 0
    for linha in gzip.open(a.certificados, "rt"):
        reg = json.loads(linha)
        i = reg["inst"]
        s, K, t = ins[i]
        fs = reg["folhas"]
        if (i != vistos or [reg["s"], reg["K"], reg["t"]] != [s, K, t] or not fs
                or not arvore([no_da_folha(f) for f in fs])
                or not all(folha_ok(a.n, a.R, a.M, s, K, t, f) for f in fs)):
            ruins.append(i)
        vistos += 1
        folhas += len(fs or [])
    ok = not ruins and vistos == len(ins)
    print(f"K_2({a.n},{a.R}) M={a.M}: {vistos} de {len(ins)} instâncias, {folhas} folhas, "
          f"recusadas {len(ruins)} {ruins[:20]} -> {'TODAS INVIÁVEIS' if ok else 'FALHOU'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
