// mirror of CoveringKernel.go / stepAll ; counts item-steps per subtree at depth D
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct { long row; int d; int rad; } It;
static int Q, N, R;
static long steps;
static int go(int m, It *items, int len) {
  if (m == 0) { for (int i=0;i<len;i++) if (items[i].d <= items[i].rad) return 1; return 0; }
  for (int i=0;i<len;i++) if (items[i].d + m <= items[i].rad) return 1;
  It *nx = malloc(sizeof(It)*(len+1));
  for (int v=0; v<Q; v++) {
    int k=0; steps += len;
    for (int i=0;i<len;i++){ int dd = items[i].d + ((items[i].row % Q)==v?0:1);
      if (dd <= items[i].rad){ nx[k].row = items[i].row / Q; nx[k].d=dd; nx[k].rad=items[i].rad; k++; } }
    if (!go(m-1, nx, k)) { free(nx); return 0; }
  }
  free(nx); return 1;
}
int main(int argc, char**argv){
  Q=atoi(argv[1]); N=atoi(argv[2]); R=atoi(argv[3]); int D=atoi(argv[4]);
  static It W[100000]; int n=0; long x;
  while (scanf("%ld",&x)==1){ W[n].row=x; W[n].d=0; W[n].rad=R; n++; }
  // enumerate prefixes of depth D, cost of subtree go(N-D, stepAll^D W)
  long tot=0; int allok=1; int npref=1; for(int i=0;i<D;i++) npref*=Q;
  It *cur = malloc(sizeof(It)*n), *tmp=malloc(sizeof(It)*n);
  for (int p=0;p<npref;p++){
    int digs[16]; int pp=p; for(int i=0;i<D;i++){digs[i]=pp%Q; pp/=Q;}
    memcpy(cur,W,sizeof(It)*n); int len=n; long pre=0;
    for(int i=0;i<D;i++){ int k=0; pre+=len; for(int j=0;j<len;j++){int dd=cur[j].d+((cur[j].row%Q)==digs[i]?0:1); if(dd<=cur[j].rad){tmp[k].row=cur[j].row/Q;tmp[k].d=dd;tmp[k].rad=cur[j].rad;k++;}} memcpy(cur,tmp,sizeof(It)*k); len=k; }
    steps=0; int ok=go(N-D,cur,len); if(!ok) allok=0; tot+=steps;
    printf("P");for(int i=0;i<D;i++)printf("%d",digs[i]); printf(" %ld %d %d\n",steps,len,ok);
  }
  fprintf(stderr,"TOTAL %ld ALLOK %d n=%d\n",tot,allok,n);
}
