import sys;sys.path.insert(0,'.')
from ads import *
import random, itertools, math, time
exec(open('t1.py').read().split("pts=[p")[0].split("rng=random.Random(1)")[1]) if False else None
def lin_code(cols,r):
    n=len(cols);words=[]
    for x in itertools.product(range(q),repeat=n):
        if all(sum(x[j]*cols[j][i] for j in range(n))%q==0 for i in range(r)): words.append(x)
    return words
def covers(cols,r,R):
    syn={tuple([0]*r)};fr=set(syn)
    for _ in range(R):
        nf=set()
        for s in fr|syn:
            for c in cols:
                for a in range(1,q): nf.add(tuple((s[i]+a*c[i])%q for i in range(r)))
        syn|=nf;fr=nf
    return len(syn)==q**r
def prof_arrays(code,n,ci):
    rest=[k for k in range(n) if k!=ci]
    sub=[[] for _ in range(q)]
    for w in code: sub[w[ci]].append([w[k] for k in rest])
    P=allpts(n-1).astype(np.int8)
    D=np.full((len(P),q),9,dtype=np.int16)
    for b in range(q):
        if sub[b]:
            S=np.array(sub[b],dtype=np.int8)
            D[:,b]=(P[:,None,:]!=S[None,:,:]).sum(2).min(1)
    return D,[len(s) for s in sub]
def cost(D1,U2,w2,R):
    T=D1[:,None,:]+U2[None,:,:]   # u,k,b
    bad=0
    for a in range(q):
        Ta=T+1; Ta[:,:,a]-=1
        v=Ta.min(2)
        bad+=int(((v>R)*w2[None,:]).sum())
    return bad
def run(C2,ci2,M,R=4,steps=4000,seed=0,n1=4):
    D2,s2=prof_arrays(C2,6,ci2)
    U2,inv=np.unique(D2,axis=0,return_counts=True)
    w2=inv
    rng=random.Random(seed)
    P=allpts(n1-1).astype(np.int8)
    code=[tuple(rng.randrange(q) for _ in range(n1)) for _ in range(M)]
    def D1of(code):
        D,_=prof_arrays(code,n1,0); return D
    # coordinate 0 merged
    D1=D1of(code); c=cost(D1,U2,w2,R)
    best=c
    for s in range(steps):
        if c==0: return code,s2
        i=rng.randrange(M); old=code[i]; w=list(old); j=rng.randrange(n1); w[j]=rng.randrange(q); code[i]=tuple(w)
        D1n=D1of(code); cn=cost(D1n,U2,w2,R)
        T=0.05*(1-s/steps)+0.002
        if cn<=c or rng.random()<math.exp((c-cn)/(T*max(c,1))):
            c=cn;D1=D1n
        else: code[i]=old
        if c<best: best=c
    return None,best
if __name__=="__main__":
    rng=random.Random(int(sys.argv[1]))
    pts=[p for p in itertools.product(range(q),repeat=3) if any(p)]
    while True:
        cols=rng.sample(pts,6)
        if covers(cols,3,2): break
    C2=lin_code(cols,3)
    for ci2 in range(2):
        t=time.time()
        r=run(C2,ci2,19,steps=int(sys.argv[2]),seed=1)
        print(cols,ci2,r if r[0] is None else ('FOUND',r[0]),time.time()-t,flush=True)
