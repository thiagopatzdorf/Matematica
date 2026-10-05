# K₃(6,2), M = 15: reprodução independente (2026-10-05)

Frente de reprodução. Objetivo: chegar a "não existe C ⊂ Z₃⁶ com |C| = 15 e raio de cobertura 2"
(logo K₃(6,2) ≥ 16) por um caminho que não reaproveita o código de `tools/exatos/gaps2/` nem de
`tools/exatos/k362/` (os documentos foram lidos para a ideia da fibra; nenhum código foi importado nem
copiado). Código: `tools/exatos/k362_repro/`. Testes: `tests/test_k362_repro.py`.

Estados: OBSERVED (medido, sem garantia), COMPUTATIONALLY_VERIFIED (conferido por programa),
INDEPENDENTLY_REPRODUCED (concorda com uma implementação sem código comum), PROVED (prova escrita
aqui). **Nenhuma cota muda com este documento; o ledger não foi tocado.**

## Resultado

* **M = 15: as 11 496 instâncias são inviáveis, cada uma com prova VeriPB conferida** (cadeia OPB);
  11 171 delas também com prova LRAT conferida (cadeia CNF, outro sistema de prova). Logo não
  existe código de 15 palavras e **K₃(6,2) ≥ 16** — INDEPENDENTLY_REPRODUCED em relação ao PR #57.
