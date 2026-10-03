import sys,time
n=6;R=1;N=64
ball=[0]*N
for c in range(N):
    m=1<<c
    for i in range(n): m|=1<<(c^(1<<i))
    ball[c]=m
FULL=(1<<N)-1
cover_by=[[c for c in range(N) if ball[c]>>p&1] for p in range(N)]
sys.setrecursionlimit(10000)
nodes=0
def dfs(cov,left,chosen):
    global nodes; nodes+=1
    if cov==FULL: return list(chosen)
    unc=N-bin(cov).count('1')
    if left==0 or unc>left*7: return None
    # ponto não coberto com menos opções (todas 7) -> primeiro
    p=(~cov & FULL & -(~cov&FULL)).bit_length()-1
    for c in cover_by[p]:
        chosen.append(c); r=dfs(cov|ball[c],left-1,chosen)
        if r: return r
        chosen.pop()
    return None
for k in (11,12):
    t=time.time(); nodes=0
    # simetria: a palavra 0 pode ser fixada (translação) 
    r=dfs(ball[0],k-1,[0]); print('k=',k,'existe' if r else 'NÃO existe', 'nós',nodes,'t=%.1fs'%(time.time()-t), r)
