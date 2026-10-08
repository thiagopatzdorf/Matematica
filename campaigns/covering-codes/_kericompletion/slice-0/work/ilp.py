import sys,itertools,numpy as np,time
from scipy.optimize import milp,LinearConstraint,Bounds
from scipy.sparse import lil_matrix,csr_matrix
q,n,R,secs=map(int,sys.argv[1:5]); Mmax=int(sys.argv[5]) if len(sys.argv)>5 else None
N=q**n
pts=np.array(list(itertools.product(range(q),repeat=n)))
# ball adjacency: dist<=R
rows=[];cols=[]
for i in range(N):
    d=(pts!=pts[i]).sum(1); nb=np.nonzero(d<=R)[0]
    rows+= [i]*len(nb); cols+=list(nb)
A=csr_matrix((np.ones(len(rows)),(rows,cols)),shape=(N,N))
cons=[LinearConstraint(A,lb=1,ub=np.inf)]
if Mmax: cons.append(LinearConstraint(np.ones((1,N)),lb=0,ub=Mmax))
t=time.time()
r=milp(np.ones(N),constraints=cons,integrality=np.ones(N),bounds=Bounds(0,1),options={"time_limit":secs,"disp":False})
print("status",r.status,r.message,"obj",r.fun,"dual",getattr(r,'mip_dual_bound',None),"time",round(time.time()-t,1))
if r.x is not None:
    sel=np.nonzero(r.x>0.5)[0]; print("M",len(sel))
    open(sys.argv[6] if len(sys.argv)>6 else '/tmp/ilp.txt','w').write("\n".join("".join(map(str,pts[i])) for i in sel)+"\n")
