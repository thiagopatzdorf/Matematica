# Validação independente de K_7(9,4) ≤ 1137

Data: 2026-10-02. Status: **VALIDATED**. Todos os gates do item 19 da campanha passaram (tabela abaixo).

O objetivo foi tentar **derrubar** o resultado, não defendê-lo. A pergunta foi uma só: existe mesmo
um conjunto explícito de 1137 palavras em (Z/7)^9 com raio de cobertura ≤ 4? Nenhum ataque achou falha.

## THEOREM

> Existe um código 7-ário `C ⊂ (Z/7)^9` com `|C| = 1137` e raio de cobertura 4. Logo, `K_7(9,4) ≤ 1137`.

- **Witness:** `artifacts/k7_9_4_1137/code_1137.txt`, sha256
  `df3e8d527bc393a9680fe4b2b39e7bde088ab6a02f2f94ee26019a5efc05a102`.
- **Prova formal:** `Syn.K7_9_4_le_1137_syn : ∃ C : Finset (Fin 9 → ZMod 7), C.card = 1137 ∧ CoveringA2.Covers 4 C`,
  em Lean 4.34.1 com Mathlib `d13f23b7`. Axiomas: `propext`, `Classical.choice` e `Quot.sound`.
- **Prova computacional:** três verificadores diferentes em método (A, B, C), do mesmo autor do verificador oficial (independentes de método, não de autoria) varrem os 40 353 607 pontos.
  Os três dão `uncovered = 0` e a mesma distribuição de distâncias.

## COMPUTATIONAL SEARCH RESULT (separado do teorema)

- **O que diz:** entre as 7737 classes monomiais de códigos `[9,3]_7`, o menor número de síndromes
  órfãs de uma base de 3 classes laterais é 6, e só uma classe chega a esse mínimo.
- **Condição:** vale se o programa de busca (`exactT2`) estiver correto.
- **Onde está:** `audit/k794-base-sweep/`.
- **O que não faz:** não entra na prova do teorema; nem o Lean nem os verificadores dependem dela.

## NOT PROVED

- Que 1137 seja ótimo, ou o valor exato de K_7(9,4).
- Qualquer cota inferior nova. A cota conhecida continua 264 (Haas–Halupczok–Schlage-Puchta).
- Que a base campeã seja a melhor fora da família "3 classes laterais de um `[9,3]_7`".
- Que o remendo de 108 palavras seja mínimo. A cota inferior desse remendo, com esta base, é 86.

## Gates (item 19)

| gate | resultado | evidência |
|---|---|---|
| witness congelado, formato e SHA reproduzíveis | PASS | `artifacts/k7_9_4_1137/SHA256SUMS`, `verification/validate_witness.py` |
| A: força bruta | PASS | `verification/outputs/verifier_A_bruteforce.txt` |
| B: união das bolas | PASS | `verification/outputs/verifier_B_balls.txt` |
| C: terceira implementação (BFS) | PASS | `verification/outputs/verifier_C_bfs.txt` |
| distribuições idênticas em A, B e C | PASS | tabela abaixo |
| Lean: build limpo | PASS (exit 0, 318 s) | `LEAN_REVIEW.md`, `verification/lean/build_summary.txt` |
| Lean: red team | PASS (0 crítico/alto/médio) | `LEAN_RED_TEAM.md` |
| palavras no Lean = witness | PASS (mesmo sha256) | `verification/lean/decode_synData.py` |
| redundância individual | PASS (nenhuma palavra sobra) | `verification/outputs/redundancy_check.txt` |
| mutações destrutivas | PASS (8/8 rejeitadas) | `verification/outputs/mutations.md` |
| revisão bibliográfica | PASS (nenhum resultado ≤ 1137) | `STATE_OF_ART.md` |

Os critérios de parada do item 18 foram todos checados, e nenhum disparou.

## Os três verificadores

Cada verificador tem parser próprio e uma noção própria de "coberto". Nenhum código é compartilhado.

