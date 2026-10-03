# uso: cd <repo>/data && python3 ../campaigns/covering-codes/_literatura/profunda/scripts/verifica_625.py  (caminhos relativos a data/)
import json,itertools
d=json.load(open('structured/q5_n10_R4_M625.json'))
H=[[int(c) for c in r] for r in d['linear_base']['parity_check']]
G=[[int(c) for c in r] for r in d['linear_base']['generator']]
# check G H^T=0
print(all(sum(g[j]*h[j] for j in range(10))%5==0 for g in G for h in H))
cols=[tuple(H[i][j] for i in range(6)) for j in range(10)]
# covering radius: BFS over syndromes
seen={(0,)*6:0};fr=[(0,)*6]
for r in range(1,8):
    nf=[]
    for s in fr:
        for c in cols:
            for a in range(1,5):
                t=tuple((s[i]+a*c[i])%5 for i in range(6))
                if t not in seen: seen[t]=r;nf.append(t)
    fr=nf
    print(r,len(seen))
    if len(seen)==5**6:break
# words from txt linear?
W=[l.strip() for l in open('codes/q5_n10_R4_M625.txt')]
S=set(W)
ok=all(''.join(str((int(a)+int(b))%5) for a,b in zip(W[i],W[j])) in S for i in range(0,625,7) for j in range(0,625,11))
print(len(S),ok)
# rank of G
import sympy
print(sympy.Matrix(G).rank(iszerofunc=lambda x: x%5==0) )
