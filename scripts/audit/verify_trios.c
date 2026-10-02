/* verify_trios.c -- verificador SIMPLES e independente das órfãs de bases com 3 classes laterais.
 *
 * Não usa kit.h nem base_search.c. Para H = [I_r | A] sobre F_q (q primo, r = n - k):
 *   B  = { H e : wt(e) <= R }            (calculada enumerando todos os e de peso <= R)
 *   Bc = complemento de B em F_q^r
 *   órfãs(0, s1, s2) = | Bc ∩ (Bc + s1) ∩ (Bc + s2) |
 * Lista TODOS os trios {0,s1,s2} (a menos de translação e escalar) com órfãs <= T e o mínimo.
 *
 * Por que é exato (sem as otimizações do exactT2):
 *  - escalar: λB = B (o peso não muda), então órfãs(0,λs1,λs2) = órfãs(0,s1,s2); basta s1 com
 *    1º dígito não nulo = 1 (um por classe escalar). s2 percorre TODO F_q^r \ {0, s1}.
 *  - poda: para Y ⊂ X(s1) = Bc ∩ (Bc+s1), |Y ∩ (Bc+s2)| <= |X ∩ (Bc+s2)| = órfãs; se a conta em Y
 *    já passa de T, o trio não serve. Os demais são contados em X inteiro. Vale para QUALQUER Y.
 *  - cada trio encontrado é escrito na forma canônica: o menor (lexicográfico) entre os 3 pontos-base
 *    x 6 escalares da tripla ordenada {λ(p - b)}; a saída é ordenada e sem repetição.
 *
 * Uso: verify_trios q n R T "A" [m=200]      (A = "linha linha ...", r linhas de k dígitos)
 * Saída: linhas "TRIO o a b c" (forma canônica, a=0) e uma linha final "MIN o" (ou "MIN none").
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int q, n, R, r, k, T;
static long N;
static long pw[16];
static int H[16][16];
static uint8_t *inB;

static int digit(long x, int i){ return (int)((x / pw[i]) % q); }
static long sub(long a, long b){       /* a - b dígito a dígito, mod q */
  long s = 0;
  for (int i = 0; i < r; i++){ int d = (digit(a, i) - digit(b, i) + q) % q; s += d * pw[i]; }
  return s;
}
static long scal(long a, int l){ long s = 0; for (int i = 0; i < r; i++) s += ((digit(a, i) * l) % q) * pw[i]; return s; }

/* bola: soma recursiva de c * coluna_j para suportes de tamanho <= R */
static long col[16];
static void ball(int start, int left, long s){
  inB[s] = 1;
  if (!left) return;
  for (int j = start; j < n; j++)
    for (int c = 1; c < q; c++){
      long t = s;
      for (int u = 0; u < c; u++){ long v = 0; for (int i = 0; i < r; i++) v += ((digit(t, i) + digit(col[j], i)) % q) * pw[i]; t = v; }
      ball(j + 1, left - 1, t);
    }
}

typedef struct { long a, b, c; int o; } Tri;
static int cmp_tri(const void *x, const void *y){
  const Tri *p = x, *s = y;
  if (p->b != s->b) return p->b < s->b ? -1 : 1;
  if (p->c != s->c) return p->c < s->c ? -1 : 1;
  return 0;
}
static void canon(long s1, long s2, Tri *out){
  long P[3] = {0, s1, s2}; int first = 1;
  for (int bi = 0; bi < 3; bi++) for (int l = 1; l < q; l++){
    long v[3]; for (int i = 0; i < 3; i++) v[i] = scal(sub(P[i], P[bi]), l);
    /* ordena 3 */
    for (int i = 0; i < 3; i++) for (int j = i + 1; j < 3; j++) if (v[j] < v[i]){ long t = v[i]; v[i] = v[j]; v[j] = t; }
    if (first || v[1] < out->b || (v[1] == out->b && v[2] < out->c)){ out->a = v[0]; out->b = v[1]; out->c = v[2]; first = 0; }
  }
}

