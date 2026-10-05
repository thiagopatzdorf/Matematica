/*
 * cobre_n2.c -- verificador independente para R = n - 2 (qualquer q <= 64, n <= 32).
 *
 * Uso: cobre_n2 Q N ARQUIVO      (uma palavra por linha; dígitos 0-9 e depois a-z, A-Z para q > 10)
 *
 * Por que existe: tools/verify/verify.c só aceita q <= 10 e marca bolas num bitset de q^n bits;
 * aqui a conta é outra, para servir de segundo avaliador. Com R = n - 2, x está coberto sse alguma
 * palavra concorda com x em >= 2 coordenadas. Uma busca em profundidade fixa x coordenada a
 * coordenada e mantém, para cada palavra, quantas concordâncias já houve; assim que uma palavra
 * chega a 2, a subárvore inteira (q^(resto) pontos) está coberta e é podada. Só se desce nos ramos
 * em que todas as palavras têm <= 1 concordância, e cada folha alcançada é um ponto descoberto.
 * Imprime "uncovered=<n> points=<q^n>" e sai com 0 sse uncovered = 0.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int q, n, M;
static unsigned char W[4096][32];
static unsigned char agree[4096];
static unsigned long long uncovered;
static int verbose_left = 5;
static unsigned char x[32];

static int dig(int ch) {
    if (ch >= '0' && ch <= '9') return ch - '0';
    if (ch >= 'a' && ch <= 'z') return 10 + ch - 'a';
    if (ch >= 'A' && ch <= 'Z') return 36 + ch - 'A';
    return -1;
}

static void dfs(int p) {
    if (p == n) {
        uncovered++;
        if (verbose_left > 0) {
            verbose_left--;
            fprintf(stderr, "descoberto:");
            for (int i = 0; i < n; i++) fprintf(stderr, " %d", x[i]);
            fprintf(stderr, "\n");
        }
        return;
    }
    for (int a = 0; a < q; a++) {
        /* palavras com símbolo a na coordenada p ganham uma concordância */
        int hit = 0, k;
        for (k = 0; k < M; k++)
            if (W[k][p] == a && agree[k] == 1) { hit = 1; break; }
        if (hit) continue; /* subárvore toda coberta */
        for (k = 0; k < M; k++) if (W[k][p] == a) agree[k]++;
        x[p] = (unsigned char)a;
        dfs(p + 1);
        for (k = 0; k < M; k++) if (W[k][p] == a) agree[k]--;
    }
}

int main(int argc, char **argv) {
    if (argc != 4) { fprintf(stderr, "uso: cobre_n2 Q N ARQUIVO\n"); return 2; }
    q = atoi(argv[1]); n = atoi(argv[2]);
    if (q < 2 || q > 62 || n < 2 || n > 32) { fprintf(stderr, "parâmetros fora do alcance\n"); return 2; }
    FILE *f = fopen(argv[3], "r");
    if (!f) { perror("arquivo"); return 2; }
    char line[256];
    while (fgets(line, sizeof line, f)) {
        int len = (int)strcspn(line, "\r\n");
        if (len == 0) continue;
        if (len != n) { fprintf(stderr, "linha com %d dígitos, esperado %d\n", len, n); return 2; }
        if (M >= 4096) { fprintf(stderr, "palavras demais\n"); return 2; }
        for (int i = 0; i < n; i++) {
            int d = dig((unsigned char)line[i]);
            if (d < 0 || d >= q) { fprintf(stderr, "dígito inválido\n"); return 2; }
            W[M][i] = (unsigned char)d;
        }
        for (int k = 0; k < M; k++)
            if (memcmp(W[k], W[M], (size_t)n) == 0) { fprintf(stderr, "palavra repetida\n"); return 2; }
        M++;
    }
    fclose(f);
    dfs(0);
    double pts = 1; for (int i = 0; i < n; i++) pts *= q;
    printf("M=%d q=%d n=%d R=%d uncovered=%llu points=%.0f\n", M, q, n, n - 2, uncovered, pts);
    return uncovered == 0 ? 0 : 1;
}