| | A | B | C |
|---|---|---|---|
| método | `d(x,C)` = mínimo sobre as 1137 palavras, para cada x | marca a bola de raio r de cada palavra, com os vetores de erro gerados por `itertools` | BFS multifonte no grafo de Hamming H(9,7) |
| linguagem | C + OpenMP | Python + NumPy | Rust |
| runtime | 233 s (4 núcleos) | 126 s | 18 s |
| memória de pico | 10 MB | 1,6 GB | 197 MB |
| N_0 | 1 137 | 1 137 | 1 137 |
| N_1 | 61 225 | 61 225 | 61 225 |
| N_2 | 1 421 934 | 1 421 934 | 1 421 934 |
| N_3 | 15 340 089 | 15 340 089 | 15 340 089 |
| N_4 | 23 529 222 | 23 529 222 | 23 529 222 |
| total | 40 353 607 | 40 353 607 | 40 353 607 |
| uncovered | 0 | 0 | 0 |
| max_distance | 4 | 4 | 4 |

- **Pontos mais distantes:** 23 529 222, todos a distância 4. Os três de menor índice são `211100000`,
  `311100000` e `611100000`; os três verificadores dão os mesmos.
- **Contagem das bolas (B):** `ball_hits` = 1137 × 182 791 = 207 833 367, `duplicate_cover_hits` =
  167 479 760, e o máximo de palavras cobrindo um mesmo ponto é 16.

## Redundância individual

Para cada `c_i`, o teste é se `C − {c_i}` ainda cobre tudo. Dois métodos independentes:

1. **`redundancy_check.c`:** para cada ponto da bola `B(c_i, 4)`, procura outra palavra a distância ≤ 4.
2. **Verificador B:** `c_i` é redundante se todo ponto da sua bola tiver multiplicidade ≥ 2.

Os dois concordam: **nenhuma palavra é redundante**. Toda palavra cobre pelo menos 6 pontos que só
ela cobre; o mínimo está em `164224152`. No total, 383 492 pontos são cobertos por uma única palavra.

## Mutações

| mutação | resultado |
|---|---|
| tirar 1 palavra | deixa 423 pontos descobertos |
| tirar 5 palavras | deixa 1817 pontos descobertos |
| mudar 1 coordenada | deixa 6 pontos descobertos |
| trocar 1 palavra por uma aleatória | deixa 17 pontos descobertos |
| duplicata, palavra truncada, valor 7, valor negativo | recusadas pelo validador de formato e pelo parser do verificador C |

Detalhes em `verification/outputs/mutations.md`.

## O que o Lean certifica (resumo de LEAN_REVIEW.md e LEAN_RED_TEAM.md)

- **Definição de cobertura:** `Covers R C := ∀ x, ∃ c ∈ C, hammingDist x c ≤ R`, com o `hammingDist`
  do Mathlib. O alfabeto é `ZMod 7`, a dimensão `Fin 9`, o raio 4.
- **Cardinalidade:** exata. A lista é estritamente crescente, com valores < 7^9, e `card_codeOf` é
  provado por injetividade.
- **Palavras:** estão como literal em `SynData_K1137.lean`. Decodificadas, dão byte a byte o
  `code_1137.txt`.
- **Método:** a cobertura sai de um certificado por síndromes. `syn_cert` (`SynBridge.lean:339`) prova
  dentro do Lean que as checagens booleanas implicam `Covers`. Tudo fecha por `decide +kernel`.
- **Construções proibidas:** nenhuma (`native_decide`, `sorry`, `axiom`, `implemented_by`, `extern`,
  `unsafe`).
- **Recheck pelo kernel:** `leanchecker` deu exit 0 nos 19 módulos usados.
- **Ataques do red team:**
  - enunciados adulterados contra o mesmo certificado (raio 3, card 1136, `Fin 8`, `ZMod 6`): todos
    rejeitados;
  - certificados adulterados (palavra removida, órfão removido): rejeitados pelo kernel.
- **Achado de processo (baixo):** o CI do repositório só roda `lake build` do alvo padrão, então **não**
  recompila `Syn_K1137` a cada commit. A prova vale, mas a garantia contínua depende de build manual.
  Isso fica como recomendação de issue separada; não muda este resultado.

