"""Red team de K_7(5,3) = 17, ataque 1: a lista dos perfis de M = 16 está completa?

Enumeração independente (não importa nada de tools/exatos/fibras): tipos por força bruta sobre
itertools.product, perfis = multiconjuntos de n tipos, comparados conjunto a conjunto com os
registros. Também confere, registro a registro: (q, n, M, k, s_min), UNSAT + lrat_check VERIFIED,
sem controle (`sem`), tipos válidos (partição de M em q partes >= s_min, decrescente), ordem dos
tipos coerente com a `ordem` do registro (min ou max: simetria residual crescente ou decrescente,
depois lexicográfica) e o índice `inst` igual à posição do perfil nessa ordem.

A string do tipo junta as partes sem separador ("10111111" = 10,1,1,1,1,1,1); aqui ela é lida
por todas as decomposições possíveis e só vale se a decomposição for única.

Uso: k753_perfis.py q n M smin INTEIROS.jsonl [CUBOS.jsonl ...]
  INTEIROS: um registro por perfil fechado inteiro (o merge do autor);
  CUBOS: registros com L (perfis fechados só por cubos; a cobertura dos cubos é k753_cubos.py)."""
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


def ler_tipo(s, q, M, smin):
    """Todas as leituras de s como q partes (>= smin, soma M, decrescente); exige uma só."""
    sols = []

    def rec(pos, partes):
        if len(partes) == q:
            if pos == len(s) and sum(partes) == M:
                sols.append(tuple(partes))
            return
        for tam in (1, 2):
            if pos + tam > len(s) or (tam == 2 and s[pos] == "0"):
                continue
            v = int(s[pos:pos + tam])
            if v < smin or (partes and v > partes[-1]):
                continue
            rec(pos + tam, partes + [v])

    rec(0, [])
    if len(sols) != 1:
        raise ValueError(f"tipo {s!r}: {len(sols)} leituras")
    return sols[0]


def residual(t):
    return math.prod(math.factorial(c) for c in Counter(t).values())


def chave(t, ordem):
    return (-residual(t) if ordem == "max" else residual(t), t)


def indices(ts_todos, n, ordem):
    ordenados = sorted(ts_todos, key=lambda t: chave(t, ordem))
    return {p: i for i, p in enumerate(itertools.combinations_with_replacement(ordenados, n))}


def main():
    q, n, M, smin = map(int, sys.argv[1:5])
    inteiros, cubos = sys.argv[5], sys.argv[6:]
    T = tipos_forca_bruta(q, M, smin)
    esperado = {tuple(sorted(p)) for p in itertools.combinations_with_replacement(T, n)}
    idx = {o: indices(T, n, o) for o in ("min", "max")}
    vistos, problemas, ordens = Counter(), Counter(), Counter()
    exemplos = {}

    def conferir(r, via_cubo):
        prob = []
        if (r["q"], r["n"], r["M"], r["k"], r["smin"]) != (q, n, M, n, smin):
            prob.append("parametros")
        if r.get("sem"):
            prob.append("controle sem quebra")
        if r.get("resultado") != "UNSAT" or r.get("lrat_check") != "VERIFIED":
            prob.append("nao fechado")
        ts = tuple(ler_tipo(s, q, M, smin) for s in r["tipos"])
        if any(t not in T for t in ts):
            prob.append("tipo invalido")
        o = r.get("ordem", "min")
        ordens[o] += 1
        if list(ts) != sorted(ts, key=lambda t: chave(t, o)):
            prob.append("fora de ordem")
        elif idx[o].get(ts) != r["inst"]:
            prob.append("inst nao bate")
        for p in prob:
            problemas[p] += 1
            exemplos.setdefault(p, r.get("inst"))
        return tuple(sorted(ts))

    n_int = 0
    for ln in open(inteiros):
        r = json.loads(ln)
        if r.get("L"):
            continue
        vistos[conferir(r, False)] += 1
        n_int += 1
    por_cubo = set()
    for arq in cubos:
        for ln in open(arq, errors="replace"):
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if not r.get("L") or (r["q"], r["n"], r["M"]) != (q, n, M):
                continue
            por_cubo.add(conferir(r, True))
    so_cubo = por_cubo - set(vistos)
    todos = set(vistos) | so_cubo
    dup = sum(1 for c in vistos.values() if c > 1)
    out = {"tipos": len(T), "perfis_esperados": len(esperado), "comb": math.comb(len(T) + n - 1, n),
           "registros_inteiros": n_int, "perfis_inteiros": len(vistos), "duplicados": dup,
           "perfis_so_em_cubos": len(so_cubo), "so_cubo": [" | ".join("".join(map(str, t)) for t in p) for p in sorted(so_cubo)],
           "faltam": len(esperado - todos), "sobram": len(todos - esperado),
           "falta_lista": [" | ".join("".join(map(str, t)) for t in p) for p in sorted(esperado - todos)][:20],
           "problemas": dict(problemas), "exemplos": exemplos, "ordens": dict(ordens)}
    print(json.dumps(out, ensure_ascii=False))
    sys.exit(0 if not (out["faltam"] or out["sobram"] or problemas) else 1)


if __name__ == "__main__":
    main()
