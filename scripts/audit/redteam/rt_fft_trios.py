#!/usr/bin/env python3
"""rt_fft_trios.py -- red team: contagem EXATA de órfãs de todos os trios {0,s1,s2}, sem poda.

Algoritmo diferente do exactT/exactT2/verify_trios (não há amostra Y, blocos, simetria nem
saída antecipada): para cada s1 (um por classe escalar), X = Bc ∩ (Bc+s1) e
cnt[s2] = |X ∩ (Bc+s2)| para TODO s2 de uma vez, por correlação cíclica em Z_7^6 via FFT
6-dimensional (numpy). Os valores são inteiros <= 117649, arredondados de float64 (o erro
de arredondamento medido é impresso: tem de ficar << 0.5).

B = {He : wt(e) <= R} é montada enumerando todos os e de peso <= R (sem DFS do kit).

Uso: rt_fft_trios.py T "A" [saida.txt]
Saída: "TRIO o a b c" em forma canônica (menor tripla ordenada {λ(p-b)} sobre 3 bases e 6
escalares -- a mesma convenção de verify_trios.c, para comparar com diff), "MIN o", e
"MIN_GLOBAL o" = mínimo verdadeiro sobre todos os trios (mesmo acima de T).
"""
import itertools, sys, time
import numpy as np

q, n, R, r = 7, 9, 4, 6
N = q ** r
T = int(sys.argv[1]); Astr = sys.argv[2]
rows = Astr.split()
assert len(rows) == r and all(len(x) == n - r for x in rows)
H = np.zeros((r, n), dtype=np.int64)
H[:, :r] = np.eye(r, dtype=np.int64)
for i, row in enumerate(rows):
    for j, ch in enumerate(row):
        H[i, r + j] = int(ch)
pw = q ** np.arange(r, dtype=np.int64)          # dígito i vale 7^i (mesma codificação do kit)

def to_int(vecs):
    return (vecs % q) @ pw

inB = np.zeros(N, dtype=bool)
for w in range(R + 1):
    for supp in itertools.combinations(range(n), w):
        if w == 0:
            inB[0] = True; continue
        coef = np.array(list(itertools.product(range(1, q), repeat=w)), dtype=np.int64)
        syn = coef @ H[:, list(supp)].T
        inB[to_int(syn)] = True
Bc = (~inB).astype(np.float64)
nBc = int(Bc.sum())

shape = (q,) * r
def digits_axes(s):
    # índice achatado em C-order de shape (7,)*6 == inteiro s (eixo a <-> dígito 5-a)
    return np.unravel_index(s, shape)
Bc6 = Bc.reshape(shape)
FBc_conj = np.conj(np.fft.fftn(Bc6))

def scal(s, lam):
    d = [(s // q ** i) % q for i in range(r)]
    return sum(((x * lam) % q) * q ** i for i, x in enumerate(d))
def sub(a, b):
    return sum((((a // q ** i) % q - (b // q ** i) % q) % q) * q ** i for i in range(r))
def canon(s1, s2):
    P = (0, s1, s2); best = None
    for b in P:
        for lam in range(1, q):
            v = tuple(sorted(scal(sub(p, b), lam) for p in P))
            if best is None or v < best: best = v
    return best

def is_scal_canon(s):
    if s == 0: return False
    while s % q == 0: s //= q
    return s % q == 1

t0 = time.time(); maxerr = 0.0; gmin = 10 ** 9; trios = {}
ar = np.arange(N)
for s1 in range(1, N):
    if not is_scal_canon(s1): continue
    X = Bc6 * np.roll(Bc6, shift=digits_axes(s1), axis=tuple(range(r)))   # X(x) = Bc(x) Bc(x-s1)
    c = np.fft.ifftn(np.fft.fftn(X) * FBc_conj).real.ravel()               # c[s2] = sum_x X(x) Bc(x-s2)
    ci = np.rint(c); err = float(np.abs(c - ci).max()); maxerr = max(maxerr, err)
    ci = ci.astype(np.int64)
    ci[0] = 1 << 40; ci[s1] = 1 << 40
    m = int(ci.min()); gmin = min(gmin, m)
    for s2 in np.nonzero(ci <= T)[0]:
        key = canon(s1, int(s2)); o = int(ci[s2])
        if key in trios and trios[key] != o:
            print("INCONSISTENTE", key, trios[key], o); sys.exit(3)
        trios[key] = o
out = [f"TRIO {o} {a} {b} {c}" for (a, b, c), o in sorted(trios.items(), key=lambda kv: (kv[0][1], kv[0][2]))]
mn = min(trios.values()) if trios else None
out.append(f"MIN {mn}" if mn is not None else "MIN none")
txt = "\n".join(out) + "\n"
if len(sys.argv) > 3:
    open(sys.argv[3], "w").write(txt)
print(txt, end="")
print(f"MIN_GLOBAL {gmin}")
print(f"# A={Astr} nBc={nBc} T={T} orbitas<=T={len(trios)} erro_arred_max={maxerr:.2e} secs={time.time()-t0:.0f}", file=sys.stderr)
