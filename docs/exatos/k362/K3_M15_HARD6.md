# K_3(6,2), M = 15: autópsia das 6 instâncias duras (2026-10-05)

Pergunta: por que 6 das 240 instâncias da amostra de `GAPS2_RESULTADOS.md` (índices 7955, 9118,
10603, 11739, 11804 e 11927, todas `s* = 5`, blocos (5,5)) levam de 3,5 min a mais de 30 min no
RoundingSat, enquanto a mediana das outras 234 é 3,6 s?

**Resposta curta (medida):** elas não são difíceis. Cada uma é refutada em 0,05 a 1,4 s por um
**subconjunto literal das linhas do próprio OPB**, que só olha a fatia 0, e o VeriPB confere as seis
provas (0,7 a 25 MB, contra GB na rodada original). O que é difícil é **achar** essa refutação dentro
da fórmula inteira: o núcleo usa cerca de 10 % das restrições de cobertura (os pontos de `U`, os da
fatia 0 longe de `K`), e as outras ~400 coberturas (fatias 1 e 2) puxam a busca para longe dele.
Isso acontece quando o lema da fatia 0 vale **com pouca folga**. Não é simetria: o grupo da fórmula
tem ordem 2 a 12. Também não é quase-viabilidade: o melhor código achado deixa 36 a 43 pontos
descobertos.

**Censo (seção própria):** os mesmos dois subconjuntos refutam, com VeriPB, **12 040 das 12 049**
instâncias de M = 15 em 2 830 s de solver no total. Sobram 9, que precisam da fórmula inteira.

Estados usados: **OBSERVED** (medido uma vez, sem conferência independente), **COMPUTATIONALLY_VERIFIED**
(prova conferida por verificador independente: VeriPB), **REFUTED** (a hipótese foi testada e falhou).

## O que foi medido

Ferramentas: `tools/exatos/k362/hard6/` (`autopsia.py`, `solvers.py`, `censo_projecao.py`), com
teste em `tests/test_k362_hard6.py`. Registros brutos: `tools/exatos/k362/hard6/registros/`.
Container de 4 núcleos compartilhado com outras frentes, no máximo 2 processos meus. **Os tempos
são de CPU e ficam ruidosos com a carga** (load 4 a 7): uma janela de 300 s de parede deu 170 a
300 s de CPU.

1. **Regeneração.** `rodar_pb.py --listar` regerou as 12 049 instâncias. Os 234 OPBs registrados
   batem por sha256 (234/234). As 6 duras **não têm sha no registro** (rodaram sem prova e ficaram
   fora do `.jsonl`): os sha delas estão em `registros/medir.jsonl` daqui em diante. OBSERVED.
2. **Amostra de comparação:** as 6 duras mais 20 fáceis de `s* = 5`, uma em cada vigésimo dos
   tempos registrados, de 0,05 s (6738) a 215 s (1999).

## Tabela: duras (D) × fáceis

`restr.` = restrições da fórmula efetiva (a fatia 0 substituída: 486 variáveis livres).
`|Aut|` = grupo de automorfismos da fórmula (nauty/Traces no grafo de incidência colorido).
`UP` = variáveis fixadas por propagação na raiz / literais falhos por sondagem. `mod.` =
modularidade de Louvain do grafo de incidência. `RS` = RoundingSat na fórmula inteira (teto de
300 s de parede): veredito, CPU e conflitos. `CaD 30 s` = CaDiCaL na CNF do totalizador por
30 s: conflitos / nível médio de decisão / glue (LBD) médio. `SA` = menor número de pontos
descobertos que o recozimento achou respeitando a instância. `U`, `ν`, `τ`, `γ`: lema da fatia 0
(seção seguinte). `sub.` = subconjunto que refuta (A ou B) e tempo do RoundingSat nele.

