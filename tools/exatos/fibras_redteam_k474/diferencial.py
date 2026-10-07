#!/usr/bin/env python3
"""Codificação da cobertura por t-uplas (Lema 2') contra a codificação independente (`cobertura_indep`).

Para uma instância (perfil de tipos por coordenada, k = n), os dois codificadores recebem as MESMAS
células fixadas e têm de dar o mesmo veredito SAT/UNSAT:
  A = fib_encode.codificar(..., quebra=False)  (projeção por t-uplas, variáveis P[T,v])
  B = cobertura_indep (uma variável m[x][u] por ponto e palavra, contador próprio) + a mesma estrutura
      de perfil escrita aqui: coordenada 0 em blocos, fibras exatas por coluna.
Também confere, quando SAT, que o código decodificado pelos DOIS cobre (predicado por força bruta).
Uso: python3 diferencial.py q n R M N_casos SEMENTE
"""
import os
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "fibras"))
sys.path.insert(0, AQUI)
import cobertura_indep as ci  # noqa: E402
import fib_encode as enc  # noqa: E402
from pysat.solvers import Solver  # noqa: E402


def forma_perfil(cod, q, n, ordem):
    """Código -> (prefixo de tipos, palavras em blocos pela coordenada 0, símbolos por fibra decrescente).
    Escrito aqui; só usa enc.chave_tipo para escolher a ordem das coordenadas (a convenção do repo)."""
    from collections import Counter
    M = len(cod)
    tipos = [tuple(sorted((Counter(c[i] for c in cod).get(a, 0) for a in range(q)), reverse=True)) for i in range(n)]
    perm = sorted(range(n), key=lambda i: enc.chave_tipo(tipos[i], ordem))
    cod = [tuple(c[i] for i in perm) for c in cod]
    tipos = [tipos[i] for i in perm]
    novo = [list(c) for c in cod]
    for i in range(n):
        cnt = Counter(c[i] for c in cod)
        ordsim = sorted(range(q), key=lambda a: (-cnt.get(a, 0), a))
        ren = {a: r for r, a in enumerate(ordsim)}
        for w in range(M):
            novo[w][i] = ren[novo[w][i]]
    novo.sort(key=lambda c: c[0])           # blocos pelo símbolo da coordenada 0 (estável)
    return tuple(tipos), [tuple(c) for c in novo]


ORCAMENTO = 300000


def resolver_limitado(cl, assum, dec):
    """glucose4 com orçamento de conflitos: devolve (True|False|None, código); None = não decidiu."""
    with Solver(name="glucose4", bootstrap_with=cl) as s:
        s.conf_budget(ORCAMENTO)
        ok = s.solve_limited(assumptions=assum)
        return ok, (dec(s.get_model()) if ok else None)


def veredito_B(q, n, R, M, tipos, fixas):
    f, w = ci.codificar(q, n, R, M, ordem_lex=False)
    bl = []
    for a in range(q):
        bl += [a] * tipos[0][a]
    for u in range(M):
        f.add([w[u][0][bl[u]]])
    for i in range(n):
        for a in range(q):
            ci.exatamente(f, [w[u][i][a] for u in range(M)], tipos[i][a])
    for (u, i, a) in fixas:
        f.add([w[u][i][a]])
    return resolver_limitado(f.cl, [], lambda m: ci.decodificar(m, w, q, n))


def veredito_A(q, n, R, M, tipos, fixas, smin):
    cnf, x, sim0, ts = enc.codificar(q, n, M, tipos, smin, quebra=False, R=R)
    unit = []
    for (u, i, a) in fixas:
        if i == 0:
            if sim0[u] != a:
                return False, None
        else:
            unit.append(x[u][i][a])
    return resolver_limitado(cnf.cl, unit, lambda m: enc.decodificar(m, x, sim0, q, n, M))


def main():
    q, n, R, M, N, sem = map(int, sys.argv[1:7])
    rng = random.Random(sem)
    smin = 0
    desacordos = sat = unsat = indef = 0
    # códigos que cobrem de verdade (por SAT da codificação B, com ordem lex) servem de semente
    f, w = ci.codificar(q, n, R, M)
    with Solver(name="cadical153", bootstrap_with=f.cl) as s:
        reais = []
        for _ in range(4):
            if not s.solve():
                break
            cod = ci.decodificar(s.get_model(), w, q, n)
            reais.append(cod)
            s.add_clause([-w[u][i][cod[u][i]] for u in range(M) for i in range(n)])
    print(f"códigos reais (cobrem) achados para M={M}: {len(reais)}")
    for r in range(N):
        if reais and rng.random() < 0.7:
            cod = list(rng.choice(reais))
            if not ci.cobre(cod, q, n, R):
                raise SystemExit("codificador B devolveu código que não cobre")
            perm = list(range(n)); rng.shuffle(perm)
            sims = [rng.sample(range(q), q) for _ in range(n)]
            cod = [tuple(sims[i][c[perm[i]]] for i in range(n)) for c in cod]
        else:
            cod = [tuple(rng.randrange(q) for _ in range(n)) for _ in range(M)]
        ordem = rng.choice(["min", "max"])
        tipos, forma = forma_perfil(cod, q, n, ordem)
        fixas = [(u, i, forma[u][i]) for u in range(M) for i in range(n) if rng.random() < rng.choice([0.3, 0.6, 0.9, 1.0])]
        if rng.random() < 0.5 and fixas:                           # estraga uma célula: tende a UNSAT
            k = rng.randrange(len(fixas)); u, i, a = fixas[k]; fixas[k] = (u, i, (a + 1) % q)
        okA, codA = veredito_A(q, n, R, M, tipos, fixas, smin)
        okB, codB = veredito_B(q, n, R, M, tipos, fixas)
        for c in (codA, codB):
            if c is not None and not ci.cobre(c, q, n, R):
                print("DESACORDO: modelo que não cobre", tipos, fixas); desacordos += 1
        if okA is None or okB is None:
            indef += 1
            continue
        if okA != okB:
            desacordos += 1
            print("DESACORDO", "A(fib_encode)=", okA, "B(indep)=", okB, tipos, fixas, flush=True)
        sat += okA
        unsat += (not okA)
    print(f"K_{q}({n},{R}) M={M}: {N} casos, SAT={sat} UNSAT={unsat} sem decisão={indef}, desacordos={desacordos}")
    sys.exit(1 if desacordos else 0)


if __name__ == "__main__":
    main()
