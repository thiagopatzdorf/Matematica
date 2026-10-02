/* base_search.c -- busca de bases [n,k]_q para coberturas por classes laterais.
 *
 * Uma "base" é a união de t classes laterais de um código linear C [n,k]_q com síndromes
 * {0, s_1, ..., s_{t-1}}. O que sobra sem cobrir são as síndromes órfãs
 *   O = Bc ∩ (Bc+s_1) ∩ ... ∩ (Bc+s_{t-1}),  B = {H e : wt(e) <= R}.
 * Cada órfã custa uma classe lateral inteira (q^k palavras) para o remendo; menos órfãs
 * = remendo menor (é a alavanca medida: 27 órfãs -> 1323, 24 órfãs -> 1285 em K_7(9,4)).
 *
 * MODOS
 *   enum  q n k R t nS1 [shard nshard]
 *     Enumera TODAS as classes de equivalência de códigos [n,k]_q não degenerados
 *     (sem coluna nula e cujas colunas contêm k+1 pontos em posição geral), como órbitas
 *     de PGL(k,q) sobre multiconjuntos de n pontos de PG(k-1,q). Representante canônico:
 *     o menor multiconjunto ordenado entre as imagens por todos os referenciais
 *     ordenados (k+1 pontos em posição geral -> referencial padrão). Geração ordenada:
 *     todo representante contém o referencial padrão, então basta percorrer os
 *     multiconjuntos de n-k-1 pontos restantes e aceitar os que são canônicos.
 *     Para cada classe: avalia órfãs (ver eval) e imprime uma linha JSON.
 *   eval  q n R t nS1 A          (A = "linha linha ..." de H=[I_r|A], ex "652 132 256 141 231 402")
 *   exact q n R A               (t=3: varre TODO s1 (classes por escalar) com s2 exato)
 *
 * AVALIAÇÃO (t=3): c(s) = |Bc ∩ (Bc+s)| por autocorrelação via DFT em Z_q^r; os nS1
 * candidatos a s1 de menor c (um por classe escalar; a contagem é invariante por
 * escalar e por translação do trio), e para cada um o s2 ÓTIMO é exato:
 * cnt[s2] = |X ∩ (Bc+s2)|, X = Bc ∩ (Bc+s1), por varredura direta |X|·|Bc|.
 * O modo exact faz isso para todo s1 e devolve o mínimo verdadeiro do trio.
 * Para t>3, as classes extras são escolhidas gulosamente com contagem exata.
 *
 * q precisa ser primo. Compilar: gcc -O3 -march=native -o base_search base_search.c -lm
 */
#include "kit.h"
#include <math.h>
#include <complex.h>

int cmp_int(const void *a, const void *b);
/* ---------- DFT em Z_q^r ---------- */
static double complex *W; /* raízes q-ésimas */
static void dft(const Kit *K, double complex *a, int inv){
  int q = K->q; double complex tmp[32];
  for (int d = 0; d < K->r; d++){
    long st = K->pw[d];
    for (long base = 0; base < K->N; base++){
      if ((base / st) % q) continue;
      for (int u = 0; u < q; u++){ double complex s = 0;
        for (int v = 0; v < q; v++) s += a[base + v * st] * W[((inv ? q - 1 : 1) * u * v) % q];
        tmp[u] = s; }
      for (int u = 0; u < q; u++) a[base + u * st] = tmp[u];
    }
  }
  if (inv){ for (long i = 0; i < K->N; i++) a[i] /= (double)K->N; }
}

static int *cX; static double complex *FB;
static void autocorr(const Kit *K){
  double complex *a = FB;
  for (long i = 0; i < K->N; i++) a[i] = 0;
  for (long i = 0; i < K->nBc; i++) a[K->Bc[i]] = 1;
  dft(K, a, 0);
  for (long i = 0; i < K->N; i++) a[i] = creal(a[i]) * creal(a[i]) + cimag(a[i]) * cimag(a[i]);
  dft(K, a, 1);
  for (long i = 0; i < K->N; i++) cX[i] = (int)lround(creal(a[i]));
}

