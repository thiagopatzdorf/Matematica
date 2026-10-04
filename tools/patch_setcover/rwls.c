/* rwls.c -- busca local de SET COVER UNICUSTO com pesos de linha e configuration checking.
 *
 * Algoritmo: RWLS de Gao, Yao, Weise & Li (2015), "An efficient local search heuristic with
 * row weighting for the unicost set covering problem", EJOR 246(3):750-761,
 * doi:10.1016/j.ejor.2015.05.038. Com a opção -c 2, o configuration checking passa a ser o
 * "por hiperaresta" de Wang, Ouyang, Zhang & Yin (2017), Sci. China Inf. Sci. 60:062103,
 * doi:10.1007/s11432-015-5377-8 (NuSC). Ver README.md para o pseudocódigo e o que é nosso.
 *
 * Núcleo (RWLS):
 *   - cada ponto (linha) e tem peso w(e), começa em 1;
 *   - score(s) = soma de w(e) dos pontos descobertos de s, se s está fora da solução;
 *              = -soma de w(e) dos pontos que SÓ s cobre, se s está dentro;
 *   - quando a solução cobre tudo: grava, tira o conjunto de maior score e continua (k-1);
 *   - passo: tira o conjunto da solução de maior score (empate: o mais antigo), que não seja
 *     o recém-posto (tabu); sorteia um ponto descoberto e põe, entre os conjuntos que o
 *     cobrem e têm canAdd, o de maior score (empate: o mais antigo); por fim w(e)++ para
 *     todo ponto descoberto;
 *   - canAdd (configuration checking): conjunto tirado fica proibido de voltar até que a
 *     vizinhança mude. -c 1 (RWLS): vizinho = compartilha um ponto, e todo flip de s libera
 *     os vizinhos. -c 2 (NuSC): libera os conjuntos de um ponto que mudou de coberto para
 *     descoberto ou vice-versa. -c 0: sem CC.
 *
 * POR QUE o xor por ponto: quando um ponto tem exatamente 1 cobridor na solução, precisamos
 * dele para ajustar o score em O(1); guardar o xor dos ids dos cobridores dá isso de graça.
 *
 * Uso: rwls inst.bin [-t segundos] [-s semente] [-k alvo] [-c 0|1|2] [-i inicial.txt]
 *                   [-o melhor.txt] [-q] [-T corte] [-b 0|1]
 *   Para em -t segundos ou quando acha cobertura com <= alvo conjuntos.
 *   -i: palavras (uma por linha) que viram a solução inicial (as que não são candidatas
 *       são ignoradas, com aviso); sem -i, guloso + remoção de redundantes.
 *   -o: grava a melhor cobertura (palavras-centro, mesma convenção de dígitos do repo) a
 *       cada recorde. Imprime "best k t_s iter" a cada recorde e um resumo JSON no fim.
 * Compilar: gcc -O3 -march=native -o rwls rwls.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <limits.h>

typedef long long ll;
static uint32_t q, n, R, T, npts, nsets; static uint64_t npairs;
static uint32_t *pts, *setw, *elem, *selem; static uint64_t *off, *eoff;
static ll *score, *wgt; static uint32_t *cnt, *xorc; static uint8_t *insol, *canadd;
static ll *stamp; static ll iter = 0;
static uint32_t *sol, *solpos, nsol = 0; static uint32_t *unc, *uncpos, nunc = 0;
static int ccmode = 1, tiebreak = 0;
/* Desempate. RWLS: o mais antigo. -b 1 (nosso, medido em K_7(9,4)): antes da idade, o MAIOR
 * conjunto ao pôr e o MENOR ao tirar. POR QUE: com corte T baixo há ~170 mil conjuntos de
 * tamanho 18-19 e só 3 087 de tamanho 24; empatados em score, o "mais antigo" é quase sempre
 * um 18 nunca usado, e a solução se enche de conjuntos pequenos. */
static inline uint32_t ssize(uint32_t s);
static inline int better_add(uint32_t s, uint32_t b){
  if (tiebreak){ uint32_t a = ssize(s), c = ssize(b); if (a != c) return a > c; }
  return stamp[s] < stamp[b];
}
static inline int better_del(uint32_t s, uint32_t b){
  if (tiebreak){ uint32_t a = ssize(s), c = ssize(b); if (a != c) return a < c; }
  return stamp[s] < stamp[b];
}

static uint64_t rng_s;
static inline uint64_t rnd(void){ rng_s ^= rng_s << 13; rng_s ^= rng_s >> 7; rng_s ^= rng_s << 17; return rng_s; }
static double now(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }

