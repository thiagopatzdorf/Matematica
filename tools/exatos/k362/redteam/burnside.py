#!/usr/bin/env python3
"""Red team K_3(6,2), M = 15: contagem de órbitas por Burnside, independente de `fatia.py`.

Conta as órbitas de conjuntos de s pontos de Z_q^m sob o grupo de isometrias de Hamming
S_q wr S_m (permutar coordenadas e, em cada coordenada, os símbolos), pelo lema de Burnside
sobre classes de conjugação. Serve para conferir que `fatia.configuracoes(q, m, s)` sem filtro
devolve exatamente uma configuração por órbita: se as formas são duas a duas distintas (o que a
deduplicação garante) e a contagem bate com Burnside, nenhuma órbita ficou de fora.

Por que classes e não o grupo inteiro: |S_3 wr S_5| = 933 120 elementos com 243 pontos cada é
caro em Python; o tipo de ciclo de g em Z_q^m só depende do tipo de ciclo de sigma em S_m e, em
cada ciclo de sigma, da classe de conjugação da holonomia (produto das permutações de símbolos ao
longo do ciclo). O número de elementos com holonomia numa classe C num ciclo de comprimento L é
|S_q|^(L-1)·|C|.
"""
import argparse
import itertools
from fractions import Fraction
from math import factorial


def particoes(n, maximo=None):
    maximo = n if maximo is None else maximo
    if n == 0:
        yield ()
        return
    for k in range(min(n, maximo), 0, -1):
        for resto in particoes(n - k, k):
            yield (k,) + resto


def z_lambda(lam):
    out = 1
    for k in set(lam):
        c = lam.count(k)
        out *= k ** c * factorial(c)
    return out


def classes_sym(q):
    """Representante e tamanho de cada classe de conjugação de S_q (como tupla-permutação)."""
    reps = {}
    for p in itertools.permutations(range(q)):
        tipo, visto = [], set()
        for i in range(q):
            if i not in visto:
                L, j = 0, i
                while j not in visto:
                    visto.add(j)
                    j = p[j]
                    L += 1
                tipo.append(L)
        chave = tuple(sorted(tipo))
        reps.setdefault(chave, [p, 0])[1] += 1
    return [(p, n) for p, n in reps.values()]


def ciclos_no_espaco(q, m, sigma, pis):
    """Comprimentos dos ciclos de g: x -> x', x'_{sigma(i)} = pis[i](x_i), em Z_q^m."""
    pts = list(itertools.product(range(q), repeat=m))
    idx = {p: k for k, p in enumerate(pts)}
    img = []
    for x in pts:
        y = [0] * m
        for i in range(m):
            y[sigma[i]] = pis[i][x[i]]
        img.append(idx[tuple(y)])
    visto, out = [False] * len(pts), []
    for i in range(len(pts)):
        if not visto[i]:
            L, j = 0, i
            while not visto[j]:
                visto[j] = True
                j = img[j]
                L += 1
            out.append(L)
    return out


def fixos(ciclos, s):
    """Conjuntos de s pontos que são união de ciclos: coeficiente de x^s em prod(1 + x^L)."""
    poli = [1] + [0] * s
    for L in ciclos:
        for k in range(s, L - 1, -1):
            poli[k] += poli[k - L]
    return poli[s]


def orbitas(q, m, ss):
    """{s: número de órbitas de s-subconjuntos de Z_q^m sob S_q wr S_m} e |G| conferido."""
    cls = classes_sym(q)
    ident = tuple(range(q))
    soma = {s: 0 for s in ss}
    peso_total = 0
    for lam in particoes(m):
        n_sigma = factorial(m) // z_lambda(lam)
        # sigma com ciclos (0..L1-1), (L1..), ...
        sigma, inicio, ciclos_sigma = [0] * m, 0, []
        for L in lam:
            cyc = list(range(inicio, inicio + L))
            for k in range(L):
                sigma[cyc[k]] = cyc[(k + 1) % L]
            ciclos_sigma.append(cyc)
            inicio += L
        for escolha in itertools.product(cls, repeat=len(lam)):
            pis = [ident] * m
            peso = n_sigma
            for cyc, (h, tam) in zip(ciclos_sigma, escolha):
                pis[cyc[-1]] = h
                peso *= factorial(q) ** (len(cyc) - 1) * tam
            cic = ciclos_no_espaco(q, m, sigma, pis)
            peso_total += peso
            for s in ss:
                soma[s] += peso * fixos(cic, s)
    ordem = factorial(q) ** m * factorial(m)
    assert peso_total == ordem, (peso_total, ordem)
    return {s: Fraction(soma[s], ordem) for s in ss}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--q", type=int, default=3)
    ap.add_argument("--m", type=int, default=5)
    ap.add_argument("--s", default="2,3,4,5")
    a = ap.parse_args()
    for s, v in orbitas(a.q, a.m, [int(x) for x in a.s.split(",")]).items():
        print(f"q={a.q} m={a.m} s={s}: {v} órbitas")


if __name__ == "__main__":
    main()
