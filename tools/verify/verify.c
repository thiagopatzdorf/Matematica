/*
 * verify.c -- verificador oficial de códigos de cobertura K_q(n,R) <= M.  C99, sem dependências.
 *
 * Uso:   verify [-q Q -n N -r R] [-m M] [-u K] ARQUIVO|-
 *        Sem -q/-n/-r, os parâmetros saem do nome do arquivo (q<Q>_n<N>_R<R>_M<M>.txt).
 *        "-" lê a entrada padrão (ex.: a saída de scripts/codes/expand.py).
 *        -u K: se sobrar ponto descoberto, imprime até K deles (um por linha, "uncovered_point=<palavra>",
 *        em ordem crescente do índice) depois da linha de resumo. Sem -u a saída é a de sempre.
 *
 * Entrada: uma palavra por linha, n dígitos '0'..'9' (s[0] .. s[n-1]); linhas vazias ignoradas.
 *          Índice da palavra = sum_k s[k] * q^k (little-endian, a convenção dos C1_Data_*.lean).
 *
 * Confere, nesta ordem, e para no primeiro defeito (código de saída 2):
 *   - todo caractere é dígito < q e toda linha tem exatamente n dígitos;
 *   - não há palavra repetida;
 *   - o total é M (se M veio do nome ou de -m).
 * Depois marca num bitset de q^n bits a bola de raio R de cada palavra e conta os pontos
 * descobertos. Saída 0 sse descobertos = 0; saída 1 se algum ponto ficou descoberto.
 *
 * As bolas são enumeradas por busca em profundidade sobre (posição, deslocamento) com a tabela
 * delta[p][a][v] = (((a + v) mod q) - a) * q^p pré-computada: trocar o dígito p de a para a+v
 * soma delta ao índice, então cada ponto da bola custa uma soma e um "ou" no bitset.
 *
 * Também imprime o sha256 canônico: sha256 das palavras ordenadas por byte, unidas por LF, com
 * LF final (o mesmo de scripts/codes/codefmt.py e dos cabeçalhos C1_Data_*.lean).
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 20
#define MAXQ 10
#define MAXPOINTS (1ULL << 36) /* 64 GiB de pontos = 8 GiB de bitset: teto de sanidade */

/* ------------------------------------------------------------------ sha256 (FIPS 180-4) */
typedef struct {
    uint32_t h[8];
    uint8_t buf[64];
    uint64_t len;
    size_t nbuf;
} sha256_ctx;

static const uint32_t K256[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2};

#define ROR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))

static void sha256_block(sha256_ctx *c, const uint8_t *p) {
    uint32_t w[64], a, b, d, e, f, g, h, cc, t1, t2;
    int i;
    for (i = 0; i < 16; i++)
        w[i] = (uint32_t)p[4 * i] << 24 | (uint32_t)p[4 * i + 1] << 16 | (uint32_t)p[4 * i + 2] << 8 | p[4 * i + 3];
    for (i = 16; i < 64; i++) {
        uint32_t s0 = ROR(w[i - 15], 7) ^ ROR(w[i - 15], 18) ^ (w[i - 15] >> 3);
        uint32_t s1 = ROR(w[i - 2], 17) ^ ROR(w[i - 2], 19) ^ (w[i - 2] >> 10);
        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }
    a = c->h[0]; b = c->h[1]; cc = c->h[2]; d = c->h[3];
    e = c->h[4]; f = c->h[5]; g = c->h[6]; h = c->h[7];
    for (i = 0; i < 64; i++) {
        t1 = h + (ROR(e, 6) ^ ROR(e, 11) ^ ROR(e, 25)) + ((e & f) ^ (~e & g)) + K256[i] + w[i];
        t2 = (ROR(a, 2) ^ ROR(a, 13) ^ ROR(a, 22)) + ((a & b) ^ (a & cc) ^ (b & cc));
        h = g; g = f; f = e; e = d + t1; d = cc; cc = b; b = a; a = t1 + t2;
    }
    c->h[0] += a; c->h[1] += b; c->h[2] += cc; c->h[3] += d;
    c->h[4] += e; c->h[5] += f; c->h[6] += g; c->h[7] += h;
}

static void sha256_init(sha256_ctx *c) {
    static const uint32_t iv[8] = {0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                                   0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19};
    memcpy(c->h, iv, sizeof iv);
    c->len = 0;
    c->nbuf = 0;
}

