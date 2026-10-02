/* rt_orbits.c -- red team, ataques 3 e 6: completude das 6362 + 1375 classes [9,3]_7,
 * reimplementado do zero (não usa kit.h, base_search.c, pg2_orbits.c nem audit_lib.py).
 *
 * Entrada: arquivos JSONL com campo "A" (H = [I6 | A]); lê todos os arquivos dados.
 * Para cada linha: G = [-A^T | I3]; colunas nulas = z; as m = 9 - z colunas não nulas viram
 * pontos de PG(2,7) (multiconjunto S). Exige posto 3.
 *
 * Grupo: PGL(3,7). Todo g que leva S num conjunto que contém e1,e2,e3 manda alguma tripla
 * ordenada NÃO colinear (a,b,c) de pontos do suporte de S em (e1,e2,e3); esses g são
 * exatamente D·M_abc, com M_abc = [a b c]^{-1} e D diagonal diag(1,x,y) (36 escolhas).
 *  - Forma canônica: o menor multiconjunto ordenado entre as imagens D·M_abc·S. O conjunto
 *    dessas imagens é o mesmo para S e hS (h em PGL), então é invariante da órbita e só
 *    contém elementos da órbita: canon(S1) == canon(S2) sse S1 ~ S2. Vale com ou sem
 *    referencial (só precisa de posto 3).
 *  - |Stab(S)| = #{(a,b,c,D) : D·M_abc·S == canon(S)} (cada g com gS = canon é desses).
 * Massa: para cada z, soma de |PGL(3,7)|/|Stab| deve ser o número de m-multiconjuntos de
 * posto 3: C(m+56,m) - 57·C(m+7,m) + 57·7 (inclusão–exclusão sobre as 57 retas; o
 * multiconjunto concentrado num ponto cai nas 8 retas pelo ponto).
 *
 * Saída: por z, número de linhas, formas canônicas distintas, massa e esperado; e o total de
 * pares duplicados (mesma órbita em duas linhas) e linhas inválidas.
 * Compilar: gcc -O2 -o rt_orbits rt_orbits.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define Q 7
static int inv7[Q] = {0, 1, 4, 5, 2, 3, 6};
static int norm(const int *v){            /* chave 0..342 do vetor normalizado; -1 se nulo */
  int f = -1; for (int i = 0; i < 3; i++) if (v[i] % Q){ f = i; break; }
  if (f < 0) return -1;
  int c = inv7[((v[f] % Q) + Q) % Q], k = 0;
  for (int i = 0; i < 3; i++) k = k * Q + (((v[i] * c) % Q) + Q) % Q;
  return k;
}
static void unkey(int k, int *v){ v[2] = k % Q; v[1] = (k / Q) % Q; v[0] = k / 49; }
static int det3(int M[3][3]){
  long d = (long)M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - (long)M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0]) + (long)M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]);
  return (int)(((d % Q) + Q) % Q);
}
static int inv3(int M[3][3], int R[3][3]){
  int d = det3(M); if (!d) return 0; int di = inv7[d];
  for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++){
    int a = (j + 1) % 3, b = (j + 2) % 3, c = (i + 1) % 3, e = (i + 2) % 3;
    long cof = (long)M[a][c] * M[b][e] - (long)M[a][e] * M[b][c];   /* adjunta (transposta dos cofatores) */
    R[i][j] = (int)((((cof % Q) * di) % Q + Q) % Q);
  }
  return 1;
}
static int cmpi(const void *a, const void *b){ return *(const int *)a - *(const int *)b; }

typedef struct { int z, m, S[9], canon[9], stab; } Cls;

