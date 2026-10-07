/*
 * tabu_gpu.cu -- PoC: a busca tabu de tools/busca_direta/tabu.c (movimento de Östergård, casca de raio
 * exato R) com UMA CADEIA POR BLOCO de GPU. Serve para MEDIR o que uma T4 daria nas cotas superiores de
 * K_q(n,R) <= M; não é uma ferramenta de produção e o resultado de busca é HIPÓTESE até passar por
 * tools/verify/verify.
 *
 * Paralelismo dentro do bloco (128 threads): varredura dos descobertos (sorteio de x), avaliação dos
 * candidatos (um por thread) e aplicação do movimento (as duas cascas de ~C(n-1,R)(q-1)^R pontos, sem
 * conflito: os pontos de uma casca são distintos entre si e disjuntos da outra). Entre blocos: cadeias
 * independentes (sementes diferentes).
 *
 * Modo EMU (-DEMU, compila com g++ -x c++): o MESMO código roda em CPU, thread a thread, para testar a
 * correção sem GPU (contagens incrementais == recontagem do zero). Não mede desempenho de GPU.
 *
 * Uso:  tabu_gpu q n R M cadeias segundos semente [tenure=1] [iter_por_lancamento=2000] [saida] [modo=0]
 *                [ciclo=2000000] [T0=2.0] [Tmin=0.05]     (modo 0 = tabu, 1 = SA guiado de 1 coordenada, 2 = SA que realoca palavra, como sa_cover)
 * Saída (stdout, uma linha por evento):
 *   CFG ...                      parâmetros e tamanho da casca
 *   LANCA t=<s> it_total=<n> descobertos_min=<d> ok=<k>   a cada lançamento
 *   ACHOU cadeia=<c> it=<n> t=<s> arquivo=<f>              cadeia que zerou os descobertos
 *   FIM t=<s> it_total=<n> it_por_s=<x> sucessos=<k>
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <limits.h>
#include <math.h>

#define MAXN 12
#define MAXM 128
#ifndef MAXC
#define MAXC (MAXM * MAXN) /* candidatos por iteração; -DMAXC=640 libera memória compartilhada (mais blocos por SM) */
#endif
#define NT 128

#ifdef EMU
#define DEV
#define SHARED static
#define PHASE for (int t = 0; t < NT; t++)
#define SYNC
static inline int atomicAddI(int *a, int v) { int o = *a; *a += v; return o; }
#define CONSTANT
#else
#include <cuda_runtime.h>
#define DEV __device__
#define SHARED __shared__
#define PHASE for (int t = threadIdx.x, _o = 1; _o; _o = 0)
#define SYNC __syncthreads()
#define atomicAddI(a, v) atomicAdd(a, v)
#define CONSTANT __constant__
#endif

typedef struct { int q, n, R, M, S, N, tenure, mode, cycle, nball; float T0, Tmin; int pw[MAXN + 1]; } Par;
typedef struct { uint64_t rng; int64_t it; int nunc, best, done, pad; } St;
typedef struct { uint8_t *cnt, *cw, *shell, *bt; int *ci; int64_t *tabu; St *st; } Dev;

CONSTANT Par P;
CONSTANT int dlt[MAXN][10][10]; /* dlt[k][a][v]: troca o dígito k de a para (a+v) mod q, em unidades do índice */

DEV static inline uint64_t xs(uint64_t *s) {
    uint64_t x = *s;
    x ^= x << 13; x ^= x >> 7; x ^= x << 17;
    *s = x;
    return x;
}

