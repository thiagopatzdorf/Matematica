#!/usr/bin/env python3
"""Conta C2=[n2,3]_7 (n2 colunas em PG(2,7), contendo um referencial) com raio de cobertura <= R2.
Uso: c2_classes.py n2 R2   -- saida: lista de colunas extras. Equivale a: conjuntos (R2-1)-saturantes de n2 pontos contendo 4 pontos em posicao geral."""
import sys,itertools,numpy as np
q=7;n2,R2=int(sys.argv[1]),int(sys.argv[2])
pts=[]
for v in itertools.product(range(q),repeat=3):
    if any(v):
        f=next(x for x in v if x); inv=pow(f,-1,q)
        if tuple(x*inv%q for x in v)==v: pts.append(v)
P=np.array(pts); frame=[(1,0,0),(0,1,0),(0,0,1),(1,1,1)]
rest=[p for p in pts if p not in frame]
# saturacao: toda sindrome (ponto de F^3, 343) e combinacao de <=R2 colunas (com escalares)
allv=np.array(list(itertools.product(range(q),repeat=3)))
def covered(cols):
    cur={ (0,0,0) }; seen={(0,0,0)}
    C=[np.array(c) for c in cols]
    layer=np.zeros((1,3),dtype=int)
    cover=np.zeros(343,bool); cover[0]=True
    idx=lambda v:(v[:,0]*49+v[:,1]*7+v[:,2])
    cur=layer
    for _ in range(R2):
        nxt=[(cur+s*c)%q for c in C for s in range(1,q)]
        cur=np.unique(np.concatenate(nxt),axis=0)
        cover[idx(cur)]=True
        if cover.all(): return True
    return bool(cover.all())
good=[]
for comb in itertools.combinations(rest,n2-4):
    cols=frame+list(comb)
    if covered(cols): good.append(comb)
print(len(good),'de',sum(1 for _ in itertools.combinations(rest,n2-4)))
for g in good[:5]: print(g)
