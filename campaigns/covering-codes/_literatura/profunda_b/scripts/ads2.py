"""Teste (meu, não de terceiros): a soma direta amalgamada (ADS) de um (4,24,1)_4 e um (7,32,3)_4
dá um (10,192,4)_4? Verificação por cobertura direta do código resultante (não depende de teoria de normalidade)."""
import numpy as np, itertools, sys, time, subprocess
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 11)

def patterns(n, R):
    P = []
    for w in range(R + 1):
        for pos in itertools.combinations(range(n), w):
            for vals in itertools.product((1, 2, 3), repeat=w):
                e = np.zeros(n, dtype=np.int64); e[list(pos)] = vals; P.append(e)
    return np.array(P)

P7 = patterns(7, 3); P10 = patterns(10, 4)

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

def find_C():
    while True:
        C = random_additive(7, 5)
        if C is not None and covers(C, P7, 7):
            return C

def sa_B(seed):
    r = subprocess.run(['./sa', '4', '4', '1', '24', str(seed), '5000000'], capture_output=True, text=True)
    if r.returncode != 0: return None
    return np.array([[int(ch) for ch in l] for l in r.stdout.split()], dtype=np.int64)

X = rng.integers(0, 4, size=(1500, 10))
def quick(A):
    d = (X[:, None, :] != A[None, :, :]).sum(2).min(1)
    return bool((d <= 4).all())

def ads(B, i, Cc, j, perm):
    out = []
    for a in range(4):
        Ba = [np.delete(b, i) for b in B if b[i] == a]
        Ca = [np.delete(c, j) for c in Cc if c[j] == perm[a]]
        for b in Ba:
            for c in Ca:
                out.append(np.concatenate([b, [a], c]))
    return np.array(out)

nC = int(sys.argv[2]) if len(sys.argv) > 2 else 3
nB = int(sys.argv[3]) if len(sys.argv) > 3 else 25
tested = 0; hits = []
t0 = time.time()
for ci in range(nC):
    C = find_C()
    print('C (7,32,3)_4 aditivo #', ci, 'achado', round(time.time() - t0), 's', flush=True)
    for bs in range(1, nB + 1):
        B = sa_B(1000 * ci + bs)
        if B is None: continue
        for j in range(7):
            if sorted(np.bincount(C[:, j], minlength=4)) != [8] * 4: continue
            for perm in itertools.permutations(range(4)):
                A = ads(B, 0, C, j, perm)
                tested += 1
                if len(A) == 192 and quick(A) and covers(A, P10, 10):
                    hits.append((ci, bs, j, perm)); print('HIT ADS 192 cobre R=4:', ci, bs, j, perm, flush=True)
                    np.save('ads192_hit.npy', A)
                    break
            if hits: break
        if hits: break
        print("B",bs,"testados",tested,flush=True)
    if hits: break
print('testados', tested, 'hits', len(hits), 'tempo', round(time.time() - t0))
