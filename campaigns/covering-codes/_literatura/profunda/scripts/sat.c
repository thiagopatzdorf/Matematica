// own code: search for n columns in F_5^r giving covering radius <= R (linear [n,n-r]_5 R code)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#define Q 5
int r,R,n; int Qr;
int pw[10];
static inline int addv(int a,int b){ // vector add in base 5 digits
  int res=0; for(int i=0;i<r;i++){ int da=(a/pw[i])%Q, db=(b/pw[i])%Q; res+=((da+db)%Q)*pw[i]; } return res; }
int mulv(int a,int c){ int res=0; for(int i=0;i<r;i++){ int da=(a/pw[i])%Q; res+=((da*c)%Q)*pw[i]; } return res; }
int *addtab; // too big (15625^2)? use digit-add via arrays
int D[15625][6];
unsigned long long rs=88172645463325252ULL;
static inline unsigned long long rnd(){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
int cols[16]; unsigned char cov[15625];
int mult[Q][15625];
int add2(int a,int b){ int res=0; for(int i=0;i<r;i++){ res+=((D[a][i]+D[b][i])%Q)*pw[i]; } return res; }
int evalcost(){
  // layered BFS over syndromes: reach set after j steps
  static int cur[15625], nxt[15625]; static unsigned char seen[15625];
  memset(seen,0,Qr); int nc=1; cur[0]=0; seen[0]=1; int tot=1;
  for(int step=0;step<R;step++){
    int nn=0;
    for(int i=0;i<nc;i++){ int s=cur[i];
      for(int j=0;j<n;j++) for(int a=1;a<Q;a++){ int t=add2(s,mult[a][cols[j]]); if(!seen[t]){seen[t]=1;nxt[nn++]=t;tot++;} } }
    memcpy(cur,nxt,nn*sizeof(int)); nc=nn;
    if(tot==Qr) break;
  }
  return Qr-tot;
}
int main(int argc,char**argv){
  n=atoi(argv[1]); r=atoi(argv[2]); R=atoi(argv[3]); long iters=atol(argv[4]); rs^=atol(argv[5])*2654435761ULL; for(int i=0;i<20;i++)rnd();
  pw[0]=1; for(int i=1;i<10;i++)pw[i]=pw[i-1]*Q; Qr=pw[r];
  for(int s=0;s<Qr;s++) for(int i=0;i<r;i++) D[s][i]=(s/pw[i])%Q;
  for(int a=0;a<Q;a++) for(int s=0;s<Qr;s++) mult[a][s]=mulv(s,a);
  for(int rest=0;rest<1000;rest++){
    for(int j=0;j<n;j++) cols[j]=1+rnd()%(Qr-1);
    int c=evalcost(); int best=c;
    for(long it=0;it<iters && c>0;it++){
      int j=rnd()%n, old=cols[j]; cols[j]=1+rnd()%(Qr-1);
      int c2=evalcost();
      double T=0.3*(1.0-(double)it/iters)+0.02;
      if(c2<=c || (double)(rnd()%1000000)/1e6 < exp((c-c2)/(T*(c>200?c/20.0:10))) ){ c=c2; if(c<best)best=c; } else cols[j]=old;
    }
    printf("restart %d best %d final %d\n",rest,best,c); fflush(stdout);
    if(c==0){ printf("FOUND n=%d r=%d R=%d cols:",n,r,R); for(int j=0;j<n;j++){ printf(" "); for(int i=r-1;i>=0;i--)printf("%d",D[cols[j]][i]); } printf("\n"); return 0; }
  }
}
