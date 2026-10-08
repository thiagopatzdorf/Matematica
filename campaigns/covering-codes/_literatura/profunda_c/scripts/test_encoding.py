#!/usr/bin/env python3
"""Teste de corretude da condicao (E)/tau-clausulas usadas em ads_exact.py: para C1 aleatorios, 'clausulas satisfeitas' <=> 'ADS cobre com raio R' (forca bruta em F_7^9).
Falha em qualquer linha = o codificador SAT esta errado e NENHUM UNSAT/SAT dele vale."""
import sys,itertools,random,numpy as np
sys.argv=['x','4','6','4','2','0','0','1','1','10']
src=open('ads_exact.py').read().split("print('C2 candidatos")[0]
exec(src)
cols=good[0]; W=words(cols); S2=prof(W); mt=mintaus(S2)
rng=random.Random(5)
def adsradius(C1):
    words_=[]
    for *u,a in C1:
        for w in W[W[:,0]==a]: words_.append(list(u)+[a]+list(map(int,w[1:])))
    Cw=np.array(words_); n=9
    cov=np.zeros(q**n,bool); cov[(Cw*(q**np.arange(n-1,-1,-1))).sum(1)]=True
    A=cov.reshape((q,)*n); r=0
    while not A.all():
        B=A.copy()
        for ax in range(n): B|=A.any(axis=ax,keepdims=True)
        A=B; r+=1
    return r
def clauses_ok(C1):
    C1=np.array(C1); p=np.full((nx,q),99)
    for *u,a in C1.tolist():
        d=(X!=np.array(u)[None]).sum(1); p[:,a]=np.minimum(p[:,a],d)
    return all(any(t[a]>=1 and p[x,a]<=t[a]-1 for a in range(q)) for t in mt for x in range(nx))
allw=[list(u)+[a] for u in X.tolist() for a in range(q)]
res=[]
for M in [30,60,80,90,100,110,120,140,160,180]:
    C1=rng.sample(allw,M); ok=clauses_ok(C1); r=adsradius(C1)
    print('M1=%d clausulas_ok=%s raio_ADS=%d  %s'%(M,ok,r,'OK' if ok==(r<=4) else 'DIVERGE!!'),flush=True)
