"""Controle: CNF do repo SEM (d)-(f) (quebra=False), só (a)-(c), resolvida com CaDiCaL 1.9.5 (pysat)."""
import os as _os, sys as _sys
_AQUI=_os.path.dirname(_os.path.abspath(__file__)); _K742=_os.path.dirname(_AQUI)
import sys, json, time
sys.path.insert(0,_K742); import encode
from pysat.solvers import Solver
q,M=int(sys.argv[1]),int(sys.argv[2]); sel=[int(i) for i in sys.argv[3].split(',')] if len(sys.argv)>3 else None
ps=encode.perfis(q,M)
for i in (sel if sel is not None else range(len(ps))):
    cnf,_,_=encode.codificar(q,M,ps[i],quebra=False); t=time.time()
    with Solver(name='cadical195',bootstrap_with=cnf.cl) as s: r=s.solve()
    print(json.dumps({'q':q,'M':M,'perfil':i,'sat':r,'t':round(time.time()-t,1)}),flush=True)