/* uma cadeia = um bloco; `iters` iterações do tabu e devolve o estado para o hospedeiro */
DEV static void run_chain(const Dev *D, int ch, int iters) {
    const int q = P.q, n = P.n, R = P.R, M = P.M, S = P.S, N = P.N;
    (void)q;
    uint8_t *cnt = D->cnt + (size_t)ch * N;
    uint8_t *cw = D->cw + (size_t)ch * M * n;
    int *ci = D->ci + (size_t)ch * M;
    int64_t *tb = D->tabu + (size_t)ch * M;
    St *st = D->st + ch;
    SHARED int s_nunc, s_ncand, s_x, s_best, s_stop, s_bm, s_bj, s_owner, s_off, s_dsum, s_pick, s_loss, s_gain, s_widx;
    SHARED uint8_t s_wd[MAXN];
    SHARED int s_cm[MAXC], s_cj[MAXC], s_dv[MAXC], s_cz[NT];
    SHARED uint8_t s_xd[MAXN];
    SHARED uint64_t s_rng;
    SHARED int64_t s_it;
    PHASE { if (t == 0) { s_nunc = st->nunc; s_best = st->best; s_rng = st->rng; s_it = st->it; s_stop = st->done; } }
    SYNC;
    const int seg = (N + NT - 1) / NT;
    for (int iter = 0; iter < iters; iter++) {
        if (s_stop) break;
        if (s_nunc == 0) {
            PHASE { if (t == 0) { st->done = 1; s_stop = 1; } }
            SYNC;
            break;
        }
        /* 1. sorteia um ponto descoberto x: contagem de zeros por segmento, depois o r-ésimo */
        PHASE {
            int lo = t * seg, hi = lo + seg, c = 0;
            if (hi > N) hi = N;
            for (int y = lo; y < hi; y++) c += (cnt[y] == 0);
            s_cz[t] = c;
        }
        SYNC;
        PHASE {
            if (t == 0) {
                int r = (int)(xs(&s_rng) % (uint64_t)s_nunc), acc = 0, o = 0;
                for (; o < NT - 1; o++) { if (r < acc + s_cz[o]) break; acc += s_cz[o]; }
                s_owner = o; s_off = r - acc; s_ncand = 0;
            }
        }
        SYNC;
        PHASE {
            if (t == s_owner) {
                int lo = t * seg, hi = lo + seg, k = s_off, x = lo;
                if (hi > N) hi = N;
                for (int y = lo; y < hi; y++)
                    if (cnt[y] == 0) { if (k == 0) { x = y; break; } k--; }
                s_x = x;
                for (int d = 0; d < n; d++) { s_xd[d] = (uint8_t)(x % P.q); x /= P.q; }
            }
        }
        SYNC;
        if (P.mode == 2) {
            /* SA "realoca" (o movimento do sa_cover.c): uma palavra i qualquer vai para um ponto sorteado da bola
               de raio R em volta do descoberto x. Custo exato = perde(bola velha com cnt==1) - ganha(bola nova com
               cnt - [na bola velha] == 0); aplica em duas fases (tira a velha, põe a nova) para não haver corrida. */
            PHASE {
                if (t == 0) {
                    int i = (int)(xs(&s_rng) % (uint64_t)M), r = (int)(xs(&s_rng) % (uint64_t)P.nball), idx = 0;
                    for (int k = 0; k < n; k++) { int d = ((int)s_xd[k] + D->bt[r * n + k]) % P.q; s_wd[k] = (uint8_t)d; idx += d * P.pw[k]; }
                    s_pick = i; s_widx = idx; s_loss = 0; s_gain = 0;
                }
            }
            SYNC;
            PHASE {
                const uint8_t *oc = cw + s_pick * n;
                int oi = ci[s_pick], ls = 0, gn = 0;
                for (int b = t; b < P.nball; b += NT) {
                    const uint8_t *e = D->bt + (size_t)b * n;
                    int offo = 0, offn = 0, dist = 0;
                    for (int k = 0; k < n; k++) {
                        offo += dlt[k][oc[k]][e[k]];
                        offn += dlt[k][s_wd[k]][e[k]];
                        dist += ((s_wd[k] + e[k]) % P.q) != oc[k];
                    }
                    ls += (cnt[oi + offo] == 1);
                    gn += ((int)cnt[s_widx + offn] - (dist <= R) == 0);
                }
                atomicAddI(&s_loss, ls);
                atomicAddI(&s_gain, gn);
            }
            SYNC;
            PHASE {
                if (t == 0) {
                    int d = s_loss - s_gain;
                    float frac = (float)(s_it % P.cycle) / (float)P.cycle;
                    float T = P.Tmin + P.T0 * powf(0.002f, frac);
                    float u = (float)(xs(&s_rng) >> 40) * (1.0f / 16777216.0f);
                    s_bm = (d <= 0 || u < expf(-(float)d / T)) ? s_pick : -1;
                }
            }
            SYNC;
            PHASE {  /* fase A: tira a bola velha */
                if (s_bm >= 0) {
                    const uint8_t *oc = cw + s_bm * n;
                    int oi = ci[s_bm], ld = 0;
                    for (int b = t; b < P.nball; b += NT) {
                        const uint8_t *e = D->bt + (size_t)b * n;
                        int off = 0;
                        for (int k = 0; k < n; k++) off += dlt[k][oc[k]][e[k]];
                        uint8_t v = (uint8_t)(cnt[oi + off] - 1);
                        cnt[oi + off] = v;
                        ld += (v == 0);
                    }
                    atomicAddI(&s_nunc, ld);
                }
            }
            SYNC;
            PHASE {  /* fase B: põe a bola nova */
                if (s_bm >= 0) {
                    int ld = 0;
                    for (int b = t; b < P.nball; b += NT) {
                        const uint8_t *e = D->bt + (size_t)b * n;
                        int off = 0;
                        for (int k = 0; k < n; k++) off += dlt[k][s_wd[k]][e[k]];
                        uint8_t w = cnt[s_widx + off];
                        cnt[s_widx + off] = (uint8_t)(w + 1);
                        ld -= (w == 0);
                    }
                    atomicAddI(&s_nunc, ld);
                }
            }
            SYNC;
            PHASE {
                if (t == 0) {
                    if (s_bm >= 0) { ci[s_bm] = s_widx; for (int k = 0; k < n; k++) cw[s_bm * n + k] = s_wd[k]; }
                    s_it++;
                    if (s_nunc < s_best) s_best = s_nunc;
                }
            }
            SYNC;
            continue;
        }
        /* 2. candidatos: palavras a distância exatamente R+1 de x, uma coordenada j em que diferem */
        PHASE {
            if (t < M) {
                int d = 0;
                for (int k = 0; k < n; k++) d += cw[t * n + k] != s_xd[k];
                if (d == R + 1)
                    for (int k = 0; k < n; k++)
                        if (cw[t * n + k] != s_xd[k]) { int p = atomicAddI(&s_ncand, 1); s_cm[p] = t; s_cj[p] = k; }
            }
        }
        SYNC;
        if (P.mode == 1) {
            /* SA guiado: UM candidato sorteado entre os de distância R+1, custo exato pelas cascas
               (as threads dividem a casca), aceita com Metropolis; T cai geometricamente por ciclo */
            PHASE { if (t == 0) { s_dsum = 0; s_pick = s_ncand > 0 ? (int)(xs(&s_rng) % (uint64_t)s_ncand) : 0; } }
            SYNC;
            PHASE {
                if (s_ncand > 0) {
                    int m = s_cm[s_pick], j = s_cj[s_pick];
                    const uint8_t *c = cw + m * n;
                    int ia = ci[m], ib = ia + ((int)s_xd[j] - (int)c[j]) * P.pw[j], dv = 0;
                    const uint8_t *E = D->shell + (size_t)j * S * n;
                    for (int s = t; s < S; s += NT) {
                        const uint8_t *e = E + (size_t)s * n;
                        int off = 0;
                        for (int k = 0; k < n; k++) off += dlt[k][c[k]][e[k]];
                        dv += (cnt[ia + off] == 1) - (cnt[ib + off] == 0);
                    }
                    atomicAddI(&s_dsum, dv);
                }
            }
            SYNC;
            PHASE {
                if (t == 0) {
                    int bm = -1, bj = -1;
                    if (s_ncand == 0) { /* ninguém a R+1: aproxima uma palavra qualquer de x (sempre aceita) */
                        bm = (int)(xs(&s_rng) % (uint64_t)M);
                        int dif[MAXN], nd = 0;
                        for (int k = 0; k < n; k++) if (cw[bm * n + k] != s_xd[k]) dif[nd++] = k;
                        bj = dif[xs(&s_rng) % (uint64_t)nd];
                    } else {
                        float frac = (float)(s_it % P.cycle) / (float)P.cycle;
                        float T = P.Tmin + P.T0 * powf(0.002f, frac);
                        float u = (float)(xs(&s_rng) >> 40) * (1.0f / 16777216.0f);
                        if (s_dsum <= 0 || u < expf(-(float)s_dsum / T)) { bm = s_cm[s_pick]; bj = s_cj[s_pick]; }
                    }
                    s_bm = bm; s_bj = bj;
                }
            }
            SYNC;
        } else {
        /* 3. custo exato de cada candidato: perde(cnt==1) - ganha(cnt==0) nas duas cascas */
        PHASE {
            for (int ic = t; ic < s_ncand; ic += NT) {
                int m = s_cm[ic], j = s_cj[ic];
                const uint8_t *c = cw + m * n;
                int ia = ci[m], ib = ia + ((int)s_xd[j] - (int)c[j]) * P.pw[j], dv = 0;
                const uint8_t *E = D->shell + (size_t)j * S * n;
                for (int s = 0; s < S; s++) {
                    const uint8_t *e = E + (size_t)s * n;
                    int off = 0;
                    for (int k = 0; k < n; k++) off += dlt[k][c[k]][e[k]];
                    dv += (cnt[ia + off] == 1) - (cnt[ib + off] == 0);
                }
                s_dv[ic] = dv;
            }
        }
        SYNC;
        /* 4. escolha (thread 0): melhor não tabu, aspiração por melhor global, empate sorteado */
        PHASE {
            if (t == 0) {
                int bd = INT_MAX, bm = -1, bj = -1, emp = 0;
                for (int i = 0; i < s_ncand; i++) {
                    int m = s_cm[i], dv = s_dv[i];
                    int livre = tb[m] <= s_it || s_nunc + dv < s_best;
                    if (!livre) continue;
                    if (dv < bd) { bd = dv; bm = m; bj = s_cj[i]; emp = 1; }
                    else if (dv == bd && xs(&s_rng) % (uint64_t)(++emp) == 0) { bm = m; bj = s_cj[i]; }
                }
                if (s_ncand > 0 && bm < 0) { int r = (int)(xs(&s_rng) % (uint64_t)s_ncand); bm = s_cm[r]; bj = s_cj[r]; }
                if (s_ncand == 0) { /* ninguém a R+1: aproxima uma palavra qualquer de x */
                    bm = (int)(xs(&s_rng) % (uint64_t)M);
                    int dif[MAXN], nd = 0;
                    for (int k = 0; k < n; k++) if (cw[bm * n + k] != s_xd[k]) dif[nd++] = k;
                    bj = dif[xs(&s_rng) % (uint64_t)nd];
                }
                s_bm = bm; s_bj = bj;
            }
        }
        SYNC;
        }
        /* 5. aplica o movimento: as duas cascas, sem conflito entre threads */
        PHASE {
            if (s_bm >= 0) {
            int m = s_bm, j = s_bj, ld = 0;
            const uint8_t *c = cw + m * n;
            int ia = ci[m], ib = ia + ((int)s_xd[j] - (int)c[j]) * P.pw[j];
            const uint8_t *E = D->shell + (size_t)j * S * n;
            for (int s = t; s < S; s += NT) {
                const uint8_t *e = E + (size_t)s * n;
                int off = 0;
                for (int k = 0; k < n; k++) off += dlt[k][c[k]][e[k]];
                uint8_t v = (uint8_t)(cnt[ia + off] - 1);
                cnt[ia + off] = v;
                ld += (v == 0);
                uint8_t w = cnt[ib + off];
                cnt[ib + off] = (uint8_t)(w + 1);
                ld -= (w == 0);
            }
            atomicAddI(&s_nunc, ld);
            }
        }
        SYNC;
        PHASE {
            if (t == 0) {
                if (s_bm >= 0) {
                    int m = s_bm, j = s_bj;
                    ci[m] += ((int)s_xd[j] - (int)cw[m * n + j]) * P.pw[j];
                    cw[m * n + j] = s_xd[j];
                    tb[m] = s_it + 1 + P.tenure + (int64_t)(xs(&s_rng) % 3);
                }
                s_it++;
                if (s_nunc < s_best) s_best = s_nunc;
            }
        }
        SYNC;
    }
    PHASE { if (t == 0) { st->nunc = s_nunc; st->best = s_best; st->rng = s_rng; st->it = s_it; } }
    SYNC;
}

