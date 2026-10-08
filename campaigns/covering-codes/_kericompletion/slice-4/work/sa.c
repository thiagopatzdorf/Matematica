// SA generico para K_q(n,R)<=M: minimiza pontos descobertos com M palavras. uso: sa q n R M secs seed out
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>
static int q,n,R; static long N; static long pw[32]; static int *cnt; static long unc;
static long delta[32][16][16];
static uint64_t s[2]; static inline uint64_t rn(void){uint64_t a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static inline double ur(void){return (rn()>>11)*(1.0/9007199254740992.0);}
static int dg[32];
static void ball(long idx,int start,int rem,int d){
  if(d>0){ if(d==1){ if(cnt[idx]++==0) unc--; } else { if(cnt[idx]--==1) unc++; } } // placeholder replaced below
}
static int mode; // +1 add, -1 remove
static void rec(long idx,int start,int rem){
  if(mode>0){ if(cnt[idx]++==0) unc--; } else { if(--cnt[idx]==0) unc++; }
  if(rem==0) return;
  for(int p=start;p<n;p++){ int a=(idx/pw[p])%q; for(int v=1;v<q;v++) rec(idx+delta[p][a][v],p+1,rem-1); }
}
int main(int argc,char**argv){
  q=atoi(argv[1]);n=atoi(argv[2]);R=atoi(argv[3]);int M=atoi(argv[4]);double secs=atof(argv[5]);s[0]=atol(argv[6])*2654435761u+1;s[1]=88172645463325252ULL;for(int i=0;i<20;i++)rn();
  pw[0]=1;for(int i=1;i<=n;i++)pw[i]=pw[i-1]*q;N=pw[n];
  for(int p=0;p<n;p++)for(int a=0;a<q;a++)for(int v=0;v<q;v++)delta[p][a][v]=(long)(((a+v)%q)-a)*pw[p];
  cnt=calloc(N,sizeof(int)); unc=N;
  long *C=malloc(M*sizeof(long));
  for(int i=0;i<M;i++){C[i]=rn()%N;mode=1;rec(C[i],0,R);}
  long best=unc; double T0=0.6,T1=0.08; time_t t0=time(0); long it=0; double T=T0;
  long *bestC=malloc(M*sizeof(long)); memcpy(bestC,C,M*sizeof(long));
  while(unc>0){
    if((it&255)==0){ double el=difftime(time(0),t0); if(el>secs)break; double f=fmod(el/ (secs/8.0),1.0); T=T0*pow(T1/T0,f);}
    it++;
    int i=rn()%M; long c=C[i]; int p=rn()%n; int a=(c/pw[p])%q; int v=1+rn()%(q-1); long c2=c+delta[p][a][v];
    long u0=unc; mode=-1; rec(c,0,R); mode=1; rec(c2,0,R);
    long d=unc-u0;
    if(d<=0 || ur()<exp(-d/T)){ C[i]=c2; if(unc<best){best=unc;memcpy(bestC,C,M*sizeof(long));} }
    else { mode=-1; rec(c2,0,R); mode=1; rec(c,0,R); }
  }
  fprintf(stderr,"q=%d n=%d R=%d M=%d best_unc=%ld iters=%ld secs=%.0f\n",q,n,R,M,unc==0?0:best,it,difftime(time(0),t0));
  if(unc==0){ FILE*f=fopen(argv[7],"w"); for(int i=0;i<M;i++){ long w=C[i]; for(int k=0;k<n;k++){fputc('0'+(w%q),f);w/=q;} fputc('\n',f);} fclose(f); printf("FOUND\n"); return 0;}
  printf("BEST %ld\n",best); return 1;
}
