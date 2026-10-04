/*
 * motor.c -- busca exaustiva de códigos de cobertura K_q(n,R) com rejeição de isomorfos.
 *
 * Pergunta: existe C ⊂ Z_q^n com |C| <= M e todo ponto a distância de Hamming <= R de C?
 * O grupo de automorfismos do espaço de Hamming é G = S_q ≀ S_n (ordem q!^n · n!).
 *
 * Algoritmo (prova de correção completa no README.md):
 *   Topo (níveis 1..D): busca em largura. O nível 1 é {canon({0})}. Para cada representante S do
 *   nível k, escolhe um ponto descoberto p = f(S) (o de menor índice) e gera, para cada palavra
 *   w da bola B(p), o filho canon(S ∪ {w}); filhos iguais (mesma forma canônica) entram uma vez
 *   só. A forma canônica vem do nauty, sobre o grafo palavras–(coord,símbolo)–coordenadas, cujos
 *   automorfismos são exatamente G.
 *   Fundo (níveis > D): busca em profundidade sem simetria a partir de cada representante do
 *   nível D, com proibição dos irmãos já tentados e escolha do ponto com menos centros permitidos.
 *   Podas (válidas, ver README): (i) l·|B| < descobertos; (ii) soma dos l maiores ganhos dos
 *   centros permitidos < descobertos; (iii) ponto descoberto sem centro permitido.
 *
 * Modos:
 *   motor Q N R M --D d                    existência (topo até d, fundo DFS); imprime certificado
 *   motor Q N R M --classificar            topo até M sem fundo: conta as classes de códigos
 *                                          ótimos de tamanho M e a soma |G|/|Aut(C)|
 *   motor Q N R M --ingenuo                contagem rotulada (sem simetria) de códigos de tamanho M
 *                                          (cada código contado exatamente uma vez)
 *   motor Q N R M --D d --reps-out ARQ      só o topo: grava os representantes do nível d
 *   motor Q N R M --reps-in ARQ --parte i/P roda o fundo nos representantes j com j % P == i
 *   motor Q N R M --D d --estimar P         estimador de Knuth do fundo (P sondas)
 *   --ordem inv                             variante: ponto de ramificação do topo = maior índice
 *                                          descoberto (segunda execução independente)
 *
 * Saída de existência: "EXISTE" (e o código), "NAO_EXISTE" (busca completa).
 */
#define WORDSIZE 64
#define MAXN WORDSIZE
#include <nauty/nauty.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXPAL 24
typedef uint16_t word_t; /* índice de palavra: NP <= 65536 */

static int Q, N, R, M;
static long NP, W, V;
static long pw[32];
static uint8_t *dig;      /* NP x N */
static uint64_t *ball;    /* NP x W */
static word_t *blist;     /* NP x V */
static int ordem_inv = 0;
static int poda_topo_l = 3; /* a poda (ii) no topo só compensa perto do fim; desligá-la não muda a resposta */

static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }
static inline long popc_and(const uint64_t *a, const uint64_t *b) { long s = 0; for (long i = 0; i < W; i++) s += __builtin_popcountll(a[i] & b[i]); return s; }
static inline long popc(const uint64_t *a) { long s = 0; for (long i = 0; i < W; i++) s += __builtin_popcountll(a[i]); return s; }
static inline int tstb(const uint64_t *a, long x) { return (a[x >> 6] >> (x & 63)) & 1; }

static void setup(void) {
    pw[0] = 1; for (int i = 1; i <= N; i++) pw[i] = pw[i - 1] * Q;
    NP = pw[N]; W = (NP + 63) / 64;
    if (NP > 65536) { fprintf(stderr, "espaço grande demais (%ld > 65536)\n", NP); exit(2); }
    dig = malloc(NP * N);
    for (long x = 0; x < NP; x++) for (int k = 0; k < N; k++) dig[x * N + k] = (x / pw[k]) % Q;
    V = 0;
    for (long x = 0; x < NP; x++) { int d = 0; for (int k = 0; k < N; k++) d += dig[x * N + k] != 0; if (d <= R) V++; }
    ball = calloc(NP * W, 8);
    blist = malloc(sizeof(word_t) * NP * V);
    for (long c = 0; c < NP; c++) {
        long k = 0;
        for (long x = 0; x < NP; x++) {
            int d = 0; for (int j = 0; j < N && d <= R; j++) d += dig[c * N + j] != dig[x * N + j];
            if (d <= R) { ball[c * W + (x >> 6)] |= 1ULL << (x & 63); blist[c * V + k++] = (word_t)x; }
        }
    }
}

