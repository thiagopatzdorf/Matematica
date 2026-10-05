// SA direto de codigo de cobertura: q n R M secs seed T0 T1 saida
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>
static int q,n,R; static long N; static long pw[32];
static uint16_t *cov; static int *unc,*upos; static long U;
static uint64_t s[2];
static inline uint64_t rn(void){uint64_t a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static inline double ur(void){return (rn()>>11)*(1.0/9007199254740992.0);}
static int dig[32];
// implementacao iterativa simples: gera ball em lista
static long *tmp; static long tn;
static void gen(long idx,int start,int left,int *d){
  tmp[tn++]=idx;
  if(!left) return;
  for(int p=start;p<n;p++) for(int e=1;e<q;e++){
    int nd=(d[p]+e)%q; long ni=idx+(long)(nd-d[p])*pw[p];
    int old=d[p]; d[p]=nd; gen(ni,p+1,left-1,d); d[p]=old;
  }
}
static void decode(long w,int*d){for(int i=0;i<n;i++){d[i]=w%q;w/=q;}}
static void add(long w){ int d[32]; decode(w,d); tn=0; gen(w,0,R,d);
  for(long i=0;i<tn;i++){long x=tmp[i]; if(cov[x]++==0){ // sai da lista de descobertos
      int p=upos[x]; long last=unc[--U]; unc[p]=last; upos[last]=p; upos[x]=-1; } } }
static void rem(long w){ int d[32]; decode(w,d); tn=0; gen(w,0,R,d);
  for(long i=0;i<tn;i++){long x=tmp[i]; if(--cov[x]==0){ unc[U]=x; upos[x]=U; U++; } } }
int main(int c,char**v){
  q=atoi(v[1]);n=atoi(v[2]);R=atoi(v[3]);int M=atoi(v[4]);double secs=atof(v[5]);
  s[0]=atol(v[6])*2654435761u+88172645463325252ull; s[1]=s[0]^0x9E3779B97F4A7C15ull; for(int i=0;i<20;i++)rn();
  double T0=atof(v[7]),T1=atof(v[8]); const char*out=v[9];
  N=1;for(int i=0;i<n;i++){pw[i]=N;N*=q;}
  cov=calloc(N,2);unc=malloc(N*sizeof(int));upos=malloc(N*sizeof(int));
  long B=0; {tmp=malloc(sizeof(long)*4000000); int d[32]={0}; tn=0; gen(0,0,R,d); B=tn;}
  U=N; for(long i=0;i<N;i++){unc[i]=i;upos[i]=i;}
  long *W=malloc(M*sizeof(long)); for(int i=0;i<M;i++){W[i]=rn()%N; add(W[i]);}
  fprintf(stderr,"N=%ld B=%ld M=%d U0=%ld\n",N,B,M,U);
  time_t t0=time(0); long it=0; long best=U; double T=T0;
  double span=secs;
  while(1){
    if((it&1023)==0){ double el=difftime(time(0),t0); if(el>=secs)break; double f=el/span; T=T0*pow(T1/T0,f);
       if((it&((1<<22)-1))==0) fprintf(stderr,"t=%.0f U=%ld best=%ld T=%.3f\n",el,U,best,T);}
    it++;
    if(U==0) break;
    int i=rn()%M; long ow=W[i];
    long p=unc[rn()%U]; int d[32]; decode(p,d);
    // novo ponto: p com ate R coordenadas mudadas ao acaso
    if(rn()&1){ decode(ow,d); int pos=rn()%n; d[pos]=(d[pos]+1+rn()%(q-1))%q; }
    else { int k=rn()%(R+1); for(int j=0;j<k;j++){int pos=rn()%n; d[pos]=rn()%q;} }
    long nw=0; for(int j=0;j<n;j++) nw+=d[j]*pw[j];
    if(nw==ow) continue;
    long U0=U; rem(ow); add(nw);
    long dU=U-U0;
    if(dU<=0 || ur()<exp(-dU/T)){ W[i]=nw; if(U<best){best=U;} }
    else { rem(nw); add(ow); }
  }
  fprintf(stderr,"fim U=%ld best=%ld it=%ld t=%.0f\n",U,best,it,difftime(time(0),t0));
  if(U==0){ FILE*f=fopen(out,"w"); for(int i=0;i<M;i++){long w=W[i];for(int j=0;j<n;j++){fputc('0'+w%q,f);w/=q;}fputc('\n',f);} fclose(f); printf("FOUND M=%d\n",M); return 0;}
  printf("NOTFOUND M=%d bestU=%ld\n",M,best); return 1;
}
