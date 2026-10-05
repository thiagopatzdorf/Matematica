#!/usr/bin/env python3
"""Red team K_3(6,2), M = 15 e 16: a cadeia (normalização -> instância -> restrições -> LP) nunca recusa
um código que existe.

Para cada código real de K_3(6,2) (17 palavras; nenhum de 16 é conhecido) e várias isometrias
aleatórias de cada um:

  * `canon_fatia.normalizar` (código auditado) leva o código a (s*, K, t);
  * K é forma canônica (`fatia.forma`) e passa no filtro de contagem com o M do código;
  * o código transformado satisfaz TODAS as restrições da instância, avaliadas pelo sistema escrito
    do zero em `farkas_min.Sistema` (não pelo OPB do `fatia_pb`);
  * nenhum multiplicador (y, mu) é aceito por `farkas_min.folga` contra essa instância viável:
    usamos como "certificados candidatos" os 12 054 do PR #57 transplantados (Farkas diz que todos
    têm de falhar; se algum passasse, o verificador seria falso);
  * os lemas citados no PR (#55 soma de |U|, lema da fatia tau* <= M - s, identidade do perfil,
    lema de projeção em duas coordenadas) valem com o M do código.

E, com T = --tamanho palavras (subcódigos de T = |C| - 1 palavras de cada código real, todos;
subconjuntos de códigos reais, conjuntos aleatórios e conjuntos com fibras equilibradas, que não
cobrem): se a instância normalizada passa no filtro de M = T, ela TEM de estar na lista de M = T e
só pode violar linhas de cobertura.
"""
import argparse
import gzip
import itertools
import json
import os
import random
import sys
from math import ceil, comb

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "gaps2"))
sys.path.insert(0, AQUI)
import canon_fatia  # noqa: E402
import farkas_min  # noqa: E402
import fatia  # noqa: E402

Q, N, R = 3, 6, 2
PTS = list(itertools.product(range(Q), repeat=N))


def d(a, b):
    return sum(x != y for x, y in zip(a, b))


def cobre(cod):
    return all(any(d(x, c) <= R for c in cod) for x in PTS)


def isometria_aleatoria(cod, rng):
    perm = list(range(N))
    rng.shuffle(perm)
    sims = []
    for _ in range(N):
        p = list(range(Q))
        rng.shuffle(p)
        sims.append(p)
    return [tuple(sims[i][c[perm[i]]] for i in range(N)) for c in cod]


def distribuicao(cod):
    return tuple(sorted(d(a, b) for a, b in itertools.combinations(cod, 2)))


def ler(arq):
    return [tuple(int(ch) for ch in ln.strip()) for ln in open(arq) if ln.strip()]


def viola(sis, cod):
    """Restrições da instância violadas pelo código (sistema de farkas_min, escrito do zero)."""
    z = {c: 0 for c in sis.pts}
    for c in cod:
        z[c] = 1
    ruins = []
    lo, hi = sis.caixa([])
    ruins += [("caixa", c) for c in sis.pts if not lo[c] <= z[c] <= hi[c]]
    nge = len(sis.pts) + ((N - 1) * Q if sis.s > 0 else 0)
    for k in range(nge):
        coef, b = sis.linha_ge(k)
        if sum(a * z[c] for c, a in coef.items()) < b:
            ruins.append(("ge", k))
    for i in range(Q):
        coef, b = sis.linha_eq(i)
        if sum(a * z[c] for c, a in coef.items()) != b:
            ruins.append(("eq", i))
    return ruins


def tau_estrela(Uset):
    """Número de cobertura fracionário de U por bolas de raio 1 em Z_3^5 (LP, scipy)."""
    import numpy as np
    from scipy.optimize import linprog
    if not Uset:
        return 0.0
    P5 = list(itertools.product(range(Q), repeat=N - 1))
    A = np.array([[1.0 if d(u, c) <= 1 else 0.0 for c in P5] for u in Uset])
    r = linprog(np.ones(len(P5)), A_ub=-A, b_ub=-np.ones(len(Uset)), bounds=(0, None), method="highs")
    return r.fun


