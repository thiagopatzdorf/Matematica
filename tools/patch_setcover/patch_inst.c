/* patch_inst.c -- gera a instância de SET COVER UNICUSTO do remendo de uma cobertura q-ária.
 *
 * Dada uma BASE (lista de palavras, ex.: as classes laterais de um código linear), o
 * resíduo U = pontos de F_q^n a distância > R da base. Os conjuntos candidatos são as bolas
 * B_R(w) ∩ U de TODAS as palavras w do espaço (sem simetria imposta) com |B_R(w) ∩ U| >= T.
 * Um remendo de tamanho k é exatamente uma cobertura de U por k desses conjuntos.
 *
 * POR QUE o corte T: com T = 1 a instância de K_7(9,4) tem ~376 M incidências (2058 pontos ×
 * 182 791 por bola); conjuntos que cobrem poucos pontos quase nunca entram numa cobertura
 * mínima (a média num remendo de ~105 é 2058/105 ≈ 19,6). T é declarado no cabeçalho e no
 * relatório: a busca é ótima/completa só dentro da família com cobertura >= T.
 *
 * Saída (binária, little-endian, tudo uint32 salvo o cabeçalho):
 *   "PSC1" q n R T npts nsets npairs(uint64)
 *   pts[npts]   (inteiro da palavra, w = sum s[k] q^k)
 *   sets[nsets] (inteiro da palavra-centro)
 *   off[nsets+1] (uint64) e elem[npairs] (índice do ponto do resíduo), CSR por conjunto.
 *
 * Uso: patch_inst q n R base.txt T saida.bin [remendo.txt]
 *   remendo.txt (opcional): imprime a cobertura de cada palavra de um remendo conhecido.
 * Compilar: gcc -O3 -march=native -o patch_inst patch_inst.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int q, n, R;
static uint64_t pw[16], NN;
/* erros de peso 1..R: posições e valores, como deltas aplicados dígito a dígito */
static int nerr; static uint8_t (*epos)[8], (*eval)[8], *ewt;

static void gen_err(void){
  size_t cap = 1 << 20; epos = malloc(cap * 8); eval = malloc(cap * 8); ewt = malloc(cap);
  nerr = 0;
  int pos[8], val[8];
  for (int w = 1; w <= R; w++){
    for (int i = 0; i < w; i++) pos[i] = i;
    while (1){
      for (int i = 0; i < w; i++) val[i] = 1;
      while (1){
        if ((size_t)nerr >= cap){ cap *= 2; epos = realloc(epos, cap * 8); eval = realloc(eval, cap * 8); ewt = realloc(ewt, cap); }
        for (int i = 0; i < w; i++){ epos[nerr][i] = pos[i]; eval[nerr][i] = val[i]; }
        ewt[nerr++] = w;
        int i = w - 1; while (i >= 0 && val[i] == q - 1){ val[i] = 1; i--; }
        if (i < 0) break;
        val[i]++;
      }
      int i = w - 1; while (i >= 0 && pos[i] == n - w + i) i--;
      if (i < 0) break;
      pos[i]++; for (int j = i + 1; j < w; j++) pos[j] = pos[j - 1] + 1;
    }
  }
}
static inline uint64_t apply(uint64_t x, const uint8_t *d, int e){
  uint64_t y = x;
  for (int i = 0; i < ewt[e]; i++){ int p = epos[e][i]; int a = d[p]; int b = (a + eval[e][i]) % q; y += ((int64_t)b - a) * (int64_t)pw[p]; }
  return y;
}
static inline void digits(uint64_t x, uint8_t *d){ for (int i = 0; i < n; i++){ d[i] = x % q; x /= q; } }

