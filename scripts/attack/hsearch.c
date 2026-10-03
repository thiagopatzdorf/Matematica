/* hsearch.c -- escolhe a matriz de checagem H = [I_r | A] de um [n,k]_q para a base de classes
 * laterais com t grande (coset_sa).
 *
 * POR QUE: com t grande, a base cobre F_q^r com t translações de B = {H e : wt(e) <= R}.
 * Pela conta de esfera no espaço de síndromes, t >= q^r / |B|; colisões (duas e de peso <= R
 * com a mesma síndrome) encolhem B e sobem t. Maximizar |B| é o avaliador barato (uma DFS de
 * custo |bola de Hamming|) antes do caro (o SA de cobertura). Medido em K_7(9,4): bases com B
 * maior deram menos órfãs.
 *
 * Busca: reinícios aleatórios + subida de encosta trocando uma entrada de A por vez
 * (aceita se |B| não diminui). Imprime as melhores H distintas, uma por linha:
 *   nB=<|B|> N=<q^r> cota_t=<ceil(N/nB)> H="<linhas de H separadas por espaço>" A="<linhas de A>"
 * O H= serve direto como argumento de coset_sa.
 *
 * Uso: hsearch q n k R reinicios passos seed [ntop] [t] [L]
 *   t (padrão 1): objetivo = órfãs da melhor base de t classes (t <= 3), depois |B|.
 * Compilar: gcc -O3 -march=native -o hsearch hsearch.c -lm   (inclui ../search/kit.h)
 */
#include "../search/kit.h"

/* Objetivo lexicográfico: (órfãs da melhor base de t classes, -|B|), codificado num long
 * (maior = melhor). t=1: órfãs = |Bc|. t=2: exato, min_s |Bc ∩ (Bc+s)| por contagem de pares
 * O(|Bc|^2). t=3: para os L melhores s1 da contagem, o s2 ótimo é exato (|X|·|Bc|) -- o mesmo
 * avaliador do base_search eval, reescrito aqui para rodar dentro da subida de encosta. */
static int T_ = 1, L_ = 16; static uint32_t *cnt_; static int *X_, *ord_;
static int sub_(Kit *K, int a, int b){ return kit_sub(K, a, b); }
static long orphans(Kit *K, int *bs1, int *bs2){
  long nb = K->nBc; *bs1 = *bs2 = 0;
  if (T_ == 1 || nb == 0) return nb;
  memset(cnt_, 0, sizeof(uint32_t) * K->N);
  for (long i = 0; i < nb; i++) for (long j = 0; j < nb; j++) cnt_[sub_(K, K->Bc[i], K->Bc[j])]++;
  /* cnt_[s] = |Bc ∩ (Bc + s)| */
  if (T_ == 2){ long best = 1L << 40; for (long s = 1; s < K->N; s++) if (cnt_[s] < best){ best = cnt_[s]; *bs1 = (int)s; } return best; }
  /* L menores s1 */
  int nl = 0;
  for (long s = 1; s < K->N; s++){
    if (nl < L_){ int p = nl++; while (p > 0 && cnt_[ord_[p - 1]] > cnt_[s]){ ord_[p] = ord_[p - 1]; p--; } ord_[p] = (int)s; }
    else if (cnt_[s] < cnt_[ord_[nl - 1]]){ int p = nl - 1; while (p > 0 && cnt_[ord_[p - 1]] > cnt_[s]){ ord_[p] = ord_[p - 1]; p--; } ord_[p] = (int)s; }
  }
  long best = 1L << 40;
  uint32_t *c2 = cnt_ + K->N;
  for (int u = 0; u < nl; u++){
    int s1 = ord_[u], nx = 0;
    for (long i = 0; i < nb; i++){ int x = K->Bc[i]; if (!K->inB[sub_(K, x, s1)]) X_[nx++] = x; }
    if (nx >= best) continue;
    memset(c2, 0, sizeof(uint32_t) * K->N);
    for (int a = 0; a < nx; a++) for (long j = 0; j < nb; j++) c2[sub_(K, X_[a], K->Bc[j])]++;
    for (long s = 1; s < K->N; s++) if (s != s1 && c2[s] < best){ best = c2[s]; *bs1 = s1; *bs2 = (int)s; }
  }
  return best;
}
static long S1_, S2_;
static long evalB(Kit *K){ kit_compute_ball(K); int a, b; long o = orphans(K, &a, &b); S1_ = a; S2_ = b;
  return -o * (K->N + 1) + K->nB; }

