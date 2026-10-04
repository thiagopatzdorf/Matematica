/*
 * sa_cover.c -- busca local (recozimento simulado) por código de cobertura K_q(n,R) <= M.
 *
 * Uso: sa_cover Q N R M SEGUNDOS SEMENTE [SAIDA]
 *   Imprime o melhor número de pontos descobertos; se chegar a 0, grava SAIDA no formato
 *   de data/codes (uma palavra por linha, dígito k = (w / q^k) % q; q <= 10 para o verificador
 *   oficial, q > 10 grava os dígitos separados por espaço).
 *
 * Por que assim: é a heurística clássica de Östergård/Wille (mover uma palavra do código para
 * perto de um ponto descoberto, aceitar piora com probabilidade exp(-delta/T)). Serve só para
 * triagem barata ("o lb é atingível por busca curta?"), não para provar nada: um 0 aqui ainda
 * precisa passar por tools/verify/verify.
 */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int Q, N, R, M;
static long NP;          /* q^n */
static long *pw;         /* q^k */
static int *cov;         /* quantas palavras cobrem cada ponto */
static long *code;       /* índices das palavras */
static long nunc;        /* pontos descobertos */
static int *own;         /* xor dos índices (no código) das palavras que cobrem o ponto */
static int *uniq;        /* pontos cobertos só pela palavra i */
static long *added_at;   /* iteração em que a palavra i entrou (tabu) */
static long *ulist, *upos; /* lista de descobertos com posição (remoção O(1)) */
/* bola: lista de padrões de erro (posições e deslocamentos) */
static int nball;
static int *bpos, *boff, *bw; /* até R entradas por padrão */

static uint64_t rs;
static inline uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static inline double urand(void) { return (rnd() >> 11) * (1.0 / 9007199254740992.0); }

static void gen_ball(int start, int depth, int *pp, int *oo) {
    /* grava o padrão atual */
    for (int i = 0; i < depth; i++) { bpos[nball * R + i] = pp[i]; boff[nball * R + i] = oo[i]; }
    bw[nball] = depth; nball++;
    if (depth == R) return;
    for (int p = start; p < N; p++)
        for (int v = 1; v < Q; v++) { pp[depth] = p; oo[depth] = v; gen_ball(p + 1, depth + 1, pp, oo); }
}

static long ball_count(void) {
    long v = 0, c = 1; /* sum_{i<=R} C(n,i)(q-1)^i */
    for (int i = 0; i <= R; i++) {
        if (i > 0) c = c * (N - i + 1) / i;
        long t = c; for (int j = 0; j < i; j++) t *= (Q - 1);
        v += t;
    }
    return v;
}

static inline long apply(long x, int b) {
    for (int i = 0; i < bw[b]; i++) {
        int p = bpos[b * R + i];
        long d = (x / pw[p]) % Q;
        long nd = (d + boff[b * R + i]) % Q;
        x += (nd - d) * pw[p];
    }
    return x;
}

static inline void uadd(long x) { upos[x] = nunc; ulist[nunc++] = x; }
static inline void udel(long x) { long i = upos[x], y = ulist[--nunc]; ulist[i] = y; upos[y] = i; }

static void add_word_i(long w, int id) {
    for (int b = 0; b < nball; b++) {
        long x = apply(w, b); int c = cov[x]++;
        if (c == 0) { udel(x); uniq[id]++; }
        else if (c == 1) uniq[own[x]]--;
        own[x] ^= id;
    }
}
static void del_word_i(long w, int id) {
    for (int b = 0; b < nball; b++) {
        long x = apply(w, b); int c = --cov[x]; own[x] ^= id;
        if (c == 0) { uadd(x); uniq[id]--; }
        else if (c == 1) uniq[own[x]]++;
    }
}
static long gain_of(long w) { long g = 0; for (int b = 0; b < nball; b++) if (cov[apply(w, b)] == 0) g++; return g; }

