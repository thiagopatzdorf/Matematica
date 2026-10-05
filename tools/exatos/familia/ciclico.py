#!/usr/bin/env python3
"""Busca exaustiva de códigos por blocos invariantes pela rotação das coordenadas (K_q(n, n-2)).

Construção por blocos (blocos_sat.py, docs/exatos/FAMILIA_KQ_N_N2.md): C = ∪ C_j, C_j ⊂ A_j^n, e

    C cobre  <=>  para toda partição ordenada (S_j) de [n] existe j com S_j ∈ f(C_j),

onde f(D) = {S : D|S cobre A^S com >= 2 concordâncias} (a "família" de D). Aqui cada C_j é a união
de órbitas sob a rotação cíclica das n coordenadas, mais palavras constantes. Então f(C_j) é
invariante por rotação e o espaço é pequeno o bastante para enumerar TUDO:

  1. para cada bloco (a, constantes c, r órbitas) enumera as palavras representantes, canoniza por
     rotação e por permutação de símbolos que preserva o conjunto das constantes, e calcula f;
  2. guarda só as famílias maximais (para o mesmo número de palavras);
  3. combina blocos cuja soma de tamanhos é q e de palavras é <= M, conferindo a condição acima em
     todas as k^n partições ordenadas.

Bloco de tamanho 1 com sua constante cobre todo S com |S| >= 2. Sem resultado = não existe código
dessa forma (é exaustivo dentro da forma); com resultado, o código é reconferido por cobre_n2.c.

Uso: ciclico.py q n M [--r2 AMAX]    (--r2: também blocos com 2 órbitas quando a <= AMAX)
"""
import itertools
import sys

import numpy as np

DIG = "0123456789abcdefghijklmnopqrstuvwxyz"


def orbita(w):
    n = len(w)
    return sorted({tuple(w[(i + t) % n] for i in range(n)) for t in range(n)})


def familia(code, a, n):
    """bitset (array bool de tamanho 2^n) dos S em que code|S cobre Z_a^S."""
    f = np.zeros(1 << n, dtype=bool)
    C = np.array(code, dtype=np.int8)  # (m, n)
    for S in range(1 << n):
        pos = [i for i in range(n) if (S >> i) & 1]
        s = len(pos)
        if s < 2:
            continue
        # cobertura é monótona: se algum S sem uma coordenada já cobre, S cobre
        if any(f[S & ~(1 << i)] for i in pos):
            f[S] = True
            continue
        pts = np.array(list(itertools.product(range(a), repeat=s)), dtype=np.int8)  # (a^s, s)
        ag = (pts[:, None, :] == C[None, :, pos]).sum(axis=2)  # (a^s, m)
        f[S] = bool((ag.max(axis=1) >= 2).all())
    return f


def canon(words, a, const):
    """forma canônica de um conjunto de palavras sob rotação e permutações de símbolos que fixam const."""
    n = len(words[0])
    best = None
    resto = [v for v in range(a) if v not in const]
    for pc in itertools.permutations(const):
        for pr in itertools.permutations(resto):
            mp = {}
            for x, y in zip(const, pc):
                mp[x] = y
            for x, y in zip(resto, pr):
                mp[x] = y
            for t in range(n):
                key = tuple(sorted(tuple(mp[w[(i + t) % n]] for i in range(n)) for w in words))
                if best is None or key < best:
                    best = key
    return best


def blocos_possiveis(a, n, c, r, M):
    """lista de (palavras, família) maximais para um bloco de tamanho a com c constantes e r órbitas."""
    const = list(range(c))
    consts = [tuple([v] * n) for v in const]
    vistos = set()
    out = []
    reps = list(itertools.product(range(a), repeat=n))
    for combo in itertools.combinations(reps, r):
        code = set(consts)
        for w in combo:
            code.update(orbita(w))
        code = sorted(code)
        if len(code) > M:
            continue
        key = canon(code, a, const) if a <= 5 else tuple(code)
        if key in vistos:
            continue
        vistos.add(key)
        out.append((code, familia(code, a, n)))
    # maximais por número de palavras: descarta família contida em outra com <= palavras
    out.sort(key=lambda t: (len(t[0]), -int(t[1].sum())))
    keep = []
    for code, f in out:
        if any(len(c2) <= len(code) and (f <= f2).all() for c2, f2 in keep):
            continue
        keep.append((code, f))
    return keep


def particoes(n, k):
    """matriz (k^n, k) com o submask de cada bloco em cada partição ordenada."""
    rows = []
    for sig in itertools.product(range(k), repeat=n):
        rows.append([sum(1 << i for i in range(n) if sig[i] == j) for j in range(k)])
    return np.array(rows, dtype=np.int64)


def main(argv):
    q, n, M = int(argv[1]), int(argv[2]), int(argv[3])
    r2 = int(argv[argv.index("--r2") + 1]) if "--r2" in argv else 0
    tipos = {}  # (a, c, r) -> lista de blocos
    for a in range(2, q + 1):
        for r in (1, 2) if a <= r2 else (1,):
            for c in range(0, a + 1):
                if a ** n * (1 if r == 1 else a ** n) > 200_000:
                    continue
                bl = blocos_possiveis(a, n, c, r, M)
                if bl:
                    tipos[a, c, r] = bl
                    print(f"bloco a={a} c={c} r={r}: {len(bl)} famílias maximais, palavras {sorted({len(b[0]) for b in bl})}", file=sys.stderr)
    full = (1 << n) - 1
    achou = 0
    # singleton = bloco de 1 símbolo com a constante: família {|S| >= 2}
    fs = np.array([bin(S).count("1") >= 2 for S in range(1 << n)])
    chaves = list(tipos)
    for k in (1, 2):
        for escolha in itertools.combinations_with_replacement(chaves, k):
            asz = sum(t[0] for t in escolha)
            if asz > q:
                continue
            t = q - asz  # singletons
            P = particoes(n, k + t) if k + t <= 4 or n <= 7 else None
            if P is None:
                continue
            for blks in itertools.product(*[tipos[c] for c in escolha]):
                nw = sum(len(b[0]) for b in blks) + t
                if nw > M:
                    continue
                fams = [b[1] for b in blks] + [fs] * t
                cov = np.zeros(len(P), dtype=bool)
                for j, f in enumerate(fams):
                    cov |= f[P[:, j]]
                if cov.all():
                    achou += 1
                    off = 0
                    linhas = []
                    for c, b in zip(escolha, blks):
                        linhas += ["".join(DIG[off + v] for v in w) for w in b[0]]
                        off += c[0]
                    for s in range(t):
                        linhas.append(DIG[off + s] * n)
                    print(f"# ACHOU q={q} n={n} M={nw} blocos={escolha} singletons={t}")
                    print("\n".join(linhas))
                    sys.stdout.flush()
                    if achou >= 3:
                        return
    print(f"# fim: {achou} códigos achados com <= {M} palavras", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv)
