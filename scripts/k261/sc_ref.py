#!/usr/bin/env python3
"""Espelho de referência de SearchCore.chkN (4a). Uso:
  sc_ref.py n m [d]      -> conta nós da busca a partir de root n m; com d, imprime a fronteira
Saída: JSON {"ok": bool, "nodes": int, "frontier": [[l,cov,forb],...]}
"""
import json, sys

def bm(n, c):
    r = 1 << c
    for k in range(n):
        r |= 1 << (c ^ (1 << k))
    return r

def nbr(n, u):
    return [u] + [u ^ (1 << k) for k in range(n)]

def run(n, s, d, frontier, stats):
    """devolve True se o nó passa; acrescenta em frontier os estados da profundidade d."""
    l, cov, forb = s
    full = (1 << (1 << n)) - 1
    x = full ^ (cov & full)
    stats[0] += 1
    if x == 0:
        return False
    if l * (n + 1) < bin(x).count("1"):
        return True
    if d == 0:
        frontier.append([l, cov, forb])
        return True
    u = (x & -x).bit_length() - 1
    F = forb
    for c in nbr(n, u):
        if (F >> c) & 1:
            continue
        if not run(n, (l - 1, cov | bm(n, c), F | (1 << c)), d - 1, frontier, stats):
            return False
        F |= 1 << c
    return True

def root(n, m):
    top = (1 << n) - 1
    return (m, bm(n, top), 1 << top)

if __name__ == "__main__":
    n, m = int(sys.argv[1]), int(sys.argv[2])
    d = int(sys.argv[3]) if len(sys.argv) > 3 else m + 1
    fr, st = [], [0]
    ok = run(n, root(n, m), d, fr, st)
    print(json.dumps({"ok": ok, "nodes": st[0], "frontier_len": len(fr), "frontier": fr if len(sys.argv) > 3 else []}))