#ifndef EMU
__global__ void kern(Dev D, int iters) { run_chain(&D, blockIdx.x, iters); }
#endif

/* ------------------------------------------------------------------ hospedeiro */
static double agora(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + 1e-9 * t.tv_nsec;
}
static uint64_t hrng = 88172645463325252ULL;
static uint64_t hrnd(void) { hrng ^= hrng << 13; hrng ^= hrng >> 7; hrng ^= hrng << 17; return hrng; }

static Par hp;
static int hdlt[MAXN][10][10];

/* soma (+1) a bola de raio R em volta da palavra c no vetor de contagem (hospedeiro) */
static void ball(uint8_t *cnt, const uint8_t *c, int p, int left, long idx) {
    cnt[idx]++;
    if (left == 0) return;
    for (int k = p; k < hp.n; k++)
        for (int v = 1; v < hp.q; v++) ball(cnt, c, k + 1, left - 1, idx + hdlt[k][c[k]][v]);
}

static uint8_t *ball_tab; static int nball_h;
static uint8_t *shell_tab; /* [n][S][n] vetores de erro de peso exato R com e_j = 0 */
static void gen_shell(int j, int p, int left, uint8_t *e, int *cntS) {
    if (left == 0) {
        memcpy(shell_tab + ((size_t)j * hp.S + (*cntS)) * hp.n, e, hp.n);
        (*cntS)++;
        return;
    }
    for (int k = p; k < hp.n; k++) {
        if (k == j) continue;
        for (int v = 1; v < hp.q; v++) { e[k] = (uint8_t)v; gen_shell(j, k + 1, left - 1, e, cntS); }
        e[k] = 0;
    }
}


