// SA generico para cobertura q-aria: sa q n R M segundos semente saida [T0] [T1]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>
static uint64_t S[2];
static inline uint64_t rn(void){uint64_t s1=S[0],s0=S[1];S[0]=s0;s1^=s1<<23;S[1]=s1^s0^(s1>>18)^(s0>>5);return S[1]+s0;}
static inline double ru(void){return (rn()>>11)*(1.0/9007199254740992.0);}
int q,n,R,M; long N; long pw[32]; uint8_t *cnt; long unc; long *ul,*up; // uncovered list
static inline void addu(long p){up[p]=unc;ul[unc++]=p;}
static inline void delu(long p){long i=up[p];long l=ul[--unc];ul[i]=l;up[l]=i;}
static void ball(long w,int pos,int r,int d){ // d=+1/-1
  // enumerate points: change up to r coords from index pos on
  // iterative recursion
  if(pos==n){ return; }
}
// recursive enumerate
static int D;
static void rec(long cur,int pos,int left){
  // visit cur is done by caller at entry
  for(int i=pos;i<n;i++){
    long dig=(cur/pw[i])%q;
    for(int v=1;v<q;v++){
      long nd=(dig+v)%q; long p=cur+(nd-dig)*pw[i];
      if(D>0){ if(cnt[p]++==0) delu(p);} else { if(--cnt[p]==0) addu(p);}
      if(left>1) rec(p,i+1,left-1);
    }
  }
}
static void apply(long w,int d){D=d; if(d>0){if(cnt[w]++==0)delu(w);}else{if(--cnt[w]==0)addu(w);} rec(w,0,R);}
int main(int argc,char**argv){
  q=atoi(argv[1]);n=atoi(argv[2]);R=atoi(argv[3]);M=atoi(argv[4]);double secs=atof(argv[5]);
  uint64_t seed=atoll(argv[6]);const char*out=argv[7];
  double T0=argc>8?atof(argv[8]):0.6,T1=argc>9?atof(argv[9]):0.12;
  S[0]=seed*0x9E3779B97F4A7C15ULL+1;S[1]=seed^0xD1B54A32D192ED03ULL;for(int i=0;i<20;i++)rn();
  pw[0]=1;for(int i=1;i<=n;i++)pw[i]=pw[i-1]*q;N=pw[n];
  cnt=calloc(N,1);ul=malloc(N*8);up=malloc(N*8);unc=0;for(long p=0;p<N;p++)addu(p);
  long *W=malloc(M*8);
  for(int i=0;i<M;i++){W[i]=rn()%N;apply(W[i],1);}
  long best=unc;time_t t0=time(0);double el=0;long it=0;
  while(1){
    if((it&255)==0){el=difftime(time(0),t0);if(el>secs)break;}
    it++;
    if(unc==0)break;
    double T=T0*pow(T1/T0,el/secs);
    int c=rn()%M;long w=W[c];
    // guided: with prob 1/2 move toward a random uncovered point by copying one coord
    int i=rn()%n;long dig=(w/pw[i])%q;long nd;
    if(rn()&1){long u=ul[rn()%unc];nd=(u/pw[i])%q;if(nd==dig)nd=(dig+1+rn()%(q-1))%q;}
    else nd=(dig+1+rn()%(q-1))%q;
    long w2=w+(nd-dig)*pw[i];
    long before=unc;
    apply(w,-1);apply(w2,1);
    long delta=unc-before;
    if(delta<=0||ru()<exp(-delta/T)){W[c]=w2;if(unc<best)best=unc;}
    else{apply(w2,-1);apply(w,1);}
  }
  fprintf(stderr,"q=%d n=%d R=%d M=%d seed=%llu iters=%ld best_unc=%ld final_unc=%ld t=%.0fs\n",q,n,R,M,(unsigned long long)seed,it,best,unc,difftime(time(0),t0));
  if(unc==0){FILE*f=fopen(out,"w");for(int j=0;j<M;j++){long w=W[j];for(int i=0;i<n;i++)fputc('0'+(w/pw[i])%q,f);fputc('\n',f);}fclose(f);printf("FOUND\n");}
  return unc==0?0:1;
}
