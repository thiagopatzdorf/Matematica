/*
 * blocos_sa.c -- recozimento para K_q(n, n-2) com palavras "puras por bloco".
 *
 * Construção (generaliza a partição do alfabeto, docs/exatos/FAMILIA_KQ_N_N2.md):
 * parta Z_q em blocos A_0..A_{k-1} e tome C = U C_j com C_j ⊂ A_j^n. Para x ∈ Z_q^n seja S_j o
 * conjunto das coordenadas em que x_i ∈ A_j. Só palavras de C_j podem concordar com x em S_j, então
 *
 *     x descoberto  <=>  para todo j, x|S_j não é coberto (>= 2 concordâncias) por C_j|S_j,
 *     #descobertos  =  Σ_{S_0 ⊔ ... ⊔ S_{k-1} = [n]}  Π_j u_j(S_j),
 *
 * com u_j(S) = número de pontos de A_j^S que C_j|S não cobre (u(∅) = 1, u(S) = |A_j|^|S| se |S| = 1).
 * A contagem é EXATA quando todos os S com |S| >= 2 são acompanhados (smax = n). Com smax < n,
 * supõe-se u_j(S) = 0 para |S| > smax (a cobertura é monótona em S, então isso vale assim que todos
 * os S de tamanho smax estão cobertos); o resultado final é sempre reconferido por um avaliador
 * exato (cobre_n2 e tools/verify/verify), nunca aceito pela conta interna.
 *
 * Uso: blocos_sa q n smax iters seed restarts T0 a_0:m_0 a_1:m_1 ...   [-i ARQUIVO_SEMENTE]
 *   a_j = tamanho do bloco, m_j = número de palavras do bloco. Σ a_j = q.
 *   Bloco de tamanho 1 com 1 palavra = palavra constante (cobre todo S com |S| >= 2).
 *   -t T: calcula g(a, n, T) = menor código em Z_a^n cujas projeções em todo T-subconjunto de
 *   coordenadas cobrem Z_a^T com >= 2 concordâncias (q é ignorado; um bloco só).
 * Saída: melhor código em stdout (dígitos 0-9 e a-z), uma palavra por linha; progresso em stderr.
 */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXK 12
#define MAXN 12
#define MAXW 128

static int q, n, smax, k;
static int famt = 0; /* -t T: modo g(a,n,T), um bloco, objetivo = soma de u(S) com |S| = T */
static int asz[MAXK], msz[MAXK], off[MAXK];
static unsigned char word[MAXK][MAXW][MAXN];
static uint32_t *cnt[MAXK][1 << MAXN];   /* contagem de cobertura por (S, ponto) */
static int64_t u[MAXK][1 << MAXN];
static int popc[1 << MAXN];
static int64_t powa[MAXK][MAXN + 1];

static uint64_t rng = 88172645463325252ULL;
static inline uint64_t rnd(void) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }
static inline double rndu(void) { return (rnd() >> 11) * (1.0 / 9007199254740992.0); }

/* enumera os pontos de A^S com >= 2 concordâncias com w|S e soma delta na contagem */
static int pos[MAXN], npos;
static void walk(int j, int S, const unsigned char *w, int d, int idx, int ag, int64_t mult, int delta) {
    if (d == npos) {
        if (ag >= 2) {
            uint32_t *c = &cnt[j][S][idx];
            if (delta > 0) { if ((*c)++ == 0) u[j][S]--; }
            else { if (--(*c) == 0) u[j][S]++; }
        }
        return;
    }
    int rem = npos - d;
    if (ag + rem < 2) return;
    int a = asz[j];
    int wi = w[pos[d]];
    if (ag >= 2) { /* já coberto: todo o resto vale */
        for (int v = 0; v < a; v++) walk(j, S, w, d + 1, idx + (int)(v * mult), ag, mult * a, delta);
        return;
    }
    for (int v = 0; v < a; v++) walk(j, S, w, d + 1, idx + (int)(v * mult), ag + (v == wi), mult * a, delta);
}