static void full_unc(uint64_t *u) { for (long i = 0; i < W; i++) u[i] = ~0ULL; if (NP % 64) u[W - 1] = (1ULL << (NP % 64)) - 1; }

/* ------------------------------------------------------------ forma canônica (nauty) */
static long long ncanon = 0;
/* Grafo: palavras 0..k-1 | (coord j, símbolo a) em k + j*Q + a | coordenada j em k + N*Q + j.
   Cores fixas por classe de vértice. Automorfismos do grafo colorido = isometrias do espaço de
   Hamming que preservam o conjunto (palavras distintas têm vizinhanças distintas). */
static double canon(const word_t *S, int k, word_t *out) {
    int n = k + N * Q + N, m = 1;
    graph g[MAXN], cg[MAXN];
    int lab[MAXN], ptn[MAXN], orb[MAXN];
    static DEFAULTOPTIONS_GRAPH(opt);
    statsblk st;
    opt.getcanon = TRUE; opt.defaultptn = FALSE;
    EMPTYGRAPH(g, m, n);
    for (int i = 0; i < k; i++) for (int j = 0; j < N; j++) ADDONEEDGE(g, i, k + j * Q + dig[S[i] * N + j], m);
    for (int j = 0; j < N; j++) for (int a = 0; a < Q; a++) ADDONEEDGE(g, k + j * Q + a, k + N * Q + j, m);
    for (int i = 0; i < n; i++) { lab[i] = i; ptn[i] = 1; }
    ptn[k - 1] = 0; ptn[k + N * Q - 1] = 0; ptn[n - 1] = 0;
    densenauty(g, lab, ptn, orb, &opt, &st, m, n, cg);
    ncanon++;
    int newc[32], newsym[32][16], cntj[32];
    for (int i = k + N * Q; i < n; i++) newc[lab[i] - (k + N * Q)] = i - (k + N * Q);
    for (int j = 0; j < N; j++) cntj[j] = 0;
    for (int i = k; i < k + N * Q; i++) { int v = lab[i] - k, j = v / Q, a = v % Q; newsym[j][a] = cntj[j]++; }
    for (int i = 0; i < k; i++) {
        long x = 0;
        for (int j = 0; j < N; j++) x += newsym[j][dig[S[i] * N + j]] * pw[newc[j]];
        out[i] = (word_t)x;
    }
    /* ordena */
    for (int a = 1; a < k; a++) { word_t v = out[a]; int b = a - 1; while (b >= 0 && out[b] > v) { out[b + 1] = out[b]; b--; } out[b + 1] = v; }
    { double g = st.grpsize1; for (int e = 0; e < st.grpsize2; e++) g *= 10; return g; }
}

/* ------------------------------------------------------------ conjunto de formas (hash) */
typedef struct { long cap, n; int k; word_t *keys; uint8_t *used; double *stab; } hset;
static uint64_t hkey(const word_t *a, int k) { uint64_t h = 1469598103934665603ULL; for (int i = 0; i < k; i++) { h ^= a[i]; h *= 1099511628211ULL; h ^= h >> 29; } return h; }
static void hinit(hset *h, int k, long cap) { h->cap = cap; h->n = 0; h->k = k; h->keys = malloc(sizeof(word_t) * k * cap); h->used = calloc(cap, 1); h->stab = malloc(sizeof(double) * cap); }
static void hfree(hset *h) { free(h->keys); free(h->used); free(h->stab); }
static int hins(hset *h, const word_t *a, double stab);
static void hgrow(hset *h) {
    hset n2; hinit(&n2, h->k, h->cap * 2);
    for (long i = 0; i < h->cap; i++) if (h->used[i]) hins(&n2, h->keys + i * h->k, h->stab[i]);
    hfree(h); *h = n2;
}
static int hins(hset *h, const word_t *a, double stab) {
    if (2 * (h->n + 1) > h->cap) hgrow(h);
    long i = hkey(a, h->k) & (h->cap - 1);
    while (h->used[i]) { if (!memcmp(h->keys + i * h->k, a, sizeof(word_t) * h->k)) return 0; i = (i + 1) & (h->cap - 1); }
    h->used[i] = 1; memcpy(h->keys + i * h->k, a, sizeof(word_t) * h->k); h->stab[i] = stab; h->n++;
    return 1;
}

