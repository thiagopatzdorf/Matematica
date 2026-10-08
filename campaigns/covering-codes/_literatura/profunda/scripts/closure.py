import itertools
def closure(q,tab,N,Rmax):
    K=dict(tab)
    def g(n,R):
        if R>=n: return 1
        return K.get((n,R),10**18)
    ch=True
    while ch:
        ch=False
        for n in range(1,N+1):
            for R in range(1,Rmax+1):
                cands=[]
                if n>1: cands.append((q*g(n-1,R),'q*K(n-1,R)'))
                if n>1 and R>1: cands.append((g(n-1,R-1),'K(n-1,R-1)'))
                if R>1: cands.append((g(n,R-1),'K(n,R-1)'))
                for n1 in range(1,n):
                    for R1 in range(0,R+1):
                        if R1==0: continue
                        R2=R-R1
                        if R2<1: continue
                        cands.append((g(n1,R1)*g(n-n1,R2),f'DS({n1},{R1})+({n-n1},{R2})'))
                b=min(cands) if cands else (10**18,'')
                if b[0]<g(n,R):
                    K[(n,R)]=b[0]; ch=True
    return K
K7={}
def put(d,R,vals,n0):
    for i,v in enumerate(vals): d[(n0+i,R)]=v
put(K7,1,[1,7,25,123,769,4435,31045,117649,823543,5764801],1)
put(K7,2,[1,7,19,97,343,2401,15129,94587,420175],2)
put(K7,3,[1,7,17,77,343,2337,8575,42189],3) # n=3..10 -> K7(3,3)=1,(4,3)=7,(5,3)=17,(6,3)=77,(7,3)=343,(8,3)=2337,(9,3)=8575,(10,3)=42189
put(K7,4,[1,7,15,49,343,1843,6517],4)
put(K7,5,[1,7,11,49,323,1225],5)
# base (primitive) tabulated, then closure from only trivial/low values to see what rules alone give vs table
for k in list(K7):
    pass
base=dict(K7)
C=closure(7,base,10,5)
for c in [(8,3),(9,4),(8,4),(9,5)]:
    print('K7',c,'table',base[c],'closure',C[c])
# closure from "primitives" only: remove the f,c,e-derived cells (8,3),(9,4) to see what rules recover
prim=dict(base); del prim[(8,3)]; del prim[(9,4)]
C2=closure(7,prim,10,5)
print('K7 w/o those cells -> (8,3)',C2[(8,3)],'(9,4)',C2[(9,4)])