def lemas(cod):
    """Confere os lemas auxiliares (versão com o M do código). Devolve lista de falhas."""
    M = len(cod)
    falhas = []
    F = {(j, a): [c for c in cod if c[j] == a] for j in range(N) for a in range(Q)}
    # identidade do perfil: sum_c (n - d(x,c)) = sum_j |F(j, x_j)|
    for x in PTS:
        if sum(N - d(x, c) for c in cod) != sum(len(F[j, x[j]]) for j in range(N)):
            falhas.append(("perfil", x))
            break
    # lema da soma (#55): sum |U(j,a)| <= sum_x d(x,C) <= R (q^n - M)
    U = {k: [x for x in PTS if x[k[0]] == k[1] and all(d(x, c) > R for c in F[k])] for k in F}
    sU = sum(len(u) for u in U.values())
    sd = sum(min(d(x, c) for c in cod) for x in PTS)
    if not sU <= sd <= R * (Q ** N - M):
        falhas.append(("soma", sU, sd))
    if min(len(u) for u in U.values()) > R * (Q ** N - M) // (Q * N):
        falhas.append(("min_U", min(len(u) for u in U.values())))
    # lema da fatia: tau*_1(U(j,a)) <= M - |F(j,a)| em toda fibra
    for (j, a), u in U.items():
        proj = [x[:j] + x[j + 1:] for x in u]
        if tau_estrela(proj) > M - len(F[j, a]) + 1e-7:
            falhas.append(("fatia", j, a))
    # projeção em duas coordenadas: r_a + c_b + 2 n_ab >= ceil((81 - M)/8)
    lim = ceil((Q ** (N - 2) - M) / 8)
    for j, k in itertools.combinations(range(N), 2):
        for a in range(Q):
            for b in range(Q):
                ra = len(F[j, a])
                cb = len(F[k, b])
                nab = sum(1 for c in cod if c[j] == a and c[k] == b)
                if ra + cb + 2 * nab < lim:
                    falhas.append(("proj2", j, k, a, b))
    return falhas


def cap(M, s):
    return (M - s) * sum(comb(N - 1, i) * (Q - 1) ** i for i in range(R))


