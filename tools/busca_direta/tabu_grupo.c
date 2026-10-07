/*
 * tabu_grupo.c -- busca tabu de códigos de cobertura K_q(n,R) invariantes por um grupo G de isometrias.
 *
 * Por que existe: a busca direta (tabu.c) fica longe dos recordes de 2011 nas células médias, e esses
 * recordes quase sempre têm estrutura. O método clássico para achá-los é prescrever automorfismos
 * (Östergård e Weakley, "Constructing covering codes with given automorphisms", Des. Codes Cryptogr. 16
 * (1999)): o código é a união das órbitas por G de poucos representantes, e a busca anda só neles.
 *
 * Uso: tabu_grupo q n R nrep segundos semente prefixo "geradores" [tenure=1] [max_cand=0 (todos)]
 *   geradores: separados por ';', cada um "p0,...,p{n-1}[:a0,...,a{n-1}[:m0,...,m{n-1}]]", que age como
 *   y_i = m_i x_{p_i} + a_i (mod q), com m_i invertível mod q (padrão a = 0, m = 1). Ex. (n=6): troca
 *   cíclica "1,2,3,4,5,0"; translação por 111111: "0,1,2,3,4,5:1,1,1,1,1,1"; negação em F_5^6:
 *   "0,1,2,3,4,5:0,0,0,0,0,0:4,4,4,4,4,4".
 *
 * A conta: a órbita de pontos o fica coberta sse alguma bola B_R(r) de um representante r a intersecta
 * (x em o é coberto por g·r sse g^{-1}x ∈ B_R(r) ∩ o). Então basta cO[o] = soma_r |o ∩ B_R(r)|, e mover
 * um representante custa as mesmas duas cascas da busca direta, com o índice da órbita no lugar do
 * ponto. O objetivo é o número de PONTOS descobertos (soma dos tamanhos das órbitas descobertas).
 * Avaliar um movimento = acumular a variação de cada órbita tocada pelas duas cascas num rascunho
 * (dlt) e contar quem passa de coberta a descoberta e vice-versa; nada em cO muda na avaliação.
 *
 * Ao zerar: expande as órbitas, tira repetidas e grava `<prefixo>_M<M>.txt`; depois tira o representante
 * cuja saída descobre menos pontos e segue. O resultado é HIPÓTESE até tools/verify/verify.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAXN 24
#define MAXQ 10
#define MAXG 4096

static int q, n, R;
static uint64_t N;
static int64_t pw[MAXN + 1];
static int64_t delta[MAXN][MAXQ][MAXQ];
static uint32_t *oid, *osz, *orep, nor;
static uint32_t *cO;
static uint32_t *uo, *upos, nuo; /* órbitas descobertas */
static uint64_t nunc;           /* pontos descobertos */
static int ng;
static uint8_t gp[MAXG][MAXN], ga[MAXG][MAXN], gm[MAXG][MAXN];
static int nrep;
static uint8_t (*rp)[MAXN];
static int64_t *ri;
static int32_t *dlt;    /* rascunho da avaliação, por órbita */
static uint32_t *toc;   /* órbitas tocadas na avaliação */
static size_t ntoc;
static uint64_t rng = 0x2545F4914F6CDD1DULL;

static inline uint64_t rnd(void) { rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }
static double agora(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }

static void digitos(uint64_t x, uint8_t *d) { for (int k = 0; k < n; k++) { d[k] = (uint8_t)(x % q); x /= q; } }
static uint64_t indice(const uint8_t *d) { uint64_t x = 0; for (int k = 0; k < n; k++) x += d[k] * (uint64_t)pw[k]; return x; }
static void aplica(int g, const uint8_t *x, uint8_t *y) { for (int i = 0; i < n; i++) y[i] = (uint8_t)((gm[g][i] * x[gp[g][i]] + ga[g][i]) % q); }

/* transições de cobertura de uma órbita; modo 1 mexe na lista de descobertas, modo 0 só em cO
 * (modo 0 serve para medir a saída de um representante e desfazer) */