* **M = 16 (segunda via do PR #60): 11 582 de 11 592 instâncias refutadas com prova; 10 em aberto**
  (prova acima do teto de 3 GB). Esta cadeia **não** fecha K₃(6,2) ≥ 17.
* Nenhum código de 15 ou 16 palavras apareceu (nenhuma formulação completa satisfazível).
* Custo: uma VM spot t2d-standard-8 por ~4 h 25 min (≈ US$ 0,80 a US$ 0,177/h), destruída no fim.
  Registros compactos (sem provas) em `tools/exatos/k362_repro/registros/` (1,7 MB).


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

`repro_enumera.classes(q, m, s)`. Uma matriz `s × m` de símbolos é um conjunto ordenado de `s` pontos. A
menos de permutar os símbolos de cada coordenada, cada coluna é uma partição das `s` linhas em ≤ q
blocos (guardada como cadeia de crescimento restrito). A classe de `K` sob `S₃ ≀ S₅` é então o
multiconjunto de 5 partições a menos de `S_s` agindo nas linhas, com linhas distintas. O programa
percorre todos os multiconjuntos (C(45,5) = 1 221 759 para `s = 5`), descarta os de linhas repetidas,
e toma como forma canônica o menor multiconjunto ordenado sobre as `s!` reordenações das linhas
(vetorizado em numpy). É uma enumeração exaustiva com deduplicação, não uma busca: não há como
perder classe.

Conferências:
* **Burnside.** `repro_enumera.burnside_orbitas` conta as órbitas de `s`-subconjuntos de Z_q^m pela fórmula
  de Cauchy–Frobenius, somando sobre tipos de ciclo de `π ∈ S_m` e classes de conjugação do produto de
  cada ciclo (uniforme em `S_q`). Nada em comum com a enumeração. Bate em todos os casos testados e em
  Z₃⁵: 1, 5, 35, 490, 11 075 classes para `s = 1..5`.
* **Filtro:** passam 0, 1, 27, 468, 11 000 classes para `s = 1..5`. Bate com as contagens de
  `GAPS2_K362.md`/`K3_M15_CANONICAL.md` (1, 27, 468, 11 000) — INDEPENDENTLY_REPRODUCED.
* **nauty com grafo próprio** (`canon.c` + `repro_canon.py`, libnauty em C): um vértice por ponto, um por
  (coordenada, símbolo), os 3 vértices de cada coordenada formando um **triângulo** (não um vértice
  de coordenada), e o ponto ligado a `(i, p_i)`. Os triângulos são as componentes do subgrafo da
  segunda cor, então todo automorfismo é um elemento de `S₃ ≀ S_m` mais a permutação induzida, e o
  `grpsize` é `|Stab|`. Teste: 200 conjuntos de 4 pontos de Z₃⁴ (com 50 pares forçados equivalentes):
  "mesma forma por colunas" ⇔ "mesmo certificado nauty" nos 19 900 pares; certificado e `|Stab|`
  idênticos em 600 imagens por isometrias aleatórias de Z₃⁵; `|Stab|` igual à força bruta sobre os
  1 296 elementos de `S₃ ≀ S₃`.

**Classificações conhecidas** (testam o canonizador sobre códigos inteiros, não só sobre `K`):

| célula | publicado | aqui | método | tempo |
|---|---|---|---|---|
| K₃(4,1) = 9 | 1 classe (Hamming) | 1 | os dois abaixo | < 1 s |
| K₃(5,2) = 8 | 1 classe | 1 | `classificar_por_reducao`: todos os modelos da formulação completa de cada instância de M = 8 (CaDiCaL do python-sat com bloqueio), deduplicados pelo nauty | 100 s |
| K₃(6,3) = 6 | 28 classes | 28 | `classificar`: geração nível a nível ramificando no menor ponto descoberto, poda por contagem, dedup pelo nauty | 168 s |

O segundo método é também um teste de ponta a ponta da redução: se a lista de `K`, a normalização ou
as restrições (inclusive as fibras) perdessem algum código, a contagem de K₃(5,2) = 8 cairia para 0.
Os dois lentos ficam atrás de `K362_REPRO_LENTO=1` nos testes; rodados aqui, passam.


## 3. Cadeia SAT/PB com prova

Duas cadeias, ambas sobre fórmulas escritas por `repro_sat.py`:

| formato | solver | prova | verificador |
|---|---|---|---|
| OPB | RoundingSat (commit d4edbf7) | VeriPB (`--proof-log`) | VeriPB 3.0.2 (Rust, commit 3e00f69): exige `s VERIFIED UNSATISFIABLE` |
| CNF | CaDiCaL 3.0.1 | LRAT (`--lrat`) | `lrat-check` (drat-trim): exige `c VERIFIED` |

Na CNF a cardinalidade vai por um totalizador truncado escrito aqui (`repro_sat.cnf`), e "≥ k" vira
"≤ len − k" nas negações. Fórmula e prova vivem num diretório temporário; só o registro fica (uma
linha JSON por instância: `s`, `K`, sha256 da fórmula, veredito, tempos de solver e verificador,
bytes da prova). Um modelo satisfazível da formulação completa é convertido em código e conferido
por um cálculo de raio que não passa pelo solver.

Calibração em valores conhecidos (mesmo programa, `repro_rodar.py q n R M`):

| alvo | M | instâncias | OPB (RoundingSat + VeriPB) | CNF (CaDiCaL + LRAT) |
|---|---|---|---|---|
| K₃(4,1) ≥ 9 | 8 | 0 (o lema já exclui `s ≤ 2`) | — | — |
| K₃(4,1) = 9 | 9 | 1 | SAT, código de 9 palavras conferido | SAT, conferido |
| K₃(5,2) ≥ 8 | 7 | 5 | 5 UNSAT, 5 VERIFIED | 5 UNSAT, 5 VERIFIED |
| K₃(5,2) = 8 | 8 | 5 | 3 UNSAT VERIFIED + 2 SAT, códigos conferidos | idem |
| K₃(6,2) ≥ 15 | 14 | 423 | 423 UNSAT, 423 VERIFIED | não rodado (custo; ver §4) |

Um teste (`test_restricao_que_viola_codigo_verdadeiro_tornaria_a_reducao_falsa`) leva o código de
Hamming e o código de 17 palavras de K₃(6,2) (dado de `tests/test_gaps2.py`), sob 10 isometrias
aleatórias cada, à sua fibra mínima e confere que o código satisfaz **todas** as restrições das duas
formulações da sua instância, e que seu `K` está na lista de classes. Uma restrição inválida
apareceria aqui.


## 4. M = 15

Lista: 11 496 instâncias (1 + 27 + 468 + 11 000 para `s = 2..5`). A mesma lista foi gerada no
container e na VM, de forma independente: o sha256 da lista ordenada de pares
`(K, sha256 da fórmula da fatia)` é `6a8376b490059b129817b76416bf39343a260e57e0517e5a5812b8b8da29ecb8`
nas duas máquinas (enumeração e codificação determinísticas).

**Cadeia OPB (RoundingSat + VeriPB), VM t2d-standard-8:**

| s | instâncias | fatia UNSAT | fatia SAT → completa UNSAT | VeriPB |
|---|---|---|---|---|
| 2 | 1 | 1 | 0 | 1 / 1 |
| 3 | 27 | 26 | 1 | 27 / 27 |
| 4 | 468 | 463 | 5 | 468 / 468 |
| 5 | 11 000 | 10 681 | 319 | 11 000 / 11 000 |
| **total** | **11 496** | **11 171** | **325** | **11 496 / 11 496 VERIFIED** |

CPU total (solver + verificador): 164 s. Maior prova: 35,6 MB. Pior formulação completa: 2,3 s.
`|U|` das 325 que precisaram da completa vai de 42 a 120: não são as de `|U|` extremo.

Réplica parcial no container (outro binário do RoundingSat, máquina compartilhada com carga 10 em
4 núcleos): 6 828 instâncias processadas antes de eu parar, todas UNSAT VERIFIED exceto 62 da
formulação completa que estouraram 60 s ali (na VM, as mesmas fecham em menos de 3 s) — OBSERVED,
diferença de binário e de carga, não de fórmula (sha256 idênticos).

**Cadeia CNF (CaDiCaL + LRAT), VM:** a relaxação da fatia é refutada com prova LRAT aceita pelo
`lrat-check` em **11 171 de 11 496** instâncias — exatamente as mesmas 11 171 em que o RoundingSat
refutou a fatia; nas outras 325 o CaDiCaL também acha a fatia satisfazível (os dois solvers concordam
instância a instância). Na formulação completa dessas 325, o CaDiCaL não fecha em 30 s (num teste
com 900 s, 7 de 8 seguiam abertas aos 8 min e as provas encheram 20 GB de disco); essas 325 ficam
cobertas só pela cadeia OPB. CPU total da CNF: 114 415 s (~32 h de núcleo, 4 h de parede em 8
núcleos); maior prova LRAT: 396 MB.

Comparação com o PR #57 (LP/Farkas sobre as 12 049 instâncias do PR #51): lá, das 11 000 configurações
de `s = 5`, 10 591 morrem pelo LP de cobertura só da fatia; aqui, 10 681 morrem pela versão **inteira**
da mesma relaxação (o RoundingSat corta com planos de corte, não só com o LP), o que é coerente
(10 681 ≥ 10 591). As contagens de órbitas (Burnside: 1/1/5/35/490/11 075) e de sobreviventes do
filtro (0/0/1/27/468/11 000) coincidem com as do PR #57. **Nenhuma divergência de resultado.**

### M = 16 (pedido depois, segunda via para o PR #60)

Mesma cadeia OPB, `repro_rodar.py 3 6 2 16`, teto de prova de 3 GB por instância
(`K362_REPRO_MAX_PROVA_GB`). Lista: 11 592 instâncias (3 + 31 + 487 + 11 071).

| s | instâncias | fatia UNSAT | completa UNSAT | em aberto (prova > 3 GB) |
|---|---|---|---|---|
| 2 | 3 | 3 | 0 | 0 |
| 3 | 31 | 30 | 1 | 0 |
| 4 | 487 | 461 | 25 | 1 |
| 5 | 11 071 | 9 498 | 1 564 | 9 |
| **total** | **11 592** | **9 992** | **1 590** | **10** |

**11 582 de 11 592 instâncias refutadas com prova VeriPB conferida; 10 em aberto.** Nas 10, a prova
passou de 3 GB depois de 213 a 465 s de solver (duas, antes do teto, chegaram a 5,7 e 9,8 GB em 20 min
e foram mortas para não encher o disco). Medi sem prova, com 600–900 s por fórmula: a completa
pura não fecha a primeira delas em 600 s; acrescentando os blocos `Σ_{c₀=b} z ≥ s` fecha em 543 s;
dividindo pelos blocos exatos `(t₁, t₂)` (válido: trocar os símbolos 1 e 2 da coordenada 0 fixa `K`,
então `t₁ ≥ t₂`), o caso (8,4) fecha em 0,2 s mas o (7,5) não fecha em 900 s. Parei aí: fechar as 10
com prova pediria horas de solver por instância e provas de dezenas de GB, além do teto de disco da VM.
**Esta cadeia não reproduz K₃(6,2) ≥ 17**; ela é compatível com o PR #60 (nenhum código de 16
palavras apareceu, nenhum modelo satisfazível), mas deixa 10 instâncias sem certificado. As 10, com o
`K` de cada uma, estão no registro (`veredito: PROVA_GRANDE`).


