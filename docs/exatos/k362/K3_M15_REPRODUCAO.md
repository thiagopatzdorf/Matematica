# K₃(6,2), M = 15: reprodução independente (2026-10-05)

Frente de reprodução. Objetivo: chegar a "não existe C ⊂ Z₃⁶ com |C| = 15 e raio de cobertura 2"
(logo K₃(6,2) ≥ 16) por um caminho que não reaproveita o código de `tools/exatos/gaps2/` nem de
`tools/exatos/k362/` (os documentos foram lidos para a ideia da fibra; nenhum código foi importado nem
copiado). Código: `tools/exatos/k362_repro/`. Testes: `tests/test_k362_repro.py`.

Estados: OBSERVED (medido, sem garantia), COMPUTATIONALLY_VERIFIED (conferido por programa),
INDEPENDENTLY_REPRODUCED (concorda com uma implementação sem código comum), PROVED (prova escrita
aqui). **Nenhuma cota muda com este documento; o ledger não foi tocado.**

RESULTADO

## 1. A redução (PROVED)

Notação: `d` é a distância de Hamming, `B_r(y)` a bola de raio `r`, `V(m,r) = |B_r|` em Z₃^m
(`V(5,1) = 11`, `V(5,2) = 51`). `G = S₃ ≀ S₆` são as isometrias de Z₃⁶ (permutar coordenadas e, em
cada coordenada, os símbolos); elas preservam o raio de cobertura.

Suponha que existe `C` com `|C| ≤ 15` e raio 2. Acrescentando palavras, `|C| = 15` e as palavras são
distintas. Para a coordenada `j` e o símbolo `a`, a **fibra** é `F(j,a) = {c ∈ C : c_j = a}`; as três
fibras de uma coordenada particionam `C`, então a menor fibra tem `s ≤ 5` palavras.

**Passo 1 (normalização).** Escolha `(j,a)` com `|F(j,a)| = s` mínimo e aplique a isometria que leva
`j` à coordenada 0 e `a` ao símbolo 0. Seja `K ⊂ Z₃⁵` a projeção de `F(0,0)` nas coordenadas 1..5:
`s` pontos distintos (palavras distintas com a mesma coordenada 0). As isometrias que fixam a
coordenada 0 e o símbolo 0 agem em `K` como `S₃ ≀ S₅`; aplicando uma delas ao código inteiro (o que
não muda o tamanho de fibra nenhuma, só as permuta entre si), `K` vira o representante listado da sua
classe (seção 2). A fibra (0,0) continua mínima.

**Passo 2 (lema da fatia).** Seja `U = {y ∈ Z₃⁵ : d(y,K) > 2}`. O ponto `(0,y)`, `y ∈ U`, não é
coberto por `F(0,0)`; quem o cobre é `c = (b,y')` com `b ≠ 0`, que já difere na coordenada 0, logo
`d(y,y') ≤ 1`. Cada uma das `15 − s` palavras fora de `F(0,0)` cobre no máximo `V(5,1) = 11` pontos de
`{0} × U`, então `|U| ≤ 11(15 − s)`. Para `s = 0`, `|U| = 243 > 165`; para `s = 1`, `|U| = 192 > 154`.
Sobram `s ∈ {2,3,4,5}` e os `K` que passam no filtro.

**Passo 3 (relaxação projetada, "fatia").** Defina `w_y = 1` se existe `b ≠ 0` com `(b,y) ∈ C`
(`y ∈ Z₃⁵`). Então
* `Σ_y w_y ≤ 15 − s` (cada `y` marcado gasta ao menos uma palavra fora de `F(0,0)`);
* para todo `y ∈ U`, `Σ_{y' ∈ B₁(y)} w_{y'} ≥ 1` (pelo argumento do passo 2).

São 243 variáveis. Note que a relaxação não usa os blocos `x₀ = 1, 2` separadamente nem as fibras.

**Passo 4 (formulação completa, só quando a fatia é satisfazível).** Variáveis `z_c` para os 486
pontos com `c₀ ≠ 0`; a fatia `c₀ = 0` fica fixa em `{0} × K`. Restrições:
* cobertura: para todo `x ∈ Z₃⁶` a distância > 2 de `{0} × K`, `Σ_{c₀ ≠ 0, d(c,x) ≤ 2} z_c ≥ 1`;
* tamanho: `Σ z_c ≤ 15 − s`;
* fibras: para `j = 1..5` e `a ∈ Z₃`, `Σ_{c₀ ≠ 0, c_j = a} z_c ≥ s − #{k ∈ K : k_j = a}`, porque
  `|F(j,a)| ≥ s` (a fibra escolhida é mínima).

O código normalizado satisfaz as duas formulações da instância `(s, K)` do seu `K`. Logo, **se toda
instância `(s, K)` da lista for inviável (fatia ou completa), não existe código de 15 palavras.** ∎

