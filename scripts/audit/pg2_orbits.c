/* pg2_orbits.c — auditoria INDEPENDENTE do base_search (não compartilha código com ele).
 *
 * Geometria de PG(2,q), q primo. Índice de ponto PRÓPRIO desta auditoria: vetores
 * normalizados (1ª coordenada não nula = 1) em ordem lexicográfica de (x,y,z).
 * (O base_search usa outra ordem: referencial padrão primeiro. A diferença é proposital:
 * nada aqui reaproveita a numeração dele.)
 *
 * Fato usado (teorema fundamental da geometria projetiva): para duas 4-uplas ordenadas
 * de pontos em posição geral existe exatamente uma projetividade de PGL(3,q) levando
 * uma na outra. Daí, para um multiconjunto S que contém um referencial:
 *   - canon(S) = min lexicográfico, sobre as 4-uplas ordenadas F de pontos DISTINTOS de S
 *     em posição geral, da imagem ordenada N_F(S), onde N_F leva F ao referencial padrão
 *     ((1,0,0),(0,1,0),(0,0,1),(1,1,1)). canon é invariante completo da órbita.
 *   - |Stab(S)| = número de F que atingem o mínimo (bijeção F <-> h = N_F0^{-1} N_F).
 *
 * Modos:
 *   stab q m            lê linhas com m índices (ordem qualquer), escreve "canon... | stab"
 *   enum q m [sh nsh]   enumera representantes canônicos das órbitas de m-multiconjuntos
 *                       com referencial: S = referencial padrão ∪ T, T multiconjunto de m-4
 *                       pontos; aceita S se nenhuma imagem é menor que S. Escreve S | stab.
 *   equiv q m           lê pares de linhas (S1, S2) e escreve 1 se existe g com g(S1) = S2, senão 0.
 *                       Força bruta direta: fixa UM referencial ordenado F0 de S1 e testa todas as
 *                       4-uplas ordenadas F de pontos distintos de S2 (g = N_F^{-1} N_F0):
 *                       g(S1) = S2  <=>  N_F0(S1) = N_F(S2). Não usa a forma canônica.
 *   livres q smax       conta, por busca em profundidade SEM supor a classificação "reta + ponto",
 *                       os CONJUNTOS de pontos de tamanho 1..smax sem 4 pontos em posição geral
 *                       (propriedade hereditária: todo subconjunto de um conjunto livre é livre),
 *                       separando os contidos numa reta (posto <= 2) dos de posto 3.
 * Compilar: gcc -O3 -march=native -o pg2_orbits pg2_orbits.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXM 16
static int q, NP, PT[400][3], KEY[400], INVq[64], FR[4];

static int idx_of(int x, int y, int z){
  x %= q; y %= q; z %= q; if (x < 0) x += q; if (y < 0) y += q; if (z < 0) z += q;
  int c;
  if (x) c = INVq[x]; else if (y) c = INVq[y]; else if (z) c = INVq[z]; else return -1;
  return KEY[(x * c % q) * q * q + (y * c % q) * q + (z * c % q)];
}
static void build(void){
  for (int a = 1; a < q; a++) for (int b = 1; b < q; b++) if (a * b % q == 1) INVq[a] = b;
  NP = 0;
  for (int k = 0; k < q * q * q; k++) KEY[k] = -1;
  for (int x = 0; x < q; x++) for (int y = 0; y < q; y++) for (int z = 0; z < q; z++){
    int f = x ? x : (y ? y : z);
    if (f != 1) continue;
    PT[NP][0] = x; PT[NP][1] = y; PT[NP][2] = z; KEY[x * q * q + y * q + z] = NP; NP++;
  }
  FR[0] = idx_of(1,0,0); FR[1] = idx_of(0,1,0); FR[2] = idx_of(0,0,1); FR[3] = idx_of(1,1,1);
}
static int det3(int M[3][3]){
  long d = (long)M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1]) - (long)M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])
         + (long)M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]);
  d %= q; if (d < 0) d += q; return (int)d;
}
/* matriz N (3x3) com N*a~e1, N*b~e2, N*c~e3, N*d~(1,1,1); 0 se não estão em posição geral */
static int normmap(int a, int b, int c, int d, int N[3][3]){
  int P[3][3];
  for (int i = 0; i < 3; i++){ P[i][0] = PT[a][i]; P[i][1] = PT[b][i]; P[i][2] = PT[c][i]; }
  int D = det3(P); if (!D) return 0;
  int Di = INVq[D], A[3][3];
  /* adjunta: inv = adj / det */
  for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++){
    int r0 = (j + 1) % 3, r1 = (j + 2) % 3, c0 = (i + 1) % 3, c1 = (i + 2) % 3;
    long v = (long)P[r0][c0] * P[r1][c1] - (long)P[r0][c1] * P[r1][c0];
    v %= q; if (v < 0) v += q; A[i][j] = (int)(v * Di % q);
  }
  int lam[3];
  for (int i = 0; i < 3; i++){ long s = 0; for (int j = 0; j < 3; j++) s += A[i][j] * PT[d][j]; lam[i] = (int)(s % q); if (!lam[i]) return 0; }
  for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) N[i][j] = INVq[lam[i]] * A[i][j] % q;
  return 1;
}
/* ---- conjuntos sem referencial (busca em profundidade) ---- */
static unsigned char COL[400][400][400 / 8 + 1];
static int colin(int a, int b, int c){ return (COL[a][b][c >> 3] >> (c & 7)) & 1; }
static long cntL[MAXM], cnt3[MAXM]; static int smax_, cur[MAXM];
static void dfs(int sz, int start){
  if (sz){ int r3 = 0; for (int i = 0; i < sz && !r3; i++) for (int j = i + 1; j < sz && !r3; j++) for (int k = j + 1; k < sz; k++) if (!colin(cur[i], cur[j], cur[k])){ r3 = 1; break; }
    if (r3) cnt3[sz]++; else cntL[sz]++; }
  if (sz == smax_) return;
  for (int p = start; p < NP; p++){
    int bad = 0;
    for (int i = 0; i < sz && !bad; i++) for (int j = i + 1; j < sz && !bad; j++){
      if (colin(cur[i], cur[j], p)) continue;
      for (int k = j + 1; k < sz; k++)
        if (!colin(cur[i], cur[j], cur[k]) && !colin(cur[i], cur[k], p) && !colin(cur[j], cur[k], p)){ bad = 1; break; }
    }
    if (bad) continue;
    cur[sz] = p; dfs(sz + 1, p + 1);
  }
}
static int cmpi(const void *a, const void *b){ return *(const int*)a - *(const int*)b; }
static void image(int N[3][3], const int *S, int m, int *out){
  for (int t = 0; t < m; t++){
    const int *v = PT[S[t]];
    out[t] = idx_of(N[0][0]*v[0]+N[0][1]*v[1]+N[0][2]*v[2], N[1][0]*v[0]+N[1][1]*v[1]+N[1][2]*v[2], N[2][0]*v[0]+N[2][1]*v[1]+N[2][2]*v[2]);
  }
  /* inserção: m pequeno */
  for (int i = 1; i < m; i++){ int x = out[i], j = i - 1; while (j >= 0 && out[j] > x){ out[j + 1] = out[j]; j--; } out[j + 1] = x; }
}
static int lexcmp(const int *a, const int *b, int m){ for (int i = 0; i < m; i++){ if (a[i] != b[i]) return a[i] < b[i] ? -1 : 1; } return 0; }

