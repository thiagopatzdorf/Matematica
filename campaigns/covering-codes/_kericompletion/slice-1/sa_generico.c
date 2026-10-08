// SA generico de cobertura: sa q n R M secs seed T0 T1 saida
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>
static uint64_t s[2];
static inline uint64_t rn(void){uint64_t a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static inline double ur(void){return (rn()>>11)*(1.0/9007199254740992.0);}
int q,n,R; long N; long pw[32];
int *offp,*offd; int *offlen,B; // offsets
uint16_t *cnt; long *unc,*upos; long nunc;
static void gen(int *pos,int *del,int k,int start,int rem){
  // recursive enumeration of weight<=R vectors, stored
}
int cap=0; int *op,*od,*ol;
static void addoff(int *p,int *d,int k){
  op=realloc(op,sizeof(int)*(size_t)(B+1)*R); od=realloc(od,sizeof(int)*(size_t)(B+1)*R); ol=realloc(ol,sizeof(int)*(B+1));
  for(int i=0;i<k;i++){op[B*R+i]=p[i];od[B*R+i]=d[i];} ol[B]=k;B++;
}
static void rec(int *p,int *d,int k,int start){
  addoff(p,d,k);
  if(k==R) return;
  for(int i=start;i<n;i++) for(int x=1;x<q;x++){p[k]=i;d[k]=x;rec(p,d,k+1,i+1);}
}
static inline void dig(long w,int *dd){for(int i=0;i<n;i++){dd[i]=w%q;w/=q;}}
static void apply(long w,int sgn){
  int dd[32]; dig(w,dd);
  for(int b=0;b<B;b++){
    long idx=w; int k=ol[b];
    for(int i=0;i<k;i++){int p=op[b*R+i];int nd=(dd[p]+od[b*R+i])%q; idx+=(long)(nd-dd[p])*pw[p];}
    if(sgn>0){ if(cnt[idx]++==0){ long ps=upos[idx]; long last=unc[--nunc]; unc[ps]=last; upos[last]=ps; } }
    else { if(--cnt[idx]==0){ unc[nunc]=idx; upos[idx]=nunc++; } }
  }
}
static long ball_pt(long u,int b){ // point at offset b from u
  int dd[32]; dig(u,dd); long idx=u; int k=ol[b];
  for(int i=0;i<k;i++){int p=op[b*R+i];int nd=(dd[p]+od[b*R+i])%q; idx+=(long)(nd-dd[p])*pw[p];}
  return idx;
}
int main(int c,char**v){
  q=atoi(v[1]);n=atoi(v[2]);R=atoi(v[3]);int M=atoi(v[4]);double secs=atof(v[5]);uint64_t seed=atoll(v[6]);
  double T0=atof(v[7]),T1=atof(v[8]);const char*out=v[9];
  s[0]=seed*0x9E3779B97F4A7C15ULL+1;s[1]=seed^0xD1B54A32D192ED03ULL;for(int i=0;i<20;i++)rn();
  pw[0]=1;for(int i=1;i<=n;i++)pw[i]=pw[i-1]*q;N=pw[n];
  int p[32],d[32];rec(p,d,0,0);
  cnt=calloc(N,2);unc=malloc(N*8);upos=malloc(N*8);
  for(long i=0;i<N;i++){unc[i]=i;upos[i]=i;}nunc=N;
  long *W=malloc(M*8);
  for(int i=0;i<M;i++){ // init: greedy-ish random: word in ball of random uncovered
    long u=unc[rn()%nunc]; W[i]=ball_pt(u,rn()%B); apply(W[i],1);}
  fprintf(stderr,"N=%ld B=%d M=%d init unc=%ld\n",N,B,M,nunc);
  struct timespec t0,t1;clock_gettime(CLOCK_MONOTONIC,&t0);
  long best=nunc,it=0;double T=T0;
  long *bestW=malloc(M*8);memcpy(bestW,W,M*8);
  while(1){
    if((it&255)==0){clock_gettime(CLOCK_MONOTONIC,&t1);double e=(t1.tv_sec-t0.tv_sec)+(t1.tv_nsec-t0.tv_nsec)*1e-9;
      if(e>secs)break; T=T0*pow(T1/T0,e/secs);
      if((it&((1<<20)-1))==0)fprintf(stderr,"%.0fs it=%ld unc=%ld best=%ld T=%.3f\n",e,it,nunc,best,T);}
    it++;
    if(nunc==0)break;
    long before=nunc;
    int j=rn()%M; long old=W[j];
    long u=unc[rn()%nunc]; long nw=ball_pt(u,rn()%B);
    apply(old,-1);apply(nw,1);
    long dlt=nunc-before;
    if(dlt<=0||ur()<exp(-dlt/T)){W[j]=nw;if(nunc<best){best=nunc;memcpy(bestW,W,M*8);}}
    else{apply(nw,-1);apply(old,1);}
  }
  fprintf(stderr,"final best=%ld it=%ld\n",best,it);
  printf("%ld\n",best);
  if(best==0){ FILE*f=fopen(out,"w"); long *src=(nunc==0)?W:bestW; for(int i=0;i<M;i++){long w=src[i];for(int k=0;k<n;k++){fputc('0'+w%q,f);w/=q;}fputc('\n',f);}fclose(f);}
  return best!=0;
}
