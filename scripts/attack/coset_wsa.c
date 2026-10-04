/* coset_wsa.c -- base de classes laterais com t LIVRE: SA no custo total estimado.
 *
 * Derivado do coset_sa (scripts/search), que fixa t e só encolhe quando as órfãs zeram. POR QUE
 * outro programa: medido em K_7(10,4) (k=3, 2026-10-03), uma síndrome órfã custa ~50 palavras de
 * remendo (343 pontos, no máximo 7 por palavra), enquanto uma classe lateral custa 343. Então a
 * base ótima NÃO é a de zero órfãs: trocar uma classe por até ~6 órfãs ainda ganha. O coset_sa
 * não enxerga isso; aqui o objetivo é o tamanho estimado do código,
 *     F = t * q^k + w * U,      U = nº de síndromes órfãs, w = custo estimado por órfã (palavras),
 * e os movimentos mudam t: troca (como no coset_sa), entra (cobre uma órfã) e sai (o membro de
 * menor perda entre 3 sorteados). w vem de fora: comece com ceil(q^k / cobertura máx por palavra)
 * e corrija pelo remendo real (patch_opt).
 *
 * Uso: coset_wsa q n R "H" w secs seed T0 T1 out [init.txt]
 *   H: linhas de H (r x n) separadas por espaço; k = n - r. init: síndromes (inteiros).
 * Saída: out_F<F>_t<t>_o<U>.txt sempre que F melhora (síndromes, uma por linha).
 * Compilar: gcc -O3 -march=native -o coset_wsa coset_wsa.c -lm
 */
#include "../search/kit.h"
#include <math.h>