/* canonical scalar rep: first nonzero digit == 1 */
static int is_scal_canon(const Kit *K, long s){
  if (!s) return 0; while (s % K->q == 0) s /= K->q; return (s % K->q) == 1;
}

static uint16_t *cnt; static int *Xbuf; static uint8_t *inX; static int *NBL, *NBH;
/* best s2 for given s1 (exact). returns orphans */
static int best_s2(const Kit *K, int s1, int *out_s2){
  int nx = 0;
  for (long i = 0; i < K->nBc; i++){ int b = K->Bc[i]; if (!K->inB[kit_sub(K, b, s1)]) Xbuf[nx++] = b; }
  memset(cnt, 0, sizeof(uint16_t) * K->N);
  const int LO = (int)K->LO, HI = (int)K->HI;
  for (int i = 0; i < nx; i++){ int x = Xbuf[i];
    const int *rl = K->addlo + (x % LO) * LO, *rh = K->addhi + (x / LO) * HI;
    for (long j = 0; j < K->nBc; j++) cnt[rl[NBL[j]] + LO * rh[NBH[j]]]++; }
  int bv = 1 << 30, bs = -1;
  for (long s = 1; s < K->N; s++) if (s != s1 && cnt[s] < bv){ bv = cnt[s]; bs = (int)s; }
  *out_s2 = bs; return bv;
}

typedef struct { int orph; int s[16]; int t; } Res;

static int cmp_c(const void *a, const void *b){ int x = cX[*(int*)a], y = cX[*(int*)b]; return (x > y) - (x < y); }
static int *cand;

static Res evaluate(Kit *K, int t, int nS1, int exact){
  kit_compute_ball(K);
  for (long j = 0; j < K->nBc; j++){ int nb = kit_neg(K, K->Bc[j]); NBL[j] = nb % (int)K->LO; NBH[j] = nb / (int)K->LO; }
  Res R = { 1 << 30, {0}, t };
  if (t == 1){ R.orph = (int)K->nBc; return R; }
  if (!exact) autocorr(K);
  long nc = 0;
  for (long s = 1; s < K->N; s++) if (is_scal_canon(K, s)) cand[nc++] = (int)s;
  if (!exact){ qsort(cand, nc, sizeof(int), cmp_c); if (nc > nS1) nc = nS1; }
  if (t == 2){ /* min c */ for (long i = 0; i < nc; i++){ int c = 0; for (long j=0;j<K->nBc;j++) if(!K->inB[kit_sub(K,K->Bc[j],cand[i])]) c++; if (c < R.orph){ R.orph = c; R.s[1] = cand[i]; } } return R; }
  for (long i = 0; i < nc; i++){ int s2, o = best_s2(K, cand[i], &s2); if (o < R.orph){ R.orph = o; R.s[1] = cand[i]; R.s[2] = s2; } }
  /* greedy extra cosets for t>3 */
  for (int j = 3; j < t; j++){
    int no = 0;
    for (long i = 0; i < K->nBc; i++){ int b = K->Bc[i], ok = 1; for (int u = 1; u < j; u++) if (K->inB[kit_sub(K, b, R.s[u])]){ ok = 0; break; } if (ok) Xbuf[no++] = b; }
    memset(cnt, 0, sizeof(uint16_t) * K->N);
    for (int a = 0; a < no; a++) for (long b = 0; b < K->nBc; b++) cnt[kit_sub(K, Xbuf[a], K->Bc[b])]++;
    int bv = 1 << 30, bs = 0; for (long s = 1; s < K->N; s++){ int dup = 0; for (int u = 1; u < j; u++) if (R.s[u] == s) dup = 1; if (!dup && cnt[s] < bv){ bv = cnt[s]; bs = (int)s; } }
    R.s[j] = bs; R.orph = bv;
  }
  return R;
}


