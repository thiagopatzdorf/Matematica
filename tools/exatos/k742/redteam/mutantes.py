import os as _os, sys as _sys
_AQUI=_os.path.dirname(_os.path.abspath(__file__)); _K742=_os.path.dirname(_AQUI)
_sys.path.insert(0,_AQUI)
import sys, random, importlib.util, re
sys.path.insert(0,_AQUI)
import orbita
src=open(_os.path.join(_K742,'encode.py')).read()
muts={
 'f_ignora_classe': ("            if t[i][a] != t[i][a + 1]:\n                continue\n            for k in range(M):", "            for k in range(M):"),
 'e_ignora_classe': ("        if t[1][a] != t[1][a + 1]:\n            continue\n", ""),
 'e_estrita': ("for bb in bl[: bi + 1]", "for bb in bl[: bi]"),
 'd_estrita': ("for b in range(a):\n                    cnf.add([-x[k][1][a], -x[k + 1][1][b]])", "for b in range(a + 1):\n                    cnf.add([-x[k][1][a], -x[k + 1][1][b]])"),
 'f_tambem_coord0_ordem': ("    for i in (2, 3):\n        for a in range(q - 1):", "    for i in (1, 2, 3):\n        for a in range(q - 1):"),
}
q,M,n=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3])
for nome,(a,b) in muts.items():
    assert a in src, nome
    s2=src.replace(a,b)
    spec=importlib.util.spec_from_loader('m_'+nome,loader=None); m=importlib.util.module_from_spec(spec); exec(s2,m.__dict__)
    rng=random.Random(7); smin=orbita.encode.fibra_minima(q,M); falhas=0
    for _ in range(n):
        C=orbita.rand_code(q,M,smin,rng)
        if not orbita.orbit_sat(C,q,mut=lambda q_,M_,p_: m.codificar(q_,M_,p_),cover=orbita.covers(C,q)): falhas+=1
    print(nome, 'falhas', falhas,'/',n, flush=True)
