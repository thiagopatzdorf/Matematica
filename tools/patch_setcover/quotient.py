#!/usr/bin/env python3
"""quotient.py -- instância PSC1 do remendo com simetria de translação imposta (quociente).

Uso: quotient.py inst.bin g saida.bin
  g: palavra (n dígitos, convenção do repo) que gera o grupo de translações {0, g, 2g, ...}
     de ordem q; tem de deixar o resíduo invariante (ex.: g no código linear da base).
Elementos = órbitas de pontos do resíduo; conjuntos = órbitas de palavras candidatas (cada
uma custa q palavras de verdade). Uma cobertura de k órbitas = remendo de k*q palavras
invariante por g. É a família do candidates/k7_9_4_1134/ilp_sym.py (reta de C0), agora
resolvida pelo rwls em vez do ILP. Expandir a solução: expand_orbits() abaixo.
"""
import sys

import numpy as np

import psc_io


def digits(x, q, n):
    x = np.asarray(x, dtype=np.int64)
    return np.stack([(x // q**k) % q for k in range(n)], 1)


def undigits(D, q):
    return (D.astype(np.int64) * (q ** np.arange(D.shape[1]))).sum(1)


def translates(x, g, q, n):
    D = digits(x, q, n)
    return np.stack([undigits((D + c * g) % q, q) for c in range(q)], 0)  # (q, len(x))


def build(inst, gword):
    q, n = inst["q"], inst["n"]
    g = np.array([int(c) for c in gword], dtype=np.int64)
    pts = inst["pts"].astype(np.int64)
    tp = translates(pts, g, q, n)
    if not np.isin(tp, pts).all():
        raise ValueError("g não deixa o resíduo invariante")
    porb = tp.min(0)                                   # órbita de cada ponto (rótulo = mínimo)
    po_ids, pinv = np.unique(porb, return_inverse=True)
    sets = inst["sets"].astype(np.int64)
    worb = translates(sets, g, q, n).min(0)
    rep = sets == worb                                 # um representante por órbita de palavra
    members = []
    off, elem = inst["off"], inst["elem"]
    for j in np.flatnonzero(rep):
        members.append(np.unique(pinv[elem[off[j]:off[j + 1]]]))
    return dict(q=q, n=n, R=inst["R"], T=inst["T"], npts=len(po_ids),
                sets=sets[rep], members=members)


def expand_orbits(words, gword, q):
    """Palavras representantes -> todas as palavras das órbitas (lista de strings)."""
    g = np.array([int(c) for c in gword], dtype=np.int64)
    out = set()
    for w in words:
        d = np.array([int(c) for c in w], dtype=np.int64)
        for c in range(q):
            out.add("".join(str(v) for v in (d + c * g) % q))
    return sorted(out)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "expand":
        _, _, gw, q, fin = sys.argv[:5]
        print("\n".join(expand_orbits(open(fin).read().split(), gw, int(q))))
        sys.exit(0)
    inst = psc_io.load(sys.argv[1])
    Q = build(inst, sys.argv[2])
    psc_io.write(sys.argv[3], Q["q"], Q["n"], Q["R"], Q["T"], np.arange(Q["npts"]), Q["sets"], Q["members"])
    print(f"órbitas: {Q['npts']} de pontos, {len(Q['sets'])} de palavras")