| inst. | tempo registrado | restr. | \|Aut\| | UP | mod. | RS (fórmula inteira) | CaD 30 s | SA | U | ν | τ | γ | sub. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11927 **D** | 3:30 | 457 | 12 | 0/0 | 0,28 | sem veredito 168,38 s / 169,96 mil | 140 mil / 33 / 21 | 39 | 54 | 9 | 11,25 | 12 | A 0,11 s |
| 7955 **D** | 26:10 | 454 | 4 | 0/0 | 0,30 | sem veredito 261,39 s / 294,40 mil | 251 mil / 18 / 10 | 39 | 57 | 8 | 9,50 | 10 | B 1,39 s |
| 9118 **D** | 29:08 | 466 | 8 | 0/0 | 0,32 | sem veredito 266,58 s / 303,90 mil | 361 mil / 26 / 19 | 43 | 69 | 9 | 10,67 | 12 | A 0,13 s |
| 10603 **D** | >30:00 | 447 | 8 | 0/0 | 0,31 | sem veredito 211,23 s / 275,16 mil | 196 mil / 17 / 9 | 36 | 54 | 9 | 10,00 | 11 | A 0,31 s |
| 11739 **D** | 7:41 | 441 | 2 | 0/0 | 0,30 | sem veredito 300,00 s / 343,50 mil | 346 mil / 17 / 10 | 38 | 48 | 9 | 10,40 | 11 | A 0,46 s |
| 11804 **D** | 9:48 | 442 | 2 | 0/0 | 0,32 | sem veredito 300,00 s / 280,62 mil | 369 mil / 30 / 22 | 36 | 49 | 9 | 10,34 | 11 | A 0,73 s |
| 6738 | 0,05 s | 503 | 12 | 0/0 | 0,31 | UNSAT 0,03 s / 0,23 mil | 324 mil / 16 / 10 | 54 | 90 | 11 | 12,30 | 14 | A 0,01 s |
| 7850 | 0,20 s | 489 | 8 | 0/0 | 0,31 | UNSAT 0,11 s / 0,91 mil | 338 mil / 17 / 10 | 54 | 80 | 10 | 12,62 | 14 | A 0,04 s |
| 5696 | 0,34 s | 484 | 4 | 0/0 | 0,26 | UNSAT 0,25 s / 1,39 mil | 360 mil / 16 / 9 | 52 | 79 | 11 | 12,28 | 13 | A 0,03 s |
| 5013 | 0,51 s | 485 | 2 | 0/0 | 0,32 | UNSAT 0,32 s / 1,96 mil | 331 mil / 17 / 9 | 47 | 78 | 11 | 12,61 | 14 | A 0,03 s |
| 1738 | 0,80 s | 503 | 8 | 0/0 | 0,33 | UNSAT 0,61 s / 2,54 mil | 356 mil / 15 / 9 | 52 | 95 | 11 | 13,00 | 13 | A 0,01 s |
| 4060 | 1,03 s | 484 | 2 | 0/0 | 0,26 | UNSAT 0,74 s / 3,36 mil | 376 mil / 23 / 17 | 47 | 81 | 12 | 12,39 | 13 | A 0,03 s |
| 8296 | 1,52 s | 476 | 2 | 0/0 | 0,33 | UNSAT 1,02 s / 3,94 mil | 345 mil / 31 / 22 | 37 | 77 | 10 | 11,32 | 12 | A 0,05 s |
| 2209 | 1,76 s | 472 | 8 | 0/0 | 0,31 | UNSAT 1,33 s / 4,98 mil | 353 mil / 26 / 19 | 44 | 76 | 10 | 12,00 | 12 | A 0,03 s |
| 7420 | 2,23 s | 478 | 4 | 0/0 | 0,28 | UNSAT 1,58 s / 6,06 mil | 348 mil / 16 / 10 | 51 | 73 | 11 | 12,61 | 13 | A 0,22 s |
| 5370 | 3,07 s | 467 | 2 | 0/0 | 0,29 | UNSAT 2,21 s / 9,72 mil | 338 mil / 16 / 9 | 44 | 70 | 10 | 11,29 | 12 | A 0,05 s |
| 7494 | 3,86 s | 474 | 2 | 0/0 | 0,29 | UNSAT 2,67 s / 9,76 mil | 365 mil / 27 / 19 | 48 | 71 | 11 | 11,43 | 12 | A 0,12 s |
| 9609 | 4,79 s | 459 | 2 | 0/0 | 0,30 | UNSAT 3,49 s / 11,37 mil | 346 mil / 16 / 9 | 38 | 62 | 10 | 11,07 | 12 | A 0,09 s |
| 8567 | 5,76 s | 476 | 4 | 0/0 | 0,33 | UNSAT 3,65 s / 13,99 mil | 355 mil / 28 / 20 | 47 | 79 | 11 | 11,44 | 12 | A 0,06 s |
| 6533 | 7,00 s | 471 | 2 | 0/0 | 0,29 | UNSAT 5,03 s / 15,88 mil | 417 mil / 15 / 9 | 45 | 70 | 10 | 11,45 | 12 | A 0,08 s |
| 10195 | 9,11 s | 455 | 4 | 0/0 | 0,31 | UNSAT 6,44 s / 19,17 mil | 336 mil / 17 / 10 | 42 | 58 | 10 | 10,65 | 11 | A 0,14 s |
| 7375 | 10,72 s | 472 | 8 | 0/0 | 0,32 | UNSAT 7,85 s / 22,40 mil | 310 mil / 14 / 9 | 41 | 73 | 10 | 10,00 | 10 | B 0,05 s |
| 5234 | 17,39 s | 472 | 2 | 0/0 | 0,33 | UNSAT 12,89 s / 34,61 mil | 315 mil / 25 / 18 | 41 | 71 | 11 | 11,61 | 13 | A 0,04 s |
| 9460 | 26,78 s | 464 | 2 | 0/0 | 0,32 | UNSAT 18,88 s / 41,56 mil | 341 mil / 17 / 10 | 35 | 67 | 9 | 11,21 | 12 | A 0,04 s |
| 9596 | 57,90 s | 461 | 2 | 0/0 | 0,32 | UNSAT 44,91 s / 86,28 mil | 343 mil / 31 / 23 | 44 | 64 | 10 | 10,94 | 12 | A 0,04 s |
| 1999 | 215,43 s | 469 | 24 | 0/0 | 0,33 | UNSAT 212,70 s / 232,66 mil | 356 mil / 24 / 17 | 24 | 77 | 9 | 9,00 | 9 | B 0,40 s |