int main(int argc, char **argv){
  if (argc < 6){ fprintf(stderr, "uso: verify_trios q n R T A [m]\n"); return 2; }
  q = atoi(argv[1]); n = atoi(argv[2]); R = atoi(argv[3]); T = atoi(argv[4]);
  const char *A = argv[5]; int m = argc > 6 ? atoi(argv[6]) : 200;
  r = 1; for (const char *p = A; *p; p++) if (*p == ' ') r++;
  k = n - r;
  pw[0] = 1; for (int i = 1; i < 16; i++) pw[i] = pw[i - 1] * q;
  N = pw[r];
  const char *p = A;
  for (int i = 0; i < r; i++){
    while (*p == ' ') p++;
    for (int j = 0; j < r; j++) H[i][j] = (i == j);
    for (int j = 0; j < k; j++) H[i][r + j] = *p++ - '0';
  }
  for (int j = 0; j < n; j++){ col[j] = 0; for (int i = 0; i < r; i++) col[j] += (H[i][j] % q) * pw[i]; }
  inB = calloc(N, 1);
  ball(0, R, 0);
  long nBc = 0; for (long x = 0; x < N; x++) if (!inB[x]) nBc++;
  long *Bc = malloc(sizeof(long) * nBc); nBc = 0;
  for (long x = 0; x < N; x++) if (!inB[x]) Bc[nBc++] = x;
  /* tabela de subtração por metades, montada a partir de sub() (independente do kit) */
  int lo = (r + 1) / 2, hi = r - lo; long LO = pw[lo], HI = pw[hi];
  int *slo = malloc(sizeof(int) * LO * LO), *shi = malloc(sizeof(int) * HI * HI);
  { long sv = r; r = lo; for (long a = 0; a < LO; a++) for (long b = 0; b < LO; b++) slo[a * LO + b] = (int)sub(a, b); r = hi;
    for (long a = 0; a < HI; a++) for (long b = 0; b < HI; b++) shi[a * HI + b] = (int)sub(a, b); r = (int)sv; }
#define SUB(a, b) (slo[((a) % LO) * LO + ((b) % LO)] + LO * shi[((a) / LO) * HI + ((b) / LO)])
  long *X = malloc(sizeof(long) * nBc); uint16_t *cnt = malloc(sizeof(uint16_t) * N);
  long ntri = 0, cap = 1024; Tri *tri = malloc(sizeof(Tri) * cap);
  int best = 1 << 30;
  unsigned long long rs = 88172645463325252ULL;
  for (long s1 = 1; s1 < N; s1++){
    long t = s1; while (t % q == 0) t /= q; if (t % q != 1) continue;      /* 1º dígito não nulo = 1 */
    long nx = 0;
    for (long i = 0; i < nBc; i++) if (!inB[SUB(Bc[i], s1)]) X[nx++] = Bc[i];
    long my = nx < m ? nx : m;
    for (long i = 0; i < my; i++){ rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; long j = i + (long)(rs % (unsigned long long)(nx - i)); long u = X[i]; X[i] = X[j]; X[j] = u; }
    memset(cnt, 0, sizeof(uint16_t) * N);
    for (long i = 0; i < my; i++) for (long j = 0; j < nBc; j++) cnt[SUB(X[i], Bc[j])]++;   /* s2 com X[i] ∈ Bc + s2 */
    for (long s2 = 1; s2 < N; s2++){
      if (s2 == s1 || cnt[s2] > T) continue;
      int o = cnt[s2];
      for (long i = my; i < nx && o <= T; i++) if (!inB[SUB(X[i], s2)]) o++;
      if (o <= T){
        if (o < best) best = o;
        if (ntri == cap){ cap *= 2; tri = realloc(tri, sizeof(Tri) * cap); }
        canon(s1, s2, &tri[ntri]); tri[ntri].o = o; ntri++;
      }
    }
  }
  qsort(tri, ntri, sizeof(Tri), cmp_tri);
  for (long i = 0; i < ntri; i++){
    if (i && tri[i].b == tri[i - 1].b && tri[i].c == tri[i - 1].c){
      if (tri[i].o != tri[i - 1].o){ fprintf(stderr, "INCONSISTENTE: trio com duas contagens\n"); return 3; }
      continue; }
    printf("TRIO %d %ld %ld %ld\n", tri[i].o, tri[i].a, tri[i].b, tri[i].c);
  }
  if (best <= T) printf("MIN %d\n", best); else printf("MIN none\n");
  fprintf(stderr, "nBc=%ld\n", nBc);
  return 0;
}
