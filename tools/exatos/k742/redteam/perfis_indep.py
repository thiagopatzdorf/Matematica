import os as _os, sys as _sys
_AQUI=_os.path.dirname(_os.path.abspath(__file__)); _K742=_os.path.dirname(_AQUI)
import itertools, subprocess, sys
def parts(M,q,smin):
    S=set()
    for v in itertools.product(range(smin,M+1),repeat=q):
        if sum(v)==M: S.add(tuple(sorted(v,reverse=True)))
    return S
for q,M in [(7,17),(7,18),(5,10),(4,6)]:
    # smin by direct check of lemma with ceil(v^2/2) for v<=7 and elementary for q=7
    T=parts(M,q,2 if q==7 else (1 if q==5 else None)) if q!=4 else None
    if T is None: continue
    mine=set(frozenset(itertools.combinations_with_replacement(sorted(T),4)))
    mine={tuple(sorted(p)) for p in itertools.combinations_with_replacement(sorted(T),4)}
    out=subprocess.run([sys.executable,_os.path.join(_K742,'encode.py'),'--q',str(q),'--M',str(M),'--listar'],capture_output=True,text=True).stdout.splitlines()
    print(out[0])
    theirs={tuple(sorted(tuple(int(c) for c in t.strip()) for t in l.split(' ',1)[1].split('|'))) for l in out[1:]}
    print(q,M,len(T),len(mine),len(theirs),mine==theirs, len(out)-1)