static void sha256_update(sha256_ctx *c, const void *data, size_t n) {
    const uint8_t *p = data;
    c->len += n;
    while (n) {
        size_t k = 64 - c->nbuf;
        if (k > n) k = n;
        memcpy(c->buf + c->nbuf, p, k);
        c->nbuf += k; p += k; n -= k;
        if (c->nbuf == 64) { sha256_block(c, c->buf); c->nbuf = 0; }
    }
}

static void sha256_final(sha256_ctx *c, char hex[65]) {
    uint64_t bits = c->len * 8;
    uint8_t pad = 0x80, z = 0, lenb[8];
    int i;
    sha256_update(c, &pad, 1);
    while (c->nbuf != 56) sha256_update(c, &z, 1);
    for (i = 0; i < 8; i++) lenb[i] = (uint8_t)(bits >> (56 - 8 * i));
    sha256_update(c, lenb, 8);
    for (i = 0; i < 8; i++) sprintf(hex + 8 * i, "%08x", c->h[i]);
    hex[64] = 0;
}

/* ------------------------------------------------------------------ cobertura */
static int Q, N, R;
static uint64_t POW[MAXN + 1];
static int64_t DELTA[MAXN][MAXQ][MAXQ]; /* delta[p][a][v], v = 1..q-1 */
static uint64_t *COV;

/* marca todos os pontos obtidos de `idx` trocando até `left` dígitos nas posições >= p */
static void ball(const uint8_t *dig, int p, int left, uint64_t idx) {
    COV[idx >> 6] |= 1ULL << (idx & 63);
    if (!left) return;
    if (left == 1) { /* último nível sem recursão: é onde estão quase todos os pontos */
        for (int i = p; i < N; i++) {
            const int64_t *d = DELTA[i][dig[i]];
            for (int v = 1; v < Q; v++) {
                uint64_t j = (uint64_t)((int64_t)idx + d[v]);
                COV[j >> 6] |= 1ULL << (j & 63);
            }
        }
        return;
    }
    for (int i = p; i < N; i++) {
        const int64_t *d = DELTA[i][dig[i]];
        for (int v = 1; v < Q; v++) ball(dig, i + 1, left - 1, (uint64_t)((int64_t)idx + d[v]));
    }
}

static int cmp_words(const void *a, const void *b) { return memcmp(a, b, (size_t)N); }

static int parse_name(const char *path, int *q, int *n, int *r, long *m) {
    const char *b = strrchr(path, '/');
    b = b ? b + 1 : path;
    return sscanf(b, "q%d_n%d_R%d_M%ld", q, n, r, m) == 4;
}

static int die(const char *msg, long line) {
    if (line > 0) fprintf(stderr, "ERRO linha %ld: %s\n", line, msg);
    else fprintf(stderr, "ERRO: %s\n", msg);
    return 2;
}