static inline uint32_t ssize(uint32_t s){ return (uint32_t)(off[s + 1] - off[s]); }
static void unc_add(uint32_t e){ uncpos[e] = nunc; unc[nunc++] = e; }
static void unc_del(uint32_t e){ uint32_t p = uncpos[e], l = unc[--nunc]; unc[p] = l; uncpos[l] = p; }
static void neigh_free(uint32_t s){
  for (uint64_t a = off[s]; a < off[s + 1]; a++){ uint32_t e = elem[a];
    for (uint64_t b = eoff[e]; b < eoff[e + 1]; b++) canadd[selem[b]] = 1; }
}
static void add_set(uint32_t s){
  score[s] = -score[s]; insol[s] = 1; solpos[s] = nsol; sol[nsol++] = s; stamp[s] = iter;
  for (uint64_t a = off[s]; a < off[s + 1]; a++){
    uint32_t e = elem[a], c = cnt[e];
    if (c == 0){
      unc_del(e);
      for (uint64_t b = eoff[e]; b < eoff[e + 1]; b++){ uint32_t t = selem[b]; if (t != s){ score[t] -= wgt[e]; if (ccmode == 2) canadd[t] = 1; } }
    } else if (c == 1){ score[xorc[e]] += wgt[e]; }
    cnt[e] = c + 1; xorc[e] ^= s;
  }
  if (ccmode == 1) neigh_free(s);
}
static void del_set(uint32_t s){
  score[s] = -score[s]; insol[s] = 0; { uint32_t p = solpos[s], l = sol[--nsol]; sol[p] = l; solpos[l] = p; } stamp[s] = iter;
  for (uint64_t a = off[s]; a < off[s + 1]; a++){
    uint32_t e = elem[a], c = cnt[e];
    xorc[e] ^= s; cnt[e] = c - 1;
    if (c == 1){
      unc_add(e);
      for (uint64_t b = eoff[e]; b < eoff[e + 1]; b++){ uint32_t t = selem[b]; if (t != s){ score[t] += wgt[e]; if (ccmode == 2) canadd[t] = 1; } }
    } else if (c == 2){ score[xorc[e]] -= wgt[e]; }
  }
  if (ccmode == 1) neigh_free(s);
  if (ccmode) canadd[s] = 0;
}
static void bump_weights(void){
  for (uint32_t i = 0; i < nunc; i++){ uint32_t e = unc[i]; wgt[e]++;
    for (uint64_t b = eoff[e]; b < eoff[e + 1]; b++) score[selem[b]]++; }
}

#ifdef CHECK
static void check(void){
  for (uint32_t e = 0; e < npts; e++){ uint32_t c = 0, x = 0; for (uint64_t b = eoff[e]; b < eoff[e + 1]; b++) if (insol[selem[b]]){ c++; x ^= selem[b]; }
    if (c != cnt[e] || x != xorc[e]){ fprintf(stderr, "CHECK cnt/xor e=%u\n", e); exit(9); } }
  for (uint32_t s = 0; s < nsets; s++){ ll v = 0; for (uint64_t a = off[s]; a < off[s + 1]; a++){ uint32_t e = elem[a];
      if (insol[s] && cnt[e] == 1) v -= wgt[e]; if (!insol[s] && cnt[e] == 0) v += wgt[e]; }
    if (v != score[s]){ fprintf(stderr, "CHECK score s=%u %lld != %lld (in=%d)\n", s, score[s], v, insol[s]); exit(9); } }
}
#endif
static int find_set(uint32_t w){ /* setw é crescente (patch_inst gera em ordem) */
  long lo = 0, hi = (long)nsets - 1;
  while (lo <= hi){ long m = (lo + hi) / 2; if (setw[m] == w) return (int)m; if (setw[m] < w) lo = m + 1; else hi = m - 1; }
  return -1;
}
static void save(const char *fn, uint32_t *b, uint32_t k){
  if (!fn) return;
  char tmp[1024]; snprintf(tmp, sizeof tmp, "%s.tmp", fn);
  FILE *F = fopen(tmp, "w"); if (!F){ perror(tmp); return; }
  for (uint32_t i = 0; i < k; i++){ uint32_t x = setw[b[i]]; if (q < 2){ fprintf(F, "%u\n", x); continue; } for (uint32_t j = 0; j < n; j++){ fputc('0' + x % q, F); x /= q; } fputc('\n', F); }
  fclose(F); rename(tmp, fn);
}

