/*
 * tabu.c -- busca tabu direta para códigos de cobertura K_q(n,R) <= M, sem estrutura imposta.
 *
 * Por que existe: o kit de `scripts/search` e `scripts/attack` supõe q primo e uma base de classes
 * laterais de um código linear. Nas células pequenas (q^n até ~10^8) e com q não primo (4, 6, 8, 9, 10)
 * não há base linear; a busca local direta no espaço inteiro é o método clássico (Östergård, "Constructing
 * covering codes by tabu search", J. Combin. Des. 5 (1997)) e não existia neste repositório.
 *
 * Uso:  tabu q n R M segundos semente prefixo [tenure=1] [max_cand=0 (todos)] [pesos=0] [inicial.txt]
 *
 * Movimento (o de Östergård): sorteia um ponto descoberto x; os candidatos são as palavras c a distância
 * exatamente R+1 de x, cada uma trocando UMA coordenada j em que difere de x para o valor x_j (então x
 * passa a ficar coberto). O custo exato do movimento sai de duas cascas, não da bola inteira:
 *   perde  = { y : y_j = c_j, d(y_{-j}, c_{-j}) = R }  (saem da bola)   -- conta os com cnt == 1
 *   ganha  = { y : y_j = x_j, d(y_{-j}, c_{-j}) = R }  (entram na bola) -- conta os com cnt == 0
 * Os outros pontos não mudam de distância. Escolhe o melhor candidato não tabu (critério de aspiração:
 * tabu pode se bater o melhor já visto com este M). Ao zerar os descobertos, grava
 * `<prefixo>_M<M>.txt` (palavras distintas), tira a palavra de menor cobertura exclusiva e continua com M-1.
 * tenure: a palavra movida fica tabu por tenure + {0,1,2} iterações. Medido em K_2(10,1) (ótimo 120, 10 s):
 * tenure 1 e 3 acham 120; 8, 15 e 30 não acham nem 130. Em K_4(10,5) com M = 60, tenure 1 < 2 < 4 em
 * descobertos. Por isso o padrão é 1.
 * max_cand > 0 avalia só essa quantidade de candidatos sorteados por iteração (troca qualidade por
 * velocidade quando a casca é grande).
 * pesos = 1: cada ponto tem peso (começa em 1) e todo ponto que segue descoberto depois de um movimento
 * ganha +1; o movimento escolhido é o de menor variação PONDERADA (a ideia do RWLS de set cover, aplicada
 * aqui direto ao espaço). Sem aspiração nesse modo.
 *
 * Saída de progresso no stderr. O resultado é HIPÓTESE até passar por tools/verify/verify.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXN 24
#define MAXQ 10

static int q, n, R;
static uint64_t N;
static int64_t pw[MAXN + 1];
static int64_t delta[MAXN][MAXQ][MAXQ]; /* delta[p][a][v]: troca o dígito p de a para (a+v) mod q */
/* contagem de cobertura por ponto: uint8 cabe no cache 2x melhor; com M >= 255 compile com -DCNT16 */
#ifdef CNT16
typedef uint16_t cnt_t;
#define CNT_MAX 65535
#else
typedef uint8_t cnt_t;
#define CNT_MAX 255
#endif
static cnt_t *cnt;
static uint32_t *unc, *pos;
static uint64_t nunc;
static int M, Mcap;
static uint8_t (*cw)[MAXN];
static int64_t *ci;
static int modo_ganha; /* 1: a casca só conta "perde"; o "ganha" sai da lista de descobertos (barato quando ela é curta) */
static size_t casca;   /* C(n-1,R)(q-1)^R, o tamanho de cada casca */
static uint32_t *peso;  /* NULL sem pesos */
static uint64_t rng = 88172645463325252ULL;

static inline uint64_t rnd(void) {
    rng ^= rng << 13;
    rng ^= rng >> 7;
    rng ^= rng << 17;
    return rng;
}

static double agora(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + 1e-9 * t.tv_nsec;
}

static inline void inc(uint32_t y) {
    if (cnt[y]++ == 0) { /* sai da lista de descobertos */
        uint32_t k = pos[y], last = unc[--nunc];
        unc[k] = last;
        pos[last] = k;
    }
}

