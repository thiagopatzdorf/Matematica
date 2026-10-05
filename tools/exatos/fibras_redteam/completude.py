"""Completude da quebra de simetria (a)-(h) em códigos reais e aleatórios.

Para cada código C (re-rotulado por um elemento aleatório de S_q wr S_n e com as palavras
embaralhadas) mede três coisas contra a CNF do perfil de C gerada pelo codificador AUDITADO:
  repo   : a forma normal de fib_canon.canonizar (o guloso do Lema 4 como escrito) satisfaz?
  corr   : a forma normal de canon_corrigido.canonizar satisfaz?
  orbita : algum elemento da órbita de C satisfaz? (SAT, sem canonizador nenhum)
Só `orbita` decide se a CNF perde códigos; `repo` e `corr` testam as provas construtivas.

Uso: completude.py DIR_FIBRAS q n M smin N semente [--cobre ARQ] [--orbita K] [--sem-repo]
  sem --cobre: N códigos aleatórios com fibras >= smin (as cláusulas de cobertura saem);
  com --cobre: o código do arquivo (uma palavra por linha), re-rotulado N vezes (cobertura ligada).
"""
import argparse
import json
import os
import random
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import canon_corrigido  # noqa: E402
import orbita_fibras  # noqa: E402
from checar_cnf import Checador  # noqa: E402


def codigo_aleatorio(q, n, M, smin, rng):
    """Colunas com tipo uniforme entre as partições de M em q partes >= smin."""
    tipos = canon_tipos(q, M, smin)
    cols = []
    for _ in range(n):
        t = list(rng.choice(tipos))
        rng.shuffle(t)
        col = [a for a in range(q) for _ in range(t[a])]
        rng.shuffle(col)
        cols.append(col)
    return [tuple(cols[i][w] for i in range(n)) for w in range(M)]


_TIPOS = {}


def canon_tipos(q, M, smin):
    if (q, M, smin) not in _TIPOS:
        out = []

        def rec(resto, partes, maximo, pref):
            if partes == 0:
                if resto == 0:
                    out.append(tuple(pref))
                return
            for v in range(min(maximo, resto - smin * (partes - 1)), smin - 1, -1):
                rec(resto - v, partes - 1, v, pref + [v])
        rec(M, q, M, [])
        _TIPOS[q, M, smin] = out
    return _TIPOS[q, M, smin]


def embaralhar(C, q, n, rng):
    perm = list(range(n))
    rng.shuffle(perm)
    sims = [rng.sample(range(q), q) for _ in range(n)]
    out = [tuple(sims[i][c[perm[i]]] for i in range(n)) for c in C]
    rng.shuffle(out)
    return out


def ler_codigos(caminho):
    """Um ou mais códigos (uma palavra por linha, códigos separados por linha em branco)."""
    blocos = open(caminho).read().strip().split("\n\n")
    return [[tuple(int(ch) for ch in l.strip()) for l in b.splitlines() if l.strip() and not l.startswith("#")]
            for b in blocos if b.strip()]


def ler_codigo(caminho):
    return ler_codigos(caminho)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("q", type=int)
    ap.add_argument("n", type=int)
    ap.add_argument("M", type=int)
    ap.add_argument("smin", type=int)
    ap.add_argument("N", type=int)
    ap.add_argument("semente", type=int)
    ap.add_argument("--cobre")
    ap.add_argument("--orbita", type=int, default=0, help="roda a órbita por SAT nos K primeiros")
    ap.add_argument("--sem-repo", action="store_true")
    ap.add_argument("--ordem", default="min")
    a = ap.parse_args()
    sys.path.insert(0, a.dir)
    import fib_canon
    import fib_encode as enc
    rng = random.Random(a.semente)
    chk = Checador(enc, a.q, a.n, a.M, a.smin)
    bases = ler_codigos(a.cobre) if a.cobre else None
    cont = {"repo_falha": 0, "corr_falha": 0, "orbita_unsat": 0, "orbita_testadas": 0, "codigos": 0}
    exemplos = []
    t0 = time.time()
    for it in range(a.N):
        C = embaralhar(bases[it % len(bases)], a.q, a.n, rng) if bases else codigo_aleatorio(a.q, a.n, a.M, a.smin, rng)
        assert len(C) == a.M
        if min(min(canon_corrigido.tipo(C, i, a.q)) for i in range(a.n)) < a.smin:
            continue
        cob = bases is not None
        cont["codigos"] += 1
        pref, norm = canon_corrigido.canonizar(C, a.q, a.n, a.ordem)
        pref_k = tuple(sorted(pref, key=lambda t: enc.chave_tipo(t, a.ordem)))
        assert pref_k == pref
        if not chk.satisfaz(pref, norm, cob):
            cont["corr_falha"] += 1
            exemplos.append({"tipo": "corr", "C": C})
        if not a.sem_repo:
            idx, normr = fib_canon.canonizar(C, a.q, a.n, a.n, a.smin, ordem=a.ordem)
            _, ins = enc.instancias(a.q, a.n, a.M, a.n, a.smin, ordem=a.ordem)
            if ins[idx] != pref or not chk.satisfaz(pref, normr, cob):
                cont["repo_falha"] += 1
                if len(exemplos) < 5:
                    exemplos.append({"tipo": "repo", "C": C})
        if it < a.orbita:
            cont["orbita_testadas"] += 1
            # sem as cláusulas de cobertura: para um código que cobre, toda imagem dele cobre e as P
            # são definidas por equivalência, então elas valem em qualquer elemento da órbita; com
            # elas o solver só fica mais lento (medido: > 50 min para 60 códigos de K_7(6,4), M = 14).
            # A cobertura é conferida, com as cláusulas, nas formas normais (Checador) acima.
            if not orbita_fibras.orbita_sat(enc, C, a.q, a.n, cobertura=False, ordem=a.ordem, smin=a.smin):
                cont["orbita_unsat"] += 1
                exemplos.append({"tipo": "orbita", "C": C})
    cont["segundos"] = round(time.time() - t0, 1)
    print(json.dumps({"q": a.q, "n": a.n, "M": a.M, "smin": a.smin, "semente": a.semente,
                      "cobre": os.path.basename(a.cobre) if a.cobre else None, "ordem": a.ordem, **cont,
                      "exemplos": exemplos[:5]}))


if __name__ == "__main__":
    main()
