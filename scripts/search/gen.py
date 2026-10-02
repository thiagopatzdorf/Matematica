# gen.py params.json out.txt : 3 cosets of [9,3] code H=[I6|A] (syndromes 0,s1,s2) + cosets of [9,2] subcode <gens> at reps + single words
import itertools,sys,json
P=json.load(open(sys.argv[1]))
A=[[int(c) for c in r] for r in P["A"].split()]
s1,s2=P["s1"],P["s2"]
gens=[tuple(map(int,g)) for g in P["gens"].split(",")]
def digs(s): return [(s//7**i)%7 for i in range(6)]
C=[tuple([(-sum(A[r][c]*u[c] for c in range(3)))%7 for r in range(6)]+list(u)) for u in itertools.product(range(7),repeat=3)]
out=[]
for r in [tuple([0]*9),tuple(digs(s1)+[0,0,0]),tuple(digs(s2)+[0,0,0])]:
    out+=[''.join(str((r[i]+c[i])%7) for i in range(9)) for c in C]
D=[(0,)*9]
for g in gens:
    old=len(D)
    for c in range(1,7):
        for j in range(old): D.append(tuple((D[j][i]+c*g[i])%7 for i in range(9)))
Cs=set(C); assert all(d in Cs for d in D)
for p in P["reps"]:
    pv=list(map(int,p)); out+=[''.join(str((pv[i]+d[i])%7) for i in range(9)) for d in D]
out+=P["words"]
open(sys.argv[2],"w").write("\n".join(out)+"\n"); print(len(out),len(set(out)))
