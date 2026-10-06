/* Configurações da fatia mínima por aumento canônico de McKay com rótulo canônico do nauty.
 *
 * Enumera um representante por órbita de conjuntos X de s pontos de Z_q^m sob o grupo de
 * isometrias de Hamming G = S_q wr S_m, entre os X com sobreposição
 *     ov(X) = |X|·V(m,R) − |∪_{x∈X} B_R(x)| ≤ orc,
 * que é o filtro de contagem da fatia (|U| ≤ cap ⇔ ov ≤ s·V − q^m + cap).
 * A prova (codificação em grafo e completude do aumento) está no docstring de nauty_fatia.py e
 * em docs/exatos/FATIA_NAUTY.md. Aqui só a mecânica.
 *
 * Grafo de X (k pontos): vértices 0..m−1 = coordenadas (cor 0), m + i·q + a = símbolo a da
 * coordenada i (cor 1), m + q·m + j = j-ésimo ponto de X (cor 2). Arestas: coordenada i —
 * símbolo (i,a); ponto x — símbolo (i, x_i) para todo i.
 *
 * Modos (stdout em texto simples, uma linha por item):
 *   conta  q m R s orc [W w split]   -> "nivel k nós" por nível; com W>1 só a parte w.
 *   lista  q m R s orc [W w split]   -> "X i1 i2 ... is" (índices na ordem de itertools.product)
 *   estima q m R s orc sondas semente -> estimador de Knuth (nós por nível e chamadas ao nauty)
 *   canon  q m                        -> lê "k i1..ik" por linha, imprime a chave canônica em hex
 *
 * Compilar: gcc -O3 -DWORDSIZE=64 -DMAXN=WORDSIZE nauty_fatia.c -lnautyL1 -lm -o nauty_fatia
 */
#include <nauty/nauty.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAXP 729
#define NWMAX 12

static int q, m, R, S, ORC, N, NW, V, NV0;
static int dig[MAXP][8];
static uint64_t ball[MAXP][NWMAX];
static long long chamadas = 0;

static int pop(const uint64_t *b) {
    int c = 0;
    for (int i = 0; i < NW; i++) c += __builtin_popcountll(b[i]);
    return c;
}

/* Rótulo canônico de X = pts[0..k-1] com o grafo do cabeçalho. Grava o grafo canônico em cg,
 * as órbitas de Aut(X) em orbits e a ordem canônica em lab. */
static void rotula(const int *pts, int k, graph *cg, int *lab, int *orbits, int *n_out) {
    graph g[MAXN];
    int ptn[MAXN];
    static DEFAULTOPTIONS_GRAPH(opt);
    statsblk st;
    int n = NV0 + k;
    opt.getcanon = TRUE;
    opt.defaultptn = FALSE;
    EMPTYGRAPH(g, 1, n);
    for (int i = 0; i < m; i++)
        for (int a = 0; a < q; a++) ADDONEEDGE(g, i, m + i * q + a, 1);
    for (int j = 0; j < k; j++)
        for (int i = 0; i < m; i++) ADDONEEDGE(g, NV0 + j, m + i * q + dig[pts[j]][i], 1);
    for (int v = 0; v < n; v++) { lab[v] = v; ptn[v] = 1; }
    ptn[m - 1] = 0;
    ptn[NV0 - 1] = 0;
    if (k > 0) ptn[n - 1] = 0;
    densenauty(g, lab, ptn, orbits, &opt, &st, 1, n, cg);
    chamadas++;
    *n_out = n;
}

typedef struct { int p, mo; graph cg[MAXN]; } filho_t;

/* Filhos aceitos do nó X = pts[0..k-1], com cob1 = pontos cobertos >= 1 vez, cob2 = >= 2 vezes
 * e mk = sobreposição marginal do último ponto acrescentado (0 na raiz).
 *
 * Deleção canônica m(Y): entre os pontos y de Y com maior sobreposição marginal
 * mo_Y(y) = |B(y) ∩ cob(Y − y)|, o de maior rótulo canônico. O filho X+p é aceito se p está na
 * mesma órbita de Aut(X+p) que m(X+p), e só uma vez por classe entre os filhos do mesmo pai.
 *
 * Consequência usada na poda: ao longo de um caminho da árvore, mo do ponto acrescentado nunca
 * diminui (p_{k+1} é máximo em X_{k+1} e mo_{X_{k+1}}(p_k) >= mo_{X_k}(p_k)). Como
 * ov(X_s) = ov(X_k) + Σ_{i>k} mo_{X_i}(p_i) e mo_{X_i}(p_i) >= δ(p_i) = |B(p_i) ∩ cob(X_k)|,
 *     ov(X_s) >= ov(X_k) + soma dos s−k menores max(mk, δ(p)), p fora de X_k.
 * Se isso passa de orc, nenhum descendente de X_k na árvore passa no filtro, e o nó morre. */
