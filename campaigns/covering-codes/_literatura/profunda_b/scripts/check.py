import numpy as np, itertools, sys
def load(p): return np.array([[int(c) for c in l.strip()] for l in open(p) if l.strip()],dtype=np.int8)
def covrad(C,q,R=None):
    n=C.shape[1]; N=q**n
    pw=q**np.arange(n)
    # min distance per word via per-codeword distance (chunked)
    allw=np.indices((q,)*n).reshape(n,-1).T.astype(np.int8) if N<=2_100_000 else None
    best=np.full(N,99,dtype=np.int8)
    for c in C:
        d=(allw!=c).sum(1).astype(np.int8); np.minimum(best,d,out=best)
    return int(best.max()), int((best>R).sum()) if R is not None else None
for f,q,R in [('q5_n7_R2_M500',5,2),('q4_n10_R4_M192',4,4),('q5_n9_R3_M1250',5,3),('q5_n9_R5_M50',5,5),('q5_n9_R4_M250',5,4)]:
    C=load(f'data/codes/{f}.txt'); 
    print(f,'palavras',len(C),'distintas',len({tuple(r) for r in C}))
    rad,bad=covrad(C,q,R); print('  raio de cobertura medido',rad,'não cobertos com R:',bad)
    # estrutura: estabilizador por translação
    S={tuple(r) for r in C}
    if q==5:
        base=C[0]
        stab=0
        for c in C:
            t=(c-C[0])%5
            if all(tuple((r+t)%5) in S for r in C): stab+=1
        print('  |translações que preservam C| =',stab)
    else:
        stab=0
        for c in C:
            t=c^C[0]
            if all(tuple(r^t) in S for r in C): stab+=1
        print('  |translações xor que preservam C| =',stab)
        mul=np.array([[0,0,0,0],[0,1,2,3],[0,2,3,1],[0,3,1,2]],dtype=np.int8)
        for lam in (2,3):
            # fecha por ω? testa C -> ω*C + t para algum t
            W=mul[lam][C]; ok=any(all(tuple(r^(W[0]^C[0]) ) in S for r in W) for _ in [0])
            print('  ω*C é translação de C? (lam=%d)'%lam, ok)
