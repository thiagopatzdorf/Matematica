/* coset_cov.c -- base fina com t fixo, escolhida pelo custo ESTIMADO do remendo, não só pela
 * contagem de órfãs.
 *
 * POR QUE: em K_7(10,4) (2026-10-03) três bases com 3-4 órfãs deram remendos de 128, 179 e 169
 * palavras. O que separou foi a cobertura máxima de uma palavra sobre o resíduo (11, 7, 11):
 * remendo ≈ |O|·q^k / cobmax + folga. A palavra de síndrome tau cobre, na órfã sigma,
 * m(sigma - tau) pontos (m = nº de erros de peso <= R com aquela síndrome), então
 *     cobmax(O) = max_tau sum_{sigma in O} m(sigma - tau)
 * custa |O|·q^r somas -- barato o bastante para avaliar a cada estado do platô.
 *
 * SA de troca igual ao coset_sa (minimiza órfãs); sempre que órfãs <= Umax, avalia
 *     est = t·q^k + ceil(|O|·q^k / cobmax)
 * e grava out_E<est>_o<U>_c<cobmax>.txt quando est melhora. Depois, patch_opt nos melhores.
 *
 * Uso: coset_cov q n R "H" t Umax secs seed T0 T1 out [init.txt]
 * Compilar: gcc -O3 -march=native -o coset_cov coset_cov.c -lm
 */
#include "../search/kit.h"
#include <math.h>

static uint16_t *mult;
static void mrec(Kit *K, int start, int left, int s){
  if (mult[s] < 65535) mult[s]++;
  if (!left) return;
  for (int j = start; j < K->n; j++){ int m = K->hcol[j], acc = m;
    for (int c = 1; c < K->q; c++){ mrec(K, j + 1, left - 1, kit_add(K, s, acc)); acc = kit_add(K, acc, m); } }
}

int main(int argc, char **argv){
  if (argc < 12){ fprintf(stderr, "uso: coset_cov q n R H t Umax secs seed T0 T1 out [init]\n"); return 2; }
  Kit K = {0}; K.q = atoi(argv[1]); K.n = atoi(argv[2]); K.R = atoi(argv[3]);
  const char *Hs = argv[4]; int t = atoi(argv[5]), Umax = atoi(argv[6]); double secs = atof(argv[7]);
  kit_seed(strtoull(argv[8], 0, 10)); double T0 = atof(argv[9]), T1 = atof(argv[10]); const char *out = argv[11];
  int r = 0; const char *p = Hs;
  while (*p){ while (*p == ' ') p++; if (!*p) break; for (int j = 0; j < K.n; j++) K.H[r][j] = p[j] - '0'; p += K.n; r++; }
  K.r = r; kit_init_tables(&K); kit_compute_ball(&K);
  long N = K.N; long Q = K.pw[K.n - r];
  mult = calloc(N, sizeof(uint16_t)); mrec(&K, 0, K.R, 0);
  int nB = 0; int *Bl = malloc(sizeof(int) * K.nB);
  for (long s = 0; s < N; s++) if (K.inB[s]) Bl[nB++] = (int)s;
  int LO = (int)K.LO, HI = (int)K.HI; int *Blo = malloc(sizeof(int) * nB), *Bhi = malloc(sizeof(int) * nB);
  for (int i = 0; i < nB; i++){ Blo[i] = Bl[i] % LO; Bhi[i] = Bl[i] / LO; }
  uint16_t *cov = calloc(N, 2); int32_t *unc = malloc(sizeof(int32_t) * N), *upos = malloc(sizeof(int32_t) * N); long nunc = 0;
  for (long s = 0; s < N; s++){ upos[s] = (int32_t)nunc; unc[nunc++] = (int32_t)s; }
  int *S = malloc(sizeof(int) * (t + 16)); int ns = 0; uint8_t *inS = calloc(N, 1);
  uint32_t *acc = calloc(N, sizeof(uint32_t));
#define ADDV(sig, ...) { const int *rl = K.addlo + ((sig) % LO) * LO, *rh = K.addhi + ((sig) / LO) * HI; for (int i = 0; i < nB; i++){ int v = rl[Blo[i]] + LO * rh[Bhi[i]]; __VA_ARGS__ } }
#define ADD(sig) ADDV(sig, if (cov[v]++ == 0){ int32_t ix = upos[v], last = unc[--nunc]; unc[ix] = last; upos[last] = ix; })
#define REM(sig) ADDV(sig, if (--cov[v] == 0){ upos[v] = (int32_t)nunc; unc[nunc++] = v; })
  if (argc > 12){ FILE *F = fopen(argv[12], "r"); long x; while (F && fscanf(F, "%ld", &x) == 1 && ns < t){ if (inS[x]) continue; S[ns++] = (int)x; inS[x] = 1; ADD((int)x); } if (F) fclose(F); }
  while (ns < t){ int sig; if (nunc){ int u = unc[kit_rnd() % nunc]; sig = kit_sub(&K, u, Bl[kit_rnd() % nB]); } else sig = (int)(kit_rnd() % N); if (inS[sig]) continue; S[ns++] = sig; inS[sig] = 1; ADD(sig); }
  printf("N=%ld |B|=%d t=%d inicial órfãs=%ld\n", N, nB, t, nunc); fflush(stdout);
  double t0 = kit_now(); long it = 0, best_est = 1L << 60, nev = 0; long lastU = -1; int *lastO = malloc(sizeof(int) * (Umax + 1));
  while (kit_now() - t0 < secs){
    if (nunc > 0 && nunc <= Umax){
      /* avalia só se o conjunto de órfãs mudou */
      int same = (nunc == lastU); if (same){ for (long i = 0; i < nunc; i++){ int f = 0; for (long j = 0; j < nunc; j++) if (lastO[j] == unc[i]) f = 1; if (!f){ same = 0; break; } } }
      if (!same){
        memset(acc, 0, sizeof(uint32_t) * N);
        for (long i = 0; i < nunc; i++){ int sg = unc[i]; for (long tau = 0; tau < N; tau++){ uint16_t m = mult[kit_sub(&K, sg, (int)tau)]; if (m) acc[tau] += m; } }
        uint32_t cm = 0; for (long tau = 0; tau < N; tau++) if (acc[tau] > cm) cm = acc[tau];
        long est = (long)ns * Q + (nunc * Q + cm - 1) / cm; nev++;
        if (est < best_est){ best_est = est; char fn[512]; snprintf(fn, sizeof fn, "%s_E%ld_o%ld_c%u.txt", out, est, nunc, cm);
          FILE *G = fopen(fn, "w"); for (int i = 0; i < ns; i++) fprintf(G, "%d\n", S[i]); fclose(G);
          printf("est=%ld órfãs=%ld cobmax=%u it=%ld aval=%ld (%.0fs)\n", est, nunc, cm, it, nev, kit_now() - t0); fflush(stdout); }
        lastU = nunc; for (long i = 0; i < nunc; i++) lastO[i] = unc[i];
      }
    }
    if (!nunc){ printf("órfãs=0 com t=%d: base fechada (est=%ld)\n", ns, (long)ns * Q); char fn[512]; snprintf(fn, sizeof fn, "%s_E%ld_o0.txt", out, (long)ns * Q);
      FILE *G = fopen(fn, "w"); for (int i = 0; i < ns; i++) fprintf(G, "%d\n", S[i]); fclose(G); break; }
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
  }
  printf("fim: melhor est=%ld it=%ld aval=%ld\n", best_est, it, nev);
  return 0;
}
