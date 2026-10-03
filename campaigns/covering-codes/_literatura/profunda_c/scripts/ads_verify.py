#!/usr/bin/env python3
"""Verifica por forca bruta (dilatacao de Hamming no espaco inteiro) a ADS construida a partir de ads_sat_*.json.
Uso: ads_verify.py arquivo.json   -> imprime |ADS|, n, e o raio de cobertura exato (maior distancia ao codigo). Independente do SAT."""
import sys,json,itertools,numpy as np
q=7
d=json.load(open(sys.argv[1])); cols=d['cols']; j=d['j']; C1=np.array(d['C1'])
cols=[cols[j]]+[c for i,c in enumerate(cols) if i!=j]
W=np.array(list(itertools.product(range(q),repeat=3)))@np.array(cols).T%q   # C2, col 0 = colagem
words=[]
for *u,a in C1.tolist():
    for w in W[W[:,0]==a]:
        words.append(u+[a]+list(map(int,w[1:])))
Cw=np.array(words); n=Cw.shape[1]
assert len(np.unique(Cw,axis=0))==len(Cw)
cover=np.zeros(q**n,bool); cover[(Cw*(q**np.arange(n-1,-1,-1))).sum(1)]=True
A=cover.reshape((q,)*n); r=0
while not A.all():
    B=A.copy()
    for ax in range(n): B|=A.any(axis=ax,keepdims=True)
    A=B; r+=1
print('|ADS|=',len(Cw),'n=',n,'raio exato=',r)