Leitura: nada de `restr.`, `|Aut|`, `UP` (sempre 0/0), `mod.` (0,26 a 0,33), da CNF (nenhum dos dois
solvers CDCL resolve **nenhuma** das 26 em 30 s, nem a 6738, que o RoundingSat fecha em 235
conflitos) ou da largura de árvore heurística (452 a 453 em todas, o primal é quase completo)
separa duras de fáceis. O tamanho também não: CNF de 25 281 a 26 483 variáveis e de 325 mil a 339 mil
cláusulas nas duas classes. O que separa é a coluna `τ` e a coluna `sub.`.

## O lema da fatia 0, e por que ele esconde o núcleo

Seja `U` o conjunto dos pontos de `Z_3^5` a distância > 2 de todo ponto de `K`. Um ponto `(0, y)`
com `y ∈ U` só é coberto por uma palavra `c` com `c_0 ≠ 0` e `d(c', y) ≤ 1`, em que `c'` é a
projeção de `c` nas coordenadas 1..5. As `M − s* = 10` palavras fora da fatia 0 têm de cobrir `U`
com bolas de raio 1 de `Z_3^5`. Portanto, com `γ(U)` o menor número de bolas de raio 1 que cobrem `U`:

    γ(U) > M − s*  ⇒  a instância é inviável.

O filtro de contagem de `GAPS2_K362.md` (`|U| ≤ 10 · 11`) é o caso em que as bolas não se sobrepõem.
Há três degraus de prova, do mais barato ao mais caro:

- **empacotamento:** `ν(U)`, o maior subconjunto de `U` com distâncias duas a duas ≥ 3. Duas bolas de
  raio 1 não contêm o mesmo par desses pontos, então `ν(U) > 10` dá 11 pontos que exigem 11
  palavras distintas. É um princípio da casa dos pombos `PHP(11,10)`;
- **LP:** `τ(U)`, a cobertura fracionária. `τ > 10` é uma combinação linear (Farkas) das restrições;
- **inteiro:** `τ ≤ 10 < γ`, que exige arredondamento (Chvátal–Gomory).

Os dois subconjuntos testados são linhas **literais** do OPB da instância, então a inviabilidade
deles implica a da instância, e a prova do RoundingSat sobre eles confere no VeriPB contra eles:

- **A:** fixações da fatia 0, cobertura dos 243 pontos com `x_0 = 0`, tamanho e blocos (489 de 990
  linhas). É o lema acima;
- **B:** A mais as 15 fibras (504 linhas). As fibras prescrevem quantas palavras de cada símbolo há em
  cada coordenada, ou seja, a contagem de símbolos das 10 projeções.

### As 6 duras: COMPUTATIONALLY_VERIFIED

| inst. | U | ν | τ | γ | subconjunto | RoundingSat | prova | VeriPB |
|---|---|---|---|---|---|---|---|---|
| 11927 | 54 | 9 | 11,25 | 12 | A | 0,05 s | 0,7 MB | VERIFIED |
| 9118 | 69 | 9 | 10,67 | 12 | A | 0,13 s | 1,8 MB | VERIFIED |
| 11739 | 48 | 9 | 10,40 | 11 | A | 0,29 s | 5,8 MB | VERIFIED |
| 11804 | 49 | 9 | 10,34 | 11 | A | 0,33 s | 4,8 MB | VERIFIED |
| 10603 | 54 | 9 | 10,00 | 11 | A | 0,20 s | 3,5 MB | VERIFIED |
| 7955 | 57 | 8 | 9,50 | 10 | B (A é viável) | 1,39 s | 25 MB | VERIFIED |

A 10603 nunca tinha terminado (30 min, 1,35 milhão de conflitos). Agora as seis estão refutadas
**com certificado**, coisa que a rodada original não tinha para nenhuma delas.

### Dose e resposta: o núcleo afogado (OBSERVED)

O mesmo RoundingSat, a mesma instância, acrescentando linhas ao subconjunto A (teto de 150 s):

| inst. | A (489 linhas) | + cobertura da fatia 1 (732) | + fatias 1 e 2 (975) | fórmula inteira (990) |
|---|---|---|---|---|
| 11927 | 0,05 s, 290 conflitos | 17,1 s, 35 mil | 79,8 s, 109 mil | sem veredito em 168 s de CPU (170 mil) |
| 10603 | 0,12 s, 1 012 | 22,3 s, 47 mil | 88,3 s, 121 mil | sem veredito em 211 s de CPU (275 mil) |

A refutação continua lá dentro, mas cada bloco de restrições irrelevantes para ela multiplica o
tempo. É isso que "difícil" quer dizer aqui.

### Por que só estas: a folga do lema (OBSERVED, n = 230 de `s* = 5`)

Correlação de Spearman entre o tempo registrado e as medidas do lema na amostra de 240 (`s* = 5`,
com as 6 duras pelo tempo sem prova): `τ` −0,60, `|U|` −0,59, `γ` −0,57, `ν` −0,36 (todas com
p < 10⁻⁷). Por `ν`:

| ν(U) | instâncias | mediana | > 60 s | duras |
|---|---|---|---|---|
| 8 | 2 | 800 s | 1 | 7955 |
| 9 | 25 | 11,7 s | 8 | 9118, 10603, 11739, 11804, 11927 |
| 10 | 108 | 4,1 s | 5 | — |
| 11 | 79 | 1,9 s | 2 | — |
| 12–13 | 10 | 1,0 s | 0 | — |

Interpretação (hipótese compatível com os números, não demonstrada): quando `ν > 10`, o conflito do
pombo aparece cedo, seja qual for a ordem da busca. Quando `ν ≤ 9`, a prova da fatia 0 precisa do LP inteiro, ou de arredondamento, ou das fibras (o degrau B), e a
busca, guiada pelos conflitos das fatias 1 e 2, não chega lá. As 6 duras são `ν ≤ 9` (6 de 27,
22 %). Nenhuma das 197 com `ν ≥ 10` é dura. Na amostra: 104 caem por empacotamento, 122 pelo LP, 3
só pelo inteiro (entre elas a 10603) e 11 precisam do degrau B (entre elas a 7955). As 240 caem em
A ou B, todas conferidas pelo VeriPB, somando 49 s de solver, contra os ~2 944 s mais 6 × (3 a 30
min) da rodada original.

Por que a CNF não resolve nem as fáceis: o núcleo é um princípio da casa dos pombos com 11 pombos,
que exige prova exponencial em resolução. Planos de corte o fazem em tamanho polinomial. Isso é
consistente com CaDiCaL e kissat zerados em 30 s e com o RoundingSat fechando a 6738 em 235 conflitos.

