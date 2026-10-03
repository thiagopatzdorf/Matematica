#!/usr/bin/env python3
"""Cota inferior RIGOROSA (relaxacao LP simetrizada) para |C1| em qualquer ADS valida com este C2 linear [n2,3]_7.
Argumento: o conjunto de clausulas (x,tau) e invariante por translacao de x em F_7^(n1-1); a media de um C1 viavel sobre as 7^(n1-1)
translacoes e um ponto fracionario viavel y_{c,a}=w_a (independente de c) com o mesmo custo; logo
   |C1| >= 7^(n1-1) * min sum_a w_a   s.t.  para todo tau minimal:  sum_a min(1, V(tau_a-1) w_a) >= 1,   0<=w_a<=1,
onde V(t)=volume da bola de raio t em F_7^(n1-1) (V(-1)=0).  ADS tem 49*|C1| palavras (C2 balanceado).
Uso: ads_lp_bound.py n1 n2 R R2   (varre todos os C2 contendo referencial e todas as colunas de colagem j)"""
import sys,itertools,numpy as np
from math import comb
from scipy.optimize import linprog
sys.argv=['x',sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],'0','0','0','1','1']
n1,n2,R,R2=map(int,sys.argv[1:5])
src=open('ads_exact.py').read().split("print('C2 candidatos")[0]
exec(src)
V=lambda t: 0 if t<0 else sum(comb(m,i)*6**i for i in range(0,min(t,m)+1))
N=q**m
best=None; rows=[]
for ci,cols in enumerate(good):
    for jj in range(n2):
        j=jj; W=words(cols); S2=prof(W); mt=mintaus(S2)
        if any(all(x==0 for x in t) for t in mt): rows.append((ci,jj,None)); continue
        # vars: w_a (7), u_{k,a} (len(mt)*7).  min sum w ; sum_a u_{k,a}>=1 ; u<=V w ; u<=1
        nt=len(mt); nvar=q+nt*q
        c=np.zeros(nvar); c[:q]=1
        A=[];b=[]
        for k,t in enumerate(mt):
            row=np.zeros(nvar); 
            for a in range(q): row[q+k*q+a]=-1
            A.append(row); b.append(-1)
            for a in range(q):
                r=np.zeros(nvar); r[q+k*q+a]=1; r[a]=-V(t[a]-1) if t[a]>=1 else 0
                A.append(r); b.append(0)
        bounds=[(0,1)]*q+[(0,1)]*(nt*q)
        res=linprog(c,A_ub=np.array(A),b_ub=b,bounds=bounds,method='highs')
        lb=N*res.fun
        rows.append((ci,jj,lb))
        if best is None or lb<best[0]: best=(lb,ci,jj)
vals=[r[2] for r in rows if r[2] is not None]
print('n1=%d n2=%d R=%d: pares (C2,j) testados=%d, impossiveis(tau nulo)=%d'%(n1,n2,R,len(rows),sum(1 for r in rows if r[2] is None)))
if vals: print('menor LB LP de |C1| = %.3f -> |C1|>=%d -> |ADS|>=%d  (C2 idx %d, j %d)'%(best[0],int(np.ceil(best[0]-1e-9)),49*int(np.ceil(best[0]-1e-9)),best[1],best[2]))