/* todos os vetores de erro de peso <= R (a bola em volta de uma palavra), um por linha de n bytes */
static void gen_ball_tab(int p, int left, uint8_t *e, int *cntB) {
    memcpy(ball_tab + (size_t)(*cntB) * hp.n, e, hp.n);
    (*cntB)++;
    if (left == 0) return;
    for (int k = p; k < hp.n; k++) {
        for (int v = 1; v < hp.q; v++) { e[k] = (uint8_t)v; gen_ball_tab(k + 1, left - 1, e, cntB); }
        e[k] = 0;
    }
}

/* confere, do zero, que cnt == recontagem das palavras e nunc == nº de zeros (teste do modo EMU) */
static int confere(const uint8_t *cnt, const uint8_t *cw, int nunc) {
    uint8_t *ref = (uint8_t *)calloc(hp.N, 1);
    for (int m = 0; m < hp.M; m++) {
        long idx = 0;
        for (int k = 0; k < hp.n; k++) idx += (long)cw[m * hp.n + k] * hp.pw[k];
        ball(ref, cw + m * hp.n, 0, hp.R, idx);
    }
    int z = 0, bad = 0;
    for (int y = 0; y < hp.N; y++) { z += ref[y] == 0; bad += ref[y] != cnt[y]; }
    free(ref);
    return bad == 0 && z == nunc;
}