int main(int argc, char **argv){
  if (argc < 7){ fprintf(stderr, "uso: patch_inst q n R base.txt T saida.bin\n"); return 2; }
  q = atoi(argv[1]); n = atoi(argv[2]); R = atoi(argv[3]); int T = atoi(argv[5]);
  pw[0] = 1; for (int i = 1; i <= n; i++) pw[i] = pw[i - 1] * q; NN = pw[n];
  gen_err();
  fprintf(stderr, "bola: %d erros não nulos\n", nerr);
  uint8_t *cov = calloc(NN, 1); if (!cov){ fprintf(stderr, "sem memória\n"); return 2; }
  FILE *F = fopen(argv[4], "r"); if (!F){ perror(argv[4]); return 2; }
  char line[256]; long nb = 0; uint8_t d[16];
  while (fgets(line, sizeof line, F)){
    int L = 0; while (line[L] >= '0' && line[L] <= '9') L++;
    if (L == 0) continue;
    if (L != n){ fprintf(stderr, "linha com %d dígitos\n", L); return 2; }
    uint64_t x = 0; for (int i = 0; i < n; i++){ int v = line[i] - '0'; if (v >= q){ fprintf(stderr, "dígito >= q\n"); return 2; } d[i] = v; x += v * pw[i]; }
    cov[x] = 1; for (int e = 0; e < nerr; e++) cov[apply(x, d, e)] = 1;
    nb++;
  }
  fclose(F);
  /* resíduo */
  uint32_t npts = 0; for (uint64_t x = 0; x < NN; x++) npts += !cov[x];
  uint32_t *pts = malloc(sizeof(uint32_t) * (npts + 1)); npts = 0;
  for (uint64_t x = 0; x < NN; x++) if (!cov[x]) pts[npts++] = x;
  fprintf(stderr, "base: %ld palavras, resíduo: %u pontos\n", nb, npts);
  /* cobertura de cada palavra sobre o resíduo (saturada em 255) */
  memset(cov, 0, NN);
  for (uint32_t i = 0; i < npts; i++){
    digits(pts[i], d); if (cov[pts[i]] < 255) cov[pts[i]]++;
    for (int e = 0; e < nerr; e++){ uint64_t y = apply(pts[i], d, e); if (cov[y] < 255) cov[y]++; }
  }
  uint64_t hist[256] = {0}; for (uint64_t x = 0; x < NN; x++) hist[cov[x]]++;
  int mx = 0; for (int c = 0; c < 256; c++) if (hist[c]) mx = c;
  fprintf(stderr, "cobertura máx por palavra: %d; histograma (c: #palavras) c>=1:", mx);
  for (int c = 1; c <= mx; c++) fprintf(stderr, " %d:%llu", c, (unsigned long long)hist[c]);
  fprintf(stderr, "\n");
  /* opcional: cobertura de cada palavra de um remendo conhecido (diagnóstico) */
  if (argc > 7){ FILE *W = fopen(argv[7], "r"); if (!W){ perror(argv[7]); return 2; }
    int h2[256] = {0}; while (fgets(line, sizeof line, W)){ int L = 0; while (line[L] >= '0' && line[L] <= '9') L++; if (L != n) continue;
      uint64_t x = 0; for (int i = 0; i < n; i++) x += (line[i] - '0') * pw[i]; h2[cov[x]]++; }
    fclose(W); fprintf(stderr, "remendo dado (cobertura: #palavras):"); for (int c = 0; c < 256; c++) if (h2[c]) fprintf(stderr, " %d:%d", c, h2[c]); fprintf(stderr, "\n"); }
  /* candidatos */
  uint32_t nsets = 0; uint64_t npairs = 0;
  for (uint64_t x = 0; x < NN; x++) if (cov[x] >= T){ nsets++; npairs += cov[x]; }
  uint32_t *sets = malloc(sizeof(uint32_t) * (nsets + 1)); uint64_t *off = calloc(nsets + 1, 8);
  uint32_t *cid = malloc(sizeof(uint32_t) * NN); if (!cid){ fprintf(stderr, "sem memória (cid)\n"); return 2; }
  nsets = 0;
  for (uint64_t x = 0; x < NN; x++){ if (cov[x] >= T){ cid[x] = nsets; sets[nsets] = x; off[nsets + 1] = off[nsets] + cov[x]; nsets++; } else cid[x] = UINT32_MAX; }
  if (mx == 255){ fprintf(stderr, "cobertura saturou em 255: aumente o tipo\n"); return 2; }
  uint32_t *elem = malloc(sizeof(uint32_t) * (npairs + 1)); uint64_t *fill = malloc(8 * (nsets + 1));
  memcpy(fill, off, 8 * (nsets + 1));
  for (uint32_t i = 0; i < npts; i++){
    digits(pts[i], d);
    uint32_t c = cid[pts[i]]; if (c != UINT32_MAX) elem[fill[c]++] = i;
    for (int e = 0; e < nerr; e++){ uint64_t y = apply(pts[i], d, e); c = cid[y]; if (c != UINT32_MAX) elem[fill[c]++] = i; }
  }
  for (uint32_t s = 0; s < nsets; s++) if (fill[s] != off[s + 1]){ fprintf(stderr, "CSR inconsistente\n"); return 3; }
  FILE *O = fopen(argv[6], "wb"); if (!O){ perror(argv[6]); return 2; }
  uint32_t hdr[7] = {0x31435350u, q, n, R, T, npts, nsets};
  fwrite(hdr, 4, 7, O); fwrite(&npairs, 8, 1, O);
  fwrite(pts, 4, npts, O); fwrite(sets, 4, nsets, O); fwrite(off, 8, nsets + 1, O); fwrite(elem, 4, npairs, O);
  fclose(O);
  fprintf(stderr, "instância: %u pontos, %u conjuntos (T=%d), %llu incidências\n", npts, nsets, T, (unsigned long long)npairs);
  printf("%u %u %llu %d\n", npts, nsets, (unsigned long long)npairs, mx);
  return 0;
}
