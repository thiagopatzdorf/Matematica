import os as _os, sys as _sys
_AQUI=_os.path.dirname(_os.path.abspath(__file__)); _K742=_os.path.dirname(_AQUI)
_sys.path.insert(0,_AQUI)
import sys, json
src=open(_os.path.join(_AQUI,'indep.py')).read().replace('\nmain()\n','\n'); ind={}; exec(compile(src,'indep.py','exec'),ind)
import orbita
from pysat.solvers import Solver
q,M,nsol=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]); log=sys.argv[4]
ps=orbita.encode.perfis(q,M)
sel=[json.loads(l)['perfil'] for l in open(log) if l.startswith('{') and json.loads(l)['repo']]
pts,idx,cov=ind['base'](q); ok=tot=0
for i in sel:
    cl=ind['perfil_cnf'](q,M,ps[i],pts,idx,cov)
    with Solver(name='cadical195',bootstrap_with=cl) as s:
        r=s.solve()
        for _ in range(nsol):
            if not r: break
            m=s.get_model(); C=[pts[v-1] for v in m if 0<v<=len(pts)]
            assert len(C)==M and orbita.covers(C,q)
            o=orbita.orbit_sat(C,q,cover=True); ok+=o; tot+=1
            if not o: print('FALHA',C,flush=True)
            s.add_clause([-v for v in m if 0<v<=len(pts)]); r=s.solve()
print(json.dumps({'q':q,'M':M,'perfis':len(sel),'codigos':tot,'orbita_sat':ok}))