int main(int argc, char **argv) {
    if (argc < 8) {
        fprintf(stderr, "uso: %s q n R M cadeias segundos semente [tenure=1] [iter_por_lancamento=2000] [saida=./gpu]\n", argv[0]);
        return 2;
    }
    int q = atoi(argv[1]), n = atoi(argv[2]), R = atoi(argv[3]), M = atoi(argv[4]), chains = atoi(argv[5]);
    double secs = atof(argv[6]);
    uint64_t seed = strtoull(argv[7], 0, 10);
    int tenure = argc > 8 ? atoi(argv[8]) : 1;
    int iters = argc > 9 ? atoi(argv[9]) : 2000;
    const char *pref = argc > 10 ? argv[10] : "./gpu";
    hp.mode = argc > 11 ? atoi(argv[11]) : 0;
    hp.cycle = argc > 12 ? atoi(argv[12]) : 2000000;
    hp.T0 = argc > 13 ? (float)atof(argv[13]) : 2.0f;
    hp.Tmin = argc > 14 ? (float)atof(argv[14]) : 0.05f;
    if (hp.cycle < 1) hp.cycle = 1;
    if (q < 2 || q > 10 || n < 2 || n > MAXN || R < 1 || R >= n || M < 1 || M > MAXM || M >= 255) { fprintf(stderr, "parâmetros\n"); return 2; }
    if (M * (R + 1) > MAXC) { fprintf(stderr, "M*(R+1)=%d > MAXC=%d: recompile com -DMAXC maior\n", M * (R + 1), MAXC); return 2; }
    hp.q = q; hp.n = n; hp.R = R; hp.M = M; hp.tenure = tenure;
    hp.pw[0] = 1;
    for (int k = 1; k <= n; k++) hp.pw[k] = hp.pw[k - 1] * q;
    hp.N = hp.pw[n];
    if (hp.N > 1 << 22) { fprintf(stderr, "q^n grande demais para o PoC\n"); return 2; }
    long S = 1;
    for (int i = 0; i < R; i++) S = S * (n - 1 - i) / (i + 1);
    for (int i = 0; i < R; i++) S *= (q - 1);
    hp.S = (int)S;
    for (int k = 0; k < n; k++) for (int a = 0; a < q; a++) for (int v = 0; v < q; v++) hdlt[k][a][v] = ((a + v) % q - a) * hp.pw[k];
    shell_tab = (uint8_t *)calloc((size_t)n * hp.S * n, 1);
    for (int j = 0; j < n; j++) { uint8_t e[MAXN] = {0}; int c = 0; gen_shell(j, 0, R, e, &c); if (c != hp.S) { fprintf(stderr, "casca %d != %d\n", c, hp.S); return 3; } }
    { long B = 1, c = 1;
      for (int i = 1; i <= R; i++) { c = c * (n - i + 1) / i; long t = c; for (int j = 0; j < i; j++) t *= (q - 1); B += t; }
      nball_h = (int)B; hp.nball = nball_h;
      ball_tab = (uint8_t *)calloc((size_t)B * n, 1);
      uint8_t e[MAXN] = {0}; int cb = 0; gen_ball_tab(0, R, e, &cb);
      if (cb != nball_h) { fprintf(stderr, "bola %d != %d\n", cb, nball_h); return 3; } }
    hrng ^= seed * 0x9E3779B97F4A7C15ULL;
    for (int i = 0; i < 10; i++) hrnd();

    size_t Ncnt = (size_t)chains * hp.N, Ncw = (size_t)chains * M * n;
    uint8_t *h_cnt = (uint8_t *)calloc(Ncnt, 1), *h_cw = (uint8_t *)calloc(Ncw, 1);
    int *h_ci = (int *)calloc((size_t)chains * M, sizeof(int));
    int64_t *h_tabu = (int64_t *)calloc((size_t)chains * M, sizeof(int64_t));
    St *h_st = (St *)calloc(chains, sizeof(St));
    for (int ch = 0; ch < chains; ch++) {
        for (int m = 0; m < M; m++) {
            long idx = 0;
            for (int k = 0; k < n; k++) { uint8_t d = (uint8_t)(hrnd() % q); h_cw[((size_t)ch * M + m) * n + k] = d; idx += (long)d * hp.pw[k]; }
            h_ci[ch * M + m] = (int)idx;
            ball(h_cnt + (size_t)ch * hp.N, h_cw + ((size_t)ch * M + m) * n, 0, R, idx);
        }
        int z = 0;
        for (int y = 0; y < hp.N; y++) z += h_cnt[(size_t)ch * hp.N + y] == 0;
        h_st[ch].nunc = z; h_st[ch].best = z; h_st[ch].rng = hrnd() | 1; h_st[ch].it = 0;
    }
    printf("CFG q=%d n=%d R=%d M=%d N=%d casca=%d cadeias=%d tenure=%d iter_por_lancamento=%d modo=%d ciclo=%d T0=%.2f Tmin=%.2f\n", q, n, R, M, hp.N, hp.S, chains, tenure, iters, hp.mode, hp.cycle, hp.T0, hp.Tmin);
    fflush(stdout);

    Dev D;
#ifdef EMU
    P = hp;
    memcpy(dlt, hdlt, sizeof hdlt);
    D.cnt = h_cnt; D.cw = h_cw; D.ci = h_ci; D.tabu = h_tabu; D.st = h_st; D.shell = shell_tab; D.bt = ball_tab;
#define SYNCDEV()
#define PULL()
#else
#define CK(x) do { cudaError_t e_ = (x); if (e_ != cudaSuccess) { fprintf(stderr, "CUDA: %s (%s:%d)\n", cudaGetErrorString(e_), __FILE__, __LINE__); return 4; } } while (0)
    CK(cudaMemcpyToSymbol(P, &hp, sizeof hp));
    CK(cudaMemcpyToSymbol(dlt, hdlt, sizeof hdlt));
    CK(cudaMalloc(&D.cnt, Ncnt)); CK(cudaMalloc(&D.cw, Ncw)); CK(cudaMalloc(&D.ci, (size_t)chains * M * sizeof(int)));
    CK(cudaMalloc(&D.tabu, (size_t)chains * M * sizeof(int64_t))); CK(cudaMalloc(&D.st, chains * sizeof(St)));
    CK(cudaMalloc(&D.shell, (size_t)n * hp.S * n));
    CK(cudaMalloc(&D.bt, (size_t)nball_h * n));
    CK(cudaMemcpy(D.bt, ball_tab, (size_t)nball_h * n, cudaMemcpyHostToDevice));
    CK(cudaMemcpy(D.cnt, h_cnt, Ncnt, cudaMemcpyHostToDevice)); CK(cudaMemcpy(D.cw, h_cw, Ncw, cudaMemcpyHostToDevice));
    CK(cudaMemcpy(D.ci, h_ci, (size_t)chains * M * sizeof(int), cudaMemcpyHostToDevice));
    CK(cudaMemcpy(D.tabu, h_tabu, (size_t)chains * M * sizeof(int64_t), cudaMemcpyHostToDevice));
    CK(cudaMemcpy(D.st, h_st, chains * sizeof(St), cudaMemcpyHostToDevice));
    CK(cudaMemcpy(D.shell, shell_tab, (size_t)n * hp.S * n, cudaMemcpyHostToDevice));
#endif

    double t0 = agora();
    int sucessos = 0;
    int *reportado = (int *)calloc(chains, sizeof(int));
    for (;;) {
#ifdef EMU
        for (int ch = 0; ch < chains; ch++) run_chain(&D, ch, iters);
#else
        kern<<<chains, NT>>>(D, iters);
        CK(cudaGetLastError());
        CK(cudaDeviceSynchronize());
        CK(cudaMemcpy(h_st, D.st, chains * sizeof(St), cudaMemcpyDeviceToHost));
#endif
        double t = agora() - t0;
        long long itot = 0;
        int dmin = INT_MAX;
        for (int ch = 0; ch < chains; ch++) {
            itot += h_st[ch].it;
            if (h_st[ch].nunc < dmin) dmin = h_st[ch].nunc;
            if (h_st[ch].done && !reportado[ch]) {
                reportado[ch] = 1; sucessos++;
#ifndef EMU
                CK(cudaMemcpy(h_cw + (size_t)ch * M * n, D.cw + (size_t)ch * M * n, (size_t)M * n, cudaMemcpyDeviceToHost));
#endif
                char nome[512];
                snprintf(nome, sizeof nome, "%s_c%d_M%d.txt", pref, ch, M);
                FILE *f = fopen(nome, "w");
                if (f) {
                    for (int m = 0; m < M; m++) { for (int k = 0; k < n; k++) fputc('0' + h_cw[((size_t)ch * M + m) * n + k], f); fputc('\n', f); }
                    fclose(f);
                }
                printf("ACHOU cadeia=%d it=%lld t=%.3f arquivo=%s\n", ch, (long long)h_st[ch].it, t, nome);
            }
        }
        printf("LANCA t=%.3f it_total=%lld descobertos_min=%d ok=%d\n", t, itot, dmin, sucessos);
        fflush(stdout);
#ifdef EMU
        for (int ch = 0; ch < chains; ch++)
            if (!confere(h_cnt + (size_t)ch * hp.N, h_cw + (size_t)ch * M * n, h_st[ch].nunc)) { printf("ERRO_CONTAGEM cadeia=%d\n", ch); return 5; }
#endif
        if (t >= secs || sucessos == chains) {
            printf("FIM t=%.3f it_total=%lld it_por_s=%.1f sucessos=%d\n", t, itot, itot / (t > 0 ? t : 1e-9), sucessos);
            break;
        }
    }
    return 0;
}
