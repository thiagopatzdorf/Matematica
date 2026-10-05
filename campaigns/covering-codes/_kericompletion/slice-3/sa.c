// SA generico para cobertura q-aria: sa q n R M secs seed T0 out
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <stdint.h>
static int q,n,R; static long N; static long pw[32];
static int *cnt; static long *unc,*pos; static long nunc;
static uint64_t s[2];
static inline uint64_t rn(void){uint64_t s1=s[0],s0=s[1];s[0]=s0;s1^=s1<<23;s[1]=s1^s0^(s1>>18)^(s0>>5);return s[1]+s0;}
static inline double ur(void){return (rn()>>11)*(1.0/9007199254740992.0);}
static void add1(long x){ if(cnt[x]++==0){ pos[x]=-1; long k=pos[x]; (void)k;} }
static void upd(long x,int d){
  if(d>0){ if(cnt[x]==0){ long p=pos[x]; long y=unc[--nunc]; unc[p]=y; pos[y]=p; } cnt[x]++; }
  else { if(--cnt[x]==0){ pos[x]=nunc; unc[nunc++]=x; } }
}
static void ballrec(long idx,int *dg,int i,int r,int d){
  if(i==n){ upd(idx,d); return; }
  ballrec(idx,dg,i+1,r,d);
  if(r>0) for(int v=0;v<q;v++) if(v!=dg[i]) ballrec(idx+(long)(v-dg[i])*pw[i],dg,i+1,r-1,d);
}
static void ball(int *dg,int d){ long idx=0; for(int i=0;i<n;i++) idx+=dg[i]*pw[i]; ballrec(idx,dg,0,R,d); }
int main(int argc,char**argv){
  q=atoi(argv[1]);n=atoi(argv[2]);R=atoi(argv[3]);int M=atoi(argv[4]);double secs=atof(argv[5]);
  uint64_t seed=atoll(argv[6]);double T0=atof(argv[7]);const char*out=argv[8];
  s[0]=seed*0x9E3779B97F4A7C15ULL+1;s[1]=seed^0xD1B54A32D192ED03ULL;for(int i=0;i<20;i++)rn();
  pw[0]=1;for(int i=1;i<=n;i++)pw[i]=pw[i-1]*q;N=pw[n];
  cnt=calloc(N,4);unc=malloc(N*8);pos=malloc(N*8);
  nunc=N;for(long x=0;x<N;x++){unc[x]=x;pos[x]=x;}
  int (*w)[24]=calloc(M,sizeof(int[24]));
  for(int j=0;j<M;j++){for(int i=0;i<n;i++)w[j][i]=rn()%q;ball(w[j],1);}
  long best=nunc; double t0=clock(),T=T0; long it=0; int last_ok=0;
  while(1){
    if((it&1023)==0){ double el=(clock()-t0)/CLOCKS_PER_SEC; if(el>secs)break; T=T0*(1.0-el/secs)+0.02; }
    it++;
    if(nunc==0){last_ok=1;break;}
    int j=rn()%M; int old[24]; memcpy(old,w[j],sizeof(old)); int i; int v;
    if(ur()<0.7){ long x=unc[rn()%nunc]; // coordenada que difere de x, no codeword j
      int cand[24],nc=0; long y=x; int xd[24]; for(int k=0;k<n;k++){xd[k]=y%q;y/=q;}
      for(int k=0;k<n;k++) if(xd[k]!=old[k]) cand[nc++]=k;
      i=cand[rn()%nc]; v=xd[i]; }
    else { i=rn()%n; v=(old[i]+1+rn()%(q-1))%q; }
    long before=nunc; ball(old,-1); w[j][i]=v; ball(w[j],1);
    long d=nunc-before;
    if(d<=0||ur()<exp(-d/T)){ if(nunc<best){best=nunc;} }
    else { ball(w[j],-1); w[j][i]=old[i]; ball(old,1); }
  }
  fprintf(stderr,"q%d n%d R%d M%d it=%ld best_unc=%ld final_unc=%ld\n",q,n,R,M,it,best,nunc);
  if(nunc==0){ FILE*f=fopen(out,"w"); for(int j=0;j<M;j++){for(int i=0;i<n;i++)fputc('0'+w[j][i],f);fputc('\n',f);} fclose(f); printf("FOUND\n"); return 0;}
  return 1;
}