Diferenças em relação à redução do PR #51 (`GAPS2_K362.md`): (i) não enumero os blocos
`t = (t₁, t₂)`, só uso `Σ ≤ 15 − s`; por isso a lista tem 11 496 instâncias e não 12 049
(12 049 = 5 + 108 + 936 + 11 000 conta cada `K` uma vez por `t`; aqui cada `K` aparece uma vez);
(ii) a primeira tentativa é a relaxação projetada de 243 variáveis, não o OPB de 729 variáveis;
(iii) as fibras só entram na formulação completa.

## 2. Enumeração das classes de K (COMPUTATIONALLY_VERIFIED)

`enumera.classes(q, m, s)`. Uma matriz `s × m` de símbolos é um conjunto ordenado de `s` pontos. A
menos de permutar os símbolos de cada coordenada, cada coluna é uma partição das `s` linhas em ≤ q
blocos (guardada como cadeia de crescimento restrito). A classe de `K` sob `S₃ ≀ S₅` é então o
multiconjunto de 5 partições a menos de `S_s` agindo nas linhas, com linhas distintas. O programa
percorre todos os multiconjuntos (C(45,5) = 1 221 759 para `s = 5`), descarta os de linhas repetidas,
e toma como forma canônica o menor multiconjunto ordenado sobre as `s!` reordenações das linhas
(vetorizado em numpy). É uma enumeração exaustiva com deduplicação, não uma busca: não há como
perder classe.

Conferências:
* **Burnside.** `enumera.burnside_orbitas` conta as órbitas de `s`-subconjuntos de Z_q^m pela fórmula
  de Cauchy–Frobenius, somando sobre tipos de ciclo de `π ∈ S_m` e classes de conjugação do produto de
  cada ciclo (uniforme em `S_q`). Nada em comum com a enumeração. Bate em todos os casos testados e em
  Z₃⁵: 1, 5, 35, 490, 11 075 classes para `s = 1..5`.
* **Filtro:** passam 0, 1, 27, 468, 11 000 classes para `s = 1..5`. Bate com as contagens de
  `GAPS2_K362.md`/`K3_M15_CANONICAL.md` (1, 27, 468, 11 000) — INDEPENDENTLY_REPRODUCED.
* **nauty com grafo próprio** (`canon.c`, libnauty em C): um vértice por ponto, um por
  (coordenada, símbolo), os 3 vértices de cada coordenada formando um **triângulo** (não um vértice
  de coordenada), e o ponto ligado a `(i, p_i)`. Os triângulos são as componentes do subgrafo da
  segunda cor, então todo automorfismo é um elemento de `S₃ ≀ S_m` mais a permutação induzida, e o
  `grpsize` é `|Stab|`. Teste: 200 conjuntos de 4 pontos de Z₃⁴ (com 50 pares forçados equivalentes):
  "mesma forma por colunas" ⇔ "mesmo certificado nauty" nos 19 900 pares; certificado e `|Stab|`
  idênticos em 600 imagens por isometrias aleatórias de Z₃⁵; `|Stab|` igual à força bruta sobre os
  1 296 elementos de `S₃ ≀ S₃`.

CLASSIFICACOES

## 3. Cadeia SAT/PB com prova

Duas cadeias, ambas sobre fórmulas escritas por `sat.py`:

| formato | solver | prova | verificador |
|---|---|---|---|
| OPB | RoundingSat (commit d4edbf7) | VeriPB (`--proof-log`) | VeriPB 3.0.2 (Rust, commit 3e00f69): exige `s VERIFIED UNSATISFIABLE` |
| CNF | CaDiCaL 3.0.1 | LRAT (`--lrat`) | `lrat-check` (drat-trim): exige `c VERIFIED` |

Na CNF a cardinalidade vai por um totalizador truncado escrito aqui (`sat.cnf`), e "≥ k" vira
"≤ len − k" nas negações. Fórmula e prova vivem num diretório temporário; só o registro fica (uma
linha JSON por instância: `s`, `K`, sha256 da fórmula, veredito, tempos de solver e verificador,
bytes da prova). Um modelo satisfazível da formulação completa é convertido em código e conferido
por um cálculo de raio que não passa pelo solver.

Calibração em valores conhecidos (mesmo programa, `rodar.py q n R M`):

CALIBRACAO

## 4. M = 15

TABELA

## 5. O que muda e o que não muda

ESTADOS

## 6. Como reproduzir

    sudo apt-get install libnauty-dev        # canon.c
    python3 tools/exatos/k362_repro/rodar.py 3 6 2 15 --formato opb --bin DIR --saida m15.jsonl --proc 2
    K362_REPRO_BIN=DIR python3 -m pytest -q -p no:cacheprovider tests/test_k362_repro.py

`DIR` contém `roundingsat` e `veripb` (ou `cadical` e `lrat-check` com `--formato cnf`). Sem eles,
os testes da cadeia pulam; os de enumeração e canonização rodam sempre (os de nauty precisam de
`libnauty-dev`, como `tests/test_motor_exatos.py`).
