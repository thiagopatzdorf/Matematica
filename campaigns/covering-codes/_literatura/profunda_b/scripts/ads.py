import numpy as np, itertools, sys, time
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 7)

def patterns(n, R):
    P = []
    for w in range(R + 1):
        for pos in itertools.combinations(range(n), w):
            for vals in itertools.product((1, 2, 3), repeat=w):
                e = np.zeros(n, dtype=np.int64); e[list(pos)] = vals; P.append(e)
    return np.array(P)

P7 = patterns(7, 3)
P10 = patterns(10, 4)

def covers(C, P, n):
    pw = 4 ** np.arange(n)
    mark = np.zeros(4 ** n, dtype=bool)
    for c in C:
        mark[((c[None, :] ^ P) * pw).sum(1)] = True
    return bool(mark.all())

def random_additive(n, dim):
    gens = rng.integers(0, 4, size=(dim, n))
    out = [np.zeros(n, dtype=np.int64)]
    for g in gens:
        out = out + [o ^ g for o in out]
    out = np.array(out)
    if len({tuple(r) for r in out}) != 2 ** dim:
        return None
    return out

found = []
tries = 0
t0 = time.time()
while len(found) < 6 and time.time() - t0 < 500:
    tries += 1
    C = random_additive(7, 5)
    if C is None:
        continue
    if covers(C, P7, 7):
        found.append(C)
        print('achou (7,32,3)_4 aditivo na tentativa', tries, flush=True)
print('tentativas', tries, 'achados', len(found))
np.save('c732_add.npy', np.array(found) if found else np.zeros(0))