static inline void dec(uint32_t y) {
    if (--cnt[y] == 0) {
        pos[y] = (uint32_t)nunc;
        unc[nunc++] = y;
    }
}

/* bola inteira: modo 1 soma, -1 subtrai, 0 conta os pontos com cnt == 1 (cobertura exclusiva) */
static uint64_t ball(const uint8_t *c, int p, int left, int64_t idx, int modo) {
    uint64_t s = 0;
    if (modo == 1) inc((uint32_t)idx);
    else if (modo == -1) dec((uint32_t)idx);
    else s += (cnt[idx] == 1);
    if (left == 0) return s;
    for (int k = p; k < n; k++)
        for (int v = 1; v < q; v++) s += ball(c, k + 1, left - 1, idx + delta[k][c[k]][v], modo);
    return s;
}

/* casca de raio exato R fora da coordenada j. modo 0: devolve perde - ganha (variação de descobertos);
 * modo 1: aplica o movimento. */
static int64_t shell(const uint8_t *c, int j, int p, int left, int64_t ia, int64_t ib, int modo) {
    if (left == 0) {
        if (modo == 0) {
            if (peso) return (cnt[ia] == 1 ? (int64_t)peso[ia] : 0) - (modo_ganha || cnt[ib] ? 0 : (int64_t)peso[ib]);
            return (cnt[ia] == 1) - (modo_ganha ? 0 : (cnt[ib] == 0));
        }
        dec((uint32_t)ia);
        inc((uint32_t)ib);
        return 0;
    }
    int64_t s = 0;
    for (int k = p; k < n; k++) {
        if (k == j) continue;
        int resto = n - k - (j > k ? 1 : 0); /* posições disponíveis a partir de k, sem j */
        if (resto < left) break;
        for (int v = 1; v < q; v++) {
            int64_t d = delta[k][c[k]][v];
            s += shell(c, j, k + 1, left - 1, ia + d, ib + d, modo);
        }
    }
    return s;
}

static void poe_palavra(int m, const uint8_t *d) {
    memcpy(cw[m], d, n);
    int64_t idx = 0;
    for (int k = 0; k < n; k++) idx += d[k] * pw[k];
    ci[m] = idx;
}

static void grava(const char *prefixo) {
    /* palavras distintas: duplicata não cobre nada a mais */
    char *visto = calloc((size_t)M, 1);
    int distintas = 0;
    for (int a = 0; a < M; a++) {
        visto[a] = 1;
        for (int b = 0; b < a; b++)
            if (visto[b] && ci[b] == ci[a]) { visto[a] = 0; break; }
        distintas += visto[a];
    }
    char nome[512];
    snprintf(nome, sizeof nome, "%s_M%d.txt", prefixo, distintas);
    FILE *f = fopen(nome, "w");
    if (!f) { perror(nome); exit(3); }
    for (int a = 0; a < M; a++) {
        if (!visto[a]) continue;
        for (int k = 0; k < n; k++) fputc('0' + cw[a][k], f);
        fputc('\n', f);
    }
    fclose(f);
    free(visto);
    fprintf(stderr, "ACHOU M=%d %s\n", distintas, nome);
    printf("%d %s\n", distintas, nome);
    fflush(stdout);
}

/* variação de descobertos se a palavra m trocar a coordenada j para o valor b */
static int64_t avalia(int m, int j, int b) {
    int64_t dj = (int64_t)(b - cw[m][j]) * pw[j];
    if ((uint64_t)nunc * (uint64_t)n >= casca) return shell(cw[m], j, 0, R, ci[m], ci[m] + dj, 0);
    /* ganha = descobertos y com y_j = b e d(y_{-j}, c_{-j}) = R: varre a lista curta */
    modo_ganha = 1;
    int64_t dv = shell(cw[m], j, 0, R, ci[m], ci[m] + dj, 0);
    modo_ganha = 0;
    for (uint64_t u = 0; u < nunc; u++) {
        uint32_t y = unc[u];
        int dd = 0, ok = 1;
        for (int k = 0; k < n && dd <= R; k++) {
            int yk = (int)(y % (uint32_t)q);
            y /= (uint32_t)q;
            if (k == j) {
                if (yk != b) { ok = 0; break; }
            } else dd += yk != cw[m][k];
        }
        if (ok && dd == R) dv -= peso ? (int64_t)peso[unc[u]] : 1;
    }
    return dv;
}

