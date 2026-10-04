# Glossário

Cada termo em poucas linhas. Para o contexto de uso, veja [ARQUITETURA.md](ARQUITETURA.md).

**`K_q(n,R)`**: o menor número de palavras de um código `C ⊆ Z_q^n` (comprimento `n`, alfabeto de `q` símbolos) tal
que toda palavra do espaço está a distância de Hamming ≤ `R` de alguma palavra de `C`. É o "número de cobertura".
Cota superior: um código explícito. Cota inferior: argumento de que nenhum código menor cobre.

**Célula**: um trio `(q, n, R)`, escrito `K7(9,4)`. O ledger tem uma entrada por célula (1145, `q` de 2 a 21).
Célula **exata** é aquela em que cota inferior e superior publicadas coincidem; **aberta**, a que ainda tem folga.

**Distância de Hamming**: número de posições em que duas palavras diferem.

**Raio de cobertura**: o menor `R` com que um código cobre o espaço inteiro. `R` é o terceiro parâmetro da célula.

**Bola e `V`**: a bola de raio `R` em torno de uma palavra tem `V = Σ_{i=0..R} C(n,i)·(q-1)^i` pontos.

**Cota de esfera**: como cada palavra cobre no máximo `V` pontos, `K_q(n,R) ≥ ⌈q^n / V⌉`. Para `K_7(9,4)` dá 221. É a
cota inferior mais simples; está formalizada em `CoveringLean/A2_Sphere.lean`.

**Código linear `[n,k]_q`**: subespaço de dimensão `k` de `GF(q)^n` (para `q` primo), com `q^k` palavras.

**Coset (classe lateral)**: o conjunto `a + C0` de um código linear `C0` somado a um vetor `a`. Os cosets de `C0`
particionam o espaço. Quase todos os nossos códigos são a união de alguns cosets inteiros.

**Remendo**: as palavras soltas (ou retas) acrescentadas à união de cosets para cobrir o que a base deixou de fora.

**Síndrome**: com `H` a matriz de paridade de `C0`, a síndrome de `x` é `H·x`. Dois pontos têm a mesma síndrome
exatamente quando diferem por uma palavra de `C0`, ou seja, estão no mesmo coset. Conferir a cobertura nas síndromes
é muito mais barato que nos `q^n` pontos. **Síndrome órfã** é a que a base não cobre e o remendo precisa cobrir.

**Avaliador**: programa determinístico e barato que decide se um candidato satisfaz o problema. Para cobertura é o
verificador oficial em C (`tools/verify/verify.c`): palavras distintas, `|C| = M` e zero pontos descobertos. Um modelo
de linguagem pode gerar candidatos, mas nunca é avaliador.

**Candidato**: um código achado por busca ou construção, ainda sem certificado. Fica em `data/codes/`.

**Formato `covering-code/v1`**: descrição estruturada de um código (cosets, palavras soltas, proveniência, sha256
canônico). Especificação em [code-format.md](code-format.md).

**sha256 canônico**: o sha256 das palavras como texto, ordenadas por byte, unidas por LF. É o elo entre o `.txt`, o
JSON estruturado e a lista dentro do teorema Lean.

**Kernel do Lean**: o núcleo pequeno do Lean 4 que confere cada prova passo a passo. Teorema aceito pelo kernel não
depende de confiança no programa que achou o código. `decide +kernel` pede ao kernel que calcule uma proposição decidível.

**Certificado**: o módulo Lean que prova `∃ C, C.card = M ∧ Covers R C` para um código explícito. Há dois tipos aqui:
por **prefixos** (lib `CoveringHeavy`, muito custoso) e por **síndromes** (lib `CoveringSyn`, minutos).

**Axiomas padrão**: `propext`, `Classical.choice`, `Quot.sound`. Um teorema final só pode depender deles
(`#print axioms`); `sorry` e `native_decide` são proibidos.

**Mathlib**: a biblioteca matemática do Lean sobre a qual as definições (`hammingDist`, `Finset`, `ZMod`) são tomadas.

**Ledger**: `ledger/cells.json` e arquivos vizinhos: para cada célula, as cotas publicadas (com fonte) e o nosso
estado. É gerado por `ledger/build.py`; não se edita à mão. O estado é `ours_lean` > `ours_computational` > `published`.

**Proveniência**: o registro de como um código nosso foi gerado (`gerador`, `commit`, `seed`, `comando`, `data`,
`agente`). Campo desconhecido fica `null` com uma lacuna explicada; nunca se inventa.

**SAT e prova LRAT**: SAT é a satisfatibilidade booleana. Um solucionador que diz "insatisfazível" pode errar; a prova
LRAT é um registro que um verificador independente confere. É assim que se fecha uma cota inferior sem confiar na busca.

**Loop de recordes**: `scripts/loop/record_loop.py`, que gera, verifica, registra e prepara o certificado de uma célula.

**Infinito (MCP)**: servidor de ferramentas para colaboradores, com teto de crédito por pessoa em dólares aplicado
em código. Ver [infinito/README.md](../infinito/README.md).

**Hub**: este repositório visto como um lugar de proposta, busca e prova de problemas, e não só de uma nota sobre uma célula.
