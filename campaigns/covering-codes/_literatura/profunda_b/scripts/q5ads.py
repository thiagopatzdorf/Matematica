"""Teste (meu): existe (5,35,2)_5 como união de 7 translados de <g>? e a ADS dele consigo mesmo cobre (9, R=4) com 245?"""
import numpy as np, itertools, sys, time
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
q = 5
def errs(n, R):
    P = []
    for w in range(R + 1):
        for pos in itertools.combinations(range(n), w):
            for vals in itertools.product(range(1, q), repeat=w):
                e = np.zeros(n, dtype=np.int64); e[list(pos)] = vals; P.append(e)
    return np.array(P)
E5 = errs(5, 2)
def key5(W): return (W * (q ** np.arange(5))).sum(-1)
allw5 = np.array(list(itertools.product(range(q), repeat=5)))[:, ::-1]  # índice = key5
assert (key5(allw5) == np.arange(q ** 5)).all()

def find_code(g, M7=7, tries=40, iters=60000):
    g = np.array(g)
    # classes de <g>: rótulo = menor chave do translado
    mult = np.array([(a * g) % q for a in range(q)])
    cls = np.min(np.stack([key5((allw5 + m) % q) for m in mult]), axis=0)
    labels = np.unique(cls); idx = {l: i for i, l in enumerate(labels)}
    cl = np.array([idx[c] for c in cls])
    nq = len(labels)
    # vizinhança de classe: classes alcançadas por erro de peso<=2 a partir do representante
    rep = np.zeros(nq, dtype=np.int64); rep[cl[::-1]] = np.arange(q ** 5)[::-1]
    nb = [np.unique(cl[key5((allw5[r][None, :] + E5) % q)]) for r in rep]
    cover = np.zeros((nq, nq), dtype=bool)
    for u in range(nq): cover[u, nb[u]] = True
    best = nq
    for t in range(tries):
        S = list(rng.choice(nq, M7, replace=False))
        cnt = cover[S].sum(0); unc = int((cnt == 0).sum())
        for it in range(iters):
            if unc == 0: break
            i = rng.integers(M7); v = rng.integers(nq)
            old = S[i]
            cnt2 = cnt - cover[old] + cover[v]; unc2 = int((cnt2 == 0).sum())
            if unc2 <= unc or rng.random() < np.exp(-(unc2 - unc) / 0.5):
                S[i] = v; cnt = cnt2; unc = unc2
        best = min(best, unc)
        if unc == 0:
            words = []
            for s in S:
                r = allw5[rep[s]]
                for a in range(q): words.append((r + a * g) % q)
            return np.array(words)
    print('g', g, 'melhor não-coberto', best, flush=True)
    return None

for g in [(1, 1, 1, 1, 1), (1, 1, 1, 1, 0), (1, 1, 1, 0, 0), (1, 2, 1, 2, 1), (1, 1, 2, 2, 0), (1,2,3,4,1), (1,2,1,2,0)]:
    t0 = time.time()
    C = find_code(g)
    print('g', g, 'achou 35?' , C is not None, round(time.time() - t0), 's', flush=True)
    if C is not None:
        np.save('c535_%s.npy' % ''.join(map(str, g)), C)