static void analyse(Cls *C){
  int sup[9], ns = 0;
  for (int i = 0; i < C->m; i++){ int d = 0; for (int j = 0; j < ns; j++) if (sup[j] == C->S[i]) d = 1; if (!d) sup[ns++] = C->S[i]; }
  int best[9], have = 0, cntbest = 0;
  for (int a = 0; a < ns; a++) for (int b = 0; b < ns; b++) for (int c = 0; c < ns; c++){
    if (a == b || a == c || b == c) continue;
    int P[3][3], Mi[3][3], va[3], vb[3], vc[3];
    unkey(sup[a], va); unkey(sup[b], vb); unkey(sup[c], vc);
    for (int i = 0; i < 3; i++){ P[i][0] = va[i]; P[i][1] = vb[i]; P[i][2] = vc[i]; }
    if (!inv3(P, Mi)) continue;                          /* colinear */
    for (int x = 1; x < Q; x++) for (int y = 1; y < Q; y++){
      int img[9], dg[3] = {1, x, y};
      for (int t = 0; t < C->m; t++){ int v[3], w[3]; unkey(C->S[t], v);
        for (int i = 0; i < 3; i++){ w[i] = 0; for (int j = 0; j < 3; j++) w[i] += Mi[i][j] * v[j]; w[i] = (w[i] % Q) * dg[i] % Q; }
        img[t] = norm(w); }
      qsort(img, C->m, sizeof(int), cmpi);
      int cmp = 0; if (have) for (int t = 0; t < C->m && !cmp; t++) cmp = (img[t] > best[t]) - (img[t] < best[t]);
      if (!have || cmp < 0){ memcpy(best, img, sizeof img); have = 1; cntbest = 1; }
      else if (cmp == 0) cntbest++;
    }
  }
  C->stab = have ? cntbest : 0;
  memcpy(C->canon, best, sizeof best);
}

static double binom(int n, int k){ double r = 1; for (int i = 1; i <= k; i++) r = r * (n - k + i) / i; return r; }
static int cmpcls(const void *a, const void *b){
  const Cls *x = a, *y = b; if (x->z != y->z) return x->z - y->z;
  for (int t = 0; t < x->m; t++) if (x->canon[t] != y->canon[t]) return x->canon[t] - y->canon[t];
  return 0;
}

int main(int argc, char **argv){
  static Cls cl[20000]; int nc = 0, bad = 0;
  for (int fi = 1; fi < argc; fi++){
    FILE *f = fopen(argv[fi], "r"); if (!f){ perror(argv[fi]); return 2; }
    char line[4096];
    while (fgets(line, sizeof line, f)){
      char *p = strstr(line, "\"A\""); if (!p){ bad++; continue; }
      p = strchr(p + 3, '"'); if (!p){ bad++; continue; } p++;
      int A[6][3], ok = 1;
      for (int i = 0; i < 6 && ok; i++){ for (int j = 0; j < 3; j++){ if (*p < '0' || *p > '6'){ ok = 0; break; } A[i][j] = *p++ - '0'; } if (i < 5){ if (*p != ' ') ok = 0; p++; } }
      if (!ok || *p != '"'){ bad++; fprintf(stderr, "A inválido: %s", line); continue; }
      Cls *C = &cl[nc]; C->z = 0; C->m = 0;
      for (int col = 0; col < 9; col++){ int v[3];
        for (int j = 0; j < 3; j++) v[j] = col < 6 ? (Q - A[col][j]) % Q : (col - 6 == j);
        int k = norm(v); if (k < 0) C->z++; else C->S[C->m++] = k; }
      qsort(C->S, C->m, sizeof(int), cmpi);
      analyse(C);
      if (!C->stab){ bad++; fprintf(stderr, "posto < 3: %s", line); continue; }
      nc++;
    }
    fclose(f);
  }
  const double PGL = 5630688.0;
  qsort(cl, nc, sizeof(Cls), cmpcls);
  int dup = 0; for (int i = 1; i < nc; i++) if (!cmpcls(&cl[i], &cl[i - 1])) dup++;
  printf("linhas_validas=%d invalidas=%d duplicadas(mesma_orbita)=%d\n", nc, bad, dup);
  int allok = 1;
  for (int z = 0; z <= 6; z++){
    int m = 9 - z, n = 0; double mass = 0;
    for (int i = 0; i < nc; i++) if (cl[i].z == z){ n++; mass += PGL / cl[i].stab; }
    double exp = binom(m + 56, m) - 57 * binom(m + 7, m) + 57 * 7;
    int ok = (mass > exp - 0.5 && mass < exp + 0.5);
    if (!ok) allok = 0;
    printf("z=%d m=%d classes=%d massa=%.0f esperado=%.0f %s\n", z, m, n, mass, exp, ok ? "OK" : "DIFERE");
  }
  printf("RESULTADO %s\n", (allok && !dup && !bad) ? "COMPLETO_E_SEM_DUPLICATAS" : "PROBLEMA");
  return 0;
}