## 5. O que muda e o que não muda

| afirmação | estado |
|---|---|
| a redução (§1) é completa | PROVED (texto acima) |
| a lista tem uma classe de `K` por órbita, 11 496 para M = 15 | COMPUTATIONALLY_VERIFIED (Burnside) e INDEPENDENTLY_REPRODUCED (contagens de `GAPS2_K362.md`/PR #57; nauty com grafo próprio) |
| as 11 496 instâncias de M = 15 são inviáveis | COMPUTATIONALLY_VERIFIED: 11 496 provas VeriPB conferidas; 11 171 delas também por prova LRAT conferida (as 325 restantes só pela cadeia OPB) |
| K₃(6,2) ≥ 16 | **INDEPENDENTLY_REPRODUCED** em relação ao PR #57: outra redução (sem blocos, relaxação projetada), outra enumeração e canonização (colunas + Burnside + nauty com grafo de triângulos), outro sistema de prova (planos de corte checados pelo VeriPB, e resolução checada pelo `lrat-check`), nenhum código em comum |
| K₃(6,2) ≥ 17 (M = 16) | OBSERVED apenas: 11 582 / 11 592 com prova; 10 em aberto |

O que este documento **não** faz: não muda o ledger, não formaliza em Lean, não confere as provas com
um verificador formalmente verificado (o `cake_lpr` aceitaria as provas LRAT; não rodei).


## 6. Como reproduzir

    sudo apt-get install libnauty-dev        # canon.c
    python3 tools/exatos/k362_repro/repro_rodar.py 3 6 2 15 --formato opb --bin DIR --saida m15.jsonl --proc 2
    K362_REPRO_BIN=DIR python3 -m pytest -q -p no:cacheprovider tests/test_k362_repro.py

`DIR` contém `roundingsat` e `veripb` (ou `cadical` e `lrat-check` com `--formato cnf`). Sem eles,
os testes da cadeia pulam; os de enumeração e canonização rodam sempre (os de nauty precisam de
`libnauty-dev`, como `tests/test_motor_exatos.py`).