/* percorre 4-uplas ordenadas de pontos distintos do suporte.
 * modo canon: best <- min, devolve stab (nº de 4-uplas no mínimo), -1 se não há referencial.
 * modo early (ref != NULL): devolve 0 assim que achar imagem < ref; senão devolve stab relativo a ref. */
static long scan(const int *S, int m, int *best, const int *ref){
  int sup[MAXM], ns = 0;
  for (int t = 0; t < m; t++) if (!ns || sup[ns - 1] != S[t]) sup[ns++] = S[t];
  int have = 0; long cnt = 0; int img[MAXM], N[3][3];
  if (ref){ memcpy(best, ref, sizeof(int) * m); have = 1; }
  for (int i = 0; i < ns; i++) for (int j = 0; j < ns; j++) if (j != i)
  for (int k = 0; k < ns; k++) if (k != i && k != j)
  for (int l = 0; l < ns; l++) if (l != i && l != j && l != k){
    if (!normmap(sup[i], sup[j], sup[k], sup[l], N)) continue;
    image(N, S, m, img);
    if (!have){ memcpy(best, img, sizeof(int) * m); have = 1; cnt = 1; continue; }
    int c = lexcmp(img, best, m);
    if (c < 0){ if (ref) return 0; memcpy(best, img, sizeof(int) * m); cnt = 1; }
    else if (c == 0) cnt++;
  }
  if (!have) return -1;
  return cnt;
}