/* exactT: todos os trios {0,s1,s2} com órfãs <= T (s1 em classes escalares, s2 qualquer).
 * Poda exata: as órfãs restritas a um subconjunto Y de X já são cota inferior; só os s2
 * com cnt_Y <= T são conferidos em X inteiro (com saída antecipada). */
static int exactT(Kit *K, int T, int m, int maxprint, int *bs1, int *bs2){
  kit_compute_ball(K);
  for (long j = 0; j < K->nBc; j++){ int nb = kit_neg(K, K->Bc[j]); NBL[j] = nb % (int)K->LO; NBH[j] = nb / (int)K->LO; }
  const int LO = (int)K->LO, HI = (int)K->HI;
  int best = 1 << 30, printed = 0;
  for (long s1 = 1; s1 < K->N; s1++){
    if (!is_scal_canon(K, s1)) continue;
    int nx = 0;
    for (long i = 0; i < K->nBc; i++){ int b = K->Bc[i]; if (!K->inB[kit_sub(K, b, (int)s1)]) Xbuf[nx++] = b; }
    /* embaralha parcialmente para Y ser amostra */
    int my = nx < m ? nx : m;
    for (int i = 0; i < my; i++){ int j = i + (int)(kit_rnd() % (nx - i)); int t = Xbuf[i]; Xbuf[i] = Xbuf[j]; Xbuf[j] = t; }
    memset(cnt, 0, sizeof(uint16_t) * K->N);
    for (int i = 0; i < my; i++){ int x = Xbuf[i];
      const int *rl = K->addlo + (x % LO) * LO, *rh = K->addhi + (x / LO) * HI;
      for (long j = 0; j < K->nBc; j++) cnt[rl[NBL[j]] + LO * rh[NBH[j]]]++; }
    for (long s2 = 1; s2 < K->N; s2++){
      if (s2 == s1 || cnt[s2] > T) continue;
      int o = cnt[s2];
      for (int i = my; i < nx && o <= T; i++) if (!K->inB[kit_sub(K, Xbuf[i], (int)s2)]) o++;
      if (o <= T){
        if (o < best){ best = o; *bs1 = (int)s1; *bs2 = (int)s2; }
        if (printed < maxprint){ printf("TRIO orphans=%d s1=%ld s2=%ld\n", o, s1, s2); printed++; }
      }
    }
  }
  return best;
}

/* ---------- beam: t classes laterais quaisquer (t>=2) ----------
 * Nível 1: os B1 melhores s1 (um por classe escalar) pela autocorrelação c(s1).
 * Nível j: para cada estado (conjunto parcial, órfãs O), conta |O ∩ (Bc+s)| para TODO s
 * de uma vez por DFT (correlação cruzada), gera as br melhores extensões; mantém os Bk
 * melhores estados distintos. Exato por nível; heurístico entre níveis (largura finita). */