/* ------------------------------------------------------------ podas comuns */
/* gbuf[c] = |B(c) ∩ U| para toda palavra c. Três métodos, mesmo resultado (testado):
   - q potência de 2: o índice de x em base q é a concatenação dos bits dos dígitos, então a soma
     dígito a dígito no grupo (Z_2)^{log q} é o XOR dos índices e B(c) = c XOR B(0). O ganho é a
     convolução-XOR de 1_U com 1_{B(0)}: transformada de Walsh–Hadamard (exata em inteiros);
   - poucos descobertos: acumula pelas bolas dos pontos descobertos;
   - senão: popcount de B(c) AND U. */
static int *WB = NULL, *WU = NULL;
static void wht(int *a, long n) { for (long h = 1; h < n; h <<= 1) for (long i = 0; i < n; i += h << 1) for (long j = i; j < i + h; j++) { int x = a[j], y = a[j + h]; a[j] = x + y; a[j + h] = x - y; } }
static int metodo_ganho = -1; /* -1 automático; 0 popcount; 1 acumula; 2 WHT (para testes) */
static void compute_gains(const uint64_t *unc, long nu, int *g) {
    int pot2 = (Q == 2 || Q == 4 || Q == 8);
    int m = metodo_ganho;
    if (m < 0) m = (nu * V < NP * 8) ? 1 : (pot2 ? 2 : 0);
    if (m == 2 && !pot2) m = 0;
    if (m == 1) {
        memset(g, 0, sizeof(int) * NP);
        for (long i = 0; i < W; i++) { uint64_t w = unc[i]; while (w) { long x = i * 64 + __builtin_ctzll(w); w &= w - 1; const word_t *b = blist + x * V; for (long j = 0; j < V; j++) g[b[j]]++; } }
    } else if (m == 2) {
        if (!WB) { WB = malloc(sizeof(int) * NP); WU = malloc(sizeof(int) * NP); for (long x = 0; x < NP; x++) WB[x] = tstb(ball, x); wht(WB, NP); }
        for (long x = 0; x < NP; x++) WU[x] = tstb(unc, x);
        wht(WU, NP);
        for (long x = 0; x < NP; x++) g[x] = WU[x] * WB[x];
        wht(g, NP);
        int sh = __builtin_ctzl(NP);
        for (long x = 0; x < NP; x++) g[x] >>= sh;
    } else {
        for (long c = 0; c < NP; c++) g[c] = (int)popc_and(ball + c * W, unc);
    }
}
/* soma dos l maiores ganhos entre os centros não proibidos (l <= MAXPAL); g já calculado */
static long top_l_sum(const int *g, const uint64_t *forb, int l) {
    long top[MAXPAL + 1]; int nt = 0;
    for (long c = 0; c < NP; c++) {
        long v = g[c];
        if (!v || tstb(forb, c)) continue;
        if (nt < l) { int b = nt++; while (b > 0 && top[b - 1] < v) { top[b] = top[b - 1]; b--; } top[b] = v; }
        else if (v > top[l - 1]) { int b = l - 1; while (b > 0 && top[b - 1] < v) { top[b] = top[b - 1]; b--; } top[b] = v; }
    }
    long s = 0; for (int i = 0; i < nt; i++) s += top[i];
    return s;
}

/* Poda (iv), cota dual da cobertura fracionária: y_x = 1 / max{ganho(c) : c permitido, x ∈ B(c)}
   é viável no dual (para todo c permitido, a soma de y_x sobre B(c) ∩ U é <= ganho(c)/ganho(c) = 1),
   então toda cobertura de U por centros permitidos tem pelo menos sum_x y_x palavras. */
static int usar_dual = 1;
static int dual_bound(const uint64_t *U, const uint64_t *fb, const int *g, int l) {
    double s = 0, lim = l + 1e-6;
    for (long i = 0; i < W; i++) { uint64_t w = U[i]; while (w) { long x = i * 64 + __builtin_ctzll(w); w &= w - 1;
        const word_t *b = blist + x * V; int mg = 0;
        for (long j = 0; j < V; j++) { long c = b[j]; if (g[c] > mg && !tstb(fb, c)) mg = g[c]; }
        if (mg == 0) return 1;
        s += 1.0 / mg; if (s > lim) return 1; } }
    return 0;
}