static void apply(int j, const unsigned char *w, int coord, int delta) {
    int full = (1 << n) - 1;
    for (int S = 1; S <= full; S++) {
        if (popc[S] < 2 || popc[S] > smax || (famt && popc[S] != famt)) continue;
        if (coord >= 0 && !((S >> coord) & 1)) continue;
        npos = 0;
        for (int i = 0; i < n; i++) if ((S >> i) & 1) pos[npos++] = i;
        walk(j, S, w, 0, 0, 0, 1, delta);
    }
}

static int64_t F[2][1 << MAXN];
static int64_t uval(int j, int S) {
    int p = popc[S];
    if (p <= 1) return powa[j][p];
    if (p > smax) return 0;
    return u[j][S];
}
static int64_t objective(void) {
    int full = (1 << n) - 1, cur = 0;
    if (famt) {
        int64_t s = 0;
        for (int S = 0; S <= full; S++) if (popc[S] == famt) s += u[0][S];
        return s;
    }
    for (int T = 0; T <= full; T++) F[0][T] = uval(0, T);
    for (int j = 1; j < k; j++) {
        int nx = cur ^ 1;
        for (int T = 0; T <= full; T++) {
            int64_t s = 0;
            for (int S = T;; S = (S - 1) & T) { /* S ⊆ T dado ao bloco j */
                int64_t uv = uval(j, S);
                if (uv) s += uv * F[cur][T ^ S];
                if (S == 0) break;
            }
            F[nx][T] = s;
        }
        cur = nx;
    }
    return F[cur][full];
}

static void init_tables(void) {
    int full = (1 << n) - 1;
    for (int S = 0; S <= full; S++) popc[S] = __builtin_popcount((unsigned)S);
    for (int j = 0; j < k; j++) {
        powa[j][0] = 1;
        for (int p = 1; p <= n; p++) powa[j][p] = powa[j][p - 1] * asz[j];
        for (int S = 0; S <= full; S++) {
            if (popc[S] < 2 || popc[S] > smax) continue;
            if (!cnt[j][S]) cnt[j][S] = malloc(sizeof(uint32_t) * (size_t)powa[j][popc[S]]);
            memset(cnt[j][S], 0, sizeof(uint32_t) * (size_t)powa[j][popc[S]]);
            u[j][S] = powa[j][popc[S]];
        }
    }
}

static void load_all(void) {
    init_tables();
    for (int j = 0; j < k; j++)
        for (int w = 0; w < msz[j]; w++) apply(j, word[j][w], -1, +1);
}

static const char *DIG = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
static unsigned char best[MAXK][MAXW][MAXN];

static void print_best(FILE *o) {
    for (int j = 0; j < k; j++)
        for (int w = 0; w < msz[j]; w++) {
            for (int i = 0; i < n; i++) fputc(DIG[off[j] + best[j][w][i]], o);
            fputc('\n', o);
        }
}