static inline int64_t soma(uint32_t o, int modo) {
    if (cO[o]++ == 0) {
        if (modo) { uint32_t k = upos[o], last = uo[--nuo]; uo[k] = last; upos[last] = k; nunc -= osz[o]; }
        return -(int64_t)osz[o];
    }
    return 0;
}
static inline int64_t tira(uint32_t o, int modo) {
    if (--cO[o] == 0) {
        if (modo) { upos[o] = nuo; uo[nuo++] = o; nunc += osz[o]; }
        return (int64_t)osz[o];
    }
    return 0;
}

static int64_t bola(const uint8_t *c, int p, int left, int64_t idx, int sinal, int modo) {
    int64_t s = sinal > 0 ? soma(oid[idx], modo) : tira(oid[idx], modo);
    if (left == 0) return s;
    for (int k = p; k < n; k++)
        for (int v = 1; v < q; v++) s += bola(c, k + 1, left - 1, idx + delta[k][c[k]][v], sinal, modo);
    return s;
}

/* aplica o movimento: a casca de raio R fora de j em torno de ia sai, a em torno de ib entra */
static void casca(const uint8_t *c, int j, int p, int left, int64_t ia, int64_t ib) {
    if (left == 0) {
        tira(oid[ia], 1);
        soma(oid[ib], 1);
        return;
    }
    for (int k = p; k < n; k++) {
        if (k == j) continue;
        if (n - k - (j > k ? 1 : 0) < left) break;
        for (int v = 1; v < q; v++) {
            int64_t d = delta[k][c[k]][v];
            casca(c, j, k + 1, left - 1, ia + d, ib + d);
        }
    }
}

/* avaliação: acumula a variação por órbita sem mexer em cO */
static void casca_av(const uint8_t *c, int j, int p, int left, int64_t ia, int64_t ib) {
    if (left == 0) {
        uint32_t oa = oid[ia], ob = oid[ib];
        if (dlt[oa] == 0) toc[ntoc++] = oa;
        dlt[oa]--;
        if (dlt[ob] == 0) toc[ntoc++] = ob;
        dlt[ob]++;
        return;
    }
    for (int k = p; k < n; k++) {
        if (k == j) continue;
        if (n - k - (j > k ? 1 : 0) < left) break;
        for (int v = 1; v < q; v++) {
            int64_t d = delta[k][c[k]][v];
            casca_av(c, j, k + 1, left - 1, ia + d, ib + d);
        }
    }
}

static int64_t avalia(const uint8_t *c, int j, int64_t ia, int64_t ib) {
    ntoc = 0;
    casca_av(c, j, 0, R, ia, ib);
    int64_t dv = 0;
    for (size_t t = 0; t < ntoc; t++) {
        uint32_t o = toc[t];
        if (dlt[o] == 0) continue; /* repetida (voltou a zero e foi posta de novo) ou sem efeito */
        int antes = cO[o] > 0, depois = (int64_t)cO[o] + dlt[o] > 0;
        if (antes && !depois) dv += osz[o];
        else if (!antes && depois) dv -= osz[o];
        dlt[o] = 0;
    }
    return dv;
}

