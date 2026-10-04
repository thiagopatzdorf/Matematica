import itertools
C=[(0,0,0,0)]
for off in (1,4):
    C+=[(off+a,off+b,off+(a+b)%3,off+(a+2*b)%3) for a in range(3) for b in range(3)]
assert len(set(C))==19
unc=[w for w in itertools.product(range(7),repeat=4) if min(sum(x!=y for x,y in zip(w,c)) for c in C)>2]
print(len(C),'descobertos',len(unc)); print(' '.join(''.join(map(str,c)) for c in C))