typedef struct { int s[16]; int orph; } St;
static int cmp_st(const void *a, const void *b){ return ((St*)a)->orph - ((St*)b)->orph; }
static double complex *FO;
static void corr_counts(const Kit *K, const uint8_t *inO, int *out){
  for (long i = 0; i < K->N; i++) FO[i] = inO[i];
  dft(K, FO, 0);
  for (long i = 0; i < K->N; i++) FO[i] *= conj(FB[i]);
  dft(K, FO, 1);
  for (long i = 0; i < K->N; i++) out[i] = (int)lround(creal(FO[i]));
}
static Res beam(Kit *K, int t, int B1, int br, int Bk){
  kit_compute_ball(K);
  /* FB = DFT(Bc) e c(s) */
  for (long i = 0; i < K->N; i++) FB[i] = 0;
  for (long i = 0; i < K->nBc; i++) FB[K->Bc[i]] = 1;
  dft(K, FB, 0);
  { double complex *a = FO; for (long i = 0; i < K->N; i++) a[i] = FB[i] * conj(FB[i]); dft(K, a, 1); for (long i = 0; i < K->N; i++) cX[i] = (int)lround(creal(a[i])); }
  long nc = 0; for (long s = 1; s < K->N; s++) if (is_scal_canon(K, s)) cand[nc++] = (int)s;
  if (B1 > 0){ qsort(cand, nc, sizeof(int), cmp_c); if (nc > B1) nc = B1; }
  St *cur = malloc(sizeof(St) * (Bk > nc ? Bk : nc)), *nxt = malloc(sizeof(St) * ((Bk > nc ? Bk : nc) * (long)br + 16));
  int ncur = 0;
  for (long i = 0; i < nc; i++){ St x = {{0}, cX[cand[i]]}; x.s[1] = cand[i]; cur[ncur++] = x; }
  uint8_t *inO = calloc(K->N, 1); int *cc = malloc(sizeof(int) * K->N);
  for (int lev = 2; lev < t; lev++){
    int nn = 0;
    for (int a = 0; a < ncur; a++){
      memset(inO, 0, K->N);
      for (long i = 0; i < K->nBc; i++){ int b = K->Bc[i], ok = 1; for (int u = 1; u < lev; u++) if (K->inB[kit_sub(K, b, cur[a].s[u])]){ ok = 0; break; } if (ok) inO[b] = 1; }
      corr_counts(K, inO, cc);
      for (int u = 0; u < lev; u++) cc[cur[a].s[u]] = 1 << 30;
      /* br melhores */
      int bs[64], bv[64], nb = 0;
      for (long s = 1; s < K->N; s++){ int v = cc[s]; if (nb < br || v < bv[nb - 1]){ int i = nb < br ? nb++ : br - 1; while (i > 0 && bv[i - 1] > v){ bv[i] = bv[i - 1]; bs[i] = bs[i - 1]; i--; } bv[i] = v; bs[i] = (int)s; } }
      for (int i = 0; i < nb; i++){ St x = cur[a]; x.s[lev] = bs[i]; x.orph = bv[i]; nxt[nn++] = x; }
    }
    qsort(nxt, nn, sizeof(St), cmp_st);
    /* dedupe por conjunto ordenado */
    ncur = 0;
    for (int i = 0; i < nn && ncur < Bk; i++){
      int srt[16]; memcpy(srt, nxt[i].s, sizeof srt); qsort(srt + 1, lev, sizeof(int), cmp_int);
      int dup = 0; for (int j = 0; j < ncur && !dup; j++){ int s2[16]; memcpy(s2, cur[j].s, sizeof s2); qsort(s2 + 1, lev, sizeof(int), cmp_int); if (cur[j].orph == nxt[i].orph && !memcmp(s2, srt, sizeof(int) * (lev + 1))) dup = 1; }
      if (!dup) cur[ncur++] = nxt[i];
    }
  }
  Res R = { cur[0].orph, {0}, t }; memcpy(R.s, cur[0].s, sizeof R.s);
  free(cur); free(nxt); free(inO); free(cc);
  return R;
}

static void print_A(const Kit *K, char *buf){
  int p = 0;
  for (int i = 0; i < K->r; i++){ for (int j = 0; j < K->k; j++) buf[p++] = '0' + K->H[i][K->r + j]; buf[p++] = ' '; }
  buf[p ? p - 1 : 0] = 0;
}

static void alloc_eval(Kit *K){
  cX = malloc(sizeof(int) * K->N); FB = malloc(sizeof(double complex) * K->N);
  cnt = malloc(sizeof(uint16_t) * K->N); Xbuf = malloc(sizeof(int) * K->N); inX = calloc(K->N, 1);
  FO = malloc(sizeof(double complex) * K->N); cand = malloc(sizeof(int) * K->N); NBL = malloc(sizeof(int) * K->N); NBH = malloc(sizeof(int) * K->N);
  W = malloc(sizeof(double complex) * K->q);
  for (int i = 0; i < K->q; i++) W[i] = cexp(2.0 * M_PI * I * i / K->q);
}

