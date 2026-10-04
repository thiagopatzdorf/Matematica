"""Compara, perfil a perfil, SAT/UNSAT da CNF do repo (encode.codificar, com quebra (a)-(f))
com a codificação independente (indep.py: x_w por palavra, só renomeação por fibra + lex-leader).
Se a quebra de simetria do repo perdesse códigos, apareceria perfil SAT aqui e UNSAT lá."""
import os as _os, sys as _sys
_AQUI=_os.path.dirname(_os.path.abspath(__file__)); _K742=_os.path.dirname(_AQUI)
import sys, json, random, time, itertools
sys.path.insert(0,_K742); import encode
sys.argv_saved=sys.argv; sys.argv=['x','4','4','0','none']
import importlib.util
spec=importlib.util.spec_from_file_location('indep',_os.path.join(_AQUI,'indep.py')); ind=importlib.util.module_from_spec(spec)
src=open(_os.path.join(_AQUI,'indep.py')).read().replace('\nmain()\n','\n'); exec(compile(src,'indep.py','exec'),ind.__dict__)
from pysat.solvers import Solver
args=sys.argv_saved
q,M,n,seed=int(args[1]),int(args[2]),int(args[3]),int(args[4])
ps=encode.perfis(q,M); rng=random.Random(seed)
sel=list(range(len(ps))) if n<=0 or n>=len(ps) else rng.sample(range(len(ps)),n)
pts,idx,cov=ind.base(q)
desacordo=0; ns=0
for i in sel:
    p=ps[i]
    cnf,x,s0=encode.codificar(q,M,p); t=time.time()
    with Solver(name='cadical195',bootstrap_with=cnf.cl) as s: r1=s.solve()
    t1=time.time()-t
    # mesma lista de tipos, cada coordenada com sua fibra ordenada decrescente
    cl=ind.perfil_cnf(q,M,p,pts,idx,cov); t=time.time()
    with Solver(name='cadical195',bootstrap_with=cl) as s: r2=s.solve()
    t2=time.time()-t
    ns+=r1; desacordo+=(r1!=r2)
    print(json.dumps({'perfil':i,'repo':r1,'indep':r2,'t_repo':round(t1,2),'t_indep':round(t2,2)}),flush=True)
print('RESUMO',q,M,'perfis',len(sel),'SAT repo',ns,'desacordos',desacordo)