static int filhos(const int *pts, int k, const uint64_t *cob1, const uint64_t *cob2, int mk,
                  filho_t *out) {
    int nf = 0, x[64];
    char em[MAXP];
    memset(em, 0, N);
    for (int j = 0; j < k; j++) { x[j] = pts[j]; em[pts[j]] = 1; }
    int delta[MAXP], hist[NWMAX * 64 + 1];
    int ov = k * V - pop(cob1);
    memset(hist, 0, sizeof(int) * (V + 1));
    for (int p = 0; p < N; p++) {
        if (em[p]) continue;
        int d = 0;
        for (int i = 0; i < NW; i++) d += __builtin_popcountll(ball[p][i] & cob1[i]);
        delta[p] = d;
        hist[d > mk ? d : mk]++;
    }
    int falta = S - k;
    {
        long T = 0;
        int pegos = 0;
        for (int d = 0; d <= V && pegos < falta; d++)
            for (int c = 0; c < hist[d] && pegos < falta; c++) { T += d; pegos++; }
        if (pegos < falta) return 0;
        if (ov + T > ORC) return 0;
    }
    for (int p = 0; p < N; p++) {
        if (em[p]) continue;
        int d = delta[p];
        if (d < mk) continue;                         /* mo não pode diminuir no caminho */
        if (ov + (long)d * falta > ORC) continue;     /* os s−k pontos restantes têm mo >= d */
        uint64_t c2[NWMAX];
        for (int i = 0; i < NW; i++) c2[i] = cob2[i] | (cob1[i] & ball[p][i]);
        int mos[64], maxmo = d, viola = 0;
        for (int j = 0; j < k; j++) {
            int v = 0;
            for (int i = 0; i < NW; i++) v += __builtin_popcountll(ball[pts[j]][i] & c2[i]);
            mos[j] = v;
            if (v > maxmo) { viola = 1; break; }
        }
        if (viola) continue;                          /* p não tem mo máximo: não é m(X+p) */
        mos[k] = d;
        x[k] = p;
        graph cg[MAXN];
        int lab[MAXN], orbits[MAXN], n;
        rotula(x, k + 1, cg, lab, orbits, &n);
        int alvo = -1;
        for (int t = n - 1; t >= NV0; t--)
            if (mos[lab[t] - NV0] == maxmo) { alvo = lab[t]; break; }
        if (orbits[alvo] != orbits[n - 1]) continue;
        int rep = 0;
        for (int f = 0; f < nf && !rep; f++)
            if (memcmp(out[f].cg, cg, sizeof(graph) * n) == 0) rep = 1;
        if (rep) continue;
        out[nf].p = p;
        out[nf].mo = d;
        memcpy(out[nf].cg, cg, sizeof(graph) * n);
        nf++;
    }
    return nf;
}

static long long nos[65];
static int MODO_LISTA = 0, W = 1, WID = 0, SPLIT = 0;
static long long cont_split = 0;

static void dfs(int *pts, int k, const uint64_t *cob1, const uint64_t *cob2, int mk) {
    if (k == SPLIT && W > 1) {
        long long i = cont_split++;
        if (i % W != WID) return;
    }
    nos[k]++;
    if (k == S) {
        if (MODO_LISTA) {
            printf("X");
            for (int j = 0; j < k; j++) printf(" %d", pts[j]);
            printf("\n");
        }
        return;
    }
    filho_t *fs = malloc(sizeof(filho_t) * N);
    int nf = filhos(pts, k, cob1, cob2, mk, fs);
    for (int f = 0; f < nf; f++) {
        uint64_t a1[NWMAX], a2[NWMAX];
        int p = fs[f].p;
        for (int i = 0; i < NW; i++) {
            a2[i] = cob2[i] | (cob1[i] & ball[p][i]);
            a1[i] = cob1[i] | ball[p][i];
        }
        pts[k] = p;
        dfs(pts, k + 1, a1, a2, fs[f].mo);
    }
    free(fs);
}

