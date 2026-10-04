#!/usr/bin/env python3
"""Construção por partição do alfabeto para K_q(4,2), com verificação exaustiva.

Ideia (pombal): parta o alfabeto Z_q em três blocos A_1, A_2, A_3. Uma palavra x tem 4
coordenadas e 3 blocos, então duas coordenadas j < k de x caem no mesmo bloco A_i. Se o código
C_i ⊂ A_i^4 é um arranjo de cobertura de força 2 (CA(N; 2, 4, |A_i|): toda dupla de colunas
contém todos os pares de A_i), alguma palavra de C_i concorda com x em j e k, ou seja, está a
distância <= 2. Logo

    K_q(4,2) <= CAN(2,4,a) + CAN(2,4,b) + CAN(2,4,c),   a + b + c = q.

CAN(2,4,v) = v^2 quando existem 2 quadrados latinos ortogonais de ordem v (v != 2, 6);
CAN(2,4,1) = 1, CAN(2,4,2) = 5, CAN(2,4,6) = 37. Este script constrói os arranjos
(MDS [4,2,3]_v por corpo finito para v primo ou potência de primo; CA(5;2,4,2) e CA(37;2,4,6)
achados por busca local), monta o código de cada q, confere a cobertura em todo o espaço q^4 e
compara com a cota superior do ledger.

Uso: python3 tools/exatos/particao_q42.py [--qmax 21] [--gravar DIR]
"""
import argparse, itertools, json, pathlib, random

RAIZ = pathlib.Path(__file__).resolve().parents[2]


