"""As quebras de simetria (a)-(h) de docs/exatos/FIBRAS_GERAL.md (PR #56) escritas como
predicados sobre um código já ordenado (lista de palavras), sem CNF e sem importar o repo.
Vale para k = n (todas as coordenadas com tipo fixo), que é o caso de K_7(6,4), M = 13.

viola(C, q, ordem) devolve a lista de quebras violadas (vazia = forma normal aceita)."""
import math
from collections import Counter


def tipo(C, i, q):
    return tuple(sorted((Counter(c[i] for c in C).get(a, 0) for a in range(q)), reverse=True))


def chave(t, ordem="min"):
    r = math.prod(math.factorial(v) for v in Counter(t).values())
    return (r, t) if ordem == "min" else (-r, t)


def viola(C, q, ordem="min"):
    n, M = len(C[0]), len(C)
    ts = [tipo(C, i, q) for i in range(n)]
    out = []
    ks = [chave(t, ordem) for t in ts]
    if ks != sorted(ks):
        out.append("a")
    for i in range(n):
        cnt = Counter(c[i] for c in C)
        if [cnt.get(a, 0) for a in range(q)] != list(ts[i]):
            out.append(f"b{i}")
    col0 = [c[0] for c in C]
    if col0 != sorted(col0):
        out.append("c")
    blocos = [[w for w in range(M) if C[w][0] == b] for b in range(q)]
    if any(C[B[r]][1] > C[B[r + 1]][1] for B in blocos for r in range(len(B) - 1)):
        out.append("d")
    prim = {}
    for b, B in enumerate(blocos):
        for w in B:
            prim.setdefault(C[w][1], b)
    for a in range(q - 1):
        if ts[1][a] == ts[1][a + 1] and a + 1 in prim and (a not in prim or prim[a] > prim[a + 1]):
            out.append("e")
            break
    for i in range(2, n):
        pw = {}
        for w, c in enumerate(C):
            pw.setdefault(c[i], w)
        for a in range(q - 1):
            if ts[i][a] == ts[i][a + 1] and a + 1 in pw and (a not in pw or pw[a] > pw[a + 1]):
                out.append(f"f{i}")
                break
    for i in range(2, n - 1):
        if ts[i] == ts[i + 1] and [c[i] for c in C] > [c[i + 1] for c in C]:
            out.append(f"g{i}")
    for b in range(q - 1):
        if ts[0][b] == ts[0][b + 1] and ts[0][b] > 0:
            if [C[w][1] for w in blocos[b]] > [C[w][1] for w in blocos[b + 1]]:
                out.append(f"h{b}")
    return out
