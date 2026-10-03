/* patch_dump.c -- exporta o subproblema de remendo como cobertura de conjuntos (para ILP).
 *
 * POR QUE: quando o resíduo é pequeno (K_5(10,5): 1000 pontos), um ILP exato (patch_ilp.py,
 * HiGHS) dá o remendo ótimo entre os candidatos, ou ao menos a cota do LP -- e diz se o SA
 * (patch_opt) já está no ótimo, em vez de rodar mais horas no escuro.
 *
 * Entrada: base (palavras, uma por linha). Resíduo = pontos a distância > R da base (BFS em
 * camadas). Candidatos = palavras com >= tau pontos do resíduo na bola.
 * Saída (texto): linha 1 "npontos ncand"; depois uma linha por candidato:
 *   "<palavra> <k> <i1> ... <ik>"  (índices dos pontos do resíduo cobertos).
 *
 * Uso: patch_dump q n R base.txt tau > sub.txt
 * Compilar: gcc -O3 -march=native -o patch_dump patch_dump.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int q, n, R; static uint64_t pw[16], N;
static uint16_t *cnt; static int32_t *pid; static int32_t *cid; static long *coff, *cfill; static int32_t *clist; static int curp;
static void ball(uint64_t x, int start, int left, int mode){
  if (mode == 0){ if (cnt[x] < 65535) cnt[x]++; }
  else { int32_t c = cid[x]; if (c >= 0){ if (mode == 1) coff[c + 1]++; else clist[cfill[c]++] = curp; } }
  if (!left) return;
  for (int p = start; p < n; p++){ int d = (int)((x / pw[p]) % q); uint64_t b = x - (uint64_t)d * pw[p];
    for (int v = 0; v < q; v++) if (v != d) ball(b + (uint64_t)v * pw[p], p + 1, left - 1, mode); }
}
int main(int argc, char **argv){
  if (argc < 6){ fprintf(stderr, "uso: patch_dump q n R base.txt tau\n"); return 2; }
  q = atoi(argv[1]); n = atoi(argv[2]); R = atoi(argv[3]); int tau = atoi(argv[5]);
  pw[0] = 1; for (int i = 1; i <= n; i++) pw[i] = pw[i - 1] * q; N = pw[n];
  uint8_t *dist = malloc(N); memset(dist, 255, N);
  FILE *F = fopen(argv[4], "r"); char line[64];
  while (fgets(line, sizeof line, F)){ if ((int)strcspn(line, "\r\n") != n) continue; uint64_t x = 0; for (int i = 0; i < n; i++) x += (uint64_t)(line[i] - '0') * pw[i]; dist[x] = 0; }
  fclose(F);
  for (int d = 0; d < R; d++)
    for (uint64_t x = 0; x < N; x++) if (dist[x] == d)
      for (int p = 0; p < n; p++){ int dg = (int)((x / pw[p]) % q); uint64_t b = x - (uint64_t)dg * pw[p];
        for (int v = 0; v < q; v++){ uint64_t y = b + (uint64_t)v * pw[p]; if (dist[y] == 255) dist[y] = (uint8_t)(d + 1); } }
  pid = malloc(sizeof(int32_t) * N); int np = 0; uint64_t *P = malloc(sizeof(uint64_t) * N / 8 + 16);
  for (uint64_t x = 0; x < N; x++){ pid[x] = -1; if (dist[x] == 255){ pid[x] = np; P[np++] = x; } }
  free(dist);
  cnt = calloc(N, sizeof(uint16_t));
  for (int i = 0; i < np; i++) ball(P[i], 0, R, 0);
  /* listas invertidas a partir dos pontos do resíduo (|P|·|bola|), não dos candidatos:
   * a primeira versão enumerava a bola de cada candidato (292k x 320k em K_5(10,5)) e levava horas. */
  long nc = 0; cid = malloc(sizeof(int32_t) * N); uint64_t *cw = NULL; long capw = 0;
  for (uint64_t x = 0; x < N; x++){ cid[x] = -1; if (cnt[x] >= tau){ if (nc == capw){ capw = capw ? 2 * capw : 1 << 16; cw = realloc(cw, sizeof(uint64_t) * capw); } cw[nc] = x; cid[x] = (int32_t)nc++; } }
  free(cnt); free(pid);
  coff = calloc(nc + 1, sizeof(long));
  for (int i = 0; i < np; i++) ball(P[i], 0, R, 1);
  for (long c = 0; c < nc; c++) coff[c + 1] += coff[c];
  clist = malloc(sizeof(int32_t) * (coff[nc] + 1)); cfill = malloc(sizeof(long) * (nc + 1)); memcpy(cfill, coff, sizeof(long) * (nc + 1));
  for (int i = 0; i < np; i++){ curp = i; ball(P[i], 0, R, 2); }
  printf("%d %ld\n", np, nc);
  for (long c = 0; c < nc; c++){ uint64_t x = cw[c];
    for (int i = 0; i < n; i++) putchar('0' + (int)((x / pw[i]) % q));
    printf(" %ld", coff[c + 1] - coff[c]); for (long e = coff[c]; e < coff[c + 1]; e++) printf(" %d", clist[e]); putchar('\n'); }
  fprintf(stderr, "resíduo %d pontos, %ld candidatos (tau=%d)\n", np, nc, tau);
  return 0;
}
