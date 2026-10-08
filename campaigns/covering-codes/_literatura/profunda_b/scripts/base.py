import numpy as np, json, itertools
def covrad_linear(G,q):
    k,n=G.shape
    msgs=np.array(list(itertools.product(range(q),repeat=k)),dtype=np.int64)
    L=(msgs@G)%q
    # distância de cada x ao código L
    allw=np.indices((q,)*n).reshape(n,-1).T
    # via síndrome: peso mínimo do coset; computa direto por tabela hash de coset
    pw=q**np.arange(n)
    # min dist = min over l of hamming; usar BFS por pesos de erro: conjunto de síndromes alcançadas
    return L
def syn_covrad(H,q):
    r,n=H.shape
    seen={tuple([0]*r)}; frontier=[np.zeros(r,dtype=np.int64)]; R=0
    cols=[H[:,j] for j in range(n)]
    total=q**r
    while len(seen)<total:
        new=[]
        for s in frontier:
            for j in range(n):
                for a in range(1,q):
                    t=tuple((s+a*cols[j])%q)
                    if t not in seen: seen.add(t); new.append(np.array(t))
        R+=1; frontier=new
        if not new: break
    return R
for f in ['q5_n7_R2_M500','q5_n9_R3_M1250','q5_n9_R5_M50','q5_n9_R4_M250']:
    J=json.load(open(f'data/structured/{f}.json')); lb=J['linear_base']
    H=np.array([[int(c) for c in r] for r in lb['parity_check']])
    G=np.array([[int(c) for c in r] for r in lb['generator']])
    assert ((H@G.T)%5==0).all()
    print(f,'k=',lb['k'],'n-k=',H.shape[0],'cosets=',len(lb['coset_syndromes']),'M=',len(lb['coset_syndromes'])*5**lb['k'],'raio de cobertura da base linear sozinha=',syn_covrad(H,5))
