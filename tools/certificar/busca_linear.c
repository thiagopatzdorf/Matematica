/* Busca local de código linear [n, n-r]_q com raio de cobertura R (q qualquer: aritmética em Z_q).
 *
 * H = [A | I_r]; A tem k = n - r colunas em Z_q^r. Custo = número de síndromes que nenhuma
 * combinação de <= R colunas (com multiplicadores 1..q-1) alcança: BFS nas q^r síndromes.
 * Passo: troca uma coluna de A por um vetor aleatório; aceita se o custo não sobe, ou com
 * probabilidade exp(-delta/T) (recozimento). O juiz é o verificador (lineares.cobre_por_sindromes
 * e o kernel do Lean), não esta busca: ela só propõe.
 *
 * uso: busca_linear q n r R segundos semente
 * saída (código 0, custo 0): as k colunas de A, uma por linha, dígitos separados por espaço.
 * código 1: não achou no tempo dado (o melhor custo vai para stderr). */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int q, n, r, R, k, nm;
static long S, pw[32];
static int *col, *dig, *fila, *vs;
static unsigned char *dist;

static int soma(int a, int b) {
  if (q == 2) return a ^ b;
  int s = 0, *da = dig + (long)a * r, *db = dig + (long)b * r;
  for (int i = 0; i < r; i++) { int d = da[i] + db[i]; if (d >= q) d -= q; s += d * pw[i]; }
  return s;
}

static int escala(int v, int a) {
  int s = 0;
  for (int i = 0; i < r; i++) s += ((dig[(long)v * r + i] * a) % q) * pw[i];
  return s;
}

static long custo(void) {
  for (int c = 0; c < n; c++)
    for (int a = 1; a <= nm; a++) vs[c * nm + a - 1] = escala(col[c], a);
  memset(dist, 255, S);
  dist[0] = 0;
  long h = 0, t = 0, cob = 1;
  fila[t++] = 0;
  while (h < t) {
    int s = fila[h++], d = dist[s];
    if (d >= R) continue;
    for (int j = 0; j < n * nm; j++) {
      int u = soma(s, vs[j]);
      if (dist[u] == 255) { dist[u] = d + 1; fila[t++] = u; cob++; }
    }
  }
  return S - cob;
}

int main(int argc, char **argv) {
  if (argc < 7) { fprintf(stderr, "uso: busca_linear q n r R segundos semente\n"); return 2; }
  q = atoi(argv[1]); n = atoi(argv[2]); r = atoi(argv[3]); R = atoi(argv[4]);
  double seg = atof(argv[5]);
  srand(atoi(argv[6]));
  k = n - r; nm = q - 1;
  if (q < 2 || r < 1 || k < 1 || R < 1 || R > 254) { fprintf(stderr, "parâmetros inválidos\n"); return 2; }
  pw[0] = 1;
  for (int i = 1; i <= r; i++) pw[i] = pw[i - 1] * q;
  S = pw[r];
  col = malloc(sizeof(int) * n); vs = malloc(sizeof(int) * n * nm);
  dist = malloc(S); fila = malloc(sizeof(int) * S); dig = malloc(sizeof(int) * S * r);
  for (long s = 0; s < S; s++) { long x = s; for (int i = 0; i < r; i++) { dig[s * r + i] = x % q; x /= q; } }
  for (int i = 0; i < r; i++) col[k + i] = pw[i];
  for (int j = 0; j < k; j++) col[j] = 1 + rand() % (S - 1);
  long c = custo(), melhor = c, it = 0;
  double T = 2.0;
  clock_t t0 = clock();
  while (c > 0 && (double)(clock() - t0) / CLOCKS_PER_SEC < seg) {
    int j = rand() % k, velho = col[j];
    col[j] = 1 + rand() % (S - 1);
    long c2 = custo();
    it++;
    if (c2 <= c || exp((c - c2) / T) > (double)rand() / RAND_MAX) { c = c2; if (c < melhor) melhor = c; }
    else col[j] = velho;
    T *= 0.9995;
    if (T < 0.05) T = 0.05;
  }
  fprintf(stderr, "q=%d n=%d r=%d R=%d custo=%ld melhor=%ld iteracoes=%ld\n", q, n, r, R, c, melhor, it);
  if (c != 0) return 1;
  for (int j = 0; j < k; j++)
    for (int i = 0; i < r; i++) printf("%d%s", dig[(long)col[j] * r + i], i < r - 1 ? " " : "\n");
  return 0;
}
