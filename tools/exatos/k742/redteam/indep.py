"""Codificação independente (não importa nada de tools/exatos/k742).
Uso: indep.py q M smin perfil [_ lista,de,perfis]  |  indep.py q M smin global
Variável x_w por palavra w de Z_q^4 (código como conjunto: palavras distintas).
Modo 'perfil': para cada perfil (multiconjunto de 4 tipos, enumerado aqui), fibras exatas
sum_{w_j=a} x_w = t_j[a] com símbolos em ordem decrescente de fibra (renomear símbolos e permutar
coordenadas: trivialmente válido). Cobertura: OR das bolas de raio 2 (distância de Hamming direta,
sem projeções). Nenhuma outra quebra de simetria.
Modo 'global': sum x_w <= M, fibras >= smin, x_{0000}=1 (translação), sem perfis."""
import itertools, sys, time, json
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
N=4
def tipos(q,M,smin):
    S=set()
    def rec(rest,k,mx,pref):
        if k==0:
            if rest==0: S.add(tuple(pref))
            return
        for v in range(smin,min(mx,rest)+1): rec(rest-v,k-1,v,pref+[v])
    rec(M,q,M,[])
    return sorted(S)
def base(q):
    pts=list(itertools.product(range(q),repeat=N)); idx={p:i+1 for i,p in enumerate(pts)}
    cov=[[idx[w] for w in pts if sum(a!=b for a,b in zip(p,w))<=2] for p in pts]
    return pts,idx,cov
def lexle(X,Y,pool):
    """X <=_lex Y (listas de literais). Cadeia com e_i = 'prefixo igual'."""
    cl=[]; e=None
    for a,b in zip(X,Y):
        if a==b: continue
        pre=[] if e is None else [-e]
        cl.append(pre+[-a,b])
        en=pool.id()
        cl.append(pre+[-a,-b,en]); cl.append(pre+[a,b,en])
        e=en
    return cl
def simetrias(q,perfil):
    """Elementos que preservam o perfil: transposições de símbolos vizinhos de mesma fibra numa
    coordenada, e trocas de coordenadas vizinhas de mesmo tipo."""
    gs=[]
    for j in range(N):
        for a in range(q-1):
            if perfil[j][a]==perfil[j][a+1]:
                def g(w,j=j,a=a):
                    w=list(w); w[j]={a:a+1,a+1:a}.get(w[j],w[j]); return tuple(w)
                gs.append(g)
    for j in range(N-1):
        if perfil[j]==perfil[j+1]:
            def g(w,j=j):
                w=list(w); w[j],w[j+1]=w[j+1],w[j]; return tuple(w)
            gs.append(g)
    return gs
LEX=True
def perfil_cnf(q,M,perfil,pts,idx,cov,enc=EncType.totalizer):
    pool=IDPool(start_from=len(pts)+1); cl=list(cov)
    if LEX:
        X=[idx[w] for w in pts]
        for g in simetrias(q,perfil):
            cl+=lexle(X,[idx[g(w)] for w in pts],pool)
    for j in range(N):
        for a in range(q):
            lits=[idx[w] for w in pts if w[j]==a]
            cl+=CardEnc.equals(lits,bound=perfil[j][a],vpool=pool,encoding=enc).clauses
    return cl
def main():
    q,M=int(sys.argv[1]),int(sys.argv[2]); smin=int(sys.argv[3]); modo=sys.argv[4]
    pts,idx,cov=base(q)
    if modo=='global':
        pool=IDPool(start_from=len(pts)+1); cl=list(cov)+[[idx[(0,)*N]]]
        cl+=CardEnc.atmost(list(idx.values()),bound=M,vpool=pool,encoding=EncType.seqcounter).clauses
        for j in range(N):
            for a in range(q):
                if smin>0: cl+=CardEnc.atleast([idx[w] for w in pts if w[j]==a],bound=smin,vpool=pool,encoding=EncType.seqcounter).clauses
        t=time.time()
        with Solver(name='cadical195',bootstrap_with=cl) as s: r=s.solve()
        print(json.dumps({'q':q,'M':M,'modo':'global','sat':r,'t':round(time.time()-t,1)}),flush=True); return
    ts=tipos(q,M,smin)
    ps=list(itertools.combinations_with_replacement([tuple(sorted(t,reverse=True)) for t in ts],N))
    sel=range(len(ps)) if len(sys.argv)<=6 else [int(i) for i in sys.argv[6].split(',')]
    print(f'q={q} M={M} smin={smin} tipos={len(ts)} perfis={len(ps)}',flush=True)
    for i in sel:
        cl=perfil_cnf(q,M,ps[i],pts,idx,cov); t=time.time()
        with Solver(name='cadical195',bootstrap_with=cl) as s: r=s.solve()
        print(json.dumps({'q':q,'M':M,'perfil':i,'tipos':[''.join(map(str,t)) for t in ps[i]],'sat':r,'t':round(time.time()-t,1)}),flush=True)
main()
