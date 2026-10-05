// SA generico para cobertura K_q(n,R) com M palavras: minimiza pontos descobertos.
// uso: sa q n R M secs seed T0 T1 saida
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>
static int q,n,R; static long N; static long pw[32];
static uint16_t *cnt; static long *ulist,*upos; static long nu;
static uint64_t s[2];
static inline uint64_t rnd(void){uint64_t a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static inline double ur(void){return (rnd()>>11)*(1.0/9007199254740992.0);}
static void uadd(long i){upos[i]=nu;ulist[nu++]=i;}
static void udel(long i){long p=upos[i];long l=ulist[--nu];ulist[p]=l;upos[l]=p;upos[i]=-1;}
static int dg[32];
static void ball(long c,int sign){
  // enumera bola R de c: DFS sobre posicoes
  int d[32];long t=c;for(int i=0;i<n;i++){d[i]=t%q;t/=q;}
  // iterativo via recursao
  void rec(int start,int left,long idx){
    // ponto idx pertence a bola
    if(sign>0){ if(cnt[idx]++==0) udel(idx);} else { if(--cnt[idx]==0) uadd(idx);}
    if(!left)return;
    for(int i=start;i<n;i++) for(int v=1;v<q;v++){
      int nd=(d[i]+v)%q; rec(i+1,left-1,idx+(long)(nd-d[i])*pw[i]);
    }
  }
  rec(0,R,c);
}
int main(int ac,char**av){
  q=atoi(av[1]);n=atoi(av[2]);R=atoi(av[3]);int M=atoi(av[4]);double secs=atof(av[5]);
  uint64_t seed=atoll(av[6]);double T0=atof(av[7]),T1=atof(av[8]);const char*out=av[9];
  s[0]=seed*0x9E3779B97F4A7C15ULL+1;s[1]=seed^0xD1B54A32D192ED03ULL;for(int i=0;i<20;i++)rnd();
  pw[0]=1;for(int i=1;i<=n;i++)pw[i]=pw[i-1]*q;N=pw[n];
  cnt=calloc(N,2);ulist=malloc(N*8);upos=malloc(N*8);nu=0;for(long i=0;i<N;i++)uadd(i);
  long *w=malloc(M*8);
  for(int i=0;i<M;i++){ if(nu>0) w[i]=ulist[rnd()%nu]; else w[i]=rnd()%N; ball(w[i],1);}
  long best=nu;fprintf(stderr,"init unc=%ld\n",nu);
  struct timespec ts0;clock_gettime(CLOCK_MONOTONIC,&ts0);long it=0;double T=T0;long bestsnap_ok=0;
  while(1){
    if((it&1023)==0){struct timespec ts;clock_gettime(CLOCK_MONOTONIC,&ts);double el=(ts.tv_sec-ts0.tv_sec)+(ts.tv_nsec-ts0.tv_nsec)*1e-9;if(el>secs)break;double f=el/secs;T=T0*pow(T1/T0,f);}
    it++;
    if(nu==0)break;
    long u=ulist[rnd()%nu];int k=rnd()%M;long old=w[k];
    // novo ponto: aleatorio na bola de u (j mudancas, j<=R)
    int d[32];long t=u;for(int i=0;i<n;i++){d[i]=t%q;t/=q;}
    int j=rnd()%(R+1);long np=u;
    for(int a=0;a<j;a++){int p=rnd()%n;int v=1+rnd()%(q-1);int nd=(d[p]+v)%q;np+=(long)(nd-d[p])*pw[p];d[p]=nd;}
    if(np==old)continue;
    long before=nu;ball(old,-1);ball(np,1);
    long delta=nu-before;
    if(delta<=0||ur()<exp(-delta/T)){w[k]=np;if(nu<best){best=nu;}}
    else{ball(np,-1);ball(old,1);}
  }
  fprintf(stderr,"fim it=%ld unc=%ld best=%ld\n",it,nu,best);
  printf("%ld %ld\n",nu,best);
  if(nu==0){FILE*f=fopen(out,"w");for(int i=0;i<M;i++){long x=w[i];for(int p=0;p<n;p++){fputc('0'+x%q,f);x/=q;}fputc('\n',f);}fclose(f);}
  return 0;}
