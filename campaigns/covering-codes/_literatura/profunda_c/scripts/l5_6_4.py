#!/usr/bin/env python3
"""Reproduz (independente dos scripts da profunda/): (i) o codigo q5_n10_R4_M625 do repo tem raio de cobertura exato 4;
(ii) taxa de sucesso de 10 colunas aleatorias em F_5^6 formarem [10,4]_5 de raio <=4 (i.e. 3-saturante em PG(5,5)); (iii) n=9 por amostragem (nao e prova)."""
import numpy as np,itertools,random,sys,time
q=5
C=np.array([[int(c) for c in l.strip()] for l in open('/home/user/Matematica/data/codes/q5_n10_R4_M625.txt') if l.strip()])
n=10; cov=np.zeros(q**n,bool); cov[(C*(q**np.arange(n-1,-1,-1))).sum(1)]=True
A=cov.reshape((q,)*n); r=0
while not A.all():
    B=A.copy()
    for ax in range(n): B|=A.any(axis=ax,keepdims=True)
    A=B; r+=1
print('repo M625: |C|=%d distintas=%d raio exato=%d'%(len(C),len(np.unique(C,axis=0)),r))
def radius_syn(cols):   # menor R tal que toda sindrome (F_5^6) e combinacao de <=R colunas
    cols=np.array(cols); cover=np.zeros(q**6,bool); cover[0]=True
    cur=np.zeros((1,6),dtype=int); pw=q**np.arange(5,-1,-1)
    for R in range(1,7):
        cur=np.unique(np.concatenate([cur]+[(cur+s*c)%q for c in cols for s in range(1,q)]),axis=0)
        cover[(cur*pw).sum(1)]=True
        if cover.all(): return R
rng=random.Random(1); t=time.time()
for nn in (10,9):
    ok=0;T=300 if nn==10 else 300
    hist={}
    for _ in range(T):
        cols=[[rng.randrange(q) for _ in range(6)] for _ in range(nn)]
        R=radius_syn(cols); hist[R]=hist.get(R,0)+1
    print('n=%d colunas aleatorias em F_5^6: distribuicao do raio em %d amostras: %s'%(nn,T,dict(sorted(hist.items()))))
print('%.0fs'%(time.time()-t))