/* ------------------------------------------------------------ fundo: DFS com proibição */
static long long nodes = 0, nodes_depth[64];
static uint64_t *Ust;   /* pilha de descobertos: (MAXPAL+1) x W */
static uint64_t *forb;  /* proibidos */
static int *cntv;       /* cntv[x] = nº de centros não proibidos em B(x) */
static int *gbuf;
static word_t sol[MAXPAL + 2]; static int solsize = 0;
static int contar_todos = 0; static long long nsol = 0; /* modo ingênuo: conta códigos */

static void forbid(long c) { forb[c >> 6] |= 1ULL << (c & 63); const word_t *b = blist + c * V; for (long j = 0; j < V; j++) cntv[b[j]]--; }
static void unforbid(long c) { forb[c >> 6] &= ~(1ULL << (c & 63)); const word_t *b = blist + c * V; for (long j = 0; j < V; j++) cntv[b[j]]++; }

/* Corte por representantes anteriores (README, "corte por ordem"): no fundo do representante
   j, um conjunto X que contém um subconjunto de D palavras equivalente ao representante i < j
   pode ser descartado, porque a busca do representante i já percorreu todas as completações dele.
   Testamos só os D-subconjuntos que contêm a palavra nova c (os outros já foram testados no pai). */
static hset repidx; static int cut_on = 0, cut_max = 0, Dlev = 0; static long cur_rep = 0;
static long long ncut = 0;
static int cortado(int depth, long c) {
    int n = depth + 1, k = Dlev - 1;          /* escolhe k de sol[0..depth] e junta c */
    int idx[MAXPAL]; word_t T[MAXPAL + 1], CT[MAXPAL + 1];
    for (int i = 0; i < k; i++) idx[i] = i;
    for (;;) {
        for (int i = 0; i < k; i++) T[i] = sol[idx[i]];
        T[k] = (word_t)c;
        canon(T, Dlev, CT);
        long i = hkey(CT, Dlev) & (repidx.cap - 1);
        while (repidx.used[i]) { if (!memcmp(repidx.keys + i * Dlev, CT, sizeof(word_t) * Dlev)) { if ((long)repidx.stab[i] < cur_rep) { ncut++; return 1; } break; } i = (i + 1) & (repidx.cap - 1); }
        int t = k - 1; while (t >= 0 && idx[t] == n - k + t) t--;
        if (t < 0) break;
        idx[t]++; for (int u = t + 1; u < k; u++) idx[u] = idx[u - 1] + 1;
    }
    return 0;
}

static int dfs(int l, int depth) {
    nodes++; nodes_depth[depth]++;
    const uint64_t *U = Ust + depth * W;
    long nu = popc(U);
    if (nu == 0) { if (contar_todos) { if (l == 0) nsol++; return 0; } solsize = depth + 1; return 1; }
    if (l == 0) return 0;
    if ((long)l * V < nu) return 0;                 /* poda (i) */
    long p = -1; int best = 1 << 30;
    for (long i = 0; i < W; i++) { uint64_t w = U[i]; while (w) { long x = i * 64 + __builtin_ctzll(w); w &= w - 1; if (cntv[x] < best) { best = cntv[x]; p = x; } } }
    if (best == 0) return 0;                          /* poda (iii) */
    if (l >= 2) { compute_gains(U, nu, gbuf); if (top_l_sum(gbuf, forb, l) < nu) return 0; /* poda (ii) */
                  if (usar_dual && dual_bound(U, forb, gbuf, l)) return 0; }          /* poda (iv) */
    /* candidatos: centros permitidos de B(p), por ganho decrescente */
    long nc = 0; long *cand = malloc(sizeof(long) * best); long *gn = malloc(sizeof(long) * best);
    const word_t *b = blist + p * V;
    for (long j = 0; j < V; j++) { long c = b[j]; if (tstb(forb, c)) continue; cand[nc] = c; gn[nc] = (l == 1) ? 0 : gbuf[c]; nc++; }
    for (long a = 1; a < nc; a++) { long c = cand[a], g = gn[a]; long t = a - 1; while (t >= 0 && gn[t] < g) { cand[t + 1] = cand[t]; gn[t + 1] = gn[t]; t--; } cand[t + 1] = c; gn[t + 1] = g; }
    int found = 0; long a;
    uint64_t *U2 = Ust + (depth + 1) * W;
    for (a = 0; a < nc && !found; a++) {
        long c = cand[a];
        for (long i = 0; i < W; i++) U2[i] = U[i] & ~ball[c * W + i];
        sol[depth + 1] = (word_t)c;
        forbid(c);                     /* proíbe c no filho (já está no código) e nos irmãos seguintes */
        if (cut_on && depth + 2 > Dlev && depth + 2 <= cut_max && cortado(depth, c)) continue;
        if (dfs(l - 1, depth + 1)) found = 1;
    }
    for (long t = 0; t < a; t++) unforbid(cand[t]);
    free(cand); free(gn);
    return found;
}

