# tools/exatos/k361 — K_3(6,1) (football pool) por sequências + SAT com prova LRAT

Viabilidade medida em `docs/exatos/K361_VIABILIDADE.md`. Aqui ficam o método e o argumento.

| arquivo | o que faz |
|---|---|
| `sistema.c` | enumera as soluções do sistema de cobertura (sequências `y`), um representante por órbita do grupo de ordem 72 |
| `ysip.py` | a CNF do subproblema de cada sequência (y-SIP), a quebra de simetria lex-leader e a reconstrução da atribuição a partir de um código (para os testes) |
| `amostra.py` | sorteia sequências, resolve com CaDiCaL (`--lrat`, conferido pelo `lrat-check`), kissat ou RoundingSat (prova VeriPB), grava JSONL |
| `vm.sh` | o mesmo numa VM de lote (`lote-gcp.py`) |
| `resumo.py` | mediana/p90/máx por amostra, extrapolação com bootstrap e pela escada de M (`escada`) |
| `medicoes/` | os JSONL medidos na VM em 2026-10-04 (RoundingSat M = 59, 60, 62, 72; CaDiCaL M = 59, 66) |

Testes: `tests/test_k361.py` (~10 s, sem solver externo).

## Decomposição (Östergård–Blass 2001; Linderoth–Margot–Thain 2009)

Seja C ⊂ Z_3^6 de raio 1 com |C| = M. Para o prefixo (j,k) das duas primeiras coordenadas, seja
`y[j][k]` o número de palavras com esse prefixo. O bloco W_jk tem 81 palavras; uma palavra do
próprio bloco cobre 9 delas, uma palavra de um bloco "vizinho de torre" (mesma linha ou mesma
coluna) cobre exatamente 1, as outras nenhuma. Logo

    9 y[j][k] + Σ_{vizinhos} y ≥ 81   para os 9 blocos,   Σ y = M.

Permutar os símbolos das coordenadas 0 e 1 e trocá-las entre si age sobre `y` como o grupo de
ordem 72 (linhas, colunas, transposta). `sistema` devolve o menor lexicográfico de cada órbita.

**Cota de fibra elementar.** Uma fibra (coordenada i, símbolo a) com f palavras: cada palavra
dela cobre 11 pontos da fatia `x_i = a` (243 pontos) e cada palavra fora dela cobre 1, então
`11 f + (M − f) ≥ 243`, f ≥ ⌈(243 − M)/10⌉ = 18 para M ≤ 72. Por isso a enumeração usa
linhas e colunas ≥ 18 (`sistema 6 72 18 18`), o que não muda a contagem.

**Cota do sufixo sem computação (modo `auto`).** Escolha a coordenada 0 como uma que contém a
menor fibra do código e a coordenada 1 como a de menor fibra entre as cinco restantes. Então toda
fibra das coordenadas 2..5 tem pelo menos `m1 = max(menor linha, menor coluna)` palavras (o
grupo de ordem 72 só permuta e transpõe linhas e colunas, então isso vale no representante). A
CNF ganha `Σ_{w_i = a} x_w ≥ m1` para i = 2..5. LMT usaram, em vez disso, `y_j ≥ 20` (depois
22) provado por computação própria e sem certificado; o modo `igual` reproduz isso para
comparação.

**Completude.** Se a CNF de todo representante é insatisfatível, não existe código com M
palavras. Como um código menor se completa até M palavras, ∄72 dá `K_3(6,1) ≥ 73 = ub`.

## A CNF de uma sequência

- `x_w` para as 729 palavras; uma cláusula de cobertura por ponto (13 literais);
- contagem exata por bloco e "pelo menos m1" por fibra do sufixo, com contador sequencial com
  equivalências (todas as auxiliares têm semântica fixa, o que permite reconstruir a atribuição
  de um código e conferir cláusula por cláusula);
- lex-leader `x ≤_lex x∘π` para: transposições de coordenadas vizinhas do sufixo, transposições
  de símbolos em cada coordenada do sufixo e o estabilizador de `y` no grupo de ordem 72. Isso é
  sólido para qualquer conjunto de automorfismos (o menor elemento lexicográfico da órbita
  satisfaz todas), e os testes conferem que cada π preserva cobertura, blocos e `y`.

Os testes conferem, com códigos conhecidos embaralhados, que a CNF sem quebra de simetria aceita
o código; que a cobertura está codificada com exatamente uma cláusula falsa por ponto descoberto;
que o menor elemento da órbita satisfaz o lex-leader e outros não; e que a cota `auto` vale.
