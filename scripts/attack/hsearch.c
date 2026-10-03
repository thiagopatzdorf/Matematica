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
 * Uso: hsearch q n k R reinicios passos seed [ntop]
 * Compilar: gcc -O3 -march=native -o hsearch hsearch.c -lm   (inclui ../search/kit.h)
 */
#include "../search/kit.h"

static long evalB(Kit *K){ kit_compute_ball(K); return K->nB; }

int main(int argc, char **argv){
  if (argc < 8){ fprintf(stderr, "uso: hsearch q n k R reinicios passos seed [ntop]\n"); return 2; }
  Kit K = {0}; K.q = atoi(argv[1]); K.n = atoi(argv[2]); int k = atoi(argv[3]); K.R = atoi(argv[4]);
  int restarts = atoi(argv[5]); long steps = atol(argv[6]); kit_seed(strtoull(argv[7], 0, 10));
  int ntop = argc > 8 ? atoi(argv[8]) : 5;
  K.r = K.n - k; if (K.r > MAXR || K.n > MAXN){ fprintf(stderr, "r ou n grande demais\n"); return 2; }
  kit_init_tables(&K);
  int q = K.q, r = K.r;
  for (int i = 0; i < r; i++) for (int j = 0; j < r; j++) K.H[i][j] = (i == j);
  long topB[64] = {0}; char topS[64][256]; int nt = 0;
  for (int rs = 0; rs < restarts; rs++){
    for (int i = 0; i < r; i++) for (int j = r; j < K.n; j++) K.H[i][j] = (int)(kit_rnd() % q);
    long cur = evalB(&K);
    for (long s = 0; s < steps; s++){
      int i = (int)(kit_rnd() % r), j = r + (int)(kit_rnd() % k), old = K.H[i][j];
      int v = (int)(kit_rnd() % q); if (v == old) continue;
      K.H[i][j] = v; long nb = evalB(&K);
      if (nb >= cur) cur = nb; else K.H[i][j] = old;
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
      for (int u = last; u > pos; u--){ topB[u] = topB[u - 1]; memcpy(topS[u], topS[u - 1], 256); }
      topB[pos] = cur; memcpy(topS[pos], hs, 256); if (nt < ntop) nt++;
      fprintf(stderr, "reinicio %d: nB=%ld (melhor %ld) A=\"%s\"\n", rs, cur, topB[0], as); }
  }
  for (int u = 0; u < nt; u++)
    printf("nB=%ld N=%ld cota_t=%ld H=\"%s\"\n", topB[u], K.N, (K.N + topB[u] - 1) / topB[u], topS[u]);
  return 0;
}
