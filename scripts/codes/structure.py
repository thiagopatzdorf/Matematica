#!/usr/bin/env python3
"""Lista de palavras -> JSON covering-code/v1, detectando cosets completos de subcódigos lineares.

Uso:
    structure.py data/codes/q7_n9_R4_M1351.txt [--provenance prov.json] [-o saida.json]

Algoritmo (guloso, determinístico, só biblioteca padrão), repetido sobre o que sobra:
  1. f(d) = #{(x, y) em X^2 : y - x = d} para d != 0. Se X contém c cosets completos de um
     subcódigo S, então f(d) >= c*|S| para todo d em S \\ {0}; uma diferença ao acaso tem f ~ 0.
  2. Percorre os d em ordem decrescente de f e estende uma base de S enquanto a massa
     (|S| x número de cosets de S inteiramente contidos em X) não cair abaixo da metade.
     Da cadeia S_1 < S_2 < ... assim obtida fica a de maior dimensão, ou a que --dims pedir.
  3. Aceita o nível se ele tem >= 2 cosets completos (ou 1, com dimensão >= 2); tira esses
     cosets de X e volta ao passo 1. O que sobra no fim vira patch_words.
O primeiro nível vira `linear_base` (q primo: gerador sistemático, matriz de checagem e
síndromes); os seguintes viram `subcode_cosets`. No fim o JSON é expandido de novo e tem de
reproduzir exatamente o conjunto de entrada (senão o script falha).
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import codefmt as cf  # noqa: E402


class Encoder:
    """Palavras como inteiros com subtração dígito a dígito por tabela (pedaços de c dígitos)."""

    def __init__(self, q: int, n: int, group: str = "Zq"):
        self.q, self.n = q, n
        op = (lambda a, b: a ^ b) if group == "xor" else (lambda a, b: (a - b) % q)
        c = 1
        while q ** (c + 1) <= 400:
            c += 1
        self.c = c
        self.B = q**c
        self.nch = -(-n // c)
        B = self.B
        digs = [[(v // q**i) % q for i in range(c)] for v in range(B)]
        self.tab = [
            [sum(op(da, db) * q**i for i, (da, db) in enumerate(zip(digs[a], digs[b]))) for b in range(B)]
            for a in range(B)
        ]

    def enc(self, v) -> tuple[int, ...]:
        q, c = self.q, self.c
        v = list(v) + [0] * (self.nch * self.c - self.n)
        return tuple(sum(v[j * c + i] * q**i for i in range(c)) for j in range(self.nch))

    def dec(self, e) -> tuple[int, ...]:
        q, c = self.q, self.c
        out = []
        for x in e:
            out += [(x // q**i) % q for i in range(c)]
        return tuple(out[: self.n])


def diff_counts(words, encd: Encoder) -> Counter:
    E = [encd.enc(w) for w in words]
    tab = encd.tab
    cnt: Counter = Counter()
    for y in E:
        rows = [tab[a] for a in y]
        for x in E:
            if x is y:
                continue
            cnt[tuple(r[b] for r, b in zip(rows, x))] += 1
    return cnt


def full_cosets(S, R: set, q: int, group: str = "Zq"):
    """Representantes (mínimo lexicográfico) dos cosets x+S inteiramente contidos em R."""
    seen = set()
    reps = []
    for x in sorted(R):
        if x in seen:
            continue
        cos = [cf.add(x, s, q, group) for s in S]
        seen.update(c for c in cos if c in R)
        if all(c in R for c in cos):
            reps.append(min(cos))
    return reps


def find_level(R: set, q: int, n: int, encd: Encoder, want: int | None = None, max_cand: int = 300, group="Zq"):
    if len(R) < 2:
        return None
    cnt = diff_counts(list(R), encd)
    if not cnt:
        return None
    fmax = max(cnt.values())
    floor = max(2, fmax // 8)
    cand = sorted((d for d, v in cnt.items() if v >= floor), key=lambda d: (-cnt[d], d))[:max_cand]
    basis: list = []
    S = [(0,) * n]
    mass = len(R)
    chain = []  # (dim, base, S, reps, massa) ao longo da extensão gulosa
    for de in cand:
        d = encd.dec(de)
        if d in set(S):
            continue
        S2 = cf.span(basis + [d], q, n, group)
        r2 = full_cosets(S2, R, q, group)
        m2 = len(S2) * len(r2)
        if 2 * m2 >= mass and len(r2) >= 1:
            basis.append(d)
            S, mass = S2, m2
            chain.append((list(basis), S2, r2, m2))
    if not chain:
        return None
    # Escolha da dimensão: por padrão a maior da cadeia (o subcódigo maior primeiro). `want`
    # força uma dimensão (--dims): o 1285 tem tanto "36 retas" (como o gerador o montou) quanto
    # "3 planos + 15 retas" no remendo, e só a origem decide qual descrição registrar.
    pick = len(chain) - 1
    if want is not None:
        ks = [i for i, c in enumerate(chain) if len(c[0]) == want]
        if not ks:
            raise cf.FormatError(f"nenhum subcódigo de dimensão {want} neste nível")
        pick = ks[0]
    b, S, reps, _ = chain[pick]
    # um coset só vale se o subcódigo tem dimensão >= 2 (código linear puro, como o 625);
    # uma reta isolada é só 7 palavras e não economiza nada
    if len(reps) < 2 and len(b) < 2:
        return None
    return b, S, reps


def find_levels(X: set, q: int, n: int, dims, group: str):
    encd = Encoder(q, n, group)
    levels = []
    rest = set(X)
    while True:
        want = dims[len(levels)] if dims and len(levels) < len(dims) else None
        if dims and len(levels) >= len(dims):
            break
        lv = find_level(rest, q, n, encd, want, group=group)
        if lv is None:
            break
        basis, S, reps = lv
        levels.append((basis, reps))
        for r in reps:
            for s in S:
                rest.discard(cf.add(r, s, q, group))
    return levels, rest


def structure(words: list[str], q: int, n: int, R_: int, M: int, provenance: dict | None = None, dims=None) -> dict:
    X = {cf.parse_word(w, q, n) for w in words}
    if len(X) != len(words):
        raise cf.FormatError("lista com duplicatas")
    group = "Zq"
    levels, rest = find_levels(X, q, n, dims, group)
    # q = 2^m composto (o 192 tem q = 4): Z_4 não acha nada, a soma de GF(4) (xor) acha
    if not levels and q > 2 and not q & (q - 1):
        lx, rx = find_levels(X, q, n, dims, "xor")
        if lx:
            group, levels, rest = "xor", lx, rx

    doc: dict = {
        "format": cf.FORMAT,
        "q": q,
        "n": n,
        "R": R_,
        "M": M,
        "digit_convention": "word text s[0]..s[n-1]; integer w = sum_k s[k]*q^k; digit k = (w // q^k) % q",
    }
    if group != "Zq":
        doc["group"] = group
    subs = levels
    if levels and cf.is_prime(q) and group == "Zq":
        basis, reps = levels[0]
        G, P = cf.rref_right(basis, q, n)
        H, N = cf.parity_from_generator(G, P, q, n)
        syn = sorted(cf.word_str(cf.syndrome(H, r, q)) for r in reps)
        doc["linear_base"] = {
            "k": len(G),
            "generator": [cf.word_str(g) for g in G],
            "info_columns": P,
            "parity_check": [cf.word_str(h) for h in H],
            "check_columns": N,
            "coset_syndromes": syn,
        }
        subs = levels[1:]
    blocks = []
    for basis, reps in subs:
        gens = cf.rref_right(basis, q, n)[0] if cf.is_prime(q) and group == "Zq" else basis
        blocks.append({"generators": [cf.word_str(g) for g in gens], "reps": sorted(cf.word_str(r) for r in reps)})
    doc["subcode_cosets"] = blocks
    doc["patch_words"] = sorted(cf.word_str(w) for w in rest)
    doc["provenance"] = provenance or {}
    doc["canonical_sha256"] = cf.canonical_sha256(words)

    back = cf.check_doc(doc)
    if set(back) != set(words):
        raise AssertionError("expand(structure(X)) != X")
    return doc


def summary(doc: dict) -> str:
    parts = []
    lb = doc.get("linear_base")
    if lb:
        nc = len(lb.get("coset_syndromes", [])) + len(lb.get("coset_reps", []))
        parts.append(f"{nc} cosets de [{doc['n']},{lb['k']}]_{doc['q']}")
    for b in doc.get("subcode_cosets", []):
        if doc.get("group", "Zq") == "xor":
            parts.append(f"{len(b['reps'])} cosets de um subgrupo (xor) de ordem 2^{len(b['generators'])}")
        else:
            parts.append(f"{len(b['reps'])} cosets de [{doc['n']},{len(b['generators'])}]_{doc['q']}")
    parts.append(f"{len(doc['patch_words'])} palavras")
    return " + ".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("txt")
    ap.add_argument("--provenance", help="arquivo JSON com o objeto provenance")
    ap.add_argument("-o", "--out", help="saída (padrão: stdout)")
    ap.add_argument("--dims", help="dimensões por nível, ex. 3,1 (padrão: automático, maior primeiro)")
    a = ap.parse_args(argv)
    q, n, R_, M = cf.parse_cell_name(a.txt)
    words = cf.read_txt(a.txt, q, n)
    prov = cf.load(a.provenance) if a.provenance else {}
    dims = [int(x) for x in a.dims.split(",")] if a.dims else None
    doc = structure(words, q, n, R_, M, prov, dims)
    text = cf.dump(doc)
    if a.out:
        with open(a.out, "w") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    print(f"{os.path.basename(a.txt)}: {summary(doc)}", file=sys.stderr)


if __name__ == "__main__":
    main()
