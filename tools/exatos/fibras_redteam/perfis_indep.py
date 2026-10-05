"""Enumeração independente dos perfis de K_q(n, n-2) com M palavras e fibras >= s_min (sem
importar tools/exatos/fibras) e comparação, conjunto a conjunto, com um JSONL de certificados.

Tipo = vetor decrescente das q fibras de uma coordenada (soma M, cada uma >= s_min), obtido aqui
por força bruta sobre itertools.product. Perfil = multiconjunto de n tipos."""
import itertools
import json
import math
import sys
from collections import Counter


def tipos_forca_bruta(q, M, smin):
    out = set()
    for v in itertools.product(range(smin, M - smin * (q - 1) + 1), repeat=q):
        if sum(v) == M:
            out.add(tuple(sorted(v, reverse=True)))
    return sorted(out)


def perfis(q, n, M, smin):
    return {tuple(sorted(p)) for p in itertools.combinations_with_replacement(tipos_forca_bruta(q, M, smin), n)}


def residual(t):
    return math.prod(math.factorial(c) for c in Counter(t).values())


def comparar(caminho, q, n, M, smin):
    esperado = perfis(q, n, M, smin)
    vistos = Counter()
    problemas = []
    for linha in open(caminho):
        r = json.loads(linha)
        assert (r["q"], r["n"], r["M"], r["smin"], r["k"]) == (q, n, M, smin, n), r
        ts = [tuple(int(ch) for ch in t) for t in r["tipos"]]
        chaves = [(residual(t), t) for t in ts]
        if chaves != sorted(chaves) and r.get("ordem", "min") == "min":
            problemas.append(("fora de ordem", r["inst"]))
        if r["resultado"] != "UNSAT" or r.get("lrat_check") != "VERIFIED":
            problemas.append(("não fechado", r["inst"]))
        vistos[tuple(sorted(ts))] += 1
    faltam = esperado - set(vistos)
    sobram = set(vistos) - esperado
    dup = [p for p, c in vistos.items() if c > 1]
    return len(esperado), len(vistos), faltam, sobram, dup, problemas


if __name__ == "__main__":
    caminho, q, n, M, smin = sys.argv[1], *map(int, sys.argv[2:6])
    T = len(tipos_forca_bruta(q, M, smin))
    tot, vis, faltam, sobram, dup, prob = comparar(caminho, q, n, M, smin)
    print(f"tipos={T} perfis_esperados={tot} (C(T+n-1,n)={math.comb(T + n - 1, n)}) no_jsonl={vis} "
          f"faltam={len(faltam)} sobram={len(sobram)} duplicados={len(dup)} problemas={len(prob)}")
    sys.exit(0 if not (faltam or sobram or dup or prob) else 1)