int main(int argc, char **argv) {
    int q = -1, n = -1, r = -1;
    long m = -1, show = 0;
    const char *path = NULL;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-q") && i + 1 < argc) q = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-n") && i + 1 < argc) n = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-r") && i + 1 < argc) r = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-m") && i + 1 < argc) m = atol(argv[++i]);
        else if (!strcmp(argv[i], "-u") && i + 1 < argc) show = atol(argv[++i]);
        else path = argv[i];
    }
    if (!path) { fprintf(stderr, "uso: verify [-q Q -n N -r R] [-m M] [-u K] ARQUIVO|-\n"); return 2; }
    if (q < 0 || n < 0 || r < 0) {
        int fq, fn, fr; long fm;
        if (!parse_name(path, &fq, &fn, &fr, &fm))
            return die("sem -q/-n/-r e nome fora do padrão q<Q>_n<N>_R<R>_M<M>", 0);
        if (q < 0) q = fq;
        if (n < 0) n = fn;
        if (r < 0) r = fr;
        if (m < 0) m = fm;
    }
    if (q < 2 || q > MAXQ || n < 1 || n > MAXN || r < 0) return die("parâmetros fora do suportado (2<=q<=10, 1<=n<=20)", 0);
    Q = q; N = n; R = r > n ? n : r;
    POW[0] = 1;
    for (int i = 1; i <= n; i++) POW[i] = POW[i - 1] * (uint64_t)q;
    uint64_t npts = POW[n];
    if (npts > MAXPOINTS) return die("q^n grande demais para o bitset", 0);
    for (int p = 0; p < n; p++)
        for (int a = 0; a < q; a++)
            for (int v = 1; v < q; v++) DELTA[p][a][v] = ((int64_t)((a + v) % q) - a) * (int64_t)POW[p];

    FILE *f = strcmp(path, "-") ? fopen(path, "r") : stdin;
    if (!f) return die("não consegui abrir o arquivo", 0);
    size_t cap = 1024, cnt = 0;
    uint8_t *words = malloc(cap * (size_t)n);
    uint64_t nwords64 = (npts + 63) / 64;
    uint64_t *seen = calloc(nwords64, 8);
    COV = calloc(nwords64, 8);
    if (!words || !seen || !COV) return die("sem memória", 0);

    char line[256];
    long ln = 0;
    while (fgets(line, sizeof line, f)) {
        ln++;
        size_t L = strcspn(line, "\r\n");
        if (L == strlen(line) && !feof(f)) return die("linha longa demais", ln);
        line[L] = 0;
        if (L == 0) continue;
        if ((int)L != n) return die("comprimento != n", ln);
        uint64_t idx = 0;
        for (int i = 0; i < n; i++) {
            int d = line[i] - '0';
            if (d < 0 || d > 9) return die("caractere que não é dígito", ln);
            if (d >= q) return die("dígito >= q", ln);
            idx += (uint64_t)d * POW[i];
        }
        if (seen[idx >> 6] >> (idx & 63) & 1) return die("palavra duplicada", ln);
        seen[idx >> 6] |= 1ULL << (idx & 63);
        if (cnt == cap) {
            cap *= 2;
            words = realloc(words, cap * (size_t)n);
            if (!words) return die("sem memória", 0);
        }
        memcpy(words + cnt * (size_t)n, line, (size_t)n);
        cnt++;
    }
    if (f != stdin) fclose(f);
    if (m >= 0 && (long)cnt != m) {
        fprintf(stderr, "ERRO: %zu palavras, M esperado = %ld\n", cnt, m);
        return 2;
    }

    uint8_t dig[MAXN];
    for (size_t w = 0; w < cnt; w++) {
        uint64_t idx = 0;
        for (int i = 0; i < n; i++) {
            dig[i] = (uint8_t)(words[w * n + i] - '0');
            idx += dig[i] * POW[i];
        }
        ball(dig, 0, R, idx);
    }
    /* bits além de q^n no último bloco não existem: marca-os para não contarem */
    if (npts % 64) COV[nwords64 - 1] |= ~0ULL << (npts % 64);
    uint64_t unc = 0, first = UINT64_MAX;
    for (uint64_t i = 0; i < nwords64; i++) {
        uint64_t x = ~COV[i];
        if (x) {
            unc += (uint64_t)__builtin_popcountll(x);
            if (first == UINT64_MAX) first = i * 64 + (uint64_t)__builtin_ctzll(x);
        }
    }

    qsort(words, cnt, (size_t)n, cmp_words);
    sha256_ctx c;
    char hex[65];
    sha256_init(&c);
    for (size_t w = 0; w < cnt; w++) {
        sha256_update(&c, words + w * n, (size_t)n);
        sha256_update(&c, "\n", 1);
    }
    sha256_final(&c, hex);

    printf("q=%d n=%d R=%d M=%zu points=%llu uncovered=%llu sha256=%s", q, n, R, cnt,
           (unsigned long long)npts, (unsigned long long)unc, hex);
    if (unc) {
        char s[MAXN + 1];
        for (int i = 0; i < n; i++) s[i] = (char)('0' + (first / POW[i]) % (uint64_t)q);
        s[n] = 0;
        printf(" first_uncovered=%s", s);
    }
    printf("\n");
    if (unc && show > 0) { /* lista os K primeiros descobertos, em ordem de índice */
        long listed = 0;
        for (uint64_t i = 0; i < nwords64 && listed < show; i++) {
            uint64_t x = ~COV[i];
            while (x && listed < show) {
                uint64_t idx = i * 64 + (uint64_t)__builtin_ctzll(x);
                char s[MAXN + 1];
                for (int k = 0; k < n; k++) s[k] = (char)('0' + (idx / POW[k]) % (uint64_t)q);
                s[n] = 0;
                printf("uncovered_point=%s\n", s);
                listed++;
                x &= x - 1;
            }
        }
    }
    free(words); free(seen); free(COV);
    return unc ? 1 : 0;
}