static int grupo(const char *spec) {
    /* identidade + geradores, depois fecho por composição */
    uint8_t gens[64][3][MAXN];
    int nge = 0;
    char *s = strdup(spec), *sv = NULL;
    for (char *tok = strtok_r(s, ";", &sv); tok; tok = strtok_r(NULL, ";", &sv)) {
        char *dois = strchr(tok, ':'), *tres = NULL;
        if (dois) { *dois++ = 0; tres = strchr(dois, ':'); if (tres) *tres++ = 0; }
        int i = 0;
        for (char *e = strtok(tok, ","); e && i < n; e = strtok(NULL, ",")) gens[nge][0][i++] = (uint8_t)atoi(e);
        if (i != n) { fprintf(stderr, "gerador com %d posições\n", i); return -1; }
        memset(gens[nge][1], 0, MAXN);
        if (dois) { i = 0; for (char *e = strtok(dois, ","); e && i < n; e = strtok(NULL, ",")) gens[nge][1][i++] = (uint8_t)(atoi(e) % q); }
        memset(gens[nge][2], 1, MAXN);
        if (tres) { i = 0; for (char *e = strtok(tres, ","); e && i < n; e = strtok(NULL, ",")) gens[nge][2][i++] = (uint8_t)(atoi(e) % q); }
        for (i = 0; i < n; i++) { /* multiplicador tem de ser invertível, senão não é isometria */
            int a = gens[nge][2][i], b = q;
            while (b) { int t = a % b; a = b; b = t; }
            if (a != 1) { fprintf(stderr, "multiplicador não invertível mod q\n"); return -1; }
        }
        int vis[MAXN] = {0};
        for (i = 0; i < n; i++) { if (gens[nge][0][i] >= n || vis[gens[nge][0][i]]++) { fprintf(stderr, "não é permutação\n"); return -1; } }
        nge++;
    }
    free(s);
    ng = 1;
    for (int i = 0; i < n; i++) { gp[0][i] = (uint8_t)i; ga[0][i] = 0; gm[0][i] = 1; }
    for (int a = 0; a < ng; a++)
        for (int b = 0; b < nge; b++) {
            /* h = gen_b ∘ g_a : z_i = mb_i y_{pb_i} + ab_i, y_k = ma_k x_{pa_k} + aa_k */
            uint8_t hp[MAXN], ha[MAXN], hm[MAXN];
            for (int i = 0; i < n; i++) {
                int k = gens[b][0][i], mb = gens[b][2][i];
                hp[i] = gp[a][k];
                hm[i] = (uint8_t)(mb * gm[a][k] % q);
                ha[i] = (uint8_t)((mb * ga[a][k] + gens[b][1][i]) % q);
            }
            int novo = 1;
            for (int c = 0; c < ng && novo; c++)
                if (!memcmp(gp[c], hp, n) && !memcmp(ga[c], ha, n) && !memcmp(gm[c], hm, n)) novo = 0;
            if (novo) {
                if (ng == MAXG) { fprintf(stderr, "grupo grande demais\n"); return -1; }
                memcpy(gp[ng], hp, n); memcpy(ga[ng], ha, n); memcpy(gm[ng], hm, n); ng++;
            }
        }
    return ng;
}

static void orbitas(void) {
    oid = malloc(N * sizeof *oid);
    osz = malloc(N * sizeof *osz);
    orep = malloc(N * sizeof *orep);
    for (uint64_t x = 0; x < N; x++) oid[x] = UINT32_MAX;
    nor = 0;
    uint8_t d[MAXN], e[MAXN];
    for (uint64_t x = 0; x < N; x++) {
        if (oid[x] != UINT32_MAX) continue;
        digitos(x, d);
        uint32_t tam = 0;
        for (int g = 0; g < ng; g++) {
            aplica(g, d, e);
            uint64_t y = indice(e);
            if (oid[y] == UINT32_MAX) { oid[y] = nor; tam++; }
        }
        osz[nor] = tam; orep[nor] = (uint32_t)x; nor++;
    }
}

static int cmp64(const void *a, const void *b) {
    uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
    return (x > y) - (x < y);
}

static int grava(const char *prefixo) {
    uint64_t *pal = malloc((size_t)nrep * ng * sizeof *pal);
    int np = 0;
    uint8_t e[MAXN];
    for (int m = 0; m < nrep; m++)
        for (int g = 0; g < ng; g++) { aplica(g, rp[m], e); pal[np++] = indice(e); }
    /* ordena e tira repetidas */
    qsort(pal, (size_t)np, sizeof *pal, cmp64);
    int u = 0;
    for (int i = 0; i < np; i++) if (i == 0 || pal[i] != pal[i - 1]) pal[u++] = pal[i];
    char nome[512];
    snprintf(nome, sizeof nome, "%s_M%d.txt", prefixo, u);
    FILE *f = fopen(nome, "w");
    if (!f) { perror(nome); exit(3); }
    for (int i = 0; i < u; i++) { digitos(pal[i], e); for (int k = 0; k < n; k++) fputc('0' + e[k], f); fputc('\n', f); }
    fclose(f);
    free(pal);
    fprintf(stderr, "ACHOU M=%d %s\n", u, nome);
    printf("%d %s\n", u, nome);
    fflush(stdout);
    return u;
}