/* ---------- geometria projetiva PG(k-1,q) ---------- */
static int q_, k_, NP;          /* NP = número de pontos */
static int PT[4096][6];          /* coordenadas normalizadas (1º não nulo = 1), em ordem de índice */
static int INV[64];
static int vec_index(const int *v){ /* normaliza e devolve índice */
  int f = -1; for (int i = 0; i < k_; i++) if (v[i]){ f = i; break; }
  if (f < 0) return -1;
  int c = INV[v[f]], w[6]; long key = 0;
  for (int i = 0; i < k_; i++){ w[i] = v[i] * c % q_; key = key * q_ + w[i]; }
  extern int *KEY2IDX; return KEY2IDX[key];
}
int *KEY2IDX;
static void build_points(void){
  for (int a = 1; a < q_; a++) for (int b = 1; b < q_; b++) if (a * b % q_ == 1) INV[a] = b;
  long tot = 1; for (int i = 0; i < k_; i++) tot *= q_;
  KEY2IDX = malloc(sizeof(int) * tot); for (long i = 0; i < tot; i++) KEY2IDX[i] = -1;
  NP = 0;
  /* referencial padrão primeiro: e_1..e_k, (1,...,1) */
  for (int i = 0; i <= k_; i++){ for (int j = 0; j < k_; j++) PT[NP][j] = (i == k_) ? 1 : (i == j); NP++; }
  for (long x = 1; x < tot; x++){
    int v[6]; long y = x; for (int i = k_ - 1; i >= 0; i--){ v[i] = y % q_; y /= q_; }
    int f = -1; for (int i = 0; i < k_; i++) if (v[i]){ f = i; break; }
    if (v[f] != 1) continue;
    int dup = 0; for (int p = 0; p <= k_; p++){ int same = 1; for (int j = 0; j < k_; j++) if (PT[p][j] != v[j]) same = 0; if (same) dup = 1; }
    if (dup) continue;
    memcpy(PT[NP++], v, sizeof(int) * k_);
  }
  for (int p = 0; p < NP; p++){ long key = 0; for (int j = 0; j < k_; j++) key = key * q_ + PT[p][j]; KEY2IDX[key] = p; }
}
/* inverte matriz k x k mod q; devolve 0 se singular */
static int mat_inv(int M[6][6], int R[6][6]){
  int a[6][12]; int k = k_;
  for (int i = 0; i < k; i++){ for (int j = 0; j < k; j++){ a[i][j] = M[i][j]; a[i][k + j] = (i == j); } }
  for (int c = 0; c < k; c++){
    int p = -1; for (int i = c; i < k; i++) if (a[i][c]){ p = i; break; }
    if (p < 0) return 0;
    if (p != c) for (int j = 0; j < 2 * k; j++){ int t = a[p][j]; a[p][j] = a[c][j]; a[c][j] = t; }
    int iv = INV[a[c][c]]; for (int j = 0; j < 2 * k; j++) a[c][j] = a[c][j] * iv % q_;
    for (int i = 0; i < k; i++) if (i != c && a[i][c]){ int f = a[i][c]; for (int j = 0; j < 2 * k; j++) a[i][j] = ((a[i][j] - f * a[c][j]) % q_ + q_) % q_; }
  }
  for (int i = 0; i < k; i++) for (int j = 0; j < k; j++) R[i][j] = a[i][k + j];
  return 1;
}
int cmp_int(const void *a, const void *b){ return *(int*)a - *(int*)b; }
static int nn_;
/* imagem ordenada de S pelo referencial (idx[0..k]); devolve 0 se não está em posição geral */
static int frame_image(const int *S, const int *fr, int *out){
  int P[6][6], Pi[6][6], lam[6];
  for (int i = 0; i < k_; i++) for (int j = 0; j < k_; j++) P[j][i] = PT[S[fr[i]]][j];
  if (!mat_inv(P, Pi)) return 0;
  for (int i = 0; i < k_; i++){ int s = 0; for (int j = 0; j < k_; j++) s += Pi[i][j] * PT[S[fr[k_]]][j]; lam[i] = s % q_; if (!lam[i]) return 0; }
  int Mx[6][6]; for (int i = 0; i < k_; i++) for (int j = 0; j < k_; j++) Mx[i][j] = INV[lam[i]] * Pi[i][j] % q_;
  for (int t = 0; t < nn_; t++){ int v[6]; for (int i = 0; i < k_; i++){ int s = 0; for (int j = 0; j < k_; j++) s += Mx[i][j] * PT[S[t]][j]; v[i] = s % q_; } out[t] = vec_index(v); }
  qsort(out, nn_, sizeof(int), cmp_int);
  return 1;
}
/* S ordenado é canônico? (nenhuma imagem lexicograficamente menor) */
static int is_canonical(const int *S){
  int fr[8], img[MAXN], used[MAXN] = {0};
  /* percorre tuplas ordenadas de k+1 posições distintas com pontos distintos */
  int depth = 0; fr[0] = -1;
  while (depth >= 0){
    fr[depth]++;
    if (fr[depth] >= nn_){ depth--; if (depth >= 0) used[fr[depth]] = 0; continue; }
    if (used[fr[depth]]) continue;
    int dupv = 0; for (int d = 0; d < depth; d++) if (S[fr[d]] == S[fr[depth]]) dupv = 1;
    /* para evitar duplicatas por pontos repetidos: usa só a 1ª ocorrência de cada ponto */
    if (fr[depth] > 0 && S[fr[depth] - 1] == S[fr[depth]]) continue;
    if (dupv) continue;
    if (depth == k_){
      if (frame_image(S, fr, img)){
        for (int t = 0; t < nn_; t++){ if (img[t] < S[t]) return 0; if (img[t] > S[t]) break; }
      }
      continue;
    }
    used[fr[depth]] = 1; depth++; fr[depth] = -1;
  }
  return 1;
}