int main(int argc, char **argv){
  if (argc < 2){ fprintf(stderr, "uso: rwls inst.bin [-t s] [-s seed] [-k alvo] [-c 0|1|2] [-i ini.txt] [-o out.txt] [-q]\n"); return 2; }
  double tlim = 60; uint64_t seed = 1; long target = 0; const char *ini = NULL, *out = NULL; int quiet = 0; int tmin = 0;
  for (int i = 2; i < argc; i++){
    if (!strcmp(argv[i], "-t")) tlim = atof(argv[++i]);
    else if (!strcmp(argv[i], "-s")) seed = strtoull(argv[++i], 0, 10);
    else if (!strcmp(argv[i], "-k")) target = atol(argv[++i]);
    else if (!strcmp(argv[i], "-c")) ccmode = atoi(argv[++i]);
    else if (!strcmp(argv[i], "-i")) ini = argv[++i];
    else if (!strcmp(argv[i], "-o")) out = argv[++i];
    else if (!strcmp(argv[i], "-q")) quiet = 1;
    else if (!strcmp(argv[i], "-T")) tmin = atoi(argv[++i]);
    else if (!strcmp(argv[i], "-b")) tiebreak = atoi(argv[++i]);
    else { fprintf(stderr, "opção desconhecida %s\n", argv[i]); return 2; }
  }
  rng_s = seed * 0x9E3779B97F4A7C15ull + 12345; for (int i = 0; i < 10; i++) rnd();
  FILE *F = fopen(argv[1], "rb"); if (!F){ perror(argv[1]); return 2; }
  uint32_t hdr[7]; if (fread(hdr, 4, 7, F) != 7 || hdr[0] != 0x31435350u){ fprintf(stderr, "formato inválido\n"); return 2; }
  q = hdr[1]; n = hdr[2]; R = hdr[3]; T = hdr[4]; npts = hdr[5]; nsets = hdr[6];
  if (fread(&npairs, 8, 1, F) != 1) return 2;
  pts = malloc(4 * (size_t)npts); setw = malloc(4 * (size_t)nsets); off = malloc(8 * ((size_t)nsets + 1)); elem = malloc(4 * npairs);
  if (fread(pts, 4, npts, F) != npts || fread(setw, 4, nsets, F) != nsets || fread(off, 8, nsets + 1, F) != nsets + 1 || fread(elem, 4, npairs, F) != npairs){ fprintf(stderr, "arquivo truncado\n"); return 2; }
  fclose(F);
  /* -T: descarta conjuntos com menos de tmin pontos (sobe o corte sem regerar a instância) */
  if (tmin > (int)T){ uint32_t m = 0; uint64_t p = 0;
    for (uint32_t s = 0; s < nsets; s++){ uint64_t a0 = off[s], a1 = off[s + 1]; if (a1 - a0 < (uint64_t)tmin) continue;
      setw[m] = setw[s]; off[m] = p; memmove(elem + p, elem + a0, 4 * (a1 - a0)); p += a1 - a0; m++; }
    off[m] = p; nsets = m; npairs = p; T = tmin; }
  /* CSR transposto: ponto -> conjuntos */
  eoff = calloc(npts + 1, 8); for (uint64_t a = 0; a < npairs; a++) eoff[elem[a] + 1]++;
  for (uint32_t e = 0; e < npts; e++) eoff[e + 1] += eoff[e];
  selem = malloc(4 * npairs); { uint64_t *fill = malloc(8 * ((size_t)npts + 1)); memcpy(fill, eoff, 8 * ((size_t)npts + 1));
    for (uint32_t s = 0; s < nsets; s++) for (uint64_t a = off[s]; a < off[s + 1]; a++) selem[fill[elem[a]]++] = s;
    free(fill); }
  for (uint32_t e = 0; e < npts; e++) if (eoff[e] == eoff[e + 1]){ fprintf(stderr, "ponto %u sem candidato: instância inviável (baixe T)\n", e); return 3; }
  score = malloc(8 * (size_t)nsets); stamp = calloc(nsets, 8); insol = calloc(nsets, 1); canadd = malloc(nsets); memset(canadd, 1, nsets);
  sol = malloc(4 * (size_t)nsets); solpos = malloc(4 * (size_t)nsets);
  wgt = malloc(8 * (size_t)npts); cnt = calloc(npts, 4); xorc = calloc(npts, 4); unc = malloc(4 * (size_t)npts); uncpos = malloc(4 * (size_t)npts);
  for (uint32_t e = 0; e < npts; e++){ wgt[e] = 1; unc_add(e); }
  for (uint32_t s = 0; s < nsets; s++) score[s] = (ll)(off[s + 1] - off[s]);
  double t0 = now();
  int saved_cc = ccmode; ccmode = 0;
  if (ini){
    FILE *I = fopen(ini, "r"); if (!I){ perror(ini); return 2; } char line[256]; int miss = 0;
    while (fgets(line, sizeof line, I)){ uint32_t L = 0; while (line[L] >= '0' && line[L] <= '9') L++; if (L != n) continue;
      uint32_t x = 0, p = 1; for (uint32_t j = 0; j < n; j++){ x += (line[j] - '0') * p; p *= q; }
      int s = find_set(x); if (s < 0){ miss++; continue; } if (!insol[s]) add_set(s); }
    fclose(I); if (miss) fprintf(stderr, "aviso: %d palavras iniciais não são candidatas (cobertura < T)\n", miss);
  }
  /* completa gulosamente (maior score = mais pontos descobertos) */
  while (nunc){ ll bs = -1; uint32_t b = 0; for (uint32_t s = 0; s < nsets; s++) if (!insol[s] && score[s] > bs){ bs = score[s]; b = s; } add_set(b); }
  /* tira redundantes (score 0 = não é o único cobridor de nenhum ponto) */
  for (int ch = 1; ch;){ ch = 0; for (uint32_t i = 0; i < nsol; i++) if (score[sol[i]] == 0){ del_set(sol[i]); ch = 1; break; } }
  ccmode = saved_cc;
  uint32_t bestk = nsol; uint32_t *best = malloc(4 * (size_t)nsets); memcpy(best, sol, 4 * nsol);
  double tbest = now() - t0; save(out, best, bestk);
  if (!quiet) printf("best %u %.2f %lld\n", bestk, tbest, iter);
  fflush(stdout);
  uint32_t tabu = UINT32_MAX;
  while (1){
    while (nunc == 0){
      if (nsol < bestk){ bestk = nsol; memcpy(best, sol, 4 * nsol); tbest = now() - t0; save(out, best, bestk);
        if (!quiet){ printf("best %u %.2f %lld\n", bestk, tbest, iter); fflush(stdout); } }
      if ((long)bestk <= target) goto done;
      ll bs = LLONG_MIN; uint32_t b = 0;
      for (uint32_t i = 0; i < nsol; i++){ uint32_t s = sol[i]; if (score[s] > bs || (score[s] == bs && stamp[s] < stamp[b])){ bs = score[s]; b = s; } }
      del_set(b);
    }
    iter++;
    if ((iter & 255) == 0 && now() - t0 > tlim) break;
    /* tira */
    { ll bs = LLONG_MIN; uint32_t b = UINT32_MAX;
      for (uint32_t i = 0; i < nsol; i++){ uint32_t s = sol[i]; if (s == tabu) continue;
        if (b == UINT32_MAX || score[s] > bs || (score[s] == bs && better_del(s, b))){ bs = score[s]; b = s; } }
      if (b != UINT32_MAX) del_set(b); }
    /* põe */
    { uint32_t e = unc[rnd() % nunc]; ll bs = LLONG_MIN; uint32_t b = UINT32_MAX;
      for (int pass = 0; pass < 2 && b == UINT32_MAX; pass++)
        for (uint64_t a = eoff[e]; a < eoff[e + 1]; a++){ uint32_t s = selem[a]; if (insol[s] || (pass == 0 && ccmode && !canadd[s])) continue;
          if (b == UINT32_MAX || score[s] > bs || (score[s] == bs && better_add(s, b))){ bs = score[s]; b = s; } }
      add_set(b); tabu = b; }
    bump_weights();
#ifdef CHECK
    if (iter % 97 == 0) check();
#endif
  }
done:;
  double el = now() - t0;
  /* conferência independente da melhor cobertura dentro da instância */
  { uint8_t *c = calloc(npts, 1); for (uint32_t i = 0; i < bestk; i++){ uint32_t s = best[i]; for (uint64_t a = off[s]; a < off[s + 1]; a++) c[elem[a]] = 1; }
    uint32_t miss = 0; for (uint32_t e = 0; e < npts; e++) miss += !c[e];
    if (miss){ fprintf(stderr, "ERRO interno: melhor solução deixa %u pontos descobertos\n", miss); return 4; } free(c); }
  printf("{\"q\":%u,\"n\":%u,\"R\":%u,\"T\":%u,\"npts\":%u,\"nsets\":%u,\"best\":%u,\"t_best\":%.2f,\"secs\":%.2f,\"iter\":%lld,\"seed\":%llu,\"cc\":%d,\"tb\":%d}\n",
         q, n, R, T, npts, nsets, bestk, tbest, el, iter, (unsigned long long)seed, ccmode, tiebreak);
  return 0;
}
