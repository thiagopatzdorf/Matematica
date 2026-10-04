/* verify_bfs.c -- verificador independente de K_q(n,R) <= M por BFS multifonte.
 *
 * POR QUE existe, ao lado de tools/verify/verify.c: aquele marca a bola de raio R de cada
 * palavra (DFS sobre suportes); este faz o caminho contrário -- distância de TODO ponto de
 * F_q^n ao código por BFS em camadas (vizinhos = trocar um dígito), dist em uint8. Dois
 * algoritmos diferentes, de autores/sessões diferentes, para que um erro de enumeração de
 * bola não passe nos dois. Não compartilha código com os buscadores (coset_sa, patch_opt).
 *
 * Confere: dígitos < q, exatamente n dígitos por linha, sem duplicata, |C| = M (se dado),
 * e que max_x d(x, C) <= R. Imprime o histograma de distâncias e sai com 0 sse cobre.
 *
 * Uso: verify_bfs q n R arquivo [M]
 * Memória: q^n bytes (7^10 = 282 MB) + duas filas de q^n/… inteiros no pior caso.
 * Compilar: gcc -O3 -march=native -o verify_bfs verify_bfs.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

int main(int argc, char **argv){
  if (argc < 5){ fprintf(stderr, "uso: verify_bfs q n R arquivo [M]\n"); return 2; }
  int q = atoi(argv[1]), n = atoi(argv[2]), R = atoi(argv[3]); long M = argc > 5 ? atol(argv[5]) : -1;
  if (q < 2 || q > 10 || n < 1 || n > 12){ fprintf(stderr, "parâmetros fora do alcance\n"); return 2; }
  uint64_t pw[16]; pw[0] = 1; for (int i = 1; i <= n; i++) pw[i] = pw[i - 1] * (uint64_t)q;
  uint64_t N = pw[n];
  uint8_t *dist = malloc(N); if (!dist){ fprintf(stderr, "sem memória\n"); return 2; }
  memset(dist, 255, N);
  FILE *F = fopen(argv[4], "r"); if (!F){ perror(argv[4]); return 2; }
  uint32_t *fr = malloc(sizeof(uint32_t) * N / 4 + 1024); size_t cap = N / 4 + 1024, nf = 0;
  char line[256]; long cnt = 0, lineno = 0;
  while (fgets(line, sizeof line, F)){
    lineno++; size_t L = strcspn(line, "\r\n"); line[L] = 0; if (L == 0) continue;
    if ((int)L != n){ fprintf(stderr, "linha %ld: %zu dígitos, esperava %d\n", lineno, L, n); return 2; }
    uint64_t x = 0;
    for (int i = 0; i < n; i++){ int d = line[i] - '0'; if (d < 0 || d >= q){ fprintf(stderr, "linha %ld: dígito inválido\n", lineno); return 2; } x += (uint64_t)d * pw[i]; }
    if (dist[x] == 0){ fprintf(stderr, "linha %ld: palavra duplicada %s\n", lineno, line); return 2; }
    dist[x] = 0; if (nf >= cap){ fprintf(stderr, "código grande demais para a fila\n"); return 2; } fr[nf++] = (uint32_t)x; cnt++;
  }
  fclose(F);
  if (M >= 0 && cnt != M){ fprintf(stderr, "tamanho %ld != M=%ld\n", cnt, M); return 2; }
  /* BFS em camadas: a camada d+1 é varrida no próprio array (sem fila), o que dispensa memória
   * de fila do tamanho do espaço: para d >= 1, percorre todos os x com dist == d. */
  uint64_t hist[256] = {0}; hist[0] = (uint64_t)cnt;
  /* camada 1 a partir da lista */
  for (size_t i = 0; i < nf; i++){ uint64_t x = fr[i];
    for (int p = 0; p < n; p++){ int dg = (int)((x / pw[p]) % q); uint64_t b = x - (uint64_t)dg * pw[p];
      for (int v = 0; v < q; v++) if (v != dg){ uint64_t y = b + (uint64_t)v * pw[p]; if (dist[y] == 255){ dist[y] = 1; hist[1]++; } } } }
  free(fr);
  int d = 1;
  while (hist[d] && d < 254){
    for (uint64_t x = 0; x < N; x++) if (dist[x] == d){
      for (int p = 0; p < n; p++){ int dg = (int)((x / pw[p]) % q); uint64_t b = x - (uint64_t)dg * pw[p];
        for (int v = 0; v < q; v++) if (v != dg){ uint64_t y = b + (uint64_t)v * pw[p]; if (dist[y] == 255){ dist[y] = (uint8_t)(d + 1); hist[d + 1]++; } } } }
    d++;
  }
  uint64_t tot = 0; int maxd = 0;
  for (int i = 0; i < 256; i++) if (hist[i]){ tot += hist[i]; maxd = i; }
  printf("q=%d n=%d R=%d |C|=%ld pontos=%llu alcançados=%llu raio_de_cobertura=%d\n", q, n, R, cnt,
         (unsigned long long)N, (unsigned long long)tot, maxd);
  printf("histograma:"); for (int i = 0; i <= maxd; i++) printf(" d%d=%llu", i, (unsigned long long)hist[i]); printf("\n");
  int ok = (tot == N) && maxd <= R;
  printf("%s\n", ok ? "COBRE" : "NAO COBRE");
  return ok ? 0 : 1;
}
