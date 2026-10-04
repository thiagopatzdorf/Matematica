/* Sistema de cobertura M (Östergård–Blass; LMT 2009, eq. 2.2) para K_3(v,1), m = 2.
 *
 * y[j][k] = número de palavras do código com prefixo (j,k). Para todo bloco (j,k):
 *   s*y[j][k] + (soma dos vizinhos de torre) >= N,   s = 1 + 2(v-2),  N = 3^(v-2),
 * soma = M, e opcionalmente linhas (e colunas) >= p (cota de fibra, ver README).
 * Imprime um representante por órbita do grupo de ordem 72 (linhas, colunas, transposta):
 * o menor lexicográfico das 72 imagens. Última linha: "# orbitas O rotuladas L".
 *
 * Uso: sistema v M [p_linha] [p_coluna]
 */
#include <stdio.h>
#include <stdlib.h>

static int V, M, PL, PC, S, N;
static int y[9];
static long long rot = 0, orb = 0;
static int perm[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};

static int ok_cel(int c) {
  int j = c / 3, k = c % 3, t = S * y[c];
  for (int a = 0; a < 3; a++) { if (a != k) t += y[j*3+a]; if (a != j) t += y[a*3+k]; }
  return t >= N;
}

static int menor_que(const int *a, const int *b) {
  for (int i = 0; i < 9; i++) if (a[i] != b[i]) return a[i] < b[i];
  return 0;
}

static int canonico(void) {
  int z[9];
  for (int t = 0; t < 2; t++) for (int r = 0; r < 6; r++) for (int s = 0; s < 6; s++) {
    for (int j = 0; j < 3; j++) for (int k = 0; k < 3; k++) {
      int jj = perm[r][j], kk = perm[s][k];
      z[j*3+k] = t ? y[kk*3+jj] : y[jj*3+kk];
    }
    if (menor_que(z, y)) return 0;
  }
  return 1;
}

static void dfs(int c, int resto) {
  if (c == 9) {
    if (resto != 0) return;
    for (int i = 0; i < 9; i++) if (!ok_cel(i)) return;
    rot++;
    if (getenv("TODAS") || canonico()) {
      orb++;
      for (int i = 0; i < 9; i++) printf(i ? " %d" : "%d", y[i]);
      printf("\n");
    }
    return;
  }
  int lo = 0, hi = resto;
  if (c == 8) lo = hi = resto;
  for (int x = lo; x <= hi; x++) {
    y[c] = x;
    int bom = 1;
    if (PL) { int lin = c / 3, r = 0; for (int t = lin*3; t <= c; t++) r += y[t];
      if (r > M - (2) * PL) bom = 0;
      if (c % 3 == 2 && resto - x < PL * (2 - lin)) bom = 0; }
    if (bom && c % 3 == 2 && PL) { int r = y[c-2] + y[c-1] + y[c]; if (r < PL) bom = 0; }
    if (bom && c >= 6 && PC) { int k = c % 3; if (y[k] + y[3+k] + y[6+k] < PC) bom = 0; }
    /* cotas: célula c fecha a vizinhança das células cuja linha e coluna já estão completas */
    if (bom && c == 8) for (int i = 0; i < 9; i++) if (!ok_cel(i)) { bom = 0; break; }
    /* poda: para cada célula i já atribuída, a vizinhança recebe no máximo M - y[i] menos o que
       já foi posto fora dela; se nem assim chega a N, nenhum completamento serve */
    for (int i = 0; bom && i <= c; i++) {
      int fora = 0;
      for (int t = 0; t <= c; t++)
        if (t != i && t / 3 != i / 3 && t % 3 != i % 3) fora += y[t];
      if (S * y[i] + (M - y[i] - fora) < N) bom = 0;
    }
    if (bom) dfs(c + 1, resto - x);
  }
}

int main(int argc, char **argv) {
  if (argc < 3) { fprintf(stderr, "uso: sistema v M [p_linha] [p_coluna]\n"); return 2; }
  V = atoi(argv[1]); M = atoi(argv[2]);
  PL = argc > 3 ? atoi(argv[3]) : 0; PC = argc > 4 ? atoi(argv[4]) : 0;
  S = 1 + 2 * (V - 2); N = 1; for (int i = 0; i < V - 2; i++) N *= 3;
  dfs(0, M);
  printf("# orbitas %lld rotuladas %lld\n", orb, rot);
  return 0;
}
