# Cruzamento estrutural: openai/math × este repositório (2026-10-07)

Pergunta: dos 722 manuscritos (372 famílias) publicados pela OpenAI em `openai/math`, quais têm **estrutura**
matemática que sirva às nossas frentes (cotas de cobertura `K_q(n,R)`, certificados, e as frentes do dono: escada
`J_1..J_ℓ` em isomorfismo de grafos, reconstrução por decks, Hadamard, Schur, Euler, quociente de estado)?
Pergunta transversal do dono: *quanto de informação é necessário para distinguir ou reconstruir um objeto finito?*

O panorama geral dos resultados de IA em 2026 é de outro documento (`IA-2026-problemas-resolvidos.md`, PR da m2).
Aqui só o cruzamento. Nada foi publicado, nenhum número do ledger foi tocado. Gasto: **US$ 0,085** (Gemini, pelo
ledger do Infinito); embeddings em CPU, sem VM.

## Resposta curta

Três pistas reais, todas lidas na fonte:

1. **Escada J ← família 133 + família 243.** O artigo *Parity lifts* (Thm 1.2) é um **gerador**: de qualquer
   sistema de escolhas finito sem escolha compatível sai um par explícito de grafos simples não coloridos que são
   k-WL-equivalentes, com ordem ≤ `A·M_t` (`t = k+1` no refinamento conjunto); se existe escolha, o par se separa em
   duas rodadas. A família 243 dá adversários **acima** de CFI: estruturas de grade com sistema linear sobre `F_3`
   que nem CPT com contagem distingue (CPT já resolve CFI). Juntos formam uma biblioteca graduada de pares
   (CFI sobre `F_2` < parity lifts de dimensão k < grades sobre `F_3`) para medir em que degrau `J_ℓ` separa.
   O enunciado está no Lean (`ComparatorChallenges/ParityLifts.lean`), com **o mesmo Lean 4.34.1 e o mesmo Mathlib
   `d13f23b723`** que usamos.
2. **Certificados exatos com simetria ← família 266.** Para Hadamard complexas de ordem 6 e bases mutuamente não
   enviesadas, o certificado é uma identidade racional finita: eliminação modular + teorema chinês do resto +
   reconstrução racional **propõem** as regras, aritmética inteira/racional **confere**, e um verificador completo
   acompanha o artigo. É o molde que falta para a nossa cota inferior por LP/SDP com dual racional (F11) e para os
   certificados de Farkas (F07).
3. **Reconstrução por decks ← família 122.** A cota inferior de trace reconstruction (`n^{Ω(log log n)}` traços)
   vem de **pares explícitos** de palavras binárias cuja distância de variação total após deleções é
   superpolinomialmente pequena, construídos por amplificação em blocos aninhados. É a biblioteca de pares difíceis
   que a frente de decks de palavras precisa para testar "quanta informação reconstrói".

Para **K_7(9,4) e as outras células do ledger: nada forte.** Nenhuma família trata de código de cobertura em
espaço de Hamming finito. O mais perto (092, cobertura de corpos convexos por reticulado; 162, número de cobertura de
hipergrafos de Ryser) é assintótico e não dá número em `n = 9`. A triagem automática confirma: o topo de F01 é
ruído (superstring, distância de edição).

**Correção à leitura do dono:** há Hadamard no release. A família 179 prova a conjectura de Hadamard circulante
(só ordens 1 e 4; formalizada) e a 266 trata de Hadamard complexas de ordem 6. Euler, Schur, tabelas de Kéri e
reconstrução por decks de grafos de fato não aparecem.

## Fonte

