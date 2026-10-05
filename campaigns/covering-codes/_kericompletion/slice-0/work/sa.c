// SA generico para codigos de cobertura K_q(n,R): M palavras fixas, minimiza pontos descobertos.
// uso: sa q n R M secs seed T0 T1 out.txt
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>
typedef uint64_t u64;
static int q,n,R; static long N; static long pw[32];
static uint16_t *cnt; static long *unc,*pos; static long U;
static u64 s[2];
static inline u64 rnd(void){u64 a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static inline void chg(long p,int d){ // d=+1/-1
  if(d>0){ if(cnt[p]++==0){ long i=pos[p]; long l=unc[--U]; unc[i]=l; pos[l]=i; pos[p]=-1; } }
  else { if(--cnt[p]==0){ pos[p]=U; unc[U++]=p; } }
}
static int dig[32];
static void rec(long idx,int start,int left,int d){
  chg(idx,d);
  if(!left) return;
  for(int i=start;i<n;i++){
    for(int v=0;v<q;v++){ if(v==dig[i]) continue;
      int old=dig[i]; dig[i]=v; rec(idx+(long)(v-old)*pw[i],i+1,left-1,d); dig[i]=old; }
  }
}
static void ball(long c,int d){ long t=c; for(int i=0;i<n;i++){dig[i]=t%q;t/=q;} rec(c,0,R,d); }
static void rec_pick(long idx,int start,int left,long *out,long *k){ out[(*k)++]=idx; if(!left)return;
  for(int i=start;i<n;i++) for(int v=0;v<q;v++){ if(v==dig[i])continue; int old=dig[i]; dig[i]=v; rec_pick(idx+(long)(v-old)*pw[i],i+1,left-1,out,k); dig[i]=old; } }
int main(int ac,char**av){
  q=atoi(av[1]);n=atoi(av[2]);R=atoi(av[3]);int M=atoi(av[4]);double secs=atof(av[5]);u64 seed=atoll(av[6]);
  double T0=atof(av[7]),T1=atof(av[8]);const char*out=av[9];
  s[0]=seed*0x9E3779B97F4A7C15ULL+1;s[1]=seed^0xD1B54A32D192ED03ULL;for(int i=0;i<20;i++)rnd();
  pw[0]=1;for(int i=1;i<=n;i++)pw[i]=pw[i-1]*q;N=pw[n];
  cnt=calloc(N,2);unc=malloc(N*8);pos=malloc(N*8);U=N;for(long i=0;i<N;i++){unc[i]=i;pos[i]=i;}
  long *W=malloc(M*8); for(int i=0;i<M;i++){W[i]=rnd()%N; ball(W[i],1);}
  long Ubest=U; long *buf=malloc(8*(N<4000000?N:4000000)); 
  double t0=clock()/(double)CLOCKS_PER_SEC; long it=0; double T=T0;
  while(U>0){
    if((it&255)==0){ double e=clock()/(double)CLOCKS_PER_SEC-t0; if(e>secs)break; T=T0*pow(T1/T0,e/secs);}
    it++;
    long u=unc[rnd()%U]; int j=rnd()%M; long old=W[j];
    // novo centro: ponto aleatorio na bola de u (mudar ate R digitos)
    long t=u; for(int i=0;i<n;i++){dig[i]=t%q;t/=q;}
    long nw=u; int ch=rnd()%(R+1); // mexe ch digitos
    for(int k=0;k<ch;k++){int i=rnd()%n; int v=rnd()%q; nw+= (long)(v-dig[i])*pw[i]; dig[i]=v;}
    if(nw==old)continue;
    long U0=U; ball(old,-1); ball(nw,1);
    long dU=U-U0;
    if(dU<=0 || (double)(rnd()>>11)/9007199254740992.0 < exp(-dU/T)){ W[j]=nw; if(U<Ubest){Ubest=U;} }
    else { ball(nw,-1); ball(old,1); }
  }
  double e=clock()/(double)CLOCKS_PER_SEC-t0;
  fprintf(stderr,"q=%d n=%d R=%d M=%d seed=%llu iters=%ld best_unc=%ld final_unc=%ld secs=%.1f\n",q,n,R,M,(unsigned long long)seed,it,Ubest,U,e);
  if(U==0){FILE*f=fopen(out,"w");for(int i=0;i<M;i++){long x=W[i];for(int k=0;k<n;k++){fputc('0'+x%q,f);x/=q;}fputc('\n',f);}fclose(f);printf("FOUND\n");}
  else printf("NO best=%ld\n",Ubest);
  return 0;}