## Hipóteses descartadas

**Simetria: REFUTED como explicação principal.** `|Aut|` da fórmula, medido pelo nauty e conferido
pelo estabilizador combinatório de `K` em `S_3 ≀ S_5` (sempre `|Aut| = 2 · |Stab(K)|`, o fator 2
é a troca dos símbolos 1 e 2 da coordenada 0), dá 12, 4, 8, 8, 2 e 2 nas duras, contra 2 a 24 nas
fáceis. A 11739 e a 11804 só têm a troca trivial. Quebrar um grupo de ordem `g` ganha no máximo um
fator `g`, e a distância até o subconjunto A é de 10³ a 10⁴. Teste direto na 11927 (`|Aut| = 12`,
lex-leader truncado nos 3 geradores do nauty, como PB): UNSAT em 143 s de CPU e 23,9 mil conflitos,
contra nenhum veredito em 168 s de CPU sem quebra. A quebra ajuda um pouco (7× menos conflitos,
tempo da mesma ordem por causa dos coeficientes 2^39). O subconjunto A leva 0,05 s. OBSERVED.

A simetria que o `GAPS2_RESULTADOS.md` aponta (um código equilibrado aparece em até 18 instâncias) é
**entre** instâncias. Ela multiplica o número de instâncias, mas não deixa nenhuma delas mais difícil.

**Quase satisfatível: REFUTED.** O recozimento (`autopsia.sa`, 2 sementes × 200 mil passos, K fixo,
5+5 palavras, fibras respeitadas) deixa no mínimo 36 a 43 pontos descobertos nas duras e 24 a 54 nas
fáceis. Sem as fibras, 29 a 40 contra 21 a 49. As duras não estão mais perto de um código que as
fáceis; a mais "próxima" é a 1999, uma fácil. Sem restrição nenhuma, códigos de 15 palavras em
`Z_3^6` deixam 14 pontos descobertos (`sa_cover.c`, 3 × 60 s). Nenhuma instância chega perto de um
código. O CP-SAT, com 10 s, não fecha a cota inferior (fica em 0): os números acima são cotas
superiores, OBSERVED. **Nenhum código de 15 palavras foi encontrado.**

**Estrutura do grafo (modularidade, largura de árvore), tamanho e propagação: REFUTED.** Ficam
iguais nas duas classes (tabela).

## Núcleos das fáceis (item 5)

O núcleo extraído da prova (fecho para trás a partir da contradição, pelos hints dos `rup` e pelos
operandos dos `p`, em `autopsia.nucleo_prova`) da 6738 é: as 243 fixações, 48 coberturas e o
tamanho. Não usa fibras nem blocos, e rodar de novo só com ele dá UNSAT. As 26 da comparação
compartilham o **mesmo tipo de núcleo**, não as mesmas restrições, porque cada `K` tem o seu `U`:
um subconjunto `U' ⊆ U` que não cabe em 10 bolas de raio 1. A remoção gulosa no problema projetado
deixa `|U'|` entre 27 e 44 (não é o mínimo). Quando `ν ≥ 11`, existe núcleo de 11 pontos: o
empacotamento. As que precisam do degrau B (7955, 7375, 1999) usam também a contagem de símbolos por
coordenada.

**Insumo para um lema:** *num código de cobertura `K_3(6,2)` com 15 palavras e todas as 18 fibras
de tamanho 5, cada fibra `F(j,a)` tem projeção `K_{j,a}` (5 pontos de `Z_3^5`) com
`γ_1(U(K_{j,a})) ≤ 10`. Mais forte: `U(K_{j,a})` é cobrível por 10 centros que têm, em cada
coordenada `i ≠ j` e símbolo `b`, exatamente `5 − #{k ∈ K_{j,a} : k_i = b}` centros com `k_i = b`.* Isso vale para **todas** as 18 fibras ao mesmo tempo, não só para a escolhida. É a
"escolha canônica de fibra" que o `GAPS2_RESULTADOS.md` pedia, dita como restrição.

## Censo: a reformulação sobre as 12 049 instâncias

