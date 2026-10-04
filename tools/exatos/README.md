# tools/exatos — triagem de valores exatos de K_q(n,R)

Ferramentas da triagem de 2026-10-04 (`docs/exatos/TRIAGEM_2026-10-04.md`). Nenhuma delas
emite certificado: o que sai daqui é evidência computacional ou estimativa. Código achado vai
para `tools/verify/verify` antes de qualquer afirmação; inexistência só vale com prova
independente (Lean/LRAT), nunca com um `INFEASIBLE` ou `NAO_EXISTE` destes scripts.

| arquivo | o que faz | comando |
|---|---|---|
| `folgas.py` | lista células abertas com folga (melhor ub − melhor lb) ≤ N, usando o máximo das cotas inferiores de todas as fontes do ledger e `best.ub` | `python3 tools/exatos/folgas.py --max 3 [--json]` |
| `particao_q42.py` | constrói, para cada q, o código de K_q(4,2) por partição do alfabeto em 3 blocos + arranjos de cobertura CA(N;2,4,v), confere a cobertura no espaço inteiro e compara com o ledger | `python3 tools/exatos/particao_q42.py [--gravar DIR]` (~5 s) |
| `sa_cover.c` | busca local por código com M palavras (`MODO=1` recozimento, `MODO=2` adiciona-e-remove com tabu); `INIT=arquivo` semeia com um código existente | `gcc -O2 -o sa tools/exatos/sa_cover.c -lm && MODO=1 ./sa Q N R M SEG SEMENTE [SAIDA]` |
| `dfs_cover.c` | busca exaustiva (esqueleto do `chkN`: ponto descoberto mais restrito, proibição dos irmãos, cota l·ganho_máx) com palavra 0 fixada e órbitas na raiz; `ESTIMAR=P` estima o tamanho da árvore pelo estimador de Knuth com P sondas | `gcc -O3 -march=native -o dfs tools/exatos/dfs_cover.c && ESTIMAR=2000 ./dfs Q N R M` |
| `cpsat_cover.py` | modelo CP-SAT genérico (one-hot, z[x][c]) com quebra de simetria sã (palavra 0, double lex); `--fibra F` impõe ≥ F palavras por (coordenada, símbolo) | `python3 tools/exatos/cpsat_cover.py --q 2 --n 10 --R 3 --M 11 --tempo 600` |
| `k742/` | **K_q(4,2) por perfis de fibras + SAT com prova LRAT** (método do Florath): fechou `K_7(4,2) = 19`; ver `k742/README.md` e `docs/exatos/FASE1_B_K742.md` | `python3 tools/exatos/k742/rodar.py --q 7 --M 18 --dir saida --prova` |
| `proj_q42.py` | modelo CP-SAT por projeções de pares para K_q(4,2) (x coberto sse algum par (x_i,x_j) está na projeção P_ij) | `python3 tools/exatos/proj_q42.py --q 7 --M 18 --fibra 2` |

Calibração do estimador de Knuth (`dfs_cover`, contagem exata ao lado):
K_3(5,2), M=7: 1,457e6 estimados × 1 445 669 reais; K_3(6,3), M=5: 4,125e5 × 411 177;
K_2(6,1), M=11: 9,05e4 × 90 188.