def canonica(K):
    return [tuple(p) for p in fatia.de_colunas(fatia.forma(list(K)))] == [tuple(p) for p in K]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("codigos", nargs="+")
    ap.add_argument("--isometrias", type=int, default=10)
    ap.add_argument("--instancias", required=True, help="lista de M = --tamanho")
    ap.add_argument("--certificados", required=True, help="certificados de M = --tamanho (PR #57 ou #60)")
    ap.add_argument("--transplantes", type=int, default=300, help="certificados testados por código")
    ap.add_argument("--aleatorios", type=int, default=2000)
    ap.add_argument("--semente", type=int, default=1)
    ap.add_argument("--tamanho", type=int, default=15, help="M da lista (15 ou 16)")
    ap.add_argument("--certificar-lp", help="certificar_lp.py do PR #57: roda o gerador na instância do código")
    a = ap.parse_args()
    rng = random.Random(a.semente)
    lista = json.load(open(a.instancias))
    certs = [json.loads(ln) for ln in gzip.open(a.certificados, "rt")]
    cods = [ler(f) for f in a.codigos]
    falhas = []
    classes = {}
    for f, cod in zip(a.codigos, cods):
        assert len(set(cod)) == len(cod) and cobre(cod), f
        classes.setdefault(distribuicao(cod), []).append(os.path.basename(f))
    print(f"{len(cods)} códigos de {len(cods[0])} palavras, {len(classes)} distribuições de distância distintas")
    cert_lp = None
    if a.certificar_lp:
        import importlib.util
        spec = importlib.util.spec_from_file_location("certificar_lp", a.certificar_lp)
        cert_lp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cert_lp)
    inst_lp = {}
    n_iso = n_trans = 0
    for f, cod in zip(a.codigos, cods):
        M = len(cod)
        lf = lemas(cod)
        if lf:
            falhas.append((f, "lemas", lf[:3]))
        for _ in range(a.isometrias):
            iso = isometria_aleatoria(cod, rng)
            (s, K, t), norm = canon_fatia.normalizar(iso, Q, N)
            n_iso += 1
            if distribuicao(norm) != distribuicao(cod) or not cobre(norm):
                falhas.append((f, "normalização não é isometria"))
            if s and not canonica(K):
                falhas.append((f, "K não canônica"))
            if len(fatia.descobertos(Q, N - 1, R, K)) > cap(M, s):
                falhas.append((f, "filtro recusaria código real"))
            sis = farkas_min.Sistema(Q, N, R, M, s, K, t)
            chave = (M, s, tuple(map(tuple, K)), tuple(t))
            if cert_lp is not None and chave not in inst_lp:
                # o gerador do PR não pode achar certificado numa instância que tem solução
                inst_lp[chave] = cert_lp.certificar(cert_lp.sistema(Q, N, R, M, s, K, t))
                if inst_lp[chave] is not None:
                    falhas.append((f, "gerador certificou instância viável", chave))
            v = viola(sis, norm)
            if v:
                falhas.append((f, "restrições violadas", v[:3]))
            for reg in rng.sample(certs, a.transplantes):
                for fo in reg["folhas"]:
                    # transplantado: as fixações do ramo podem contradizer a fatia (folha vazia)
                    try:
                        g = farkas_min.folga(sis, fo)
                    except ValueError:
                        continue
                    n_trans += 1
                    if g is not None and g > 0:
                        falhas.append((f, "certificado aceito numa instância viável", reg["inst"]))
    print(f"{n_iso} isometrias normalizadas, {n_trans} certificados transplantados recusados, "
          f"{len(inst_lp)} instâncias distintas passadas ao gerador LP (nenhuma deve ser certificada)")
    # T palavras (T = --tamanho): subcódigos exaustivos (se T = |C| - 1), subconjuntos de códigos
    # reais, conjuntos aleatórios e conjuntos com fibras tão equilibradas quanto T permite
    T = a.tamanho
    lista_set = {json.dumps([s, [list(p) for p in K], list(t)]) for s, K, t in lista}
    testados = dentro = 0
    por_s = {}
    sub = {"total": 0, "na_lista": 0, "fora_do_filtro": 0}
    fibras = [T // Q + (1 if i < T % Q else 0) for i in range(Q)]
    amostras = []
    for cod in cods:
        if len(cod) == T + 1:
            for i in range(len(cod)):
                amostras.append(("sub", cod[:i] + cod[i + 1:]))
    for k in range(a.aleatorios):
        if k % 3 == 0:
            amostras.append(("real", rng.sample(rng.choice(cods), T)))
        elif k % 3 == 1:
            amostras.append(("aleatorio", rng.sample(PTS, T)))
        else:
            simb = [v for v in range(Q) for _ in range(fibras[v])]
            cols = [rng.sample(simb, T) for _ in range(N)]
            pal = list({tuple(c[i] for c in cols) for i in range(T)})
            if len(pal) == T:
                amostras.append(("equilibrado", pal))
    for tipo, pal in amostras:
        pal = isometria_aleatoria(pal, rng)
        (s, K, t), norm = canon_fatia.normalizar(pal, Q, N)
        if tipo == "sub":
            sub["total"] += 1
        if s == 0 or len(fatia.descobertos(Q, N - 1, R, K)) > cap(T, s):
            if tipo == "sub":
                sub["fora_do_filtro"] += 1
            continue
        testados += 1
        por_s[s] = por_s.get(s, 0) + 1
        if json.dumps([s, [list(p) for p in K], list(t)]) in lista_set:
            dentro += 1
            sub["na_lista"] += tipo == "sub"
            sis = farkas_min.Sistema(Q, N, R, T, s, K, t)
            v = [x for x in viola(sis, norm) if x[0] != "ge" or x[1] >= len(PTS)]
            if v:
                falhas.append((f"{T} palavras", tipo, "restrição não-cobertura violada", v[:3]))
        else:
            falhas.append((f"{T} palavras", tipo, "instância fora da lista", s, K, t))
    print(f"{T} palavras: {testados} passaram no filtro, {dentro} achadas na lista; por s*: {sorted(por_s.items())}")
    print(f"subcódigos de {T} palavras: {sub}")
    print("falhas:", falhas[:10])
    print("RESULTADO:", "OK" if not falhas else "FALHOU")
    sys.exit(0 if not falhas else 1)


if __name__ == "__main__":
    main()