int main(int argc, char **argv){
  if (argc < 8){ fprintf(stderr, "uso: hsearch q n k R reinicios passos seed [ntop]\n"); return 2; }
  Kit K = {0}; K.q = atoi(argv[1]); K.n = atoi(argv[2]); int k = atoi(argv[3]); K.R = atoi(argv[4]);
  int restarts = atoi(argv[5]); long steps = atol(argv[6]); kit_seed(strtoull(argv[7], 0, 10));
  int ntop = argc > 8 ? atoi(argv[8]) : 5; T_ = argc > 9 ? atoi(argv[9]) : 1; L_ = argc > 10 ? atoi(argv[10]) : 16;
  K.r = K.n - k; if (K.r > MAXR || K.n > MAXN){ fprintf(stderr, "r ou n grande demais\n"); return 2; }
  kit_init_tables(&K);
  cnt_ = malloc(sizeof(uint32_t) * 2 * K.N); X_ = malloc(sizeof(int) * K.N); ord_ = malloc(sizeof(int) * (L_ + 1));
  int q = K.q, r = K.r;
  for (int i = 0; i < r; i++) for (int j = 0; j < r; j++) K.H[i][j] = (i == j);
  long topB[64] = {0}, topS1[64], topS2[64]; char topS[64][256]; int nt = 0;
  for (int rs = 0; rs < restarts; rs++){
    for (int i = 0; i < r; i++) for (int j = r; j < K.n; j++) K.H[i][j] = (int)(kit_rnd() % q);
    long cur = evalB(&K); long cs1 = S1_, cs2 = S2_;
    for (long s = 0; s < steps; s++){
      int i = (int)(kit_rnd() % r), j = r + (int)(kit_rnd() % k), old = K.H[i][j];
      int v = (int)(kit_rnd() % q); if (v == old) continue;
      K.H[i][j] = v; long nb = evalB(&K);
      if (nb >= cur){ cur = nb; cs1 = S1_; cs2 = S2_; } else K.H[i][j] = old;
      if (T_ > 1 && cur > 0) break; /* órfãs = 0: base fechada, |B| já não importa */
      if (cur == K.N) break;
    }
    char hs[256] = {0}, as[256] = {0}; int p = 0, pa = 0;
    for (int i = 0; i < r; i++){ for (int j = 0; j < K.n; j++) hs[p++] = '0' + K.H[i][j]; hs[p++] = ' ';
      for (int j = r; j < K.n; j++) as[pa++] = '0' + K.H[i][j]; as[pa++] = ' '; }
    hs[p - 1] = 0; as[pa - 1] = 0;
    int dup = 0; for (int u = 0; u < nt; u++) if (!strcmp(topS[u], hs)) dup = 1;
    if (dup) continue;
    /* insere ordenado */
    int pos = nt < ntop ? nt : ntop; while (pos > 0 && topB[pos - 1] < cur) pos--;
    if (pos < ntop){ int last = nt < ntop ? nt : ntop - 1;
      for (int u = last; u > pos; u--){ topB[u] = topB[u - 1]; topS1[u] = topS1[u - 1]; topS2[u] = topS2[u - 1]; memcpy(topS[u], topS[u - 1], 256); }
      topB[pos] = cur; topS1[pos] = cs1; topS2[pos] = cs2; memcpy(topS[pos], hs, 256); if (nt < ntop) nt++;
      fprintf(stderr, "reinicio %d: orfas=%ld nB=%ld A=\"%s\"\n", rs, cur >= 0 ? 0 : (-cur) / (K.N + 1) + 1, (cur % (K.N + 1) + K.N + 1) % (K.N + 1), as); }
  }
  for (int u = 0; u < nt; u++)
  { long c = topB[u], nb = ((c % (K.N + 1)) + K.N + 1) % (K.N + 1), o = (nb - c) / (K.N + 1);
    printf("t=%d orfas=%ld s=[0,%ld,%ld] nB=%ld N=%ld H=\"%s\"\n", T_, o, topS1[u], topS2[u], nb, K.N, topS[u]); }
  return 0;
}