Rodado nas 12 049 instâncias de M = 15 (`registros/censo_K3_6_2_M15.jsonl.gz`, uma linha por
instância com sha256 do OPB, veredito e tempo de cada subconjunto e o veredito do VeriPB). Teto de
600 s para A e 120 s para B. Container compartilhado, 1 a 2 processos, cerca de 1h40 de parede.

| s* | instâncias | caem em A | caem em B | sobram (A e B viáveis) |
|---|---|---|---|---|
| 2 | 5 | 5 | 0 | 0 |
| 3 | 108 | 104 | 0 | 4 (13, 14, 15, 16) |
| 4 | 936 | 926 | 8 | 2 (523, 524) |
| 5 | 11 000 | 10 681 | 316 | 3 (2178, 7388, 11160) |
| **total** | **12 049** | **11 716** | **324** | **9** |

- **12 040 das 12 049 instâncias** estão refutadas por subconjuntos literais dos próprios OPBs, e as
  12 040 provas foram conferidas pelo VeriPB (12 040/12 040 `VERIFIED`). COMPUTATIONALLY_VERIFIED, por
  instância. Soma de 2 830 s de solver, máximo de 221 s. A rodada original estimava ~48 CPU-h para as
  fáceis, mais ≥ 150 CPU-h e dezenas de GB de prova para as duras.
- Nenhum subconjunto deu `UNKNOWN`. As 9 que sobram têm A e B **viáveis**: o lema da fatia 0, mesmo
  com as fibras, não basta. Elas precisam da fórmula inteira (`registros/sobras.txt`): a 13 deu UNSAT com prova
  VeriPB (46 s); 16, 523 e 524 deram UNSAT **sem** prova (33 a 141 s de CPU), OBSERVED; 14, 15, 2178,
  7388 e 11160 ficaram **sem veredito** em 600 s de parede (186 a 466 s de CPU). Essas cinco são as
  duras de verdade: o núcleo delas não está na fatia 0. Para as três de `s* = 5` (2178, 7388, 11160),
  o próximo passo natural é o item 3 da sugestão, o lema aplicado às 18 fibras.
- **Isto não fecha `K_3(6,2) ≥ 16`.** Faltam (i) as 9 sobras com certificado, (ii) a codificação
  independente que o `GAPS2_RESULTADOS.md` exige para virar teorema, e (iii) revisão da redução. Nada
  vai para o ledger.

## Sugestão concreta de reformulação

1. Antes do solver, rodar `censo_projecao.py`: o subconjunto A e depois o B de cada instância, cada um
   com a prova conferida pelo VeriPB contra o próprio subconjunto, que é feito de linhas literais do
   OPB. Custa segundos por instância e provas de MB, contra GB.
2. Trocar o filtro de contagem `|U| ≤ (M − s*) · V(n−1, R−1)` por `τ(U) ≤ M − s*` (LP de 243
   variáveis) em `fatia.configuracoes`. É barato e corta antes de gerar a instância. A prova formal
   continua vindo do subconjunto A.
3. Para as que sobrarem, ou para um solver que precise da fórmula inteira: acrescentar como
   restrições redundantes as coberturas projetadas de **todas** as fibras (o lema acima), em vez de só
   a da fatia 0, e dar prioridade de decisão às variáveis do núcleo da fatia 0. A quebra de simetria
   intra-instância rende pouco (no máximo `|Aut| ≤ 24`).

## Reprodução

    python3 tools/exatos/gaps2/rodar_pb.py --q 3 --n 6 --R 2 --M 15 --listar i15.json
    cd tools/exatos/k362/hard6
    python3 autopsia.py --instancias i15.json --idx 11927 medir --quase-s 10
    CADICAL=... KISSAT=... ROUNDINGSAT=... python3 solvers.py --instancias i15.json --idx 11927 \
        --tempo 30 --rs-tempo 300 --dir tmp
    ROUNDINGSAT=... VERIPB=... python3 censo_projecao.py --instancias i15.json --saida censo.jsonl \
        --so 7955,9118,10603,11739,11804,11927

Binários: RoundingSat (fonte oficial), VeriPB 2 (Rust), CaDiCaL e kissat (fonte oficial), `dreadnaut`
do nauty. Python: numpy, scipy (HiGHS), networkx, python-sat, ortools.
