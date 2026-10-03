import itertools
def closure(q,base,N,Rmax):
    K=dict(base)
    for n in range(1,N+1):
        K[(n,n)]=1
        K[(n,n-1)]=min(K.get((n,n-1),9**9), q) if n>1 else q
    K[(1,0)]=q; K[(2,1)]=min(K.get((2,1),99),q)
    why={k:'tabela(base)' for k in K}
    ch=True
    while ch:
        ch=False
        def upd(key,v,w):
            nonlocal ch
            if key[0]<=N and key[1]<=key[0] and v<K.get(key,9**9):
                K[key]=v;why[key]=w;ch=True
        for (n,R),v in list(K.items()):
            upd((n,R+1),v,f'K({n},{R+1})<=K({n},{R})={v}')
            upd((n+1,R),q*v,f'K({n+1},{R})<=q*K({n},{R})={q}*{v}')
            upd((n+1,R+1),v,f'K({n+1},{R+1})<=K({n},{R})={v}')
        for (a,x),(b,y) in itertools.product(list(K.items()),repeat=2):
            (n1,R1),v1=a,x; (n2,R2),v2=b,y
            upd((n1+n2,R1+R2),v1*v2,f'K({n1+n2},{R1+R2})<=K({n1},{R1})K({n2},{R2})={v1}*{v2}')
    return K,why
K5={(3,1):13,(4,2):11,(5,2):35,(5,3):9,(6,1):625,(6,2):125,(6,3):25,(7,1):3125,(7,2):525,(7,3):100,(7,4):21,
(8,1):15625,(8,2):1625,(8,3):325,(8,4):65,(8,5):15,(9,1):78125,(9,2):6375,(9,3):1275,(9,4):255,(9,5):55,(9,6):12,
(5,1):184,(4,1):51,(6,4):5}
K4={(3,1):8,(4,1):24,(4,2):7,(5,1):64,(5,2):16,(5,3):4,(6,1):256,(6,2):52,(6,3):14,(7,1):992,(7,2):128,(7,3):32,(7,4):10,
(8,1):3456,(8,2):352,(8,3):96,(8,4):28,(9,1):12288,(9,2):1024,(9,3):256,(9,4):64,(9,5):16,(10,1):49152,(10,2):4096,(10,3):832,(10,4):208,(10,5):54}
for q,K0,cases,N in [(5,K5,[((7,2),500),((9,3),1250),((9,5),50),((9,4),250)],10),(4,K4,[((10,4),192)],11)]:
    # target excluded from base to see derivation without itself
    for t,ours in cases:
        b={k:v for k,v in K0.items() if k!=t}
        K,why=closure(q,b,N,10)
        print(q,t,'ours',ours,'derivado sem a própria célula:',K.get(t),why.get(t))

print('--- ADS otimista (valida só p/ códigos normais; usamos como ENVELOPE) ---')
def ads(q,K,t):
    n,R=t; best=[]
    for (n1,R1),v1 in K.items():
        for (n2,R2),v2 in K.items():
            if n1+n2-1==n and R1+R2==R: best.append((v1*v2/q,(n1,R1,v1),(n2,R2,v2)))
    return sorted(best)[:3]
Kc={}
for q,K0,cases,N in [(5,K5,[(7,2),(9,3),(9,5),(9,4)],10),(4,K4,[(10,4)],11)]:
    b0=dict(K0)
    # base completada com somas diretas/propagação de tudo salvo a própria célula
    for t in cases:
        b={k:v for k,v in b0.items() if k!=t}
        K,_=closure(q,b,N,10)
        K={k:v for k,v in K.items() if k!=t}
        print(q,t,ads(q,K,t))