/* prepara o estado do fundo para o conjunto S (k palavras) e roda; devolve 1 se existe */
static int run_bottom(const word_t *S, int k) {
    memset(forb, 0, W * 8);
    for (long x = 0; x < NP; x++) cntv[x] = (int)V;
    uint64_t *U = Ust + (k - 1) * W;   /* profundidade = k-1 (raiz = palavra única no nível 1) */
    full_unc(U);
    for (int i = 0; i < k; i++) { for (long t = 0; t < W; t++) U[t] &= ~ball[S[i] * W + t]; forbid(S[i]); sol[i] = S[i]; }
    int r = dfs(M - k, k - 1);
    return r;
}

/* ------------------------------------------------------------ estimador de Knuth do fundo */
static uint64_t krs = 0x9E3779B97F4A7C15ULL;
static inline uint64_t krnd(void) { krs ^= krs << 13; krs ^= krs >> 7; krs ^= krs << 17; return krs; }
static double probe(const word_t *S, int k) {
    memset(forb, 0, W * 8);
    for (long x = 0; x < NP; x++) cntv[x] = (int)V;
    uint64_t *U = malloc(W * 8); full_unc(U);
    for (int i = 0; i < k; i++) { for (long t = 0; t < W; t++) U[t] &= ~ball[S[i] * W + t]; forbid(S[i]); sol[i] = S[i]; }
    double est = 1, mult = 1; int l = M - k; int depth = k - 1;
    long *cand = malloc(sizeof(long) * V), *gn = malloc(sizeof(long) * V);
    long *forbl = malloc(sizeof(long) * V * (MAXPAL + 1)); long nfl = 0;
    for (;;) {
        long nu = popc(U);
        if (nu == 0 || l == 0 || (long)l * V < nu) break;
        long p = -1; int best = 1 << 30;
        for (long i = 0; i < W; i++) { uint64_t w = U[i]; while (w) { long x = i * 64 + __builtin_ctzll(w); w &= w - 1; if (cntv[x] < best) { best = cntv[x]; p = x; } } }
        if (best == 0) break;
        if (l >= 2) { compute_gains(U, nu, gbuf); if (top_l_sum(gbuf, forb, l) < nu) break; if (usar_dual && dual_bound(U, forb, gbuf, l)) break; }
        long nc = 0; const word_t *b = blist + p * V;
        for (long j = 0; j < V; j++) { long c = b[j]; if (tstb(forb, c)) continue; cand[nc] = c; gn[nc] = (l == 1) ? 0 : gbuf[c]; nc++; }
        for (long a = 1; a < nc; a++) { long c = cand[a], g = gn[a]; long t = a - 1; while (t >= 0 && gn[t] < g) { cand[t + 1] = cand[t]; gn[t + 1] = gn[t]; t--; } cand[t + 1] = c; gn[t + 1] = g; }
        long kk;
        if (cut_on && depth + 2 > Dlev && depth + 2 <= cut_max) {
            long nk = 0; long *ok = malloc(sizeof(long) * nc);
            for (long a = 0; a < nc; a++) if (!cortado(depth, cand[a])) ok[nk++] = a;
            if (nk == 0) { free(ok); break; }
            kk = ok[krnd() % nk]; free(ok); nc = nk;
        } else kk = (long)(krnd() % nc);
        sol[depth + 1] = (word_t)cand[kk];
        for (long a = 0; a <= kk; a++) { forbid(cand[a]); forbl[nfl++] = cand[a]; }
        for (long t = 0; t < W; t++) U[t] &= ~ball[cand[kk] * W + t];
        mult *= nc; est += mult; l--; depth++;
    }
    for (long t = 0; t < nfl; t++) unforbid(forbl[t]);
    for (int i = 0; i < k; i++) unforbid(S[i]);
    free(U); free(cand); free(gn); free(forbl);
    return est;
}