int main(int argc, char **argv) {
    if (argc < 9) { fprintf(stderr, "uso: %s q n R nrep segundos semente prefixo geradores [tenure] [max_cand]\n", argv[0]); return 2; }
    q = atoi(argv[1]); n = atoi(argv[2]); R = atoi(argv[3]); nrep = atoi(argv[4]);
    double secs = atof(argv[5]);
    rng ^= strtoull(argv[6], 0, 10) * 0x9E3779B97F4A7C15ULL;
    for (int i = 0; i < 10; i++) rnd();
    const char *prefixo = argv[7];
    int tenure = argc > 9 ? atoi(argv[9]) : 1;
    int max_cand = argc > 10 ? atoi(argv[10]) : 0;
    if (q < 2 || q > MAXQ || n < 2 || n > MAXN || R < 1 || R >= n || nrep < 1) { fprintf(stderr, "parâmetros\n"); return 2; }
    pw[0] = 1;
    for (int k = 1; k <= n; k++) pw[k] = pw[k - 1] * q;
    N = (uint64_t)pw[n];
    if (N >= (1ULL << 32)) { fprintf(stderr, "q^n grande demais\n"); return 2; }
    for (int p = 0; p < n; p++) for (int a = 0; a < q; a++) for (int v = 0; v < q; v++) delta[p][a][v] = (int64_t)(((a + v) % q) - a) * pw[p];
    if (grupo(argv[8]) < 0) return 2;
    orbitas();
    fprintf(stderr, "|G|=%d órbitas=%u\n", ng, nor);
    cO = calloc(nor, sizeof *cO);
    uo = malloc(nor * sizeof *uo);
    upos = malloc(nor * sizeof *upos);
    rp = calloc((size_t)nrep, sizeof *rp);
    ri = calloc((size_t)nrep, sizeof *ri);
    int64_t *tabu = calloc((size_t)nrep, sizeof *tabu);
    int (*cand)[3] = malloc((size_t)nrep * ng * MAXN * sizeof *cand);
    size_t cas = 1;
    for (int i = 0; i < R; i++) cas = cas * (size_t)(n - 1 - i) / (size_t)(i + 1);
    for (int i = 0; i < R; i++) cas *= (size_t)(q - 1);
    dlt = calloc(nor, sizeof *dlt);
    toc = malloc(2 * cas * sizeof *toc + 16);
    if (!cO || !uo || !upos || !rp || !ri || !tabu || !cand || !dlt || !toc) { fprintf(stderr, "memória\n"); return 3; }
    nuo = nor; nunc = N;
    for (uint32_t o = 0; o < nor; o++) { uo[o] = o; upos[o] = o; }
    for (int m = 0; m < nrep; m++) {
        for (int k = 0; k < n; k++) rp[m][k] = (uint8_t)(rnd() % q);
        ri[m] = (int64_t)indice(rp[m]);
        bola(rp[m], 0, R, ri[m], 1, 1);
    }
    double t0 = agora(), ult = t0;
    uint64_t melhor = nunc;
    int64_t it = 0;
    while (agora() - t0 < secs) {
        if (nunc == 0) {
            grava(prefixo);
            if (nrep == 1) break;
            int pior = 0;
            int64_t menor = INT64_MAX;
            for (int m = 0; m < nrep; m++) {
                int64_t perde = bola(rp[m], 0, R, ri[m], -1, 0);
                bola(rp[m], 0, R, ri[m], 1, 0);
                if (perde < menor) { menor = perde; pior = m; }
            }
            bola(rp[pior], 0, R, ri[pior], -1, 1);
            nrep--;
            memcpy(rp[pior], rp[nrep], n); ri[pior] = ri[nrep]; tabu[pior] = tabu[nrep];
            melhor = nunc;
            continue;
        }
        it++;
        uint32_t o = uo[rnd() % nuo];
        uint8_t x[MAXN], gx[MAXN];
        digitos(orep[o], x);
        int nc = 0;
        for (int g = 0; g < ng; g++) {
            aplica(g, x, gx); /* qualquer ponto da órbita serve: cobrir gx cobre a órbita */
            for (int m = 0; m < nrep; m++) {
                int d = 0;
                for (int k = 0; k < n; k++) d += rp[m][k] != gx[k];
                if (d != R + 1) continue;
                for (int j = 0; j < n; j++) if (rp[m][j] != gx[j]) { cand[nc][0] = m; cand[nc][1] = j; cand[nc][2] = gx[j]; nc++; }
            }
        }
        if (nc == 0) { /* ninguém a R+1: aproxima um representante de um ponto da órbita */
            int m = (int)(rnd() % (uint64_t)nrep);
            aplica((int)(rnd() % (uint64_t)ng), x, gx);
            int dif[MAXN], nd = 0;
            for (int k = 0; k < n; k++) if (rp[m][k] != gx[k]) dif[nd++] = k;
            if (nd == 0) continue;
            int j = dif[rnd() % (uint64_t)nd];
            bola(rp[m], 0, R, ri[m], -1, 1);
            ri[m] += (int64_t)(gx[j] - rp[m][j]) * pw[j]; rp[m][j] = gx[j];
            bola(rp[m], 0, R, ri[m], 1, 1);
            tabu[m] = it + tenure;
            continue;
        }
        if (max_cand > 0 && max_cand < nc) { /* amostra de candidatos (Fisher-Yates parcial) */
            for (int i = 0; i < max_cand; i++) {
                int r = i + (int)(rnd() % (uint64_t)(nc - i)), t3[3];
                memcpy(t3, cand[i], sizeof t3); memcpy(cand[i], cand[r], sizeof t3); memcpy(cand[r], t3, sizeof t3);
            }
            nc = max_cand;
        }
        int64_t bd = INT64_MAX;
        int bi = -1, emp = 0;
        for (int i = 0; i < nc; i++) {
            int m = cand[i][0], j = cand[i][1], b = cand[i][2];
            int64_t dj = (int64_t)(b - rp[m][j]) * pw[j];
            int64_t dv = avalia(rp[m], j, ri[m], ri[m] + dj);
            if (!(tabu[m] <= it || (int64_t)nunc + dv < (int64_t)melhor)) continue;
            if (dv < bd) { bd = dv; bi = i; emp = 1; }
            else if (dv == bd && rnd() % (uint64_t)(++emp) == 0) bi = i;
        }
        if (bi < 0) bi = (int)(rnd() % (uint64_t)nc);
        int m = cand[bi][0], j = cand[bi][1], b = cand[bi][2];
        int64_t dj = (int64_t)(b - rp[m][j]) * pw[j];
        casca(rp[m], j, 0, R, ri[m], ri[m] + dj);
        rp[m][j] = (uint8_t)b; ri[m] += dj;
        tabu[m] = it + tenure + (int64_t)(rnd() % 3);
        if (nunc < melhor) melhor = nunc;
        double tn = agora();
        if (tn - ult > 10) {
            fprintf(stderr, "t=%.0f it=%lld reps=%d descobertos=%llu melhor=%llu\n", tn - t0, (long long)it, nrep,
                    (unsigned long long)nunc, (unsigned long long)melhor);
            ult = tn;
        }
    }
    fprintf(stderr, "fim it=%lld reps=%d descobertos=%llu melhor=%llu\n", (long long)it, nrep,
            (unsigned long long)nunc, (unsigned long long)melhor);
    return 0;
}
