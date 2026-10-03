# verify-cleanroom (4º verificador, Go, BFS multi-fonte)

CLI: `verify-cleanroom --q Q --n N --R R --M M <arquivo>` (os quatro parâmetros são
obrigatórios; o nome do arquivo nunca fornece parâmetro).
Build: `cd tools/verify-cleanroom && go build -o verify-cleanroom .` (só stdlib, Go >= 1.21).
Testes: `python3 -m unittest tests.test_verify_cleanroom` (pula se não houver `go`).

Exit: 0 cobre; 1 existe palavra descoberta (imprime `first_uncovered=`); 2 conteúdo contradiz
parâmetros (comprimento ≠ n, dígito ≥ q ou não-dígito, duplicata, #distintas ≠ M); 3 uso/erro
operacional (arquivo ilegível, parâmetro ausente/repetido/fora de 2≤q≤10, n≥1, R≥0, M≥1, q^n > 1,5e9).
Erros de conteúdo (2) têm precedência sobre cobertura (1). Uma linha de resumo no stdout.

## Algoritmo
BFS multi-fonte no grafo de Hamming H(n,q) (vértices = Z_q^n, aresta = uma posição diferente).
As M palavras entram na fila com distância 0; cada vértice expandido visita seus n(q−1)
vizinhos ainda não vistos com distância+1. Por indução nos níveis, o nível em que x é
descoberto é exatamente min_c d_H(x,c). Expande-se só até o nível R (vértices de nível R não
expandem). Um vértice nunca descoberto tem distância > R, logo está descoberto pelo código;
cobre ⇔ nº de vértices visitados = q^n. A palavra impressa é a de menor índice não visitada.
Índice: x = Σ s[k]·q^k. Detecção de duplicata: marca `dist==0` já existente.

## Complexidade
Tempo O(q^n · n · q) no pior caso (cada vértice expande n(q−1) vizinhos, cada um um acesso
aleatório); espaço 1 byte (distância) + 4 bytes (fila uint32) por ponto = 5·q^n bytes,
mais O(M·n) transiente nulo (as palavras viram marcas direto). Medido (4 vCPU):

| célula | pontos | tempo | RSS |
|---|---|---|---|
| q7 n9 R4 (1285 / 1351) | 40 353 607 | 5,8 s / 5,6 s | 194 MB |
| q5 n10 R4 M625 | 9 765 625 | 0,9 s | 48 MB |
| demais | ≤ 5,8 M | ≤ 0,8 s | ≤ 109 MB |

## Declaração de independência
Li: apenas `docs/code-format.md` (formato dos dados), a especificação matemática do pedido,
a listagem de `data/codes/`, `tests/` e `tools/` por `ls` (nomes de arquivo), o início de
`data/codes/q4_n10_R4_M192.txt` e o artefato `campaigns/covering-codes/artifacts/q2_n6_R1_M12.txt`.
Não li: `tools/verify/verify.c`, `tools/campaign/verify_cover_dilation.py`, `tools/verify-rust/**`
(exceto, depois de terminar código, README e testes, `run_all.sh` para obter o comando de execução
como caixa-preta na comparação final), `scripts/codes/**`, nada em `campaigns/` além do artefato
.txt, nenhum teste existente dos verificadores. Nenhuma violação. `docs/code-format.md` descreve
sumariamente o algoritmo do verificador C (bolas em bitset); o meu é outro (BFS por camadas
com fila) e foi escrito sem olhar o código dele.