/* ------------------------------------------------------------ topo: níveis com dedup */
static int found_top = 0; static word_t found_code[MAXPAL];
static long long n_cover_classes = 0; static long double sum_orbit = 0;
static long double groupG(void) { long double g = 1; long double qf = 1; for (int i = 2; i <= Q; i++) qf *= i; for (int j = 0; j < N; j++) g *= qf; for (int i = 2; i <= N; i++) g *= i; return g; }

/* devolve o conjunto do nível D (representantes não-cobridores que sobrevivem às podas) */
static hset run_top(int D, int classificar, long long *lvl_count) {
    hset cur; hinit(&cur, 1, 4);
    word_t z = 0, cz[1]; double st0 = canon(&z, 1, cz); hins(&cur, cz, st0);
    lvl_count[1] = 1;
    uint64_t *U = malloc(W * 8);
    uint64_t *fz = calloc(W, 8);
    word_t T[MAXPAL + 1], CT[MAXPAL + 1];
    for (int k = 1; k < D; k++) {
        hset nxt; hinit(&nxt, k + 1, 1024);
        for (long i = 0; i < cur.cap; i++) {
            if (!cur.used[i]) continue;
            const word_t *S = cur.keys + i * k;
            full_unc(U);
            for (int t = 0; t < k; t++) for (long s = 0; s < W; s++) U[s] &= ~ball[S[t] * W + s];
            long nu = popc(U);
            /* p = f(S): menor (ou maior) índice descoberto -- função só da forma canônica S */
            long p = -1;
            if (!ordem_inv) { for (long s = 0; s < W && p < 0; s++) if (U[s]) p = s * 64 + __builtin_ctzll(U[s]); }
            else { for (long s = W - 1; s >= 0 && p < 0; s--) if (U[s]) p = s * 64 + 63 - __builtin_clzll(U[s]); }
            (void)nu;
            for (long j = 0; j < V; j++) {
                word_t w = blist[p * V + j];
                memcpy(T, S, sizeof(word_t) * k); T[k] = w;
                /* descobertos de T, para as podas */
                uint64_t *U2 = Ust; /* área temporária */
                for (long s = 0; s < W; s++) U2[s] = U[s] & ~ball[w * W + s];
                long nu2 = popc(U2);
                int l = M - (k + 1);
                if (nu2 == 0) {
                    double stc = canon(T, k + 1, CT);
                    if (hins(&nxt, CT, -1.0)) {
                        if (classificar && k + 1 == M) { n_cover_classes++; sum_orbit += groupG() / (long double)stc; }
                        if (!found_top) { found_top = 1; memcpy(found_code, CT, sizeof(word_t) * (k + 1)); for (int t = k + 1; t < MAXPAL; t++) found_code[t] = 0xFFFF; }
                    }
                    continue;
                }
                if (l == 0) continue;
                if ((long)l * V < nu2) continue;                         /* poda (i) */
                if (l <= poda_topo_l) { compute_gains(U2, nu2, gbuf); if (top_l_sum(gbuf, fz, l) < nu2) continue; } /* poda (ii), sem proibição */
                double stc = canon(T, k + 1, CT);
                hins(&nxt, CT, stc);
            }
        }
        hfree(&cur); cur = nxt;
        long long nn = 0; for (long i = 0; i < cur.cap; i++) if (cur.used[i] && cur.stab[i] >= 0) nn++;
        lvl_count[k + 1] = nn;
        fprintf(stderr, "  nível %d: %lld representantes (+%lld cobridores), canon=%lld\n", k + 1, nn, (long long)cur.n - nn, ncanon);
        if (found_top && !classificar) break;
        /* remove os cobridores do conjunto (não ramificam) */
        hset clean; hinit(&clean, k + 1, 1024);
        for (long i = 0; i < cur.cap; i++) if (cur.used[i] && cur.stab[i] >= 0) hins(&clean, cur.keys + i * (k + 1), cur.stab[i]);
        hfree(&cur); cur = clean;
    }
    free(U); free(fz);
    return cur;
}