def gf(v):
    """Tabelas de soma e produto de GF(v) para v primo ou 4, 8, 9."""
    if v in (2, 3, 5, 7, 11, 13):
        return (lambda a, b: (a + b) % v), (lambda a, b: (a * b) % v)
    polys = {4: (2, 2, 0b111), 8: (2, 3, 0b1011), 9: (3, 2, None)}
    p, m, poly = polys[v]
    if p == 2:
        def mul(a, b):
            r = 0
            while b:
                if b & 1:
                    r ^= a
                b >>= 1
                a <<= 1
                if a & (1 << m):
                    a ^= poly
            return r
        return (lambda a, b: a ^ b), mul
    # GF(9) = Z_3[i]/(i^2+1): elemento a = a0 + 3*a1
    def add(a, b):
        return (a % 3 + b % 3) % 3 + 3 * ((a // 3 + b // 3) % 3)
    def mul(a, b):
        a0, a1, b0, b1 = a % 3, a // 3, b % 3, b // 3
        return (a0 * b0 - a1 * b1) % 3 + 3 * ((a0 * b1 + a1 * b0) % 3)
    return add, mul


def mds42(v):
    """[4,2,3]_v: (a, b, a+b, a+t*b) com t != 0, 1; v^2 linhas."""
    if v == 1:
        return [(0, 0, 0, 0)]
    add, mul = gf(v)
    t = 2 if v != 4 else 2  # em GF(4), 2 = alfa
    if v == 8:
        t = 2
    return [(a, b, add(a, b), add(a, mul(t, b))) for a in range(v) for b in range(v)]


def e_ca(linhas, v, k=4):
    for i, j in itertools.combinations(range(k), 2):
        if len({(r[i], r[j]) for r in linhas}) < v * v:
            return False
    return True


def busca_ca(N, v, k=4, semente=1, passos=2_000_000):
    """Busca local simples por CA(N;2,k,v): minimiza pares faltantes."""
    rnd = random.Random(semente)
    A = [[rnd.randrange(v) for _ in range(k)] for _ in range(N)]
    pares = list(itertools.combinations(range(k), 2))
    cnt = {(i, j): [[0] * v for _ in range(v)] for i, j in pares}
    for r in A:
        for i, j in pares:
            cnt[(i, j)][r[i]][r[j]] += 1
    falt = sum(1 for i, j in pares for a in range(v) for b in range(v) if cnt[(i, j)][a][b] == 0)
    T = 1.0
    for it in range(passos):
        if falt == 0:
            return [tuple(r) for r in A]
        r = rnd.randrange(N); c = rnd.randrange(k); novo = rnd.randrange(v); velho = A[r][c]
        if novo == velho:
            continue
        d = 0
        for i, j in pares:
            if c not in (i, j):
                continue
            a0, b0 = A[r][i], A[r][j]
            a1, b1 = (novo, b0) if c == i else (a0, novo)
            if cnt[(i, j)][a0][b0] == 1:
                d += 1
            if cnt[(i, j)][a1][b1] == 0:
                d -= 1
        if d <= 0 or rnd.random() < pow(2.718, -d / T):
            for i, j in pares:
                if c in (i, j):
                    cnt[(i, j)][A[r][i]][A[r][j]] -= 1
            A[r][c] = novo
            for i, j in pares:
                if c in (i, j):
                    cnt[(i, j)][A[r][i]][A[r][j]] += 1
            falt += d
        T = max(0.05, T * 0.999995)
    return None


def ca(v):
    if v == 2:
        return [(0, 0, 0, 0), (0, 1, 1, 1), (1, 0, 1, 1), (1, 1, 0, 1), (1, 1, 1, 0)]
    if v == 6:
        for s in range(1, 50):
            r = busca_ca(37, 6, semente=s)
            if r:
                return r
        raise SystemExit("não achei CA(37;2,4,6)")
    return mds42(v)


CAN = {1: 1, 2: 5, 3: 9, 4: 16, 5: 25, 6: 37, 7: 49, 8: 64, 9: 81}


def melhor_particao(q):
    best = None
    for a in range(1, q + 1):
        for b in range(a, q + 1):
            c = q - a - b
            if c < b:
                continue
            if c not in CAN or b not in CAN or a not in CAN:
                continue
            s = CAN[a] + CAN[b] + CAN[c]
            if best is None or s < best[0]:
                best = (s, (a, b, c))
    return best


def codigo(q, parts, cas):
    C, base = [], 0
    for p in parts:
        for r in cas[p]:
            C.append(tuple(base + x for x in r))
        base += p
    return C


def cobre(q, C):
    P = [set() for _ in range(6)]
    pares = list(itertools.combinations(range(4), 2))
    for c in C:
        for t, (i, j) in enumerate(pares):
            P[t].add((c[i], c[j]))
    for x in itertools.product(range(q), repeat=4):
        if not any((x[i], x[j]) in P[t] for t, (i, j) in enumerate(pares)):
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qmax", type=int, default=21)
    ap.add_argument("--gravar")
    a = ap.parse_args()
    cells = {c["id"]: c for c in json.loads((RAIZ / "ledger/cells.json").read_text())["cells"]}
    cas = {}
    for v in range(1, 10):
        cas[v] = ca(v)
        assert len(cas[v]) == CAN[v] and e_ca(cas[v], v), v
    print("q  partição   |C|  ceil(q²/3)  ledger(lb-ub)  cobre?")
    for q in range(3, a.qmax + 1):
        s, parts = melhor_particao(q)
        C = codigo(q, parts, cas)
        ok = cobre(q, C)
        c = cells.get(f"K{q}(4,2)")
        led = f"{c['published']['lb']['value']}-{c['best']['ub']}" if c else "?"
        print(f"{q:2d} {str(parts):11s} {len(C):4d} {-(-q*q//3):6d}      {led:10s}  {ok}")
        if a.gravar and ok:
            d = pathlib.Path(a.gravar); d.mkdir(parents=True, exist_ok=True)
            (d / f"q{q}_n4_R2_M{len(C)}_particao.txt").write_text(
                "\n".join(" ".join(map(str, w)) for w in C) + "\n")


if __name__ == "__main__":
    main()
