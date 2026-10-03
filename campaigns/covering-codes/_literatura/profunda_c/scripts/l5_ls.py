#!/usr/bin/env python3
"""Busca local simples (semente fixa) por 10 colunas em F_5^6 com raio <= 4 (=> [10,4]_5 R=4, K_5(10,4)<=625). Mede iteracoes e tempo.
Objetivo = numero de sindromes (de 5^6) NAO alcancaveis por <=4 colunas. Aceita movimento se nao piora."""
import numpy as np,random,time,sys
q=5; pw=q**np.arange(5,-1,-1)
def unc(cols,R=4):
    cover=np.zeros(q**6,bool); cover[0]=True; cur=np.zeros((1,6),dtype=np.int64)
    for _ in range(R):
        cur=np.unique(np.concatenate([cur]+[(cur+s*c)%q for c in cols for s in range(1,q)]),axis=0); cover[cur@pw]=True
    return int((~cover).sum())
n=int(sys.argv[1]); seed=int(sys.argv[2]); rng=random.Random(seed); t=time.time()
cols=[np.array([rng.randrange(q) for _ in range(6)]) for _ in range(n)]; f=unc(cols); it=0
while f>0 and time.time()-t<float(sys.argv[3]):
    i=rng.randrange(n); old=cols[i]; cols[i]=np.array([rng.randrange(q) for _ in range(6)]); g=unc(cols); it+=1
    if g<=f: f=g
    else: cols[i]=old
print('n=%d seed=%d iter=%d descobertas_finais=%d tempo=%.1fs'%(n,seed,it,f,time.time()-t))
