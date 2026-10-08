// SA para cobertura: M palavras q-arias, raio R. Move: muda 1 digito de 1 palavra (delta exato via conjunto "distancia exata R nas outras coordenadas").
// uso: sa q n R M secs seed out.txt   (sai 0 e escreve out se cobrir; imprime melhor custo)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
static int q,n,R,M; static long S; static long pw[32];
static uint64_t st[2];
static inline uint64_t rn(void){uint64_t s1=st[0],s0=st[1];st[0]=s0;s1^=s1<<23;st[1]=s1^s0^(s1>>18)^(s0>>5);return st[1]+s0;}
static inline double ur(void){return (rn()>>11)*(1.0/9007199254740992.0);}
static int *cnt; static long unc;
static int W[1024][32]; // palavras digitos
static long idx[1024];
static int cur_i, cur_sign_x, cur_sign_x2; static long cur_base; // aplicacao
static int dig(long y,int p){return (y/pw[p])%q;}
// enumera conjuntos: posicoes outras (excluindo i), exatamente R mudadas
static int posl[32], npos;
static long offA, offB; // y com y_i=x_i : base idx ; y_i=x'_i
static int xi, xi2, qi; static long xidx; static int xd[32];
static int dA; // +1 / -1 / aplicar
static void rec(int start,int left,long yA){
  if(left==0){
    // yA tem digito i = xi; yB = yA + (xi2-xi)*pw[i]
    long yB=yA+(long)(xi2-xi)*pw[qi];
    // lost: yA ; gained: yB
    if(--cnt[yA]==0) unc++;
    if(cnt[yB]++==0) unc--;
    return;
  }
  for(int a=start;a<=npos-left;a++){
    int p=posl[a]; int d0=xd[p];
    for(int v=1;v<q;v++){
      int nd=(d0+v)%q;
      rec(a+1,left-1,yA+(long)(nd-d0)*pw[p]);
    }
  }
}
static void domove(int w,int i,int nv){
  qi=i; xi=W[w][i]; xi2=nv;
  npos=0; for(int p=0;p<n;p++) if(p!=i) posl[npos++]=p;
  for(int p=0;p<n;p++) xd[p]=W[w][p];
  rec(0,R,idx[w]);
  W[w][i]=nv; idx[w]+= (long)(nv-xi)*pw[i];
}
static void addball_full(long c,int sign){ // bola completa (para init): enumerar por recursao simples
  // usa deslocamentos por camadas
  int d[32]; for(int p=0;p<n;p++) d[p]=(c/pw[p])%q;
  // iterativo: recursao
  struct F{int p;int left;long y;} ;
  // implementacao recursiva via funcao local
  extern void ballrec(int,int,long,int*,int);
  ballrec(0,R,c,d,sign);
}
void ballrec(int start,int left,long y,int*d,int sign){
  if(sign>0){ if(cnt[y]++==0) unc--; } else { if(--cnt[y]==0) unc++; }
  if(left==0) return;
  for(int p=start;p<n;p++) for(int v=1;v<q;v++){
    int nd=(d[p]+v)%q; ballrec(p+1,left-1,y+(long)(nd-d[p])*pw[p],d,sign);
  }
}
int main(int argc,char**argv){
  q=atoi(argv[1]);n=atoi(argv[2]);R=atoi(argv[3]);M=atoi(argv[4]);double secs=atof(argv[5]);
  uint64_t seed=strtoull(argv[6],0,10);st[0]=seed*0x9E3779B97F4A7C15ULL+1;st[1]=seed^0xD1B54A32D192ED03ULL;for(int k=0;k<20;k++)rn();
  pw[0]=1;for(int i=1;i<=n;i++)pw[i]=pw[i-1]*q;S=pw[n];
  cnt=calloc(S,sizeof(int)); unc=S;
  for(int w=0;w<M;w++){idx[w]=0;for(int p=0;p<n;p++){W[w][p]=rn()%q;idx[w]+=W[w][p]*pw[p];} addball_full(idx[w],1);}
  long best=unc; time_t t0=time(0); double T0=argc>8?atof(argv[8]):0.6, T1=argc>9?atof(argv[9]):0.12;
  long it=0; double T=T0; double frac=0; long bestw[1];
  long lastchk=0; int restarts=0;
  while(unc>0){
    if((it&1023)==0){ double el=difftime(time(0),t0); if(el>secs)break; double cyc=fmod(el/ (secs/ (argc>7?atof(argv[7]):4)),1.0); frac=cyc; T=T0*pow(T1/T0,frac);}
    it++;
    int w=rn()%M,i=rn()%n; int nv=(W[w][i]+1+rn()%(q-1))%q; long before=unc;
    int old=W[w][i];
    domove(w,i,nv);
    long d=unc-before;
    if(d<=0 || ur()<exp(-d/T)){ if(unc<best){best=unc;} }
    else { domove(w,i,old); }
  }
  printf("q=%d n=%d R=%d M=%d best_unc=%ld final_unc=%ld iters=%ld secs=%.0f\n",q,n,R,M,best,unc,it,difftime(time(0),t0));
  if(unc==0){
    FILE*f=fopen(getenv("SA_OUT")?getenv("SA_OUT"):"found.txt","w");
    for(int w=0;w<M;w++){for(int p=0;p<n;p++)fputc('0'+W[w][p],f);fputc('\n',f);} fclose(f); return 0;}
  return 1;
}
