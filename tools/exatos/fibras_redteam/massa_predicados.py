"""Teste em massa barato (sem CNF): códigos aleatórios com fibras >= smin, re-rotulados; conta
quantas formas normais violam algum predicado (a)-(h) de `predicados.py`:
  corr: guloso corrigido (canon_corrigido) -- tem de ser 0;
  repo: fib_canon.canonizar do commit auditado (opcional, com --repo DIR) -- mede o defeito.

Uso: massa_predicados.py q n M smin N semente [--repo DIR] [--ordem min|max] [--cobre ARQ]"""
import argparse
import json
import os
import random
import sys
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import canon_corrigido  # noqa: E402
import predicados  # noqa: E402
from completude import codigo_aleatorio, embaralhar  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    for nome in ("q", "n", "M", "smin", "N", "semente"):
        ap.add_argument(nome, type=int)
    ap.add_argument("--repo")
    ap.add_argument("--ordem", default="min")
    ap.add_argument("--cobre")
    ap.add_argument("--dump", help="grava (JSONL) cada código cuja forma do repo viola")
    a = ap.parse_args()
    fc = None
    if a.repo:
        sys.path.insert(0, a.repo)
        import fib_canon as fc
    rng = random.Random(a.semente)
    bases = []
    if a.cobre:
        txt = open(a.cobre).read().strip().split("\n\n")
        bases = [[tuple(int(ch) for ch in l) for l in b.split()] for b in txt if b.strip()]
    corr = repo = cods = 0
    quais = Counter()
    ex = None
    for it in range(a.N):
        C = embaralhar(bases[it % len(bases)], a.q, a.n, rng) if bases else codigo_aleatorio(a.q, a.n, a.M, a.smin, rng)
        smin = min(min(predicados.tipo(C, i, a.q)) for i in range(a.n))
        if smin < a.smin:
            continue
        cods += 1
        _, norm = canon_corrigido.canonizar(C, a.q, a.n, a.ordem)
        assert sorted(map(tuple, norm)) != [] and len(norm) == len(C)
        if predicados.viola(norm, a.q, a.ordem):
            corr += 1
        if fc:
            _, nr = fc.canonizar(C, a.q, a.n, a.n, a.smin, ordem=a.ordem)
            v = predicados.viola(nr, a.q, a.ordem)
            if v:
                repo += 1
                quais.update(x[0] for x in v)
                ex = ex or C
                if a.dump:
                    with open(a.dump, "a") as fh:
                        fh.write(json.dumps({"q": a.q, "n": a.n, "M": a.M, "smin": a.smin, "ordem": a.ordem, "C": C, "viola": v}) + "\n")
    print(json.dumps({"q": a.q, "n": a.n, "M": a.M, "smin": a.smin, "ordem": a.ordem, "semente": a.semente,
                      "cobre": os.path.basename(a.cobre) if a.cobre else None, "codigos": cods,
                      "corr_viola": corr, "repo_viola": repo if fc else None, "repo_quais": dict(quais),
                      "exemplo_repo": ex}))


if __name__ == "__main__":
    main()
