"""Interface com o canonizador em C (canon.c, libnauty) e classificação de códigos de cobertura."""
import itertools
import os
import subprocess
import tempfile

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))


def binario(destino=None):
    """Compila canon.c (precisa de libnauty-dev) e devolve o caminho do executável."""
    destino = destino or os.path.join(tempfile.gettempdir(), "k362_repro_canon")
    fonte = os.path.join(AQUI, "canon.c")
    if not os.path.exists(destino) or os.path.getmtime(destino) < os.path.getmtime(fonte):
        subprocess.run(["gcc", "-O2", "-DWORDSIZE=64", "-DMAXN=WORDSIZE", "-o", destino, fonte,
                        "-lnautyL1", "-lm"], check=True)
    return destino


def formas(conjuntos, q, m, exe=None):
    """[(certificado, |Stab|)] para cada conjunto (lista de inteiros em base q)."""
    if not conjuntos:
        return []
    entrada = "".join("%d %d %d %s\n" % (q, m, len(c), " ".join(map(str, c))) for c in conjuntos)
    r = subprocess.run([exe or binario()], input=entrada, capture_output=True, text=True, check=True)
    return [(ln.split()[0], int(ln.split()[1])) for ln in r.stdout.splitlines()]


def classificar(q, n, R, M, exe=None):
    """Classes de códigos de M palavras e raio R em Z_q^n (inclui os que cobrem com menos).

    Nível a nível: cada representante S que não cobre ramifica nas palavras que cobrem o menor ponto
    descoberto, descartando o que nem por contagem fecharia com M palavras. Completo: se S está contido em g(C), alguma palavra de g(C) fora de S cobre esse
    ponto, e o representante de S + {w} está contido em h(g(C))."""
    P = np.array(list(itertools.product(range(q), repeat=n)))
    viz = [np.nonzero((P != P[x]).sum(axis=1) <= R)[0].tolist() for x in range(len(P))]
    V = len(viz[0])
    nivel, prontos = {(0,): None}, {}
    for _ in range(M - 1):
        cand = []
        for S in nivel:
            cob = set().union(*(viz[c] for c in S))
            if len(cob) == len(P):
                prontos[S] = None
                continue
            x = min(set(range(len(P))) - cob)
            for w in viz[x]:
                T = tuple(sorted(S + (w,)))
                # poda por contagem: as M - |T| palavras restantes cobrem no máximo V pontos cada
                if w not in S and len(P) - len(cob.union(viz[w])) <= (M - len(T)) * V:
                    cand.append(T)
        novo = {}
        for S, (cert, _) in zip(cand, formas(cand, q, n, exe)):
            novo.setdefault(cert, S)
        nivel = {S: None for S in novo.values()}
    finais = [S for S in list(nivel) + list(prontos) if len(set().union(*(viz[c] for c in S))) == len(P)]
    return {cert: S for S, (cert, _) in zip(finais, formas(finais, q, n, exe))}


def classificar_por_reducao(q, n, R, M, exe=None):
    """Classes de códigos de <= M palavras pela própria redução: para cada instância (s, K), todos os
    modelos da formulação completa (CaDiCaL do python-sat, com cláusulas de bloqueio) viram códigos,
    deduplicados pela forma do nauty. Todo código é isométrico a um normalizado cujo K é o
    representante listado, então aparece como modelo de alguma instância."""
    from pysat.solvers import Solver
    import repro_rodar as rodar
    import repro_sat as sat
    codigos = []
    for s, K in rodar.instancias(q, n, R, M):
        cob, nv, teto, fib = sat.restricoes(q, n, R, M, K, completa=True)
        cls = sat.cnf(cob, nv, teto, fib).splitlines()[1:]
        with Solver(name="cadical153", bootstrap_with=[[int(x) for x in c.split()[:-1]] for c in cls]) as sv:
            while sv.solve():
                mod = [v for v in sv.get_model() if 0 < v <= nv]
                codigos.append(sat.codigo_do_modelo(q, n, K, mod))
                sv.add_clause([-v for v in mod] + [v for v in range(1, nv + 1) if v not in set(mod)])
    num = [[sum(v * q ** (n - 1 - i) for i, v in enumerate(c)) for c in C] for C in codigos]
    return {cert: C for C, (cert, _) in zip(codigos, formas(num, q, n, exe))}
