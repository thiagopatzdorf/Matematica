/* coset_sa.c -- busca de BASE com muitas classes laterais de um código pequeno.
 *
 * Generaliza a base "t classes laterais de [n,k]_q" para t grande: recozimento simulado
 * direto no espaço de síndromes F_q^r. Estado = conjunto S de t síndromes; objetivo =
 * nº de síndromes sem cobertura (|F_q^r \ (S + B)|), B = {H e : wt(e) <= R}.
 * Cada síndrome descoberta é uma classe lateral órfã (q^k pontos) para o remendo.
 * Ex.: 3 classes de um [9,3]_7 = 21 classes do subcódigo [9,2]_7 que o contém; aqui as 21
 * se mexem livremente, então o ótimo só pode melhorar.
 *
 * Movimento: escolhe síndrome descoberta u, entra sigma = u - b (b sorteado em B, então
 * sigma cobre u), sai o membro de menor perda entre 3 sorteados; aceita por SA.
 * Custo do movimento ~ 5|B| somas de síndrome (sem listas: |B| é grande).
 *
 * Uso: coset_sa q n R H t secs seed T0 T1 out [init.txt]
 *   H: linhas da matriz de checagem separadas por espaço, cada uma com n dígitos
 *      (ex.: [9,3] -> [9,2]: as 6 linhas de [I|A] e mais "000000001").
 *   init.txt: síndromes iniciais (inteiros, dígito i = linha i, base q), uma por linha.
 * Saída: out_t<t>_o<órfãs>.txt com as síndromes (uma por linha), sempre que melhora.
 * Quando zera, encolhe t e continua.
 */
#include "kit.h"
#include <math.h>

int main(int argc, char **argv){
  if (argc < 11){ fprintf(stderr, "uso: coset_sa q n R H t secs seed T0 T1 out [init]\n"); return 2; }
  Kit K = {0}; K.q = atoi(argv[1]); K.n = atoi(argv[2]); K.R = atoi(argv[3]);
  const char *Hs = argv[4]; int t = atoi(argv[5]); double secs = atof(argv[6]);
  kit_seed(strtoull(argv[7], 0, 10)); double T0 = atof(argv[8]), T1 = atof(argv[9]); const char *out = argv[10];
  int r = 0; const char *p = Hs;
  while (*p){ while (*p == ' ') p++; if (!*p) break; for (int j = 0; j < K.n; j++) K.H[r][j] = p[j] - '0'; p += K.n; r++; }
  K.r = r; kit_init_tables(&K); kit_compute_ball(&K);
  long N = K.N; int nB = 0; int *Bl = malloc(sizeof(int) * K.nB);
  for (long s = 0; s < N; s++) if (K.inB[s]) Bl[nB++] = (int)s;
  int LO = (int)K.LO, HI = (int)K.HI; int *Blo = malloc(sizeof(int) * nB), *Bhi = malloc(sizeof(int) * nB);
  for (int i = 0; i < nB; i++){ Blo[i] = Bl[i] % LO; Bhi[i] = Bl[i] / LO; }
  printf("N=%ld |B|=%d t=%d\n", N, nB, t); fflush(stdout);
  uint16_t *cov = calloc(N, 2); int32_t *unc = malloc(sizeof(int32_t) * N), *upos = malloc(sizeof(int32_t) * N); long nunc = 0;
  for (long s = 0; s < N; s++){ upos[s] = (int32_t)nunc; unc[nunc++] = (int32_t)s; }
  int *S = malloc(sizeof(int) * (t + 16)); int ns = 0; uint8_t *inS = calloc(N, 1);
#define ADDV(sig, ...) { const int *rl = K.addlo + ((sig) % LO) * LO, *rh = K.addhi + ((sig) / LO) * HI; for (int i = 0; i < nB; i++){ int v = rl[Blo[i]] + LO * rh[Bhi[i]]; __VA_ARGS__ } }
  #define ADD(sig) ADDV(sig, if (cov[v]++ == 0){ int32_t ix = upos[v], last = unc[--nunc]; unc[ix] = last; upos[last] = ix; })
  #define REM(sig) ADDV(sig, if (--cov[v] == 0){ upos[v] = (int32_t)nunc; unc[nunc++] = v; })
  if (argc > 11){ FILE *F = fopen(argv[11], "r"); long x; while (F && fscanf(F, "%ld", &x) == 1 && ns < t){ if (inS[x]) continue; S[ns++] = (int)x; inS[x] = 1; ADD((int)x); } if (F) fclose(F); }
  while (ns < t){ int sig; if (nunc){ int u = unc[kit_rnd() % nunc]; sig = kit_sub(&K, u, Bl[kit_rnd() % nB]); } else sig = (int)(kit_rnd() % N); if (inS[sig]) continue; S[ns++] = sig; inS[sig] = 1; ADD(sig); }
  printf("inicial: t=%d órfãs=%ld\n", ns, nunc); fflush(stdout);
  double t0 = kit_now(), lastsave = 0; long best = nunc + 1; long it = 0;
  while (kit_now() - t0 < secs){
    if (nunc < best){ best = nunc;
      if (kit_now() - lastsave > 2 || best == 0){ char fn[512]; snprintf(fn, sizeof fn, "%s_t%d_o%ld.txt", out, ns, best); FILE *F = fopen(fn, "w"); for (int i = 0; i < ns; i++) fprintf(F, "%d\n", S[i]); fclose(F); lastsave = kit_now();
        printf("t=%d órfãs=%ld it=%ld (%.0fs)\n", ns, best, it, kit_now() - t0); fflush(stdout); } }
    if (!nunc){ /* encolhe */
      int wi = 0, wl = 1 << 30; for (int i = 0; i < ns; i++){ int l = 0; ADDV(S[i], if (cov[v] == 1) l++;) if (l < wl){ wl = l; wi = i; } }
      int sig = S[wi]; S[wi] = S[--ns]; inS[sig] = 0; REM(sig); best = nunc + 1;
      printf("encolheu para t=%d, órfãs=%ld\n", ns, nunc); fflush(stdout); continue; }
    double T = T0 - (T0 - T1) * fmod((kit_now() - t0) / 120.0, 1.0);
    int u = unc[kit_rnd() % nunc];
    int sig = kit_sub(&K, u, Bl[kit_rnd() % nB]);
    if (inS[sig]) continue;
    int ri = 0, rl = 1 << 30;
    for (int s2 = 0; s2 < 3; s2++){ int i = (int)(kit_rnd() % ns); int l = 0; ADDV(S[i], if (cov[v] == 1) l++;) if (l < rl){ rl = l; ri = i; } }
    long U0 = nunc; int old = S[ri];
    ADD(sig); REM(old);
    long dU = nunc - U0; it++;
    if (dU <= 0 || (double)(kit_rnd() >> 11) * (1.0 / 9007199254740992.0) < exp(-dU / T)){ S[ri] = sig; inS[old] = 0; inS[sig] = 1; }
    else { ADD(old); REM(sig); }
    if (it % 20000 == 0){ printf("it=%ld T=%.2f órfãs=%ld melhor=%ld (%.0fs)\n", it, T, nunc, best, kit_now() - t0); fflush(stdout); }
  }
  printf("fim: t=%d melhor=%ld it=%ld\n", ns, best, it);
  return 0;
}
