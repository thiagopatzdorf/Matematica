import numpy as np, itertools, sys, glob
q = 5
def ball_marks(C, n, R):
    P = []
    for w in range(R + 1):
        for pos in itertools.combinations(range(n), w):
            for vals in itertools.product(range(1, q), repeat=w):
                e = np.zeros(n, dtype=np.int64); e[list(pos)] = vals; P.append(e)
    return np.array(P)
P5 = ball_marks(None, 5, 2); P9 = ball_marks(None, 9, 4)
def covers(C, P, n):
    pw = q ** np.arange(n)
    mark = np.zeros(q ** n, dtype=bool)
    for c in C:
        mark[(((c[None, :] + P) % q) * pw).sum(1)] = True
    return bool(mark.all())
rng = np.random.default_rng(3)
X = rng.integers(0, q, size=(1500, 9))
def quick(A):
    return bool(((X[:, None, :] != A[None, :, :]).sum(2).min(1) <= 4).all())
def ads(B, i, C, j, perm):
    out = []
    for a in range(q):
        Ba = [np.delete(b, i) for b in B if b[i] == a]
        Ca = [np.delete(c, j) for c in C if c[j] == perm[a]]
        for b in Ba:
            for c in Ca: out.append(np.concatenate([b, [a], c]))
    return np.array(out)
files = sorted(glob.glob('c535_*.npy'))
print('códigos', files)
tot = 0; hits = 0
for f in files:
    C = np.load(f)
    print(f, 'tamanho', len(C), 'distintas', len({tuple(r) for r in C}), 'cobre (5,R=2)?', covers(C, P5, 5), flush=True)
    for i in range(5):
        for j in range(5):
            if sorted(np.bincount(C[:, i], minlength=q)) != [7] * 5 or sorted(np.bincount(C[:, j], minlength=q)) != [7] * 5: continue
            for perm in itertools.permutations(range(q)):
                A = ads(C, i, C, j, perm); tot += 1
                if len(A) == 245 and quick(A) and covers(A, P9, 9):
                    hits += 1; print('HIT: ADS 245 cobre (9, R=4):', f, i, j, perm, flush=True); np.save('ads245_hit.npy', A); break
            else: continue
            break
        else: continue
        break
print('testados', tot, 'hits', hits)