## A base campeã

**Descrição informal:** a base é um "triângulo de Hesse torcido". O resto desta seção é a descrição
exata.

- **Código:** `C0 = ker H`, com `H = [I_6 | A]` e `A = 666 065 652 643 621 615`.
  - É um `[9,3,6]_7` quase-MDS (NMDS): um `[9,3,7]_7` não existe.
  - Distribuição de pesos: A0=1, A6=18, A7=162, A8=54, A9=108.
- **Witness:** as classes laterais de síndrome 0, 4191 e 7708 (3 × 343 = 1029 palavras), mais 108
  palavras de remendo com 15 síndromes distintas. Conferido por `verification/structure_check.py`.
- **Configuração geométrica:** as 9 colunas de G, vistas em PG(2,7), ficam 3 em cada lado de um
  triângulo, sem os vértices. As 3 trissecantes não são concorrentes.
  - Forma normal: `(1,ζ,0)`, `(0,1,3ζ)`, `(1,0,3ζ)`, com ζ ∈ {1,2,4}.
  - Estabilizador em PGL(3,7): 54.
  - Grupo monomial: 324, transitivo nas 9 coordenadas.
- **Residual:**
  - 6 síndromes órfãs, numa única órbita;
  - 2058 pontos órfãos; uma bola cobre no máximo 24 deles;
  - cota inferior do remendo: 86 (LP 85,75);
  - remendo usado: 108; gap: 22.
- **Fonte:** `docs/audit/champion_and_residual.md`, na branch `feat/kit-de-busca`.

## Respostas A–J

- **A. O código tem exatamente 1137 palavras?** Sim. São 1137 linhas distintas e válidas. Os três
  verificadores e o Lean (`C.card = 1137`, igualdade exata) concordam.
- **B. As 40 353 607 palavras estão a distância ≤ 4?** Sim: `uncovered = 0` e `max_distance = 4`.
- **C. Os três verificadores concordam?** Sim, em todas as contagens N_0..N_4, nos totais e nos
  exemplos de pontos mais distantes.
- **D. Distribuição de distâncias:** N_0 = 1137, N_1 = 61 225, N_2 = 1 421 934, N_3 = 15 340 089,
  N_4 = 23 529 222 (soma 7^9).
- **E. O Lean recompila do zero?** Sim. `lake clean CoveringLean` e depois
  `lake build CoveringLean.Syn_K1137` deram exit 0. `lake clean` sem argumento apaga também o Mathlib,
  e aí o certo é baixar de novo com `lake exe cache get`.
- **F. Quais axiomas?** `propext`, `Classical.choice` e `Quot.sound`. Não há `native_decide` nem
  `sorry`.
- **G. Alguma palavra é individualmente redundante?** Não, por dois métodos. Toda palavra cobre ≥ 6
  pontos exclusivos.
- **H. Menor upper bound anterior?** 1475 (Marosi, arXiv:2608.19872, v2 de 2026-08-23 e v3 de
  2026-09-02). A v1 trazia 1743, e as tabelas de Kéri, 1843.
- **I. Existe resultado anterior ≤ 1137?** Não nas fontes revisadas. Lacunas: Google Scholar e bases
  pagas não foram consultados (ver `STATE_OF_ART.md`).
- **J. Que afirmação pública é defensável?**
  > "We construct a 7-ary covering code of length 9, covering radius 4, and cardinality 1137,
  > establishing K_7(9,4) ≤ 1137. This improves the smallest upper bound we found in the reviewed
  > literature, K_7(9,4) ≤ 1475 (Marosi, arXiv:2608.19872). The construction is verified by three
  > independent programs and by a Lean 4 proof checked by the kernel."

  Não é defensável dizer "optimal", "best possible", "solves", "exact value" nem "world record".

## Reprodução

Os passos estão em `REPRODUCE_1137.md`. `verification/run_all.sh` refaz tudo menos o Lean em cerca de
12 minutos. Os números da rodada estão em `K7_9_4_1137_CERTIFICATE.json`.
