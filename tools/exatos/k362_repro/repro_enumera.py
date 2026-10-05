"""Classes de conjuntos K de s pontos distintos de Z_q^m sob S_q wr S_m, enumeradas por colunas.

Um conjunto ordenado de s pontos é uma matriz s x m. A menos de permutar os símbolos de cada
coordenada, cada coluna é uma partição das s linhas em <= q blocos (escrita como RGS). Logo a classe
de K é o multiconjunto das m partições a menos de S_s agindo nas linhas, com a condição de que as
linhas sejam distintas (todo par de linhas separado por alguma coluna). Enumeramos os multiconjuntos
e tomamos como forma canônica o menor (em ordem lexicográfica) multiconjunto ordenado obtido
reordenando as linhas. Contagem conferida contra Burnside em `burnside_orbitas`.
"""
import itertools
import math
from fractions import Fraction

import numpy as np


def particoes(s, q):
    """RGS de comprimento s com valores < q (partições de s linhas em <= q blocos)."""
    out = []

    def rec(pref, mx):
        if len(pref) == s:
            out.append(tuple(pref))
            return
        for v in range(min(mx + 2, q)):
            rec(pref + [v], max(mx, v))
    rec([0], 0)
    return out


def rgs(col):
    ren, out = {}, []
    for v in col:
        out.append(ren.setdefault(v, len(ren)))
    return tuple(out)


def classes(q, m, s):
    """Lista de representantes (cada um: tupla de s pontos, ponto = tupla de m símbolos)."""
    P = particoes(s, q)
    idx = {p: i for i, p in enumerate(P)}
    perms = list(itertools.permutations(range(s)))
    # T[k][i]: índice da partição i depois de reordenar as linhas pela permutação k
    T = np.array([[idx[rgs([p[sg[r]] for r in range(s)])] for p in P] for sg in perms], dtype=np.int64)
    pares = list(itertools.combinations(range(s), 2))
    sep = np.array([[p[a] != p[b] for p in P] for a, b in pares], dtype=bool)  # (pares, P)
    peso = len(P) ** np.arange(m - 1, -1, -1, dtype=np.int64)
    chaves = set()
    it = itertools.combinations_with_replacement(range(len(P)), m)
    while True:
        bloco = np.array(list(itertools.islice(it, 200000)), dtype=np.int64)
        if bloco.size == 0:
            break
        # linhas distintas: todo par separado por alguma coluna
        ok = sep[:, bloco].any(axis=2).all(axis=0) if pares else np.ones(len(bloco), bool)
        bloco = bloco[ok]
        melhor = None
        for k in range(len(perms)):
            ch = np.sort(T[k][bloco], axis=1) @ peso
            melhor = ch if melhor is None else np.minimum(melhor, ch)
        chaves.update(melhor.tolist())
    reps = []
    for ch in sorted(chaves):
        cols = [P[(ch // int(w)) % len(P)] for w in peso]
        reps.append(tuple(tuple(c[r] for c in cols) for r in range(s)))
    return reps


def descobertos(K, q, R):
    """Número de pontos de Z_q^m a distância > R de todo ponto de K."""
    m = len(K[0])
    X = np.array(list(itertools.product(range(q), repeat=m)))
    d = np.stack([(X != np.array(k)).sum(axis=1) for k in K])
    return int((d.min(axis=0) > R).sum())


def volume(m, r, q):
    return sum(math.comb(m, i) * (q - 1) ** i for i in range(r + 1))


def passa_filtro(K, q, R, M):
    """Lema da fatia: os |U| pontos de {0} x U só são cobertos pelas M - s palavras com c_0 != 0,
    cada uma cobrindo no máximo V(m, R-1) deles."""
    return descobertos(K, q, R) <= (M - len(K)) * volume(len(K[0]), R - 1, q)


def _tipos(n):
    """Partições de n (tipos de ciclo) com o número de permutações de cada tipo."""
    def rec(n, mx):
        if n == 0:
            yield ()
            return
        for k in range(min(n, mx), 0, -1):
            for resto in rec(n - k, k):
                yield (k,) + resto
    for t in rec(n, n):
        cnt = math.factorial(n)
        for k in set(t):
            c = t.count(k)
            cnt //= k ** c * math.factorial(c)
        yield t, cnt


def burnside_orbitas(q, m, s):
    """Órbitas de s-subconjuntos de Z_q^m sob S_q wr S_m (Cauchy-Frobenius).

    g = (pi; sigma_1..sigma_m). Para um ciclo c de pi de comprimento l, o produto tau_c dos sigma
    no ciclo é uniforme em S_q (6^(l-1) escolhas por elemento de S_3). Um ponto fixo de g é
    determinado por um símbolo fixo de tau_c em cada ciclo. Para g^k, o ciclo c parte-se em
    h = gcd(k, l) ciclos com produto conjugado a tau_c^(k/h)."""
    classes_q = list(_tipos(q))
    total = Fraction(0)
    for tpi, npi in _tipos(m):
        for escolha in itertools.product(range(len(classes_q)), repeat=len(tpi)):
            peso = npi
            for l, e in zip(tpi, escolha):
                peso *= math.factorial(q) ** (l - 1) * classes_q[e][1]
            ordem = math.lcm(*[l * math.lcm(*classes_q[e][0]) for l, e in zip(tpi, escolha)])
            f = {}
            for k in range(1, ordem + 1):
                if ordem % k:
                    continue
                v = 1
                for l, e in zip(tpi, escolha):
                    h = math.gcd(k, l)
                    v *= sum(c for c in classes_q[e][0] if (k // h) % c == 0) ** h
                f[k] = v
            ciclos = {}
            for d in f:  # Möbius: ciclos de comprimento d nos pontos
                ciclos[d] = sum(_mobius(d // e) * f[e] for e in f if d % e == 0) // d
            poli = [1] + [0] * s
            for d, c in ciclos.items():
                for _ in range(c):
                    for j in range(s, d - 1, -1):
                        poli[j] += poli[j - d]
            total += peso * poli[s]
    G = math.factorial(q) ** m * math.factorial(m)
    assert total % G == 0
    return int(total / G)


def _mobius(n):
    r, p = 1, 2
    while p * p <= n:
        if n % p == 0:
            n //= p
            if n % p == 0:
                return 0
            r = -r
        p += 1
    return -r if n > 1 else r


def forma(K):
    """Forma canônica de um conjunto (mesma regra de `classes`, para um conjunto só)."""
    cols = list(zip(*K))
    return min(tuple(sorted(rgs([c[r] for r in sg]) for c in cols))
               for sg in itertools.permutations(range(len(K))))