int main(int argc, char **argv) {
    if (argc < 8) {
        fprintf(stderr, "uso: %s q n R M segundos semente prefixo [tenure] [max_cand] [pesos] [inicial.txt]\n", argv[0]);
        return 2;
    }
    q = atoi(argv[1]); n = atoi(argv[2]); R = atoi(argv[3]); M = atoi(argv[4]);
    double secs = atof(argv[5]);
    uint64_t seed = strtoull(argv[6], 0, 10);
    const char *prefixo = argv[7];
    int tenure = argc > 8 ? atoi(argv[8]) : 1;
    if (tenure < 0) tenure = 0;
    int max_cand = argc > 9 ? atoi(argv[9]) : 0;
    int usa_pesos = argc > 10 ? atoi(argv[10]) : 0;
    const char *inicial = argc > 11 ? argv[11] : NULL;
    if (q < 2 || q > MAXQ || n < 1 || n > MAXN || R < 1 || R >= n || M < 1) { fprintf(stderr, "parâmetros\n"); return 2; }
    pw[0] = 1;
    for (int k = 1; k <= n; k++) pw[k] = pw[k - 1] * q;
    N = (uint64_t)pw[n];
    if (N >= (1ULL << 32)) { fprintf(stderr, "q^n grande demais\n"); return 2; }
    for (int p = 0; p < n; p++)
        for (int a = 0; a < q; a++)
            for (int v = 0; v < q; v++) delta[p][a][v] = (int64_t)(((a + v) % q) - a) * pw[p];
    rng ^= seed * 0x9E3779B97F4A7C15ULL;
    for (int i = 0; i < 10; i++) rnd();
    if (M >= CNT_MAX) { fprintf(stderr, "M >= %d: recompile com -DCNT16\n", CNT_MAX); return 2; }
    casca = 1;
    for (int i = 0; i < R; i++) casca = casca * (size_t)(n - 1 - i) / (size_t)(i + 1);
    for (int i = 0; i < R; i++) casca *= (size_t)(q - 1);

    cnt = calloc(N, sizeof *cnt);
    unc = malloc(N * sizeof *unc);
    pos = malloc(N * sizeof *pos);
    Mcap = M;
    cw = calloc((size_t)Mcap, sizeof *cw);
    ci = calloc((size_t)Mcap, sizeof *ci);
    int64_t *tabu = calloc((size_t)Mcap, sizeof *tabu);
    int (*cand)[2] = malloc((size_t)Mcap * MAXN * sizeof *cand);
    if (!cnt || !unc || !pos || !cw || !ci || !tabu || !cand) { fprintf(stderr, "memória\n"); return 3; }
    for (uint64_t y = 0; y < N; y++) { unc[y] = (uint32_t)y; pos[y] = (uint32_t)y; }
    if (usa_pesos) {
        peso = malloc(N * sizeof *peso);
        if (!peso) { fprintf(stderr, "memória\n"); return 3; }
        for (uint64_t y = 0; y < N; y++) peso[y] = 1;
    }
    nunc = N;

    int lidas = 0;
    if (inicial) {
        FILE *f = fopen(inicial, "r");
        if (!f) { perror(inicial); return 2; }
        char linha[256];
        while (lidas < M && fgets(linha, sizeof linha, f)) {
            if ((int)strcspn(linha, "\r\n") != n) continue;
            uint8_t d[MAXN];
            for (int k = 0; k < n; k++) d[k] = (uint8_t)(linha[k] - '0');
            poe_palavra(lidas++, d);
        }
        fclose(f);
    }
    for (int m = lidas; m < M; m++) {
        uint8_t d[MAXN];
        for (int k = 0; k < n; k++) d[k] = (uint8_t)(rnd() % q);
        poe_palavra(m, d);
    }
    for (int m = 0; m < M; m++) ball(cw[m], 0, R, ci[m], 1);

    double t0 = agora(), ult = t0;
    uint64_t melhor = nunc;
    int64_t it = 0;
    while (agora() - t0 < secs) {
        if (nunc == 0) {
            grava(prefixo);
            if (M == 1) break;
            int pior = 0;
            uint64_t menor = UINT64_MAX;
            for (int m = 0; m < M; m++) {
                uint64_t u = ball(cw[m], 0, R, ci[m], 0);
                if (u < menor) { menor = u; pior = m; }
            }
            ball(cw[pior], 0, R, ci[pior], -1);
            M--;
            memcpy(cw[pior], cw[M], n);
            ci[pior] = ci[M];
            tabu[pior] = tabu[M];
            melhor = nunc;
            continue;
        }
        it++;
        uint32_t x = unc[rnd() % nunc];
        uint8_t xd[MAXN];
        uint32_t t = x;
        for (int k = 0; k < n; k++) { xd[k] = (uint8_t)(t % q); t /= q; }
        int nc = 0;
        for (int m = 0; m < M; m++) {
            int d = 0;
            for (int k = 0; k < n; k++) d += cw[m][k] != xd[k];
            if (d != R + 1) continue;
            for (int j = 0; j < n; j++)
                if (cw[m][j] != xd[j]) { cand[nc][0] = m; cand[nc][1] = j; nc++; }
        }
        if (nc == 0) { /* ninguém a R+1: aproxima uma palavra qualquer de x */
            int bm = (int)(rnd() % (uint64_t)M), dif[MAXN], nd = 0;
            for (int k = 0; k < n; k++) if (cw[bm][k] != xd[k]) dif[nd++] = k;
            int bj = dif[rnd() % (uint64_t)nd];
            ball(cw[bm], 0, R, ci[bm], -1);
            ci[bm] += (int64_t)(xd[bj] - cw[bm][bj]) * pw[bj];
            cw[bm][bj] = xd[bj];
            ball(cw[bm], 0, R, ci[bm], 1);
            tabu[bm] = it + tenure;
            continue;
        }
        int lim = nc;
        if (max_cand > 0 && max_cand < nc) { /* sorteia max_cand candidatos (Fisher-Yates parcial) */
            for (int i = 0; i < max_cand; i++) {
                int r = i + (int)(rnd() % (uint64_t)(nc - i));
                int t0m = cand[i][0], t0j = cand[i][1];
                cand[i][0] = cand[r][0]; cand[i][1] = cand[r][1];
                cand[r][0] = t0m; cand[r][1] = t0j;
            }
            lim = max_cand;
        }
        int64_t bd = INT64_MAX;
        int bm = -1, bj = -1, empates = 0;
        for (int i = 0; i < lim; i++) {
            int m = cand[i][0], j = cand[i][1];
            int64_t dv = avalia(m, j, xd[j]);
            int livre = tabu[m] <= it || (!peso && (int64_t)nunc + dv < (int64_t)melhor);
            if (!livre) continue;
            if (dv < bd) { bd = dv; bm = m; bj = j; empates = 1; }
            else if (dv == bd && rnd() % (uint64_t)(++empates) == 0) { bm = m; bj = j; }
        }
        if (bm < 0) { int r = (int)(rnd() % (uint64_t)lim); bm = cand[r][0]; bj = cand[r][1]; }
        int64_t dj = (int64_t)(xd[bj] - cw[bm][bj]) * pw[bj];
        shell(cw[bm], bj, 0, R, ci[bm], ci[bm] + dj, 1);
        cw[bm][bj] = xd[bj];
        ci[bm] += dj;
        tabu[bm] = it + tenure + (int64_t)(rnd() % 3);
        if (nunc < melhor) melhor = nunc;
        if (peso)
            for (uint64_t u = 0; u < nunc; u++)
                if (peso[unc[u]] < UINT32_MAX / 2) peso[unc[u]]++;
        double tn = agora();
        if (tn - ult > 10) {
            fprintf(stderr, "t=%.0f it=%lld M=%d descobertos=%llu melhor=%llu\n", tn - t0, (long long)it, M,
                    (unsigned long long)nunc, (unsigned long long)melhor);
            ult = tn;
        }
    }
    fprintf(stderr, "fim it=%lld M=%d descobertos=%llu melhor=%llu\n", (long long)it, M,
            (unsigned long long)nunc, (unsigned long long)melhor);
    return 0;
}
