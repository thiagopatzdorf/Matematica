import numpy as np, itertools, random, sys
q=7
def allpts(n):
    return np.array(list(itertools.product(range(q),repeat=n)),dtype=np.int8)
def sa_cover(n,R,M,steps=200000,seed=0,T0=1.0):
    rng=random.Random(seed)
    P=allpts(n); N=len(P)
    code=[tuple(rng.randrange(q) for _ in range(n)) for _ in range(M)]
    def cov(w): return (np.sum(P!=np.array(w,dtype=np.int8),axis=1)<=R)
    cnt=np.zeros(N,dtype=np.int32)
    cv=[cov(w) for w in code]
    for c in cv: cnt+=c
    cost=int((cnt==0).sum())
    import math
    for s in range(steps):
        if cost==0: return code
        i=rng.randrange(M); w=list(code[i]); j=rng.randrange(n); w[j]=rng.randrange(q)
        nw=cov(w)
        cnt2=cnt-cv[i]+nw
        c2=int((cnt2==0).sum())
        T=T0*(1-s/steps)+0.05
        if c2<=cost or rng.random()<math.exp((cost-c2)/T):
            code[i]=tuple(w);cv[i]=nw;cnt=cnt2;cost=c2
    return None if cost else code
def profiles(code,n,coordidx,q=7):
    # code: list of words length n; coordinate coordidx merged. returns (profiles set, sizes per symbol)
    rest=[k for k in range(n) if k!=coordidx]
    sub=[[] for _ in range(q)]
    for w in code: sub[w[coordidx]].append(np.array([w[k] for k in rest],dtype=np.int8))
    P=allpts(n-1)
    D=np.full((len(P),q),99,dtype=np.int16)
    for b in range(q):
        if sub[b]:
            S=np.array(sub[b])
            d=(P[:,None,:]!=S[None,:,:]).sum(2).min(1)
            D[:,b]=d
    prof=set(map(tuple,D))
    return prof,[len(s) for s in sub]
def ads_ok(p1,p2,R):
    bad=0
    for a in p1:
        for b in p2:
            for s in range(q):
                best=min(a[t]+b[t]+(0 if t==s else 1) for t in range(q))
                if best>R: return False
    return True
