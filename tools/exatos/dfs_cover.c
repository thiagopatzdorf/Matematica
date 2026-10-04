/*
 * dfs_cover.c -- busca exaustiva: existe código K_q(n,R) com M palavras?  (C99, sem dependências)
 *
 * Uso: dfs_cover Q N R M [LIMITE_NOS]
 *   Saída: "EXISTE" (e o código), "NAO_EXISTE" (busca completa) ou "LIMITE" (parou em LIMITE_NOS),
 *   sempre com o número de nós e o tempo, e a contagem de nós por profundidade (para extrapolar).
 *
 * Algoritmo (o mesmo esqueleto do chkN do CoveringLean/SearchCore.lean, com poda melhor):
 *   - a palavra 0 está no código (translação);
 *   - nó: escolhe o ponto descoberto u com menos centros permitidos na bola; ramifica sobre esses
 *     centros, em ordem de ganho; depois de tentar c, c fica proibido nos irmãos seguintes;
 *   - poda: se l * (maior ganho de um centro permitido) < descobertos, corta;
 *   - raiz: u = 1^{R+1} 0^{n-R-1} (descoberto pela palavra 0); os centros da bola de u são
 *     agrupados em órbitas do estabilizador de {0, u} (permutações de coordenadas que preservam o
 *     suporte de u, e permutações de símbolos que fixam 0 e 1 em cada coordenada). Só um
 *     representante por órbita é tentado, e cada órbita tentada fica inteira proibida nas
 *     seguintes. Sã: um código que contém 0 e cobre u tem um centro na bola de u; o de órbita de
 *     menor índice j é levado ao representante j por um elemento do estabilizador, que preserva
 *     0, u e as órbitas.
 *   A órbita de um centro c na bola de u é dada por (a, b, e, f): a = posições do suporte de u
 *   onde c = 1, b = onde c = 0, e = onde c é outro símbolo (q > 2), f = posições fora do suporte
 *   onde c != 0.
 * Não emite certificado; um NAO_EXISTE daqui é evidência computacional, não prova.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int Q, N, R, M;
static long NP, W; /* pontos, palavras de 64 bits por bitset */
static long *pw;
static uint64_t *ball; /* NP x W */
static long V;
static long long nodes = 0, limite = 0;
static long long nodes_depth[64];
static int aborted = 0;
static long sol[64];

static inline int digit(long x, int k) { return (int)((x / pw[k]) % Q); }
static int dist(long a, long b) { int d = 0; for (int k = 0; k < N; k++) d += digit(a, k) != digit(b, k); return d; }

static inline long popc_and(const uint64_t *a, const uint64_t *b) { long s = 0; for (long i = 0; i < W; i++) s += __builtin_popcountll(a[i] & b[i]); return s; }
static inline long popc(const uint64_t *a) { long s = 0; for (long i = 0; i < W; i++) s += __builtin_popcountll(a[i]); return s; }

/* lista de centros por ponto = a própria bola (simétrico) */
static long *blist; /* NP x V */

static int search(uint64_t *unc, uint64_t *forb, int l, int depth) {
    nodes++; nodes_depth[depth]++;
    if (limite && nodes > limite) { aborted = 1; return 0; }
    long nu = popc(unc);
    if (nu == 0) return 1;
    if (l == 0) return 0;
    /* escolhe u descoberto com menos centros permitidos; calcula maior ganho dos centros permitidos */
    long bestu = -1, bestcnt = 1L << 60;
    for (long i = 0; i < W; i++) {
        uint64_t w = unc[i];
        while (w) {
            int b = __builtin_ctzll(w); w &= w - 1;
            long u = i * 64 + b;
            long cnt = 0;
            for (long j = 0; j < V; j++) { long c = blist[u * V + j]; if (!((forb[c >> 6] >> (c & 63)) & 1)) cnt++; }
            if (cnt < bestcnt) { bestcnt = cnt; bestu = u; if (cnt == 0) return 0; }
        }
    }
    /* cota: o maior ganho possível de qualquer centro permitido é <= V; refina com ganho real dos
       centros que cobrem algum descoberto (todo centro útil cobre algum) */
    long maxg = 0;
    if ((long)l * V >= nu) {
        /* ganho máximo exato sobre todos os centros permitidos (custo NP*W) */
        for (long c = 0; c < NP; c++) {
            if ((forb[c >> 6] >> (c & 63)) & 1) continue;
            long g = popc_and(ball + c * W, unc);
            if (g > maxg) maxg = g;
        }
        if ((long)l * maxg < nu) return 0;
    } else return 0;
    /* ordena candidatos por ganho */
    long cand[4096]; long gain[4096]; int nc = 0;
    for (long j = 0; j < V; j++) {
        long c = blist[bestu * V + j];
        if ((forb[c >> 6] >> (c & 63)) & 1) continue;
        cand[nc] = c; gain[nc] = popc_and(ball + c * W, unc); nc++;
    }
    for (int a = 1; a < nc; a++) { long c = cand[a], g = gain[a]; int b = a - 1; while (b >= 0 && gain[b] < g) { cand[b + 1] = cand[b]; gain[b + 1] = gain[b]; b--; } cand[b + 1] = c; gain[b + 1] = g; }
    uint64_t *u2 = malloc(W * 8), *f2 = malloc(W * 8);
    memcpy(f2, forb, W * 8);
    int found = 0;
    for (int a = 0; a < nc && !found && !aborted; a++) {
        long c = cand[a];
        for (long i = 0; i < W; i++) u2[i] = unc[i] & ~ball[c * W + i];
        f2[c >> 6] |= 1ULL << (c & 63);
        sol[depth + 1] = c;
        if (search(u2, f2, l - 1, depth + 1)) found = 1;
    }
    free(u2); free(f2);
    return found;
}

