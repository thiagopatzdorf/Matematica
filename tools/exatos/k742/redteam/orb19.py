import random, orbita
C=[(0,0,0,0)]
for off in (1,4):
    C+=[(off+a,off+b,off+(a+b)%3,off+(a+2*b)%3) for a in range(3) for b in range(3)]
assert orbita.covers(C,7)
rng=random.Random(5); res=[]
# a órbita é invariante pelo grupo; imagens aleatórias só mudam a entrada (ordem/rotulagem), não o resultado
for _ in range(3):
    perm=list(range(4)); rng.shuffle(perm); sims=[rng.sample(range(7),7) for _ in range(4)]
    D=[tuple(sims[i][c[perm[i]]] for i in range(4)) for c in C]; rng.shuffle(D)
    res.append(orbita.orbit_sat(D,7,cover=True))
print('q=7 M=19 particao, orbita SAT com cobertura:',res)
