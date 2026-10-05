// SA generico para K_q(n,R)<=M: minimiza pontos descobertos. uso: sa q n R M secs seed [out]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
static int q,n,R; static long N; static long pw[32]; static uint16_t *cnt; static long unc;
static uint64_t s[2];
static inline uint64_t rn(void){uint64_t a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
static inline double ru(void){return (rn()>>11)*(1.0/9007199254740992.0);}
static int dig(long w,int p){return (w/pw[p])%q;}
static void dfs(long w,int p,int r,int sg){ // add sg to all points within r of w using positions >=p
  if(sg>0){ if(cnt[w]++==0) unc--; } else { if(--cnt[w]==0) unc++; }
  if(r==0) return;
  for(int i=p;i<n;i++){ int a=dig(w,i); for(int v=1;v<q;v++){ long w2=w+(long)(((a+v)%q)-a)*pw[i]; dfs(w2,i+1,r-1,sg);} }
}
static void apply(long w,int sg){dfs(w,0,R,sg);}
int main(int c,char**v){
  q=atoi(v[1]);n=atoi(v[2]);R=atoi(v[3]);int M=atoi(v[4]);double secs=atof(v[5]);s[0]=atol(v[6])*2654435761u+1;s[1]=88172645463325252ull;for(int i=0;i<20;i++)rn();
  pw[0]=1;for(int i=1;i<=n;i++)pw[i]=pw[i-1]*q;N=pw[n];cnt=calloc(N,2);unc=N;
  long *W=malloc(M*sizeof(long));
  for(int i=0;i<M;i++){W[i]=rn()%N;apply(W[i],1);}
  double T0=getenv("T0")?atof(getenv("T0")):2.0,T1=getenv("T1")?atof(getenv("T1")):0.4; long best=unc; time_t t0=time(0); long it=0; double T=T0; long bestw[1];
  long *bw=malloc(M*sizeof(long)); memcpy(bw,W,M*sizeof(long));
  while(1){
    it++;
    if((it&1023)==0){ double el=difftime(time(0),t0); if(el>secs)break; double f=fmod(el/ (secs/6.0),1.0); T=T0*pow(T1/T0,f);}
    int i=rn()%M; long old=W[i]; long u0=unc;
    // new word: random neighbour at distance 1..2 of old, or point near a random uncovered point
    long nw=old; int k=1+(rn()%2);
    if(rn()&1){ long x; do{x=rn()%N;}while(cnt[x]&&unc>0&&(it&3)); nw=x; k=1+(rn()%R);} else nw=old;
    for(int j=0;j<k;j++){int p=rn()%n;int a=dig(nw,p);int b=(a+1+rn()%(q-1))%q;nw+=(long)(b-a)*pw[p];}
    apply(old,-1);apply(nw,1);
    long d=unc-u0;
    if(d<=0|| ru()<exp(-d/T)){W[i]=nw; if(unc<best){best=unc;memcpy(bw,W,M*sizeof(long)); if(unc==0)break;}}
    else {apply(nw,-1);apply(old,1);}
  }
  fprintf(stderr,"q%d n%d R%d M%d best_unc=%ld it=%ld\n",q,n,R,M,best,it);
  if(best==0&&c>7){FILE*f=fopen(v[7],"w");for(int i=0;i<M;i++){for(int p=0;p<n;p++)fputc('0'+dig(bw[i],p),f);fputc('\n',f);}fclose(f);}
  printf("%ld\n",best);return best!=0;
}
