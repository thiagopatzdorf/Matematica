/* Forma canônica de conjuntos de pontos de Z_q^m sob S_q wr S_m, via libnauty.
 * Grafo: um vértice por ponto (cor 0) e um por par (coordenada, símbolo) (cor 1);
 * os q vértices de uma mesma coordenada formam um clique K_q, e o ponto p liga-se a
 * (i, p_i). Como os cliques são as componentes do subgrafo da cor 1, todo automorfismo
 * leva coordenada em coordenada (permutando símbolos dentro dela): é um elemento de
 * S_q wr S_m mais a permutação induzida nos pontos. Pontos distintos têm vizinhanças
 * distintas, logo Aut(grafo) = Stab(conjunto) e grpsize = |Stab|.
 * Entrada (stdin), uma linha por conjunto:  q m s p_1 ... p_s   (p em base q, coord 0 = dígito mais alto)
 * Saída: <certificado hex> <|Stab|> */
#include <stdio.h>
#include <math.h>
#include <nauty/nauty.h>

int main(void) {
    int q, m, s;
    while (scanf("%d %d %d", &q, &m, &s) == 3) {
        int n = s + m * q, pts[64];
        for (int i = 0; i < s; i++) if (scanf("%d", &pts[i]) != 1) return 2;
        if (n > WORDSIZE) { fprintf(stderr, "grafo grande demais\n"); return 3; }
        graph g[WORDSIZE], cg[WORDSIZE];
        int lab[WORDSIZE], ptn[WORDSIZE], orbits[WORDSIZE];
        static DEFAULTOPTIONS_GRAPH(opt);
        statsblk st;
        opt.getcanon = TRUE; opt.defaultptn = FALSE;
        EMPTYGRAPH(g, 1, n);
        for (int i = 0; i < m; i++)               /* clique por coordenada */
            for (int a = 0; a < q; a++)
                for (int b = a + 1; b < q; b++)
                    ADDONEEDGE(g, s + i * q + a, s + i * q + b, 1);
        for (int k = 0; k < s; k++) {
            int x = pts[k];
            for (int i = m - 1; i >= 0; i--) { ADDONEEDGE(g, k, s + i * q + x % q, 1); x /= q; }
        }
        for (int v = 0; v < n; v++) { lab[v] = v; ptn[v] = 1; }
        ptn[s - 1] = 0; ptn[n - 1] = 0;           /* duas cores: pontos | (coord, símbolo) */
        densenauty(g, lab, ptn, orbits, &opt, &st, 1, n, cg);
        for (int v = 0; v < n; v++) printf("%016lx", (unsigned long)cg[v]);
        printf(" %.0f\n", st.grpsize1 * pow(10.0, st.grpsize2));
        fflush(stdout);
    }
    return 0;
}
