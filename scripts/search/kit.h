/* kit.h -- núcleo comum do kit de busca de códigos de cobertura q-ários.
 *
 * Convenções (iguais em base_search.c e patch_opt.c):
 *   - q primo (aritmética mod q). Palavras de comprimento n; síndromes em F_q^r, r = n-k.
 *   - Uma palavra/síndrome é guardada como inteiro em base q, dígito i = coordenada i.
 *   - O código linear C é dado pela matriz de checagem H (r x n). Para H = [I_r | A]
 *     (A r x k), a síndrome de e é e[0..r-1] + A e[r..n-1].
 *   - B = { H e : wt(e) <= R } (a "bola" no espaço de síndromes); Bc = complemento.
 *   - Base com t classes laterais de síndromes s_0=0, s_1..s_{t-1}: uma síndrome s fica
 *     ÓRFÃ se s - s_j ∉ B para todo j, i.e. s ∈ ∩_j (Bc + s_j). Cada órfã é uma classe
 *     lateral inteira de C (q^k palavras) sem cobertura.
 */
#ifndef KIT_H
#define KIT_H
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXN 16
#define MAXR 12

typedef struct {
  int q, n, R, r, k;
  int H[MAXR][MAXN];   /* matriz de checagem r x n */
  long N;              /* q^r */
  long pw[MAXN + 1];
  int hcol[MAXN];      /* síndrome (inteiro) de cada coluna de H */
  /* soma de síndromes por tabela em duas metades */
  int lo_d, hi_d; long LO, HI;
  int *addlo, *addhi;  /* LO x LO e HI x HI */
  int *neglo, *neghi;
  uint8_t *inB; long nB;
  int *Bc; long nBc;
} Kit;

static inline double kit_now(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec+1e-9*t.tv_nsec; }

static inline int kit_add(const Kit *K, int a, int b){
  return K->addlo[(a % K->LO) * K->LO + (b % K->LO)] + (int)K->LO * K->addhi[(a / K->LO) * K->HI + (b / K->LO)];
}
static inline int kit_neg(const Kit *K, int a){
  return K->neglo[a % K->LO] + (int)K->LO * K->neghi[a / K->LO];
}
static inline int kit_sub(const Kit *K, int a, int b){ return kit_add(K, a, kit_neg(K, b)); }
static inline int kit_scale(const Kit *K, int a, int c){
  int res = 0; long p = 1;
  for (int i = 0; i < K->r; i++){ res += (int)((((a / p) % K->q) * c) % K->q * p); p *= K->q; }
  return res;
}

static int *kit_mk_add(int q, int d, long sz){
  int *T = malloc(sizeof(int) * sz * sz);
  for (long a = 0; a < sz; a++) for (long b = 0; b < sz; b++){
    long x = a, y = b, p = 1, res = 0;
    for (int i = 0; i < d; i++){ res += ((x % q + y % q) % q) * p; p *= q; x /= q; y /= q; }
    T[a * sz + b] = (int)res;
  }
  return T;
}
static int *kit_mk_neg(int q, int d, long sz){
  int *T = malloc(sizeof(int) * sz);
  for (long a = 0; a < sz; a++){ long x = a, p = 1, res = 0;
    for (int i = 0; i < d; i++){ res += ((q - x % q) % q) * p; p *= q; x /= q; }
    T[a] = (int)res; }
  return T;
}

/* prepara tabelas; H já preenchida em K->H, q,n,R,r setados */
static void kit_init_tables(Kit *K){
  K->k = K->n - K->r;
  K->pw[0] = 1; for (int i = 1; i <= MAXN; i++) K->pw[i] = K->pw[i - 1] * K->q;
  K->N = K->pw[K->r];
  K->lo_d = (K->r + 1) / 2; K->hi_d = K->r - K->lo_d;
  K->LO = K->pw[K->lo_d]; K->HI = K->pw[K->hi_d];
  K->addlo = kit_mk_add(K->q, K->lo_d, K->LO); K->addhi = kit_mk_add(K->q, K->hi_d, K->HI);
  K->neglo = kit_mk_neg(K->q, K->lo_d, K->LO); K->neghi = kit_mk_neg(K->q, K->hi_d, K->HI);
  K->inB = calloc(K->N, 1); K->Bc = malloc(sizeof(int) * K->N);
}

static void kit_set_cols(Kit *K){
  for (int j = 0; j < K->n; j++){ long s = 0; for (int i = 0; i < K->r; i++) s += ((K->H[i][j] % K->q + K->q) % K->q) * K->pw[i]; K->hcol[j] = (int)s; }
}

/* B por DFS sobre suportes: soma de c*h_j */
static void kit_ball_rec(Kit *K, int start, int left, int s){
  K->inB[s] = 1;
  if (!left) return;
  for (int j = start; j < K->n; j++){
    int m = K->hcol[j];
    int acc = m;
    for (int c = 1; c < K->q; c++){ kit_ball_rec(K, j + 1, left - 1, kit_add(K, s, acc)); acc = kit_add(K, acc, m); }
  }
}
static void kit_compute_ball(Kit *K){
  memset(K->inB, 0, K->N);
  kit_set_cols(K);
  kit_ball_rec(K, 0, K->R, 0);
  K->nB = 0; K->nBc = 0;
  for (long s = 0; s < K->N; s++){ if (K->inB[s]) K->nB++; else K->Bc[K->nBc++] = (int)s; }
}

/* H = [I_r | A], A dado como r linhas de k dígitos (string "652 132 ...") */
static int kit_set_A(Kit *K, const char *A){
  const char *p = A;
  for (int i = 0; i < K->r; i++){
    while (*p == ' ' || *p == ',') p++;
    for (int j = 0; j < K->k; j++){ if (*p < '0' || *p > '9') return -1; K->H[i][K->r + j] = *p - '0'; p++; }
    for (int j = 0; j < K->r; j++) K->H[i][j] = (i == j);
  }
  return 0;
}

/* syndrome of a word given as digit array */
static inline int kit_synd_digits(const Kit *K, const int *w){
  int s = 0;
  for (int j = 0; j < K->n; j++) if (w[j]){ int m = K->hcol[j]; for (int c = 0; c < w[j]; c++) s = kit_add(K, s, m); }
  return s;
}

static unsigned long long kit_rs = 88172645463325252ULL;
static inline unsigned long long kit_rnd(void){ kit_rs ^= kit_rs << 13; kit_rs ^= kit_rs >> 7; kit_rs ^= kit_rs << 17; return kit_rs; }
static void kit_seed(unsigned long long s){ kit_rs = s * 0x9E3779B97F4A7C15ULL + 7; for (int i = 0; i < 20; i++) kit_rnd(); }

#endif