int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "uso: %s Q N R M SEGUNDOS SEMENTE [SAIDA]\n", argv[0]); return 2; }
    Q = atoi(argv[1]); N = atoi(argv[2]); R = atoi(argv[3]); M = atoi(argv[4]);
    double secs = atof(argv[5]); rs = 88172645463325252ULL ^ (uint64_t)atoll(argv[6]) * 0x9E3779B97F4A7C15ULL;
    const char *out = argc > 7 ? argv[7] : NULL;
    pw = malloc(sizeof(long) * (N + 1)); pw[0] = 1; for (int i = 1; i <= N; i++) pw[i] = pw[i - 1] * Q;
    NP = pw[N];
    long V = ball_count();
    bpos = malloc(sizeof(int) * V * (R > 0 ? R : 1)); boff = malloc(sizeof(int) * V * (R > 0 ? R : 1)); bw = malloc(sizeof(int) * V);
    int pp[64], oo[64]; nball = 0; gen_ball(0, 0, pp, oo);
    cov = calloc(NP, sizeof(int)); ulist = malloc(sizeof(long) * NP); upos = malloc(sizeof(long) * NP);
    code = malloc(sizeof(long) * (M + 1)); own = calloc(NP, sizeof(int)); uniq = calloc(M + 1, sizeof(int));
    added_at = calloc(M + 1, sizeof(long));
    nunc = 0; for (long x = 0; x < NP; x++) uadd(x);
    /* INIT=arquivo: semeia com as primeiras M palavras de um código (dígitos separados por espaço
       ou colados); o resto, se faltar, é aleatório. Serve para "tirar uma palavra e consertar". */
    {
        int k = 0; FILE *fi = getenv("INIT") ? fopen(getenv("INIT"), "r") : NULL;
        char line[4096];
        while (fi && k < M && fgets(line, sizeof line, fi)) {
            long w = 0; int d = 0; char *p = line;
            while (*p && d < N) {
                if (*p >= '0' && *p <= '9') {
                    long v = strtol(p, &p, 10);
                    if (strchr(line, ' ') == NULL) { /* dígitos colados: reler um a um */ break; }
                    w += v * pw[d++];
                } else p++;
            }
            if (strchr(line, ' ') == NULL) { d = 0; w = 0; for (p = line; *p >= '0' && *p <= '9' && d < N; p++) w += (*p - '0') * pw[d++]; }
            if (d == N) { code[k] = w; add_word_i(w, k); k++; }
        }
        if (fi) fclose(fi);
        for (int i = k; i < M; i++) { code[i] = (long)(rnd() % NP); add_word_i(code[i], i); }
    }
    int modo = getenv("MODO") ? atoi(getenv("MODO")) : 1;
    int tabu = getenv("TABU") ? atoi(getenv("TABU")) : (M / 4 > 2 ? M / 4 : 2);
    int ncand = getenv("CAND") ? atoi(getenv("CAND")) : 8;
    long best = nunc; long *bestc = malloc(sizeof(long) * M); memcpy(bestc, code, sizeof(long) * M);
    double T0 = 2.0, T = T0; clock_t t0 = clock(); long it = 0, lastimp = 0;
    while (nunc > 0) {
        if ((it & 1023) == 0) {
            double el = (double)(clock() - t0) / CLOCKS_PER_SEC;
            if (el > secs) break;
            T = T0 * pow(0.002, fmod(el, secs / 4.0) / (secs / 4.0)) + 0.05; /* 4 ciclos de resfriamento */
        }
        it++;
        long u = ulist[rnd() % nunc];
        if (modo == 2) {
            /* adiciona a melhor de ncand palavras perto de u (posição M), remove a de menor uniq fora do tabu */
            long bw_ = -1, bg = -1;
            for (int t = 0; t < ncand; t++) { long w = apply(u, (int)(rnd() % nball)); long g = gain_of(w); if (g > bg || (g == bg && (rnd() & 1))) { bg = g; bw_ = w; } }
            code[M] = bw_; uniq[M] = 0; add_word_i(bw_, M); added_at[M] = it;
            int bi = -1; long bu = 1L << 60;
            for (int i = 0; i <= M; i++) {
                if (i != M && it - added_at[i] < tabu) continue;
                if (i == M) continue;
                long s = uniq[i] * 4 + (long)(rnd() & 3);
                if (s < bu) { bu = s; bi = i; }
            }
            if (bi < 0) bi = (int)(rnd() % M);
            del_word_i(code[bi], bi);
            /* move a palavra M para a posição bi (renumera own) */
            del_word_i(code[M], M); code[bi] = code[M]; uniq[bi] = 0; add_word_i(code[bi], bi); added_at[bi] = it;
            if (nunc < best) { best = nunc; memcpy(bestc, code, sizeof(long) * M); lastimp = it; }
            continue;
        }
        long w = apply(u, (int)(rnd() % nball));
        int i = (int)(rnd() % M);
        long old = code[i], before = nunc;
        del_word_i(old, i); add_word_i(w, i);
        long d = nunc - before;
        if (d <= 0 || urand() < exp(-d / T)) {
            code[i] = w;
            if (nunc < best) { best = nunc; memcpy(bestc, code, sizeof(long) * M); lastimp = it; }
        } else { del_word_i(w, i); add_word_i(old, i); }
    }
    printf("q=%d n=%d R=%d M=%d melhor_descobertos=%ld iter=%ld bola=%ld espaco=%ld\n", Q, N, R, M, best, it, V, NP);
    if (best == 0 && out) {
        FILE *f = fopen(out, "w");
        for (int i = 0; i < M; i++) {
            for (int k = 0; k < N; k++) {
                long d = (bestc[i] / pw[k]) % Q;
                if (Q <= 10) fputc('0' + (int)d, f); else fprintf(f, "%s%ld", k ? " " : "", d);
            }
            fputc('\n', f);
        }
        fclose(f);
        printf("gravado %s\n", out);
    }
    (void)lastimp;
    return best == 0 ? 0 : 1;
}