/* Estimador de Knuth (1975): desce por um caminho aleatório escolhendo um filho uniforme,
   multiplicando os graus; a média de prod(graus) somada por nível é um estimador não viesado do
   número de nós da árvore (com a mesma ordem de filhos e as mesmas proibições da busca real). */
static uint64_t krs = 0x9E3779B97F4A7C15ULL;
static inline uint64_t krnd(void) { krs ^= krs << 13; krs ^= krs >> 7; krs ^= krs << 17; return krs; }
static double probe(uint64_t *unc, uint64_t *forb, int l) {
    double est = 1.0, mult = 1.0;
    uint64_t *u = malloc(W * 8), *f = malloc(W * 8); memcpy(u, unc, W * 8); memcpy(f, forb, W * 8);
    for (;;) {
        long nu = popc(u);
        if (nu == 0 || l == 0) break;
        long bestu = -1, bestcnt = 1L << 60;
        for (long i = 0; i < W; i++) { uint64_t w = u[i]; while (w) { int b = __builtin_ctzll(w); w &= w - 1; long x = i * 64 + b; long cnt = 0;
            for (long j = 0; j < V; j++) { long c = blist[x * V + j]; if (!((f[c >> 6] >> (c & 63)) & 1)) cnt++; }
            if (cnt < bestcnt) { bestcnt = cnt; bestu = x; } } }
        if (bestcnt == 0) break;
        long maxg = 0;
        for (long c = 0; c < NP; c++) { if ((f[c >> 6] >> (c & 63)) & 1) continue; long g = popc_and(ball + c * W, u); if (g > maxg) maxg = g; }
        if ((long)l * maxg < nu) break;
        long cand[4096], gain[4096]; int nc = 0;
        for (long j = 0; j < V; j++) { long c = blist[bestu * V + j]; if ((f[c >> 6] >> (c & 63)) & 1) continue; cand[nc] = c; gain[nc] = popc_and(ball + c * W, u); nc++; }
        for (int a = 1; a < nc; a++) { long c = cand[a], g = gain[a]; int b = a - 1; while (b >= 0 && gain[b] < g) { cand[b + 1] = cand[b]; gain[b + 1] = gain[b]; b--; } cand[b + 1] = c; gain[b + 1] = g; }
        int k = (int)(krnd() % nc);
        for (int a = 0; a <= k; a++) f[cand[a] >> 6] |= 1ULL << (cand[a] & 63);
        for (long i = 0; i < W; i++) u[i] &= ~ball[cand[k] * W + i];
        mult *= nc; est += mult; l--;
    }
    free(u); free(f);
    return est;
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "uso: %s Q N R M [LIMITE_NOS]\n", argv[0]); return 2; }
    Q = atoi(argv[1]); N = atoi(argv[2]); R = atoi(argv[3]); M = atoi(argv[4]);
    limite = argc > 5 ? atoll(argv[5]) : 0;
    pw = malloc(sizeof(long) * (N + 1)); pw[0] = 1; for (int i = 1; i <= N; i++) pw[i] = pw[i - 1] * Q;
    NP = pw[N]; W = (NP + 63) / 64;
    if (NP > 70000) { fprintf(stderr, "espaço grande demais (%ld)\n", NP); return 2; }
    ball = calloc(NP * W, 8);
    V = 0;
    for (long x = 0; x < NP; x++) if (dist(0, x) <= R) V++;
    blist = malloc(sizeof(long) * NP * V);
    for (long c = 0; c < NP; c++) {
        long k = 0;
        for (long x = 0; x < NP; x++) if (dist(c, x) <= R) { ball[c * W + (x >> 6)] |= 1ULL << (x & 63); blist[c * V + k++] = x; }
    }
    clock_t t0 = clock();
    uint64_t *unc = malloc(W * 8), *forb = calloc(W, 8);
    for (long i = 0; i < W; i++) unc[i] = ~0ULL;
    if (NP % 64) unc[W - 1] = (1ULL << (NP % 64)) - 1;
    for (long i = 0; i < W; i++) unc[i] &= ~ball[i]; /* palavra 0 */
    forb[0] |= 1; sol[0] = 0;
    int found = 0;
    if (R + 1 > N) { found = 1; }
    else {
        long u = 0; for (int k = 0; k <= R; k++) u += pw[k]; /* 1^{R+1} 0^{n-R-1} */
        /* órbitas dos centros da bola de u */
        long keys[4096]; long reps[4096]; int no = 0; long okey[4096]; long nb = 0, cent[8192];
        for (long j = 0; j < V; j++) {
            long c = blist[u * V + j]; cent[nb++] = c;
            int a = 0, b = 0, e = 0, f = 0;
            for (int k = 0; k < N; k++) { int d = digit(c, k); if (k <= R) { if (d == 1) a++; else if (d == 0) b++; else e++; } else if (d) f++; }
            long key = ((a * 64 + b) * 64 + e) * 64 + f; okey[j] = key;
            int seen = 0; for (int t = 0; t < no; t++) if (keys[t] == key) seen = 1;
            if (!seen) { keys[no] = key; reps[no] = c; no++; }
        }
        printf("raiz: %d órbitas de centros na bola de u (|bola| = %ld)\n", no, V);
        if (getenv("ESTIMAR")) {
            int probes = atoi(getenv("ESTIMAR")); double tot = 0; clock_t te = clock();
            uint64_t *u2 = malloc(W * 8), *f2 = malloc(W * 8);
            for (int pnum = 0; pnum < probes; pnum++) {
                int t = (int)(krnd() % no);
                memcpy(f2, forb, W * 8);
                for (int s2 = 0; s2 < t; s2++) for (long j = 0; j < nb; j++) if (okey[j] == keys[s2]) f2[cent[j] >> 6] |= 1ULL << (cent[j] & 63);
                long c = reps[t]; f2[c >> 6] |= 1ULL << (c & 63);
                for (long i = 0; i < W; i++) u2[i] = unc[i] & ~ball[c * W + i];
                tot += no * probe(u2, f2, M - 2);
            }
            double est = tot / probes, sec = (double)(clock() - te) / CLOCKS_PER_SEC;
            printf("ESTIMATIVA K%d(%d,%d) M=%d: nos~%.3e (probes=%d, %.1fs)\n", Q, N, R, M, est, probes, sec);
            return 0;
        }
        uint64_t *u2 = malloc(W * 8);
        for (int t = 0; t < no && !found && !aborted; t++) {
            long c = reps[t];
            for (long i = 0; i < W; i++) u2[i] = unc[i] & ~ball[c * W + i];
            uint64_t *f2 = malloc(W * 8); memcpy(f2, forb, W * 8);
            f2[c >> 6] |= 1ULL << (c & 63);
            sol[1] = c;
            long long n0 = nodes;
            if (search(u2, f2, M - 2, 1)) found = 1;
            printf("  órbita %d (rep %ld): %lld nós\n", t, c, nodes - n0); fflush(stdout);
            /* proíbe a órbita inteira para as próximas */
            for (long j = 0; j < nb; j++) if (okey[j] == keys[t]) forb[cent[j] >> 6] |= 1ULL << (cent[j] & 63);
            free(f2);
        }
    }
    double el = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("K%d(%d,%d) M=%d: %s nos=%lld tempo=%.2fs\n", Q, N, R, M, found ? "EXISTE" : (aborted ? "LIMITE" : "NAO_EXISTE"), nodes, el);
    printf("nos_por_profundidade:"); for (int d = 0; d < 64 && d <= M; d++) printf(" %lld", nodes_depth[d]); printf("\n");
    if (found) for (int i = 0; i < M; i++) { for (int k = 0; k < N; k++) printf("%d", digit(sol[i], k)); printf("\n"); }
    return 0;
}