static void print_word(FILE *f, long x) { for (int k = 0; k < N; k++) fputc('0' + dig[x * N + k], f); }

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "uso: %s Q N R M [--D d] [--classificar] [--ingenuo] [--reps-out A] [--reps-in A --parte i/P] [--estimar P] [--ordem inv] [--cert A]\n", argv[0]); return 2; }
    Q = atoi(argv[1]); N = atoi(argv[2]); R = atoi(argv[3]); M = atoi(argv[4]);
    int D = 3, classificar = 0, ingenuo = 0, estimar = 0, pi = 0, pP = 1; const char *reps_out = 0, *reps_in = 0, *certf = 0;
    for (int i = 5; i < argc; i++) {
        if (!strcmp(argv[i], "--D")) D = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--classificar")) classificar = 1;
        else if (!strcmp(argv[i], "--ingenuo")) ingenuo = 1;
        else if (!strcmp(argv[i], "--reps-out")) reps_out = argv[++i];
        else if (!strcmp(argv[i], "--reps-in")) reps_in = argv[++i];
        else if (!strcmp(argv[i], "--cert")) certf = argv[++i];
        else if (!strcmp(argv[i], "--parte")) { sscanf(argv[++i], "%d/%d", &pi, &pP); }
        else if (!strcmp(argv[i], "--estimar")) estimar = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--corte")) { cut_max = atoi(argv[++i]); cut_on = cut_max > 0; }
        else if (!strcmp(argv[i], "--sem-dual")) usar_dual = 0;
        else if (!strcmp(argv[i], "--metodo-ganho")) metodo_ganho = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--ordem")) { ordem_inv = !strcmp(argv[++i], "inv"); }
        else if (!strcmp(argv[i], "--semente")) krs ^= (uint64_t)atoll(argv[++i]) * 0x2545F4914F6CDD1DULL;
        else { fprintf(stderr, "opção desconhecida %s\n", argv[i]); return 2; }
    }
    if (M > MAXPAL || M + N * Q + N > MAXN) { fprintf(stderr, "instância grande demais para o grafo (M+NQ+N <= %d)\n", MAXN); return 2; }
    setup();
    Ust = malloc((MAXPAL + 2) * W * 8); forb = calloc(W, 8); cntv = malloc(sizeof(int) * NP); gbuf = malloc(sizeof(int) * NP);
    double t0 = now();
    printf("instancia K%d(%d,%d) M=%d |B|=%ld |G|=%.6Le\n", Q, N, R, M, V, groupG());

    if (ingenuo) {
        /* contagem rotulada: DFS sem simetria a partir do vazio; cada código de tamanho M que cobre é
           achado uma vez (o primeiro centro, na ordem, de C ∩ B(p) em cada nó). Só para M ótimo. */
        contar_todos = 1;
        memset(forb, 0, W * 8); for (long x = 0; x < NP; x++) cntv[x] = (int)V;
        full_unc(Ust);
        dfs(M, 0);
        printf("INGENUO codigos_rotulados=%lld nos=%lld tempo=%.2fs\n", nsol, nodes, now() - t0);
        return 0;
    }
    if (classificar) {
        long long lc[MAXPAL + 2] = {0};
        hset h = run_top(M, 1, lc); hfree(&h);
        printf("CLASSIFICAR classes=%lld soma_orbitas=%.0Lf canon=%lld tempo=%.2fs\n", n_cover_classes, sum_orbit, ncanon, now() - t0);
        return 0;
    }

    /* conjunto de representantes do nível D: gerado aqui ou lido de arquivo */
    word_t *reps = NULL; long nreps = 0; int k = D;
    long long lc[MAXPAL + 2] = {0};
    if (reps_in) {
        FILE *f = fopen(reps_in, "r"); if (!f) { perror(reps_in); return 2; }
        int q2, n2, r2, m2; if (fscanf(f, "REPS %d %d %d %d %d %ld", &q2, &n2, &r2, &m2, &k, &nreps) != 6 || q2 != Q || n2 != N || r2 != R || m2 != M) { fprintf(stderr, "cabeçalho inválido\n"); return 2; }
        reps = malloc(sizeof(word_t) * k * nreps);
        for (long i = 0; i < nreps * k; i++) { unsigned v; if (fscanf(f, "%u", &v) != 1) { fprintf(stderr, "arquivo curto\n"); return 2; } reps[i] = (word_t)v; }
        fclose(f); D = k;
    } else {
        hset h = run_top(D, 0, lc);
        if (found_top) {
            printf("EXISTE (no topo) tempo=%.2fs\n", now() - t0);
            for (int i = 0; i < MAXPAL && found_code[i] != 0xFFFF; i++) { print_word(stdout, found_code[i]); printf("\n"); }
            return 0;
        }
        nreps = 0; reps = malloc(sizeof(word_t) * D * (h.n + 1));
        /* ordem determinística: ordena os representantes lexicograficamente */
        for (long i = 0; i < h.cap; i++) if (h.used[i]) { memcpy(reps + nreps * D, h.keys + i * D, sizeof(word_t) * D); nreps++; }
        hfree(&h);
        /* insertion-free: qsort com comparação lexicográfica de palavras */
        {
            long n = nreps; word_t *tmp = malloc(sizeof(word_t) * D);
            /* shell sort simples (estável o bastante, determinístico) */
            for (long gap = n / 2; gap > 0; gap /= 2)
                for (long i = gap; i < n; i++) {
                    memcpy(tmp, reps + i * D, sizeof(word_t) * D); long j = i;
                    while (j >= gap) { const word_t *a = reps + (j - gap) * D; int c = 0; for (int t = 0; t < D; t++) if (a[t] != tmp[t]) { c = a[t] > tmp[t] ? 1 : -1; break; } if (c <= 0) break; memcpy(reps + j * D, a, sizeof(word_t) * D); j -= gap; }
                    memcpy(reps + j * D, tmp, sizeof(word_t) * D);
                }
            free(tmp);
        }
        printf("topo: niveis");
        for (int i = 1; i <= D; i++) printf(" %lld", lc[i]);
        printf(" | reps_nivel_%d=%ld canon=%lld tempo_topo=%.2fs\n", D, nreps, ncanon, now() - t0);
        if (reps_out) {
            FILE *f = fopen(reps_out, "w");
            fprintf(f, "REPS %d %d %d %d %d %ld\n", Q, N, R, M, D, nreps);
            for (long i = 0; i < nreps; i++) { for (int t = 0; t < D; t++) fprintf(f, "%u%c", reps[i * D + t], t + 1 < D ? ' ' : '\n'); }
            fclose(f);
            printf("gravado %s\n", reps_out);
            return 0;
        }
    }

    Dlev = D;
    if (cut_on) { hinit(&repidx, D, 1024); for (long r = 0; r < nreps; r++) hins(&repidx, reps + r * D, (double)r); }
    if (estimar) {
        double tot = 0; double te = now();
        for (int pn = 0; pn < estimar; pn++) { long r = (long)(krnd() % nreps); cur_rep = r; tot += probe(reps + r * D, D); }
        double est = tot / estimar * nreps;
        printf("ESTIMATIVA_FUNDO nos~%.3e (reps=%ld, sondas=%d, %.1fs)\n", est, nreps, estimar, now() - te);
        return 0;
    }

    FILE *cf = certf ? fopen(certf, "w") : NULL;
    if (cf) fprintf(cf, "CERT %d %d %d %d D=%d reps=%ld parte=%d/%d ordem=%s\n", Q, N, R, M, D, nreps, pi, pP, ordem_inv ? "inv" : "dir");
    int found = 0; long long tot_nodes = 0; long done = 0;
    for (long r = 0; r < nreps && !found; r++) {
        if (r % pP != pi) continue;
        long long n0 = nodes; cur_rep = r;
        found = run_bottom(reps + r * D, D);
        done++;
        if (cf) { fprintf(cf, "%ld", r); for (int t = 0; t < D; t++) fprintf(cf, " %u", reps[r * D + t]); fprintf(cf, " nos=%lld %s\n", nodes - n0, found ? "EXISTE" : "vazio"); fflush(cf); }
    }
    tot_nodes = nodes;
    double el = now() - t0;
    printf("K%d(%d,%d) M=%d: %s parte=%d/%d reps_feitos=%ld nos_fundo=%lld cortes=%lld canon=%lld tempo=%.2fs\n", Q, N, R, M, found ? "EXISTE" : "NAO_EXISTE", pi, pP, done, tot_nodes, ncut, ncanon, el);
    printf("nos_por_profundidade:"); for (int d = 0; d <= M; d++) printf(" %lld", nodes_depth[d]); printf("\n");
    if (cf) { fprintf(cf, "FIM %s reps_feitos=%ld nos=%lld tempo=%.2f\n", found ? "EXISTE" : "NAO_EXISTE", done, tot_nodes, el); fclose(cf); }
    if (found) for (int i = 0; i < solsize; i++) { print_word(stdout, sol[i]); printf("\n"); }
    return found ? 10 : 0;
}