static void code_from_points(Kit *K, const int *S){
  /* G (k x n) com colunas = pontos. Conjunto de informação = 1ª ocorrência de e_1..e_k. */
  int info[6], rest[MAXN], nr = 0, isinfo[MAXN] = {0};
  for (int i = 0; i < k_; i++){ for (int t = 0; t < nn_; t++) if (S[t] == i){ info[i] = t; isinfo[t] = 1; break; } }
  for (int t = 0; t < nn_; t++) if (!isinfo[t]) rest[nr++] = t;
  /* G = [I | P] nas coords (info, rest); H = [-P^T | I]; reordena para H = [I_r | A], A = -P^T */
  for (int i = 0; i < K->r; i++){
    for (int j = 0; j < K->r; j++) K->H[i][j] = (i == j);
    for (int j = 0; j < K->k; j++) K->H[i][K->r + j] = (q_ - PT[S[rest[i]]][j]) % q_;
  }
}

int main(int argc, char **argv){
  if (argc < 2){ fprintf(stderr, "uso: ver cabeçalho do arquivo\n"); return 2; }
  Kit K = {0};
  if (!strcmp(argv[1], "eval") || !strcmp(argv[1], "exact")){
    int ex = !strcmp(argv[1], "exact");
    K.q = atoi(argv[2]); K.n = atoi(argv[3]); K.R = atoi(argv[4]);
    int t = ex ? 3 : atoi(argv[5]), nS1 = ex ? 0 : atoi(argv[6]);
    const char *A = argv[ex ? 5 : 7];
    int rows = 1; for (const char *p = A; *p; p++) if (*p == ' ') rows++;
    K.r = rows; K.k = K.n - K.r;
    kit_init_tables(&K); kit_set_A(&K, A); alloc_eval(&K);
    double t0 = kit_now();
    Res R = evaluate(&K, t, nS1, ex);
    printf("{\"q\":%d,\"n\":%d,\"R\":%d,\"A\":\"%s\",\"nBc\":%ld,\"t\":%d,\"orphans\":%d,\"coset_syndromes\":[0", K.q, K.n, K.R, A, K.nBc, t, R.orph);
    for (int j = 1; j < t; j++) printf(",%d", R.s[j]);
    printf("],\"exact\":%s,\"secs\":%.2f}\n", ex ? "true" : "false", kit_now() - t0);
    return 0;
  }
  if (!strcmp(argv[1], "exactT")){ /* exactT q n R T A [m] [maxprint] */
    K.q = atoi(argv[2]); K.n = atoi(argv[3]); K.R = atoi(argv[4]); int T = atoi(argv[5]); const char *A = argv[6];
    int m = argc > 7 ? atoi(argv[7]) : 200, mp = argc > 8 ? atoi(argv[8]) : 1000;
    int rows = 1; for (const char *p = A; *p; p++) if (*p == ' ') rows++;
    K.r = rows; K.k = K.n - K.r; kit_init_tables(&K); kit_set_A(&K, A); alloc_eval(&K);
    double t0 = kit_now(); int s1 = 0, s2 = 0; int b = exactT(&K, T, m, mp, &s1, &s2);
    printf("{\"q\":%d,\"n\":%d,\"R\":%d,\"A\":\"%s\",\"nBc\":%ld,\"t\":3,\"T\":%d,\"orphans\":%d,\"coset_syndromes\":[0,%d,%d],\"exact\":true,\"secs\":%.1f}\n", K.q, K.n, K.R, A, K.nBc, T, b > T ? -1 : b, s1, s2, kit_now() - t0);
    return 0; }
  if (!strcmp(argv[1], "beam")){ /* beam q n R t B1 br Bk A */
    K.q = atoi(argv[2]); K.n = atoi(argv[3]); K.R = atoi(argv[4]); int t = atoi(argv[5]), B1 = atoi(argv[6]), br = atoi(argv[7]), Bk = atoi(argv[8]); const char *A = argv[9];
    int rows = 1; for (const char *p = A; *p; p++) if (*p == ' ') rows++;
    K.r = rows; K.k = K.n - K.r; kit_init_tables(&K); kit_set_A(&K, A); alloc_eval(&K);
    double t0 = kit_now(); Res R = beam(&K, t, B1, br, Bk);
    printf("{\"q\":%d,\"n\":%d,\"R\":%d,\"A\":\"%s\",\"nBc\":%ld,\"t\":%d,\"orphans\":%d,\"coset_syndromes\":[0", K.q, K.n, K.R, A, K.nBc, t, R.orph);
    for (int j = 1; j < t; j++) printf(",%d", R.s[j]);
    printf("],\"exact\":false,\"secs\":%.2f}\n", kit_now() - t0);
    return 0; }
  if (!strcmp(argv[1], "canon")){ /* canon q n R A : forma canônica do código de H=[I|A] */
    q_ = K.q = atoi(argv[2]); nn_ = K.n = atoi(argv[3]); K.R = atoi(argv[4]);
    const char *A = argv[5]; int rows = 1; for (const char *p = A; *p; p++) if (*p == ' ') rows++;
    K.r = rows; k_ = K.k = K.n - K.r; build_points(); kit_init_tables(&K); kit_set_A(&K, A);
    /* G = [-A^T | I_k]: coluna i<r = -A[i][.], coluna r+j = e_j */
    int S[MAXN];
    for (int i = 0; i < K.n; i++){ int v[6]; for (int j = 0; j < k_; j++) v[j] = i < K.r ? (q_ - K.H[i][K.r + j]) % q_ : (i - K.r == j); S[i] = vec_index(v); if (S[i] < 0){ printf("coluna nula\n"); return 1; } }
    qsort(S, nn_, sizeof(int), cmp_int);
    int best[MAXN]; memcpy(best, S, sizeof S);
    int fr[8], img[MAXN];
    /* força bruta sobre referenciais */
    int idx[8]; long tot = 1; for (int i = 0; i <= k_; i++) tot *= nn_;
    for (long c = 0; c < tot; c++){ long x = c; int ok = 1; for (int i = 0; i <= k_; i++){ idx[i] = x % nn_; x /= nn_; for (int j = 0; j < i; j++) if (idx[j] == idx[i]) ok = 0; } if (!ok) continue;
      memcpy(fr, idx, sizeof idx); if (!frame_image(S, fr, img)) continue;
      int less = 0; for (int t = 0; t < nn_; t++){ if (img[t] < best[t]){ less = 1; break; } if (img[t] > best[t]) break; }
      if (less) memcpy(best, img, sizeof img); }
    printf("pts:"); for (int i = 0; i < nn_; i++) printf(" %d", best[i]); printf("  canonical=%d\n", is_canonical(best));
    code_from_points(&K, best); kit_compute_ball(&K); char Ab[128]; print_A(&K, Ab); printf("A=%s nBc=%ld\n", Ab, K.nBc);
    return 0; }
  if (!strcmp(argv[1], "enum")){
    q_ = K.q = atoi(argv[2]); nn_ = K.n = atoi(argv[3]); k_ = K.k = atoi(argv[4]); K.R = atoi(argv[5]);
    int t = atoi(argv[6]), nS1 = atoi(argv[7]);
    long shard = argc > 8 ? atol(argv[8]) : 0, nshard = argc > 9 ? atol(argv[9]) : 1;
    int evalflag = !(argc > 10 && !strcmp(argv[10], "count"));
    K.r = K.n - K.k;
    build_points();
    kit_init_tables(&K); if (evalflag) alloc_eval(&K);
    int m = nn_ - k_ - 1; int T[MAXN]; for (int i = 0; i < m; i++) T[i] = 0;
    long seen = 0, acc = 0; double t0 = kit_now();
    while (1){
      seen++;
      if ((seen % nshard) == shard){
        int S[MAXN]; for (int i = 0; i <= k_; i++) S[i] = i; for (int i = 0; i < m; i++) S[k_ + 1 + i] = T[i];
        qsort(S, nn_, sizeof(int), cmp_int);
        if (is_canonical(S)){
          acc++;
          if (evalflag){
            code_from_points(&K, S);
            Res R = nS1 < 0 ? beam(&K, t, 0, 8, -nS1) : evaluate(&K, t, nS1, 0);
            char Ab[128]; print_A(&K, Ab);
            printf("{\"pts\":[");
            for (int i = 0; i < nn_; i++) printf("%s%d", i ? "," : "", S[i]);
            printf("],\"A\":\"%s\",\"nBc\":%ld,\"t\":%d,\"orphans\":%d,\"coset_syndromes\":[0", Ab, K.nBc, t, R.orph);
            for (int j = 1; j < t; j++) printf(",%d", R.s[j]);
            printf("]}\n"); fflush(stdout);
          }
        }
      }
      /* próximo multiconjunto não decrescente */
      int i = m - 1; while (i >= 0 && T[i] == NP - 1) i--;
      if (i < 0) break;
      T[i]++; for (int j = i + 1; j < m; j++) T[j] = T[i];
    }
    fprintf(stderr, "enum: shard %ld/%ld multisets=%ld classes=%ld secs=%.1f\n", shard, nshard, seen, acc, kit_now() - t0);
    return 0;
  }
  fprintf(stderr, "modo desconhecido\n"); return 2;
}
