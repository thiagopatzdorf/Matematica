// SA para código de cobertura (q,n,R,M) com a 1a coordenada fixada por classe (balanceada).
// Uso: sa q n R M seed maxiter  -> imprime palavras (dígitos) se cobrir.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
static int q,n,R,M; static int *cnt; static int N;
static unsigned long long s[2];
static inline unsigned long long rnd(){unsigned long long s1=s[0],s0=s[1];s[0]=s0;s1^=s1<<23;s[1]=s1^s0^(s1>>18)^(s0>>5);return s[1]+s0;}
static double urand(){return (rnd()>>11)*(1.0/9007199254740992.0);}
static int pw[16];
static int *ballbuf; static int ballsz;
static void ball(int w,int pos,int left,int *out,int *k){
  if(pos==n){out[(*k)++]=w;return;}
  ball(w,pos+1,left,out,k);
  if(left>0){int d=(w/pw[pos])%q; for(int a=0;a<q;a++) if(a!=d) ball(w+(a-d)*pw[pos],pos+1,left-1,out,k);}
}
int main(int argc,char**argv){
  q=atoi(argv[1]);n=atoi(argv[2]);R=atoi(argv[3]);M=atoi(argv[4]);s[0]=atoll(argv[5])*2654435761ULL+1;s[1]=88172645463325252ULL;long long maxit=atoll(argv[6]);
  for(int i=0;i<50;i++)rnd();
  pw[0]=1;for(int i=1;i<16;i++)pw[i]=pw[i-1]*q;N=pw[n];
  cnt=calloc(N,sizeof(int)); int *code=malloc(M*sizeof(int));
  int B=1;{ // tamanho da bola
    int *tmp=malloc(N*sizeof(int)); int k=0; ball(0,0,R,tmp,&k); B=k; free(tmp);}
  int *b1=malloc(B*sizeof(int)),*b2=malloc(B*sizeof(int));
  int per=M/q; if(per*q!=M){fprintf(stderr,"M não divisível por q\n");return 2;}
  for(int i=0;i<M;i++){ int w=0; w+= (i/per)*pw[0]; for(int j=1;j<n;j++) w+=(int)(rnd()%q)*pw[j]; code[i]=w; }
  // coordenada 0 = dígito menos significativo
  int unc=N;
  for(int i=0;i<M;i++){int k=0;ball(code[i],0,R,b1,&k);for(int t=0;t<k;t++){if(cnt[b1[t]]++==0)unc--;}}
  double T=1.0; long long it;
  for(it=0;it<maxit&&unc>0;it++){
    T=0.6*(1.0-(double)(it%2000000)/2000000.0)+0.05;
    int i=rnd()%M; int j=1+rnd()%(n-1); int old=code[i]; int d=(old/pw[j])%q; int a=(d+1+rnd()%(q-1))%q; int nw=old+(a-d)*pw[j];
    int k1=0,k2=0; ball(old,0,R,b1,&k1); ball(nw,0,R,b2,&k2);
    int delta=0;
    for(int t=0;t<k1;t++){ if(--cnt[b1[t]]==0) delta++; }
    for(int t=0;t<k2;t++){ if(cnt[b2[t]]++==0) delta--; }
    if(delta<=0 || urand()<exp(-delta/T)){ code[i]=nw; unc+=delta; }
    else { for(int t=0;t<k2;t++) cnt[b2[t]]--; for(int t=0;t<k1;t++) cnt[b1[t]]++; }
  }
  if(unc==0){ for(int i=0;i<M;i++){ for(int j=0;j<n;j++) putchar('0'+(code[i]/pw[j])%q); putchar('\n'); } return 0;}
  fprintf(stderr,"falhou unc=%d it=%lld\n",unc,it); return 1;
}
