#!/usr/bin/env python3
"""Escolha canônica da fibra no caso equilibrado da fatia mínima (docs/exatos/k362/).

A redução de tools/exatos/gaps2 escolhe UMA fibra de tamanho mínimo s*. Quando M = q·s*, todas
as q·n fibras têm s* palavras e um mesmo código cai em até q·n instâncias. Aqui a fibra escolhida
passa a ser a de MENOR |U|, onde U(j,a) são os pontos de {x : x_j = a} a distância > R de toda
palavra de F(j,a). Duas consequências, provadas em K3_M15_GROUP_ACTION.md (lema da soma):

  (1) filtro: sum_{(j,a)} |U(j,a)| <= sum_x d(x,C) <= R·(q^n - M); logo a fibra escolhida tem
      |U| <= floor(R·(q^n - M) / (q·n)). Para K_3(6,2), M = 15: |U| <= 79 (o filtro antigo era 110);
  (2) quebra de simetria dentro da instância: toda fibra (j,a) tem |U(j,a)| >= |U(K)|, escrito com
      variáveis auxiliares w_{x,j} ("x não é coberto pela própria fibra na coordenada j").
"""
import argparse
import itertools
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "gaps2"))
import fatia  # noqa: E402
import fatia_pb  # noqa: E402


def equilibrada(q, M, s):
    return s > 0 and q * s == M


def limite_U(q, n, R, M):
    """Teto de |U| da fibra de menor |U| num código equilibrado (lema da soma)."""
    return R * (q ** n - M) // (q * n)


def n_descobertos(q, m, R, K):
    return len(fatia.descobertos(q, m, R, K))


def reduz(q, n, R, M, instancias):
    """Instâncias que sobrevivem ao filtro (1); as não equilibradas passam intactas."""
    teto = limite_U(q, n, R, M)
    cache, out = {}, []
    for s, K, t in instancias:
        if equilibrada(q, M, s):
            u = cache.setdefault(K, n_descobertos(q, n - 1, R, K))
            if u > teto:
                continue
        out.append((s, K, t))
    return out


def U_fibras(q, n, R, cod):
    """|U(j,a)| para toda fibra de um código (lista de tuplas)."""
    out = {}
    for j in range(n):
        for a in range(q):
            F = [c for c in cod if c[j] == a]
            out[j, a] = sum(1 for x in itertools.product(range(q), repeat=n) if x[j] == a
                            and all(fatia.dist(c, x) > R for c in F))
    return out


def opb(q, n, R, M, inst, regra="min"):
    """OPB de fatia_pb + (2) quando a instância é equilibrada. Devolve (texto, var).
    regra "min": a fibra 0 é a de menor |U| (toda fibra tem |U| >= u); "max": a de maior |U|
    (toda fibra tem |U| <= u; não vale o filtro (1), que é só da regra "min")."""
    txt, var = fatia_pb.opb(q, n, R, M, inst)
    s, K, _ = inst
    if not equilibrada(q, M, s):
        return txt, var
    u = n_descobertos(q, n - 1, R, K)
    pts = list(itertools.product(range(q), repeat=n))
    w = {}
    linhas = []
    for x in pts:
        for j in range(n):
            w[x, j] = len(var) + len(w) + 1
            viz = [var[c] for c in pts if c[j] == x[j] and fatia.dist(c, x) <= R]
            if regra == "min":  # w = 1 só se nenhuma palavra da própria fibra cobre x
                linhas.append(" ".join(f"-1 x{v}" for v in viz) + f" -{len(viz)} x{w[x, j]} >= -{len(viz)} ;")
            else:  # w = 1 sempre que nenhuma palavra da própria fibra cobre x
                linhas.append(" ".join(f"+1 x{v}" for v in viz) + f" +1 x{w[x, j]} >= 1 ;")
    for j in range(n):
        for a in range(q):
            termos = " ".join(f"{'+1' if regra == 'min' else '-1'} x{w[x, j]}" for x in pts if x[j] == a)
            linhas.append(termos + (f" >= {u} ;" if regra == "min" else f" >= -{u} ;"))
    cab, corpo = txt.split("\n", 1)
    nv, nc, ne = len(var) + len(w), len(corpo.splitlines()) + len(linhas), cab.split("#equal= ")[1].split()[0]
    cab = f"* #variable= {nv} #constraint= {nc} #equal= {ne} intsize= 8"
    return cab + "\n" + corpo + "\n".join(linhas) + "\n", var


def normalizar_canonica(cod, q, n, R, regra="min"):
    """Como canon_fatia.normalizar, mas no caso equilibrado escolhe a fibra de menor |U|
    (desempate pelo menor (j,a)). Devolve (instância, código transformado)."""
    import canon_fatia
    from collections import Counter
    cnt = Counter((j, c[j]) for c in cod for j in range(n))
    s = min(cnt.get((j, a), 0) for j in range(n) for a in range(q))
    if not equilibrada(q, len(cod), s):
        return canon_fatia.normalizar(cod, q, n)
    Us = U_fibras(q, n, R, cod)
    sinal = 1 if regra == "min" else -1
    j, a = min(Us, key=lambda k: (sinal * Us[k], k))
    # leva (j,a) para (0,0) por uma isometria e deixa canon_fatia fazer o resto: ela pega o menor
    # (j,a) de tamanho mínimo, que depois da troca é (0,0) (todas as fibras têm o mesmo tamanho)
    perm = [j] + [i for i in range(n) if i != j]
    sw = {a: 0, 0: a}
    cod = [tuple(sw.get(c[i], c[i]) if i == j else c[i] for i in perm) for c in cod]
    return canon_fatia.normalizar(cod, q, n)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--instancias", required=True, help="JSON de rodar_pb.py --listar")
    for k in ("q", "n", "R", "M"):
        ap.add_argument("--" + k, type=int, required=True)
    ap.add_argument("--saida", help="JSON com [índice original, instância] das que sobram")
    a = ap.parse_args()
    ins = [(s, tuple(tuple(k) for k in K), tuple(t)) for s, K, t in json.load(open(a.instancias))]
    red = set(reduz(a.q, a.n, a.R, a.M, ins))
    fica = [(i, x) for i, x in enumerate(ins) if x in red]
    print(f"{len(ins)} instâncias -> {len(fica)} (teto de |U| = {limite_U(a.q, a.n, a.R, a.M)})")
    if a.saida:
        json.dump([[i, [s, [list(k) for k in K], list(t)]] for i, (s, K, t) in fica], open(a.saida, "w"))


if __name__ == "__main__":
    main()