int main(int argc, char **argv){
  if (argc < 4){ fprintf(stderr, "uso: stab q m | enum q m [shard nshard]\n"); return 2; }
  q = atoi(argv[2]); int m = atoi(argv[3]); build();
  if (!strcmp(argv[1], "livres")){
    smax_ = m;
    for (int a = 0; a < NP; a++) for (int b = 0; b < NP; b++) for (int c = 0; c < NP; c++){
      int M[3][3]; for (int i = 0; i < 3; i++){ M[i][0] = PT[a][i]; M[i][1] = PT[b][i]; M[i][2] = PT[c][i]; }
      if (!det3(M)) COL[a][b][c >> 3] |= 1 << (c & 7);
    }
    dfs(0, 0);
    for (int s2 = 1; s2 <= m; s2++) printf("%d %ld %ld\n", s2, cntL[s2], cnt3[s2]);
    return 0;
  }
  if (!strcmp(argv[1], "equiv")){
    int S1[MAXM], S2[MAXM], a[MAXM], b[MAXM], N[3][3];
    while (1){
      int ok = 1;
      for (int t = 0; t < m && ok; t++) if (scanf("%d", &S1[t]) != 1) ok = 0;
      for (int t = 0; t < m && ok; t++) if (scanf("%d", &S2[t]) != 1) ok = 0;
      if (!ok) break;
      qsort(S1, m, sizeof(int), cmpi); qsort(S2, m, sizeof(int), cmpi);
      int u1[MAXM], n1 = 0, u2[MAXM], n2 = 0, found = 0, have = 0;
      for (int t = 0; t < m; t++){ if (!n1 || u1[n1 - 1] != S1[t]) u1[n1++] = S1[t]; if (!n2 || u2[n2 - 1] != S2[t]) u2[n2++] = S2[t]; }
      for (int i = 0; i < n1 && !have; i++) for (int j = i + 1; j < n1 && !have; j++) for (int k = j + 1; k < n1 && !have; k++)
        for (int l = k + 1; l < n1 && !have; l++) if (normmap(u1[i], u1[j], u1[k], u1[l], N)){ image(N, S1, m, a); have = 1; }
      if (!have){ printf("-1\n"); continue; }
      for (int i = 0; i < n2 && !found; i++) for (int j = 0; j < n2 && !found; j++) if (j != i)
      for (int k = 0; k < n2 && !found; k++) if (k != i && k != j)
      for (int l = 0; l < n2 && !found; l++) if (l != i && l != j && l != k){
        if (!normmap(u2[i], u2[j], u2[k], u2[l], N)) continue;
        image(N, S2, m, b);
        if (!lexcmp(a, b, m)) found = 1;
      }
      printf("%d\n", found);
    }
    return 0;
  }
  if (!strcmp(argv[1], "stab")){
    int S[MAXM], best[MAXM];
    while (1){
      int ok = 1; for (int t = 0; t < m; t++) if (scanf("%d", &S[t]) != 1){ ok = 0; break; }
      if (!ok) break;
      qsort(S, m, sizeof(int), cmpi);
      long st = scan(S, m, best, NULL);
      if (st < 0){ printf("SEM_REFERENCIAL\n"); continue; }
      for (int t = 0; t < m; t++) printf("%d ", best[t]);
      printf("| %ld\n", st);
    }
    return 0;
  }
  if (!strcmp(argv[1], "enum")){
    long sh = argc > 4 ? atol(argv[4]) : 0, nsh = argc > 5 ? atol(argv[5]) : 1;
    int r = m - 4, T[MAXM]; for (int i = 0; i < r; i++) T[i] = 0;
    long seen = 0, acc = 0;
    while (1){
      if ((seen++ % nsh) == sh){
        int S[MAXM], best[MAXM];
        for (int i = 0; i < 4; i++) S[i] = FR[i];
        for (int i = 0; i < r; i++) S[4 + i] = T[i];
        qsort(S, m, sizeof(int), cmpi);
        long st = scan(S, m, best, S);
        if (st > 0){ acc++; for (int t = 0; t < m; t++) printf("%d ", S[t]); printf("| %ld\n", st); }
      }
      int i = r - 1; while (i >= 0 && T[i] == NP - 1) i--;
      if (i < 0) break;
      T[i]++; for (int j = i + 1; j < r; j++) T[j] = T[i];
    }
    fflush(stdout);
    fprintf(stderr, "enum q=%d m=%d shard %ld/%ld multiconjuntos=%ld órbitas=%ld\n", q, m, sh, nsh, seen, acc);
    return 0;
  }
  return 2;
}