| item | valor |
|---|---|
| repositório | [github.com/openai/math](https://github.com/openai/math), dono `openai` (organização), licença Apache-2.0, criado em 2026-10-06 |
| revisão usada | commit `adc7f1241b42e322a6451854ab7e4b4c146bf78a` ("Initial commit", 2026-10-06T21:58:50Z) |
| conferido | `README.md` diz 722 manuscritos em 372 famílias; o parser achou 372 famílias e 722 manuscritos, todas com disciplina |
| baixado | `CONTENTS.md` (sha256 `c492802b…`), `overview.tex` (`98533a7b…`), `lean/formalization.yaml`, docs de escopo do Lean e 33 PDFs (16 MB). O repo inteiro tem ~800 MB; não foi clonado |
| Lean deles | `lean/lean-toolchain` = `v4.34.1`; Mathlib `d13f23b723b8a846827a245b89c10fc7d3f11612` (igual ao nosso `lake-manifest.json`); 235 famílias com doc de formalização, 162 artigos no `formalization.yaml` |

Links abaixo usam a revisão fixa: `https://github.com/openai/math/blob/adc7f12…/<caminho>`.

## Método

1. **Frentes nossas** (`cruzamento-openai-math/frentes.json`): 21 descrições curtas, em inglês e por estrutura,
   tiradas dos docs deste repo (F01–F14, F21) ou da fala do dono (F15–F20, que não têm arquivo aqui; a busca por
   `Weisfeiler`, `deck`, `Hadamard`, `Schur` neste repo, no `fabrica-de-sites` e nos repos ativos do dono não achou
   nada além de menções de passagem).
2. **Vocabulário de estruturas** (`cruzamento-openai-math/vocabulario.json`): 20 etiquetas (códigos de cobertura,
   códigos lineares/síndromes, grupos e órbitas, isomorfismo/WL, reconstrução, informação, designs/geometria finita,
   cobertura em hipergrafos, Ramsey/aditiva, diofantino, SAT/ILP, certificados, formalização, LP/SDP, dureza, extremal,
   construção explícita, fatoração…).
3. **Classificação automática** (`tools/literatura/cruzamento_openai_math.py`): embeddings `BAAI/bge-base-en-v1.5`
   (fastembed, CPU) de 372 famílias + 722 manuscritos + 21 frentes + 20 etiquetas. Perfil de uma unidade = etiquetas com
   z > 1 (z por etiqueta sobre todas as unidades). Nota de um par = 0,5·cos(texto) + 0,5·cos(perfil de etiquetas); a
   segunda metade é o que casa textos sem palavra em comum. Ranking **por frente** (z dentro da coluna da frente), porque
   o ranking global é dominado por frentes de vocabulário genérico. Duas execuções deram pares idênticos.
4. **Segundo juiz**: 53 famílias pré-selecionadas (topo automático + leitura dos 372 resumos) julgadas pelo
   `gemini-3.8-flash` do Infinito, nota 0–3 com motivo (`cruzamento-openai-math/juiz-gemini.txt`). Hipótese, não prova:
   um dos vereditos dele (158 "usa CNF") estava errado e foi rebaixado depois de ler o artigo.
5. **Leitura**: os pares fortes foram lidos no PDF (introdução, enunciados, seção de certificados).

**Qualidade medida da triagem automática.** Dos 8 pares que sobreviveram à leitura como fortes ou médios, o ranking
por frente pôs 6 no top 10 da frente certa (133→F15 em 1º, 122→F16 1º, 179→F17 1º, 266→F17 2º, 189→F18 1º, 129→F20
10º) e perdeu 2 (243→F15 e 266→F11: transferência de técnica entre domínios, que o embedding não vê). O ranking global
(top 60) só tinha 3 dos 8. Conclusão: embedding serve para **não perder** a família óbvia de cada frente; a pista que
vale (técnica de um domínio aplicada a outro) saiu da leitura.

## Os 20 pares, ranqueados

Coluna "auto" = posição da família no ranking automático da frente (z); "G" = nota do juiz Gemini; "lido" = o que eu li.

| # | família × frente | auto | G | veredito | o que reaproveitar |
|---|---|---|---|---|---|
| 1 | [133](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Parity-lifts-and-bounded-treewidth-witnesses-for-Weisfeiler-Leman-equivalence-September-25-2026/paper.pdf) Weisfeiler–Leman × F15 escada J | 1º (z 2,43) | 3 | **forte**, PDF lido | gerador de pares k-WL-equivalentes a partir de sistema de escolhas (Thm 1.2); com SAT esparso insatisfatível vira família infinita; enunciado no Lean (`OAI.ParityWL`) |
| 2 | [243](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Choiceless-polynomial-time-with-counting-does-not-capture-polynomial-time-September-23-2026/paper.pdf) CPT não captura P × F15 | fora do top 10 | 2 | **forte**, intro lida | estruturas de grade com sistema linear sobre `F_3`: adversário acima de CFI; se algum `J_ℓ` usa posto/solubilidade sobre `F_2`, estas o derrotam |
| 3 | [266](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Exact-Fourier-certificates-for-complex-Hadamard-matrices-of-order-six-September-24-2026/Exact-Fourier-certificates-for-complex-Hadamard-matrices-of-order-six-September-24-2026.pdf) certificados de Hadamard de ordem 6 × F11 cota inferior SDP | fora | — | **forte (técnica)**, seções 6–7 lidas | eliminação modular + CRT + reconstrução racional para achar o dual; conferência só em inteiros/racionais; Gram com momentos invariantes; verificador em Python incluso |
| 4 | [179](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/The-circulant-Hadamard-conjecture-September-23-2026/paper.pdf) Hadamard circulante × F17 Hadamard | 1º (1,90) | 3 | **direto**, intro lida | teorema e prova Lean (`CirculantHadamard.lean`, `EvenBarker.lean`); fecha a pergunta circulante para a frente Hadamard |
| 5 | [266](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/The-maximum-number-of-mutually-unbiased-bases-in-dimension-six-September-24-2026/The-maximum-number-of-mutually-unbiased-bases-in-dimension-six-September-24-2026.pdf) MUB em dimensão 6 × F17 | 2º (1,83) | 3 | **direto**, lido | Hadamard complexas de ordem 6; exclusão por subdivisão intervalar com "Root certificates"; o Lean deles prova ≤ 5, o 3 é assistido por computador |
| 6 | [122](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/quantitative-lower-bounds-for-trace-reconstruction-September-24-2026/paper.pdf) trace reconstruction × F16 decks | 1º (2,18) | 2 | **médio-forte**, intro lida | pares explícitos de palavras quase indistinguíveis sob deleção, amplificados por blocos; decodificador uniforme quasipolinomial no artigo irmão |
| 7 | [133](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/The-complexity-of-identifying-a-graph-by-Weisfeiler-Leman-refinement-September-25-2026/paper.pdf) identificação por WL × F16/F20 | 3º em F16 | — | **médio (limite)**, resumo lido | decidir se o refinamento de dimensão dada identifica um grafo é EXPTIME-completo: certificar "J identifica G" em geral não é barato; mire em famílias, não no caso geral |
| 8 | [129](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-exponential-two-way-deterministic-state-lower-bound-for-one-way-liveness-September-25-2026/main.pdf) estados de autômatos de duas vias × F20 quociente de estado | 10º | 2 | **médio**, intro lida | cota inferior de estados por produtos de relações ("liveness"): técnica para provar quanto estado é necessário |
| 9 | [189](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Cycle-clique-Ramsey-numbers-September-25-2026/Cycle-clique-Ramsey-numbers-September-25-2026.pdf) Ramsey ciclo-clique × F18/F21 | 1º em F18 | 2 | **médio**, resumo lido | 3 099 casos finitos excluídos por duas implementações exatas de regras de inferência provadas, com traços de dedução: o mesmo padrão dos nossos dois verificadores LRAT |
| 10 | [187](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Snaky-in-21-Maker-moves-September-25-2026/article.pdf) Snaky × F21/F05 | sem perfil | 3 | **médio**, seções 3 e 6 lidas | certificado literal de "cartas" numeradas + verificador autônomo + avaliador independente; formato para análise de casos grande e legível |
| 11 | [140](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Memory-and-precision-in-noiseless-Gaussian-regression-September-27-2026/paper.pdf) memória × amostras × F20 | 2º (2,01) | — | **não lido** | trade-off memória/amostras em regressão: candidato à pergunta "quanto estado", só resumo |
| 12 | [162](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-Counterexample-to-Rysers-Covering-Conjecture-September-23-2026/paper.pdf) Ryser × F01/F02 | perfil "cobertura em hipergrafo" z 3,4, fora do top de F01 | 2 | **fraco para K_7(9,4)**, intro lida | plano finito com rótulos de reta trocados e arestas excepcionais sobe o número de cobertura; assintótico (q grande), sem número para nossas células |
| 13 | [092](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-single-lattice-covering-bound-of-order-n-log-n-September-23-2026/paper.pdf) cobertura por reticulado × F01 | 4º em F02 | 1 | **fraco**, intro lida | Rogers / Fejes Tóth cobrem com O(log n) classes laterais de um reticulado, como a nossa base; o artigo troca isso por um reticulado só (cisalhamento + correções binárias). Em `q=7, n=9` um código linear `[9,4]_7` tem 2401 > 1137: não serve |
| 14 | [118](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Additive-hardness-and-unbounded-configuration-gaps-in-bin-packing-September-24-2026/Additive-hardness-and-unbounded-configuration-gaps-in-bin-packing-September-24-2026.pdf) bin packing × F07/F11 | 1º em F09 | 1 | **fraco (aviso)**, resumo lido | o LP de configurações tem gap aditivo ilimitado: LP de cobertura pode perder arbitrariamente; nenhuma técnica nova para nós |
| 15 | [126](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Exponential-PSD-rank-of-positively-shifted-matching-matrices-October-5-2026/shifted-matching-psd.pdf) posto PSD de emparelhamentos × F11 | 1º em F11 | 1 | **fraco**, resumo lido | cota inferior de tamanho de lift SDP; teoria, sem certificado numérico aproveitável |
| 16 | [095](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/An-Exact-Semidefinite-Lift-of-a-Nonspectrahedral-Hyperbolicity-Cone-October-5-2026/Exact-Semidefinite-Lift-of-a-Nonspectrahedral-Hyperbolicity-Cone.pdf) lift SDP exato × F11 | fora | 2 | **fraco**, resumo lido | objeto SDP exato e explícito (lápis 100×100, 307 variáveis auxiliares): referência de formato, não de método |
| 17 | [172](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/A-classification-of-finite-Euclidean-Ramsey-configurations-September-23-2026/paper.pdf) Ramsey euclidiano × F18 Schur | 2º (1,81) | 1 | **fraco**, resumo lido | classificação teórica; nada de computação de números de Schur |
| 18 | [142](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Deterministic-Polynomial-Factorization-over-Prime-Fields-October-4-2026/Deterministic-Polynomial-Factorization-over-Prime-Fields.pdf) fatoração de polinômios × F14 | 1º (2,16) | — | **fraco**, resumo lido | fatoração determinística de polinômios sobre `F_p`; o GNFS usa isso como sub-rotina, mas não muda o custo dominante |
| 19 | [102](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/The-Unique-Games-Theorem-September-23-2026/paper.pdf) Unique Games × NP/compressão | 1º em F07 e F02 | — | **fraco para nós**, resumo lido | teorema de dureza; não dá ferramenta de compressão informacional executável |
| 20 | [168](https://github.com/openai/math/blob/adc7f1241b42e322a6451854ab7e4b4c146bf78a/preprints/Combinatorial-Invariance-of-Kazhdan-Lusztig-Polynomials-September-24-2026/paper.pdf) invariância combinatória × F16 | 2º em F08 | 1 | **fraco**, resumo lido | teorema positivo de "a estrutura determina o invariante" (intervalos isomorfos dão o mesmo polinômio); sem método transferível |

Falsos positivos por homonímia, para ninguém perder tempo: 229 ("reconstruction threshold" em árvores é transmissão
de um bit pela árvore, não deck) e 009 (reconstrução de corpos de funções). Euler (F19): o topo automático (182, 242)
é aritmético mas não é soma de potências iguais.

## As pistas em detalhe

### P1. Biblioteca de adversários para a escada J (133, 243)

* **O que o Thm 1.2 dá, concretamente.** Entrada: domínios finitos `D_1..D_t`, rótulos `L_ij` e mapas
  `λ: D_i → L_ij`. Saída: dois grafos `X_0`, `X_⋆` de mesma ordem ≤ `A·M_t`, com
  `M_t = t·2^{t−2} + 3·C(t−1,2) + 12·C(t,3)` e `A` o maior domínio. `X_0 ≡_k X_⋆` sse não há escolha compatível. Como
  instâncias: partes de uma fórmula 3-SAT insatisfatível, um domínio por grupo de cláusulas, rótulo = restrição às
  variáveis comuns (seção 5 do artigo).
* **Como usar na escada.** Para cada `k`, gerar pares com CSP insatisfatível (equivalentes até k-WL) e com CSP
  satisfatível (separados em 2 rodadas: controle positivo). O primeiro `ℓ` em que `J_ℓ` separa um par insatisfatível
  mede a profundidade. Ressalva lida no artigo: equivalência k-WL não implica não isomorfismo; o artigo não afirma que
  `X_0` e `X_⋆` são não isomorfos, então cada par precisa de um teste de isomorfismo (nauty) antes de entrar na
  biblioteca.
* **243** sobe a régua: as testemunhas "por carga" sobre `F_3` não são distinguidas por CPT com contagem, que já
  distingue CFI. Um invariante que use álgebra linear sobre `F_2` cai aqui.
* **No Lean**: `ComparatorChallenges/ParityLifts.lean` define `ChoiceSystem`, o template e as elevações; mesmo
  toolchain e Mathlib que os nossos, então dá para vendorizar o arquivo sem atrito de versão (o `lakefile` deles puxa
  ~20 dependências pesadas; não importe o pacote inteiro).

### P2. Certificado racional de cota inferior (266 → F11, F07)

O que o artigo faz e nós ainda não: o dual vem de ponto flutuante, mas não é usado como está. Eliminação modular em
vários primos, combinação por CRT e reconstrução racional **propõem** regras racionais; substituir e limpar
denominadores **confere** em inteiros; um primo que esconde uma equação só a deixa de fora, nunca aceita algo falso.
A simetria entra pelos momentos invariantes (Gram reduzido). Aplicação direta: o dual de Schrijver/Gijswijt–Polak
para `K_q(n,R)` sai do solver em float; este é o caminho para virar certificado inteiro conferível e depois Lean.
Também vale para os vetores de Farkas da fatia mínima (F07), que hoje já são inteiros mas sem método de
arredondamento garantido.

### P3. Pares difíceis para reconstrução (122 → F16; 133, 129 → F20)

* 122: os pares de palavras binárias com TV de um traço `o(n^{−A})` para todo A são explícitos (blocos periódicos com
  sinais complementares, amplificados em profundidade). Para decks de palavras (todas as subpalavras com uma deleção),
  são o caso de teste natural: se o deck distingue estes pares, distingue o pior caso conhecido do canal de deleção.
* 133 (identificação) dá o limite: "este procedimento identifica G entre todos os grafos" é EXPTIME-completo para WL
  de dimensão variável. Medir "quanta informação" vale por família, não em geral.
* 129: cotas exponenciais de número de estados via produtos de relações. É a técnica de cota inferior para "quanto
  estado precisa ser guardado" (C-FLUXO).

## Formalização e proveniência

* 235 das 372 famílias têm doc de escopo do Lean e 162 artigos estão no `lean/formalization.yaml`; o escopo formal
  costuma ser **mais fraco** que o artigo (266: o Lean prova ≤ 5 bases, o artigo afirma 3). Este é o padrão que já
  seguimos: estado do resultado separado do estado da prova.
* O padrão Comparator (enunciado confiável num arquivo pequeno, prova separada, checagem com eixos permitidos) está
  em `lean/ComparatorChallenges/`; a m2 já o recomendou para os nossos certificados.
* Formatos de certificado vistos: cartas numeradas com verificador e avaliador independentes (187); duas
  implementações de regras de inferência com traços (189); verificador racional completo (266).

## Reproduzir

    R=adc7f1241b42e322a6451854ab7e4b4c146bf78a
    curl -sSfLO https://raw.githubusercontent.com/openai/math/$R/CONTENTS.md
    curl -sSfLO https://raw.githubusercontent.com/openai/math/$R/overview.tex
    python3 -m pip install fastembed==0.7.3 numpy
    python3 tools/literatura/cruzamento_openai_math.py CONTENTS.md overview.tex \
        docs/literatura/cruzamento-openai-math/frentes.json \
        docs/literatura/cruzamento-openai-math/vocabulario.json saida.json BAAI/bge-base-en-v1.5
    python3 -m pytest -q -p no:cacheprovider tests/test_cruzamento_openai_math.py

A saída completa tem ~130 kB. O versionado (`cruzamento-openai-math/classificacao.json`, 13,6 kB) é uma projeção:
perfil de cada família com índice da etiqueta e z com uma casa, os rankings por frente (top 10) e os 60 primeiros
pares globais. Medido: ~12 min de CPU num núcleo.

## O que ficou de fora

* Não li os 722 resumos com o mesmo cuidado: li os 372 resumos de família inteiros e só abri o PDF dos pares acima.
* Não testei nenhuma das técnicas aqui; são pistas. Os pares de P1 não foram gerados nem passados pelo nauty.
* Não rodei o Lean deles. A compatibilidade de versão foi conferida pelo `lean-toolchain` e pelo `lake-manifest.json`.
* Embeddings com modelo pequeno em inglês; frentes F15–F20 descritas pela fala do dono, sem arquivo para conferir.