int main(int argc, char **argv) {
    if (argc < 9) {
        fprintf(stderr, "uso: blocos_sa q n smax iters seed restarts T0 a:m ... [-i semente]\n");
        return 2;
    }
    q = atoi(argv[1]); n = atoi(argv[2]); smax = atoi(argv[3]);
    long long iters = atoll(argv[4]);
    rng ^= (uint64_t)atoll(argv[5]) * 0x9E3779B97F4A7C15ULL; if (!rng) rng = 1;
    int restarts = atoi(argv[6]);
    double T0 = atof(argv[7]);
    const char *seedfile = NULL;
    k = 0;
    for (int ai = 8; ai < argc; ai++) {
        if (!strcmp(argv[ai], "-i") && ai + 1 < argc) { seedfile = argv[++ai]; continue; }
        if (!strcmp(argv[ai], "-t") && ai + 1 < argc) { famt = atoi(argv[++ai]); continue; }
        if (sscanf(argv[ai], "%d:%d", &asz[k], &msz[k]) != 2) { fprintf(stderr, "bloco inválido\n"); return 2; }
        k++;
    }
    int tot = 0;
    for (int j = 0; j < k; j++) { off[j] = tot; tot += asz[j]; }
    if (famt) { if (k != 1) { fprintf(stderr, "-t exige um bloco só\n"); return 2; } smax = famt; q = tot; }
    if (tot != q || n > MAXN || smax > n) { fprintf(stderr, "soma dos blocos != q ou n grande\n"); return 2; }
    for (int i = 0; i < 20; i++) rnd();

    int64_t gbest = INT64_MAX;
    for (int r = 0; r < restarts; r++) {
        for (int j = 0; j < k; j++)
            for (int w = 0; w < msz[j]; w++)
                for (int i = 0; i < n; i++) word[j][w][i] = (unsigned char)(rnd() % asz[j]);
        if (seedfile && r == 0) {
            /* semente: palavras do arquivo, distribuídas pelos blocos pelo primeiro símbolo */
            FILE *f = fopen(seedfile, "r");
            char line[256]; int fill[MAXK] = {0};
            while (f && fgets(line, sizeof line, f)) {
                int len = (int)strcspn(line, "\r\n"); if (len != n) continue;
                int d0 = (int)(strchr(DIG, line[0]) - DIG), j;
                for (j = 0; j < k; j++) if (d0 >= off[j] && d0 < off[j] + asz[j]) break;
                if (j == k || fill[j] >= msz[j]) continue;
                int ok = 1;
                for (int i = 0; i < n; i++) {
                    int d = (int)(strchr(DIG, line[i]) - DIG) - off[j];
                    if (d < 0 || d >= asz[j]) ok = 0; else word[j][fill[j]][i] = (unsigned char)d;
                }
                if (ok) fill[j]++;
            }
            if (f) fclose(f);
        }
        load_all();
        int64_t cur = objective(), rbest = cur;
        if (cur < gbest) { gbest = cur; memcpy(best, word, sizeof best); }
        double T = T0;
        double cool = pow(0.01 / T0, 1.0 / (double)iters);
        int movable[MAXK], nm = 0, totw = 0;
        for (int j = 0; j < k; j++) if (asz[j] > 1) { movable[nm++] = j; totw += msz[j]; }
        if (nm == 0) { gbest = cur; memcpy(best, word, sizeof best); break; }
        for (long long it = 0; it < iters && cur > 0; it++, T *= cool) {
            int pick = (int)(rnd() % (uint64_t)totw), j = 0;
            for (int t = 0; t < nm; t++) { j = movable[t]; if (pick < msz[j]) break; pick -= msz[j]; }
            int w = pick, i = (int)(rnd() % (uint64_t)n);
            unsigned char old = word[j][w][i];
            unsigned char nv = (unsigned char)((old + 1 + rnd() % (uint64_t)(asz[j] - 1)) % asz[j]);
            apply(j, word[j][w], i, -1);
            word[j][w][i] = nv;
            apply(j, word[j][w], i, +1);
            int64_t nxt = objective();
            int64_t dlt = nxt - cur;
            if (dlt <= 0 || rndu() < exp(-(double)dlt / T)) {
                cur = nxt;
                if (cur < rbest) rbest = cur;
                if (cur < gbest) { gbest = cur; memcpy(best, word, sizeof best); }
            } else {
                apply(j, word[j][w], i, -1);
                word[j][w][i] = old;
                apply(j, word[j][w], i, +1);
            }
        }
        fprintf(stderr, "restart %d: melhor %lld (global %lld)\n", r, (long long)rbest, (long long)gbest);
        if (gbest == 0) break;
    }
    fprintf(stderr, "FINAL descobertos(conta interna)=%lld\n", (long long)gbest);
    print_best(stdout);
    return gbest == 0 ? 0 : 1;
}