int main(int argc, char **argv){
  if (argc < 11){ fprintf(stderr, "uso: coset_wsa q n R H w secs seed T0 T1 out [init]\n"); return 2; }
  Kit K = {0}; K.q = atoi(argv[1]); K.n = atoi(argv[2]); K.R = atoi(argv[3]);
  const char *Hs = argv[4]; double w = atof(argv[5]); double secs = atof(argv[6]);
  kit_seed(strtoull(argv[7], 0, 10)); double T0 = atof(argv[8]), T1 = atof(argv[9]); const char *out = argv[10];
  int r = 0; const char *p = Hs;
  while (*p){ while (*p == ' ') p++; if (!*p) break; for (int j = 0; j < K.n; j++) K.H[r][j] = p[j] - '0'; p += K.n; r++; }
  K.r = r; kit_init_tables(&K); kit_compute_ball(&K);
  long N = K.N; double Q = (double)K.pw[K.n - r]; int nB = 0; int *Bl = malloc(sizeof(int) * K.nB);
  for (long s = 0; s < N; s++) if (K.inB[s]) Bl[nB++] = (int)s;
  int LO = (int)K.LO, HI = (int)K.HI; int *Blo = malloc(sizeof(int) * nB), *Bhi = malloc(sizeof(int) * nB);
  for (int i = 0; i < nB; i++){ Blo[i] = Bl[i] % LO; Bhi[i] = Bl[i] / LO; }
  printf("N=%ld |B|=%d q^k=%.0f w=%.1f\n", N, nB, Q, w); fflush(stdout);
  uint16_t *cov = calloc(N, 2); int32_t *unc = malloc(sizeof(int32_t) * N), *upos = malloc(sizeof(int32_t) * N); long nunc = 0;
  for (long s = 0; s < N; s++){ upos[s] = (int32_t)nunc; unc[nunc++] = (int32_t)s; }
  int cap = 1 << 16; int *S = malloc(sizeof(int) * cap); int ns = 0; uint8_t *inS = calloc(N, 1);
#define ADDV(sig, ...) { const int *rl = K.addlo + ((sig) % LO) * LO, *rh = K.addhi + ((sig) / LO) * HI; for (int i = 0; i < nB; i++){ int v = rl[Blo[i]] + LO * rh[Bhi[i]]; __VA_ARGS__ } }
#define ADD(sig) ADDV(sig, if (cov[v]++ == 0){ int32_t ix = upos[v], last = unc[--nunc]; unc[ix] = last; upos[last] = ix; })
#define REM(sig) ADDV(sig, if (--cov[v] == 0){ upos[v] = (int32_t)nunc; unc[nunc++] = v; })
  if (argc > 11){ FILE *F = fopen(argv[11], "r"); long x; while (F && fscanf(F, "%ld", &x) == 1){ if (x < 0 || x >= N || inS[x]) continue; S[ns++] = (int)x; inS[x] = 1; ADD((int)x); } if (F) fclose(F); }
  if (!ns){ S[ns++] = 0; inS[0] = 1; ADD(0); }
  double F = ns * Q + w * nunc, best = 1e300;
  printf("inicial: t=%d órfãs=%ld F=%.0f\n", ns, nunc, F); fflush(stdout);
  double t0 = kit_now(); long it = 0;
  while (kit_now() - t0 < secs){
    F = ns * Q + w * nunc;
    if (F < best - 1e-9){ best = F; char fn[512]; snprintf(fn, sizeof fn, "%s_F%.0f_t%d_o%ld.txt", out, F, ns, nunc);
      FILE *G = fopen(fn, "w"); for (int i = 0; i < ns; i++) fprintf(G, "%d\n", S[i]); fclose(G);
      printf("F=%.0f t=%d órfãs=%ld it=%ld (%.0fs)\n", F, ns, nunc, it, kit_now() - t0); fflush(stdout); }
    double T = T0 - (T0 - T1) * fmod((kit_now() - t0) / 120.0, 1.0);
    int mv = (int)(kit_rnd() % 8); it++;
    if ((mv == 0 || !nunc) && ns > 1){ /* sai */
      int ri = 0, rl = 1 << 30;
      for (int s2 = 0; s2 < 3; s2++){ int i = (int)(kit_rnd() % ns); int l = 0; ADDV(S[i], if (cov[v] == 1) l++;) if (l < rl){ rl = l; ri = i; } }
      double d = -Q + w * rl;
      if (d <= 0 || (double)(kit_rnd() >> 11) * (1.0 / 9007199254740992.0) < exp(-d / T)){ int sig = S[ri]; REM(sig); inS[sig] = 0; S[ri] = S[--ns]; }
      continue; }
    if (!nunc) continue;
    int u = unc[kit_rnd() % nunc];
    int sig = kit_sub(&K, u, Bl[kit_rnd() % nB]);
    if (inS[sig]) continue;
    if (mv == 1 && ns < cap){ /* entra */
      int g = 0; ADDV(sig, if (cov[v] == 0) g++;)
      double d = Q - w * g;
      if (d <= 0 || (double)(kit_rnd() >> 11) * (1.0 / 9007199254740992.0) < exp(-d / T)){ S[ns++] = sig; inS[sig] = 1; ADD(sig); }
      continue; }
    /* troca */
    int ri = 0, rl = 1 << 30;
    for (int s2 = 0; s2 < 3; s2++){ int i = (int)(kit_rnd() % ns); int l = 0; ADDV(S[i], if (cov[v] == 1) l++;) if (l < rl){ rl = l; ri = i; } }
    long U0 = nunc; int old = S[ri];
    ADD(sig); REM(old);
    double d = w * (double)(nunc - U0);
    if (d <= 0 || (double)(kit_rnd() >> 11) * (1.0 / 9007199254740992.0) < exp(-d / T)){ S[ri] = sig; inS[old] = 0; inS[sig] = 1; }
    else { ADD(old); REM(sig); }
    if (it % 50000 == 0){ printf("it=%ld T=%.1f t=%d órfãs=%ld F=%.0f melhor=%.0f (%.0fs)\n", it, T, ns, nunc, ns * Q + w * nunc, best, kit_now() - t0); fflush(stdout); }
  }
  printf("fim: melhor F=%.0f it=%ld\n", best, it);
  return 0;
}
