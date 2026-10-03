#!/usr/bin/env python3
"""Teste de viabilidade EXATO (SAT) da soma direta amalgamada (ADS), q=7. Ver LITERATURA_PROFUNDA_C.md sec. 1.3.
C2 = [n2,3]_7 linear de raio <= R2 (colunas em PG(2,7)), coordenada de colagem = coluna j de C2
     (balanceada: 49 palavras por simbolo, logo |ADS| = 49*|C1|);
C1 = (n1, <=M1) arbitrario, procurado por SAT (pysat/glucose4: biblioteca padrao, nao e codigo da literatura de covering codes).
Condicao exata (E): a ADS (n1+n2-1 coords) tem raio <= R sse para todo (x,y,z) existe a com
     D1_a(x) + D2_a(y) + [a != z] <= R.
Uso: ads_exact.py n1 n2 R R2 j idx_ini idx_fim TL M1,M1,...
Resultado SAT = C1 valido (a ADS completa e conferida por ads_verify.py).
UNSAT = so para ESTE C2, ESTE j e ESTE M1.  UNKNOWN (timeout) = nada.  Falha de busca != impossibilidade."""
import sys, itertools, time, json, threading, numpy as np
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType
q = 7
n1, n2, R, R2, j, i0, i1 = map(int, sys.argv[1:8])
TL = float(sys.argv[8]); M1s = [int(x) for x in sys.argv[9].split(',')]
pts = []
for v in itertools.product(range(q), repeat=3):
    if any(v):
        f = next(x for x in v if x); inv = pow(f, -1, q)
        if tuple(x * inv % q for x in v) == v: pts.append(v)
frame = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 1)]
rest = [p for p in pts if p not in frame]
idx = lambda v: (v[:, 0] * 49 + v[:, 1] * 7 + v[:, 2])
def covered(cols):
    C = [np.array(c) for c in cols]; cover = np.zeros(343, bool); cover[0] = True; cur = np.zeros((1, 3), dtype=int)
    for _ in range(R2):
        cur = np.unique(np.concatenate([(cur + s * c) % q for c in C for s in range(1, q)]), axis=0); cover[idx(cur)] = True
    return bool(cover.all())
good = [frame + list(c) for c in itertools.combinations(rest, n2 - 4) if covered(frame + list(c))]
def words(cols):
    cols = [cols[j]] + [c for i, c in enumerate(cols) if i != j]
    return np.array(list(itertools.product(range(q), repeat=3))) @ np.array(cols).T % q
def prof(W):
    Y = np.array(list(itertools.product(range(q), repeat=n2 - 1))); r = np.zeros((len(Y), q), dtype=np.int8)
    for b in range(q):
        r[:, b] = (Y[:, None, :] != W[W[:, 0] == b][:, 1:][None]).sum(2).min(1)
    return np.unique(r, axis=0)
m = n1 - 1
X = np.array(list(itertools.product(range(q), repeat=m))); DX = (X[:, None, :] != X[None, :, :]).sum(2); nx = len(X)
def mintaus(S2):
    T = set()
    for r in S2:
        for z in range(q):
            t = [max(0, R - int(r[a])) for a in range(q)]; t[z] = max(0, R + 1 - int(r[z])); T.add(tuple(t))
    T = list(T)
    return [t for t in T if not any(u != t and all(u[i] <= t[i] for i in range(q)) for u in T)]
print('C2 candidatos (raio<=%d, contem referencial): %d' % (R2, len(good)), flush=True)
for ci in range(i0, min(i1, len(good))):
    cols = good[ci]; W = words(cols); S2 = prof(W); mt = mintaus(S2)
    if any(all(x == 0 for x in t) for t in mt):
        print(ci, cols[4:], 'j', j, 'IMPOSSIVEL: tau nulo (nenhum C1 serve com este C2)', flush=True); continue
    y = lambda c, a: 1 + c * q + a
    st_ = {'nv': nx * q}; z = {}; cl = []
    def zv(x, a, t):
        k = (x, a, t)
        if k not in z:
            st_['nv'] += 1; z[k] = st_['nv']
            cl.append([-st_['nv']] + [int(y(c, a)) for c in np.nonzero(DX[x] <= t)[0]])
        return z[k]
    for t in mt:
        for x in range(nx): cl.append([zv(x, a, min(t[a] - 1, m)) for a in range(q) if t[a] >= 1])
    cl.append([y(0, a) for a in range(q)])   # simetria: translacao em F^(n1-1) leva uma palavra a u=0
    for M1 in M1s:
        card = CardEnc.atmost(lits=list(range(1, nx * q + 1)), bound=M1, top_id=st_['nv'], encoding=EncType.seqcounter)
        s = Solver(name='glucose4', bootstrap_with=cl + card.clauses)
        t0 = time.time(); s.conf_budget(int(TL * 20000))   # orcamento em conflitos (~20k/s); Timer/interrupt nao dispara: a extensao C segura o GIL
        r = s.solve_limited()
        st = 'UNKNOWN(orcamento %d conflitos)' % int(TL*20000) if r is None else ('SAT' if r else 'UNSAT')
        print(ci, cols[4:], 'j', j, 'perfis', len(S2), 'tau', len(mt), 'M1<=', M1, st, '%.1fs' % (time.time() - t0), 'ADS<=%d' % (49 * M1), flush=True)
        if r:
            mod = set(l for l in s.get_model() if l > 0)
            C1 = [list(map(int, X[c])) + [a] for c in range(nx) for a in range(q) if y(c, a) in mod]
            print('C1', json.dumps(C1), flush=True)
            json.dump({'cols': cols, 'j': j, 'C1': C1}, open('ads_sat_%d_%d_%d.json' % (ci, j, M1), 'w'))
        s.delete()