static void prepara(void) {
    N = 1;
    for (int i = 0; i < m; i++) N *= q;
    NW = (N + 63) / 64;
    NV0 = m + q * m;
    for (int p = 0; p < N; p++) {
        int r = p;
        for (int i = m - 1; i >= 0; i--) { dig[p][i] = r % q; r /= q; }
    }
    for (int p = 0; p < N; p++) {
        memset(ball[p], 0, sizeof ball[p]);
        for (int u = 0; u < N; u++) {
            int d = 0;
            for (int i = 0; i < m; i++) d += dig[p][i] != dig[u][i];
            if (d <= R) ball[p][u / 64] |= 1ULL << (u % 64);
        }
    }
    V = pop(ball[0]);
    if (NV0 + S > MAXN || N > MAXP || m > 8) { fprintf(stderr, "grande demais\n"); exit(2); }
}

/* gerador pseudoaleatório reprodutível (splitmix64) */
static uint64_t rs;
static uint64_t rnd(void) {
    uint64_t z = (rs += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "uso: ver cabeçalho\n"); return 2; }
    const char *modo = argv[1];
    q = atoi(argv[2]);
    m = atoi(argv[3]);
    nauty_check(WORDSIZE, 1, MAXN, NAUTYVERSIONID);
    if (!strcmp(modo, "canon")) {
        R = 0; S = 0;
        prepara();
        int k, pts[64];
        while (scanf("%d", &k) == 1) {
            for (int j = 0; j < k; j++) if (scanf("%d", &pts[j]) != 1) return 3;
            graph cg[MAXN];
            int lab[MAXN], orbits[MAXN], n;
            rotula(pts, k, cg, lab, orbits, &n);
            for (int v = 0; v < n; v++) printf("%016llx", (unsigned long long)cg[v]);
            printf("\n");
        }
        return 0;
    }
    R = atoi(argv[4]); S = atoi(argv[5]); ORC = atoi(argv[6]);
    prepara();
    int pts[64];
    uint64_t z1[NWMAX] = {0}, z2[NWMAX] = {0};
    if (!strcmp(modo, "conta") || !strcmp(modo, "lista")) {
        MODO_LISTA = !strcmp(modo, "lista");
        if (argc >= 10) { W = atoi(argv[7]); WID = atoi(argv[8]); SPLIT = atoi(argv[9]); }
        dfs(pts, 0, z1, z2, 0);
        for (int k = 0; k <= S; k++) printf("nivel %d %lld\n", k, nos[k]);
        printf("chamadas %lld\n", chamadas);
        return 0;
    }
    if (!strcmp(modo, "estima")) {
        long sondas = atol(argv[7]);
        rs = strtoull(argv[8], 0, 10);
        double soma[65] = {0}, soma2[65] = {0}, cs = 0, cs2 = 0;
        filho_t *fs = malloc(sizeof(filho_t) * N);
        for (long t = 0; t < sondas; t++) {
            double prod = 1, custo = 0;
            int k = 0, mk = 0;
            uint64_t c[NWMAX] = {0}, c2[NWMAX] = {0};
            soma[0] += 1; soma2[0] += 1;
            while (k < S) {
                long long ch0 = chamadas;
                int nf = filhos(pts, k, c, c2, mk, fs);
                custo += prod * (double)(chamadas - ch0);
                if (nf == 0) break;
                prod *= nf;
                soma[k + 1] += prod; soma2[k + 1] += prod * prod;
                int f = (int)(rnd() % (uint64_t)nf);
                for (int i = 0; i < NW; i++) {
                    c2[i] |= c[i] & ball[fs[f].p][i];
                    c[i] |= ball[fs[f].p][i];
                }
                mk = fs[f].mo;
                pts[k++] = fs[f].p;
            }
            cs += custo; cs2 += custo * custo;
        }
        for (int k = 0; k <= S; k++) {
            double mu = soma[k] / sondas, var = soma2[k] / sondas - mu * mu;
            printf("nivel %d %.6e %.6e\n", k, mu, sqrt(var > 0 ? var / sondas : 0));
        }
        double mu = cs / sondas, var = cs2 / sondas - mu * mu;
        printf("chamadas_estimadas %.6e %.6e\n", mu, sqrt(var > 0 ? var / sondas : 0));
        printf("chamadas %lld\n", chamadas);
        return 0;
    }
    fprintf(stderr, "modo desconhecido\n");
    return 2;
}
