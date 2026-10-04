"""Teste de completude por SAT (independente de canonizar.py): para um código C, a CNF do perfil
(encode.codificar) restrita à órbita de C sob S_q wr S_4 x reordenação de palavras tem de ser SAT."""
import os as _os, sys as _sys
_AQUI=_os.path.dirname(_os.path.abspath(__file__)); _K742=_os.path.dirname(_AQUI)
import itertools, random, sys, time
from collections import Counter
sys.path.insert(0,_K742)
import encode
from pysat.solvers import Solver
N=4
def tipo(C,i,q): return tuple(sorted((Counter(c[i] for c in C).get(a,0) for a in range(q)),reverse=True))
def eo(lits):
    cl=[list(lits)]
    cl+= [[-a,-b] for a,b in itertools.combinations(lits,2)]
    return cl
def orbit_sat(C,q,mut=None,cover=True):
    M=len(C)
    ts=[tipo(C,i,q) for i in range(N)]
    ps=encode.perfis(q,M)
    key=tuple(sorted(ts,key=lambda t:(encode.simetria_residual(t),t)))
    p=next(pp for pp in ps if pp==key)
    cnf,x,sim0=encode.codificar(q,M,p) if mut is None else mut(q,M,p)
    cl=list(cnf.cl)
    if not cover:
        n0=len(encode.codificar(q,M,p,quebra=False)[0].cl)
        cov=set(range(n0-q**N,n0))
        cl=[c for j,c in enumerate(cl) if j not in cov]
    top=cnf.nv
    def nv():
        nonlocal top; top+=1; return top
    for rho in itertools.permutations(range(N)):
        if any(ts[rho[i]]!=p[i] for i in range(N)): continue
        extra=[]
        pi=[[nv() for c in range(M)] for k in range(M)]
        sg=[[[nv() for b in range(q)] for a in range(q)] for i in range(N)]
        for k in range(M): extra+=eo(pi[k])
        for c in range(M): extra+=eo([pi[k][c] for k in range(M)])
        for i in range(N):
            for a in range(q): extra+=eo(sg[i][a])
            for b in range(q): extra+=eo([sg[i][a][b] for a in range(q)])
        for k in range(M):
            for c in range(M):
                extra.append([-pi[k][c], sg[0][C[c][rho[0]]][sim0[k]]])
                for i in range(1,N):
                    for b in range(q):
                        extra.append([-pi[k][c], -sg[i][C[c][rho[i]]][b], x[k][i][b]])
        with Solver(name='cadical195',bootstrap_with=cl+extra) as s:
            if s.solve(): return True
    return False
def rand_code(q,M,smin,rng):
    ts=encode.tipos(q,M,smin)
    cols=[]
    for i in range(N):
        t=list(rng.choice(ts)); rng.shuffle(t)
        col=[a for a in range(q) for _ in range(t[a])]; rng.shuffle(col); cols.append(col)
    return [tuple(cols[i][k] for i in range(N)) for k in range(M)]
def covers(C,q):
    return all(any(sum(a!=b for a,b in zip(w,c))<=2 for c in C) for w in itertools.product(range(q),repeat=N))
if __name__=='__main__':
    rng=random.Random(int(sys.argv[3]) if len(sys.argv)>3 else 1)
    q,M=int(sys.argv[1]),int(sys.argv[2]); n=int(sys.argv[4]) if len(sys.argv)>4 else 50
    smin=encode.fibra_minima(q,M)
    ok=0; t=time.time()
    for it in range(n):
        C=rand_code(q,M,smin,rng)
        r=orbit_sat(C,q,cover=covers(C,q))
        ok+=r
        if not r: print("FALHA",C,flush=True)
    print(q,M,"orbita SAT",ok,"/",n,round(time.time()-t,1),"s")
