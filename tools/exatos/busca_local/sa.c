// Busca local (recozimento simulado) por código de cobertura em Z_q^n, raio R, M palavras.
// Ponto coberto <=> concorda com alguma palavra em >= n-R coordenadas. Custo = pontos
// descobertos; lance = trocar um símbolo de uma palavra. O delta de um lance só olha os 2·q^(n-1)
// pontos cujo símbolo naquela coordenada é o antigo ou o novo, por isso cada lance é barato.
// Existência só: saída vazia não prova nada; o código impresso tem de passar no tools/verify/verify.
//
// Uso:  cc -O3 -o sa tools/exatos/busca_local/sa.c -lm && ./sa <M> <seed> [T0] [iters]
//       (Q, N, R, NP=Q^N mudam por -DQ=.. -DN=.. -DR=.. -DNP=..; padrão K_7(5,3))
// K_7(5,3) <= 17: ./sa 17 12 1.5 acha data/codes/q7_n5_R3_M17.txt (depois de sort) em ~14 s.
// Determinístico dado (M, seed, T0): xorshift64 próprio, sem relógio quando a seed é dada.
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <time.h>
#ifndef Q
#define Q 7
#endif
#ifndef N
#define N 5
#endif
#ifndef R
#define R 3
#endif
#ifndef NP
#define NP 16807 /* Q^N */
#endif
static int M;
static unsigned char pt[NP][N];
static unsigned char cw[64][N];
static unsigned char agr[64][NP];
static int cov[NP];
static unsigned long long rs;
static inline unsigned long long rnd(void){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return rs;}
int main(int argc,char**argv){
  M=atoi(argv[1]); rs=argc>2?strtoull(argv[2],0,10):time(0); double T0=argc>3?atof(argv[3]):2.0;
  long long iters=argc>4?atoll(argv[4]):2000000000LL;
  int need=N-R;
  for(int p=0;p<NP;p++){int v=p;for(int i=0;i<N;i++){pt[p][i]=v%Q;v/=Q;}}
  for(;;){
  for(int w=0;w<M;w++)for(int i=0;i<N;i++)cw[w][i]=rnd()%Q;
  memset(cov,0,sizeof cov);
  int unc=0;
  for(int w=0;w<M;w++)for(int p=0;p<NP;p++){int a=0;for(int i=0;i<N;i++)a+=pt[p][i]==cw[w][i];agr[w][p]=a;if(a>=need)cov[p]++;}
  for(int p=0;p<NP;p++)unc+=cov[p]==0;
  int best=unc; double T=T0;
  for(long long it=0;it<iters;it++){
    int w=rnd()%M,i=rnd()%N,a=cw[w][i],b=rnd()%(Q-1); if(b>=a)b++;
    // delta: pontos com x_i==a perdem 1 de agr; x_i==b ganham 1
    int d=0;
    for(int p=0;p<NP;p++){unsigned char x=pt[p][i]; if(x==a){ if(agr[w][p]==need && cov[p]==1) d++; } else if(x==b){ if(agr[w][p]==need-1 && cov[p]==0) d--; } }
    if(d<=0 || (double)(rnd()%1000000)/1e6 < exp(-d/T)){
      cw[w][i]=b;
      for(int p=0;p<NP;p++){unsigned char x=pt[p][i];
        if(x==a){ if(agr[w][p]==need){cov[p]--; if(cov[p]==0)unc++;} agr[w][p]--; }
        else if(x==b){ agr[w][p]++; if(agr[w][p]==need){ if(cov[p]==0)unc--; cov[p]++;} } }
      if(unc<best){best=unc; fprintf(stderr,"it %lld unc %d T %.3f\n",it,unc,T);}
      if(unc==0){ for(int w2=0;w2<M;w2++){for(int k=0;k<N;k++)printf("%d",cw[w2][k]);printf("\n");} return 0; }
    }
    if((it&0xfff)==0){T*=0.9995; if(T<0.05)T=T0;}
  }
  }
}
