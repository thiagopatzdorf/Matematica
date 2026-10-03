import sys;sys.path.insert(0,'.')
from ads import *
from t2 import lin_code, covers, prof_arrays, cost
import random, itertools, math, time
def find_lin(n,r,R,seed):
    rng=random.Random(seed)
    pts=[p for p in itertools.product(range(q),repeat=r) if any(p)]
    while True:
        cols=rng.sample(pts,n)
        if covers(cols,r,R): return cols
def run(C2,n2,ci2,n1,M,R,steps,seed):
    D2,s2=prof_arrays(C2,n2,ci2)
    U2,w2=np.unique(D2,axis=0,return_counts=True)
    rng=random.Random(seed)
    code=[tuple(rng.randrange(q) for _ in range(n1)) for _ in range(M)]
    def D1of(c): return prof_arrays(c,n1,0)[0]
    c=cost(D1of(code),U2,w2,R); best=c
    for s in range(steps):
        if c==0: return code,s2,0
        i=rng.randrange(M); old=code[i]; w=list(old); j=rng.randrange(n1); w[j]=rng.randrange(q); code[i]=tuple(w)
        cn=cost(D1of(code),U2,w2,R)
        T=0.05*(1-s/steps)+0.002
        if cn<=c or rng.random()<math.exp((c-cn)/(T*max(c,1))): c=cn
        else: code[i]=old
        best=min(best,c)
    return None,s2,best
if __name__=="__main__":
    n1,M,n2,r2,R2,R,steps,seed=map(int,sys.argv[1:9])
    cols=find_lin(n2,r2,R2,seed); C2=lin_code(cols,r2)
    print(cols,len(C2),flush=True)
    for ci2 in range(min(n2,3)):
        t=time.time()
        res=run(C2,n2,ci2,n1,M,R,steps,seed)
        print('ci2',ci2,'FOUND' if res[0] else 'best',res[2],res[0] if res[0] else '',time.time()-t,flush=True)
