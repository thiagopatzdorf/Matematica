/* verify_bruteforce.c -- verificador A: força bruta absoluta.
 *
 * Para TODO x em (Z/7)^9 (7^9 = 40 353 607 vetores) calcula d(x,C) = min_{c em C} d_H(x,c),
 * comparando dígito a dígito com TODAS as palavras (para de comparar com uma palavra só quando a
 * distância parcial já é >= o mínimo achado, o que não muda o mínimo). Sem tabelas, sem simetria.
 *
 * Uso: verify_bruteforce code.txt [N_esperado=1137] [R=4]
 * Compilar: gcc -O2 -fopenmp -o verify_bruteforce verify_bruteforce.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define Q 7
#define N 9
#define SPACE 40353607L          /* 7^9 */

static int nw;
static unsigned char (*W)[N];

static int parse(const char *path){        /* parser próprio e estrito */
  FILE *f = fopen(path, "r"); if (!f){ perror(path); return -1; }
  int cap = 4096; W = malloc(sizeof(*W) * cap); nw = 0;
  char line[64];
  while (fgets(line, sizeof line, f)){
    size_t L = strlen(line);
    if (L != N + 1 || line[N] != '\n'){ fprintf(stderr, "FAIL formato: linha %d com tamanho errado\n", nw + 1); return -1; }
    for (int j = 0; j < N; j++){
      if (line[j] < '0' || line[j] > '6'){ fprintf(stderr, "FAIL formato: linha %d, símbolo '%c' fora de 0..6\n", nw + 1, line[j]); return -1; }
      W[nw][j] = (unsigned char)(line[j] - '0');
    }
    if (++nw == cap){ cap *= 2; W = realloc(W, sizeof(*W) * cap); }
  }
  fclose(f);
  for (int a = 0; a < nw; a++) for (int b = a + 1; b < nw; b++)
    if (!memcmp(W[a], W[b], N)){ fprintf(stderr, "FAIL formato: palavras %d e %d repetidas\n", a + 1, b + 1); return -1; }
  return 0;
}

int main(int argc, char **argv){
  if (argc < 2){ fprintf(stderr, "uso: %s code.txt [N_esperado] [R]\n", argv[0]); return 2; }
  int esperado = argc > 2 ? atoi(argv[2]) : 1137, R = argc > 3 ? atoi(argv[3]) : 4;
  if (parse(argv[1])) return 1;
  long cnt[N + 1] = {0};
  long far_count = 0; int maxd = 0;
  #pragma omp parallel
  {
    long lc[N + 1] = {0};
    #pragma omp for schedule(static)
    for (long blk = 0; blk < SPACE / Q; blk++){           /* x = blk*7 + x0 */
      unsigned char x[N]; long t = blk;
      for (int j = 1; j < N; j++){ x[j] = (unsigned char)(t % Q); t /= Q; }
      for (int x0 = 0; x0 < Q; x0++){
        x[0] = (unsigned char)x0;
        int best = N + 1;
        for (int w = 0; w < nw && best > 0; w++){
          int d = 0;
          for (int j = 0; j < N && d < best; j++) d += (x[j] != W[w][j]);
          if (d < best) best = d;
        }
        lc[best]++;
      }
    }
    #pragma omp critical
    for (int r = 0; r <= N; r++) cnt[r] += lc[r];
  }
  long total = 0, uncovered = 0;
  for (int r = 0; r <= N; r++){ total += cnt[r]; if (cnt[r]) maxd = r; if (r > R) uncovered += cnt[r]; }
  far_count = cnt[maxd];
  /* exemplos dos pontos mais distantes: os 3 de menor índice i(x) = sum x_j 7^j */
  int shown = 0; char ex[3][N + 1];
  for (long i = 0; i < SPACE && shown < 3; i++){
    unsigned char x[N]; long t = i; for (int j = 0; j < N; j++){ x[j] = (unsigned char)(t % Q); t /= Q; }
    int best = N + 1;
    for (int w = 0; w < nw && best > 0; w++){ int d = 0; for (int j = 0; j < N && d < best; j++) d += (x[j] != W[w][j]); if (d < best) best = d; }
    if (best == maxd){ for (int j = 0; j < N; j++) ex[shown][j] = (char)('0' + x[j]); ex[shown][N] = 0; shown++; }
  }
  printf("verificador A (força bruta, C/OpenMP)\n");
  printf("q = %d\nn = %d\nR = %d\n|C| = %d\n", Q, N, R, nw);
  for (int r = 0; r <= N; r++) if (cnt[r] || r <= R) printf("N_%d = %ld\n", r, cnt[r]);
  printf("total = %ld (esperado %ld)\ncovered = %ld\nuncovered = %ld\nmax_distance = %d\nfarthest_points = %ld\n",
         total, SPACE, total - uncovered, uncovered, maxd, far_count);
  for (int s = 0; s < shown; s++) printf("example_farthest = %s\n", ex[s]);
  int ok = (nw == esperado) && (total == SPACE) && (uncovered == 0) && (maxd <= R);
  printf("%s\n", ok ? "PASS" : "FAIL");
  return ok ? 0 : 1;
}
