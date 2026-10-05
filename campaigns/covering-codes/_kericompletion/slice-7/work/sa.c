/* sa.c: SA de palavras para cobertura q-aria; tenta achar M palavras cobrindo F_q^n com raio R.
   uso: sa q n R M secs seed T out.txt */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>
static int q,n,R; static uint64_t N; static uint64_t pw[32];
static uint16_t *cnt; static uint32_t *upos, *ulist; static uint64_t nunc;
static uint64_t rs=88172645463325252ULL;
static inline uint64_t rnd(void){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return rs;}
static inline double ur(void){return (rnd()>>11)*(1.0/9007199254740992.0);}
static int dig[32];
static int mode; /* 0 count zeros, 1 inc, 2 dec */
static long acc;
static inline void visit(uint64_t p){
  if(mode==0){ if(!cnt[p]) acc++; }
  else if(mode==1){ if(cnt[p]++==0){ /* remove from unc */ uint32_t i=upos[p]; uint32_t last=ulist[--nunc]; ulist[i]=last; upos[last]=i; } }
  else { if(--cnt[p]==0){ upos[p]=nunc; ulist[nunc++]=p; } }
}
static void rec(uint64_t p,int start,int left){
  visit(p);
  if(!left) return;
  for(int i=start;i<n;i++){
    int d=dig[i];
    for(int v=1;v<q;v++){
      int nd=(d+v)%q;
      uint64_t np=p+(uint64_t)((int64_t)(nd-d))*pw[i];
      rec(np,i+1,left-1);
    }
  }
}
static uint64_t enc(int*w){uint64_t p=0;for(int i=0;i<n;i++)p+=w[i]*pw[i];return p;}
static void dec(uint64_t p,int*w){for(int i=0;i<n;i++){w[i]=p%q;p/=q;}}
static void ball(int*w,int m){mode=m;acc=0;memcpy(dig,w,sizeof(int)*n);rec(enc(w),0,R);}
int main(int c,char**v){
  q=atoi(v[1]);n=atoi(v[2]);R=atoi(v[3]);int M=atoi(v[4]);double secs=atof(v[5]);rs^=(uint64_t)atoll(v[6])*0x9E3779B97F4A7C15ULL;double T=atof(v[7]);const char*out=v[8];
  pw[0]=1;for(int i=1;i<=n;i++)pw[i]=pw[i-1]*q;N=pw[n];
  cnt=calloc(N,2);upos=malloc(N*4);ulist=malloc(N*4);
  nunc=N;for(uint64_t i=0;i<N;i++){ulist[i]=i;upos[i]=i;}
  int (*W)[32]=malloc(sizeof(int[32])*M);
  for(int k=0;k<M;k++){for(int i=0;i<n;i++)W[k][i]=rnd()%q;ball(W[k],1);}
  uint64_t best=nunc;time_t t0=time(0);long it=0;int w2[32];
  while(nunc>0){
    if((it&255)==0 && difftime(time(0),t0)>secs)break;
    it++;
    int k=rnd()%M;
    int old[32];memcpy(old,W[k],sizeof old);
    uint64_t before=nunc;
    ball(old,2);
    uint64_t afterrem=nunc;
    /* proposta */
    if(rnd()%4==0){memcpy(w2,old,sizeof w2);int i=rnd()%n;w2[i]=rnd()%q;}
    else{uint64_t u=ulist[rnd()%nunc];dec(u,w2);
      int r=rnd()%(R+1);for(int j=0;j<r;j++){int i=rnd()%n;w2[i]=rnd()%q;}}
    ball(w2,0);long gain=acc;
    long delta=(long)afterrem-gain-(long)before; /* nova uncovered - antiga */
    if(delta<=0||ur()<exp(-delta/T)){memcpy(W[k],w2,sizeof w2);ball(w2,1);}
    else ball(old,1);
    if(nunc<best){best=nunc;fprintf(stderr,"  it=%ld unc=%lu t=%.0fs\n",it,(unsigned long)best,difftime(time(0),t0));}
  }
  printf("RESULT q=%d n=%d R=%d M=%d best_unc=%lu iters=%ld secs=%.0f seed=%s T=%s\n",q,n,R,M,(unsigned long)best,it,difftime(time(0),t0),v[6],v[7]);
  if(nunc==0){FILE*f=fopen(out,"w");for(int k=0;k<M;k++){for(int i=0;i<n;i++)fputc('0'+W[k][i],f);fputc('\n',f);}fclose(f);printf("FOUND %s\n",out);}
  return 0;}
