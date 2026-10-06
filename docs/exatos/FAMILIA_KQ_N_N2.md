# A família K_q(n, n−2): estrutura do código de 14 de K_7(6,4) e a construção por blocos (2026-10-05)

Missão S8. Ponto de partida: o código de 14 palavras de K_7(6,4) (`data/codes/q7_n6_R4_M14.txt`,
branch `feat/exatos-fibras`, PR #56), que bate a partição do alfabeto (15). Pergunta: o que ele tem
de estrutura, e isso generaliza para K_8(7,5), K_9(8,6), K_10(9,7) e K_q(4,2), q = 16…20?

**Estado:** nenhum código melhor que o publicado foi achado. O que sai daqui é (1) a estrutura do
código de 14, que é uma construção nova por **blocos com famílias** e contém a partição como caso
particular; (2) um critério exato para essa construção, uma CNF pequena e um verificador
independente; (3) resultados de inexistência **dentro da construção** (não do problema) para
q = 8; (4) a redução de K_q(4,2), q = 16…20, a uma quantidade só, g(b,4,3); (5) cotas inferiores
que o lema das fibras dá quando se propaga K_7(6,4) ≥ 14, e algumas que ele já dava com as cotas
publicadas. **Nada disso entrou no ledger, no paper nem em `data/`.**

## Estados (fechamento, 2026-10-05)

Rótulos: **PROVED** (argumento matemático completo escrito aqui; nenhum formalizado em Lean),
**COMPUTATIONALLY_VERIFIED** (conferido por um verificador independente do gerador:
`tools/verify/verify` e/ou `cobre_n2.c`, ou por teste contra força bruta), **OBSERVED** (saída de
uma ferramenta, sem conferência independente; todo UNSAT daqui é OBSERVED porque o kissat rodou
sem prova DRAT), **INDEFINIDO** (o solver não respondeu no tempo).

| afirmação | estado |
|---|---|
| Teorema 1: critério exato e contagem de descobertos da construção por blocos (seção 2) | PROVED; contagem também COMPUTATIONALLY_VERIFIED contra força bruta (`test_familia_blocos.py`) |
| O código de 14 de K_7(6,4) é de blocos puros 3:6 + 4:8, com a tabela de famílias da seção 1 | COMPUTATIONALLY_VERIFIED (teste) |
| \|Aut\| = 32 do código de 14 e as órbitas listadas | OBSERVED (`dreadnaut`, uma ferramenta) |
| K_7(6,4) ≤ 14 reencontrado pela CNF de blocos | COMPUTATIONALLY_VERIFIED (`cobre_n2`: 0 descobertos) |
| Formas de 13 palavras de K_7(6,4), de 15 de K_8(7,5), de 16 de K_9(8,6) e de 16 de K_7(5,3): UNSAT | OBSERVED, e só **dentro da forma** |
| Código de 16 palavras de K_8(7,5) que não é a partição (seção 4) | COMPUTATIONALLY_VERIFIED (`verify` e `cobre_n2`: 0 de 2 097 152; sha256 `5887e70d…`). **Iguala** a cota publicada (16), não bate: não vai para `data/codes/` |
| Classificação das construções por blocos para n = 4 e K_q(4,2) ≤ min_a [CAN(2,4,a) + g(q−a,4,3)] (seção 5) | PROVED |
| g(3,4,3) = 6, g(3,6,3) = 7, g(4,6,4) = 8 | OBSERVED (SAT/UNSAT da CNF) |
| g(4,4,3) = 10, g(5,4,3) = 14 | ≤: OBSERVED (SAT); ≥: PROVED condicional a K_7(4,2) = 19 e K_8(4,2) = 23 (cotas da literatura, CLAIMED no ledger) e também OBSERVED pela CNF |
| g(11,4,3) ≤ 61, g(12,4,3) ≤ 73, g(13,4,3) ≤ 85 | INDEFINIDO (12 000 s cada) |
| Cotas inferiores pelo lema das fibras (seção 6) | PROVED condicional ao Lema 1 de `FIBRAS_GERAL.md` (branch das fibras) e a cotas CLAIMED do ledger; as três primeiras dependem ainda do ∄ 13 de K_7(6,4), que é computacional. Não registradas |
| Busca por órbitas de rotação e recozimento não acham códigos (seção 7) | OBSERVED |

**Cota nova: nenhuma.** Nenhum código melhor que o publicado foi achado; nada foi gravado em
`data/codes/` nem no ledger.

## 1. O código de 14: grupo e estrutura

    000000 011111 100011 122200 212222 221122     <- só símbolos {0,1,2}
    333333 343444 434455 444366 555534 565643 656665 666556   <- só símbolos {3,4,5,6}

* **Toda palavra é pura num bloco**: 6 palavras em {0,1,2}^6 e 8 em {3,4,5,6}^6. Nenhuma mistura.
* Perfil de fibras 2222222^6: cada bloco é equilibrado (6 = 3·2, 8 = 4·2).
* **Automorfismos** (grafo palavra–(coordenada, símbolo)–coordenada no `dreadnaut`): |Aut| = 32.
  Órbitas: palavras {0,2}, {1,3}, {4,5} (bloco de 3) e as 8 do bloco de 4 numa órbita só;
  coordenadas 0, 1, 2, 3 fixas e {4,5}; símbolos da coordenada 0: {0,1}, {2}, {3,4,5,6}. O grupo
  não tem rotação de coordenadas, nem age transitivamente nos 7 símbolos.
* O código achado de novo pela CNF de blocos (seção 3) tem também |Aut| = 32.

**Por que cobre.** Com R = n − 2, x está coberto sse alguma palavra concorda com x em ≥ 2
coordenadas. Seja S = {i : x_i ∈ {0,1,2}}. Só palavras do bloco A = {0,1,2} concordam com x em
S, e só as do bloco B = {3,…,6} concordam em S^c. Medido (`fam.py` da sessão, refeito no teste):

| bloco | palavras | cobre A^S para |
|---|---|---|
| A (3 símbolos) | 6 | todo |S| ≥ 4, e 18 dos 20 triplos (falha em {0,4,5} e {1,2,3}) |
| B (4 símbolos) | 8 | todo |S| ≥ 4, e 4 triplos: {0,1,3}, {2,4,5}, {0,4,5}, {1,2,3} |

Os dois triplos que A não cobre são complementares, e B cobre os dois. Os 10 pares {S, S^c} de
triplos ficam todos resolvidos: ou A cobre S, ou B cobre S^c. |S| ≤ 2 cai em B (|S^c| ≥ 4) e
|S| ≥ 4 cai em A. É uma partição do alfabeto em 2 blocos em que **nenhum** bloco cobre todos os
pares de coordenadas: o que a partição clássica exige de cada bloco (arranjo de força 2) aqui se
divide entre os dois blocos por tamanho de S.

## 2. A construção por blocos com famílias

**Teorema 1 (critério exato).** Parta Z_q = A_0 ⊔ … ⊔ A_{k−1} e tome C = ∪ C_j com C_j ⊂ A_j^n.
Para D ⊂ A^n seja f(D) = {S ⊆ [n] : D|S cobre A^S com ≥ 2 concordâncias} (a *família* de D; é
fechada para cima). Então C tem raio n − 2 sse

    para toda partição ordenada (S_0, …, S_{k−1}) de [n] existe j com S_j ∈ f(C_j),

e o número de pontos descobertos é exatamente Σ_{(S_j)} Π_j u_j(S_j), com u_j(S) = |A_j^S não
cobertos por C_j|S| (u(∅) = 1, u(S) = a^{|S|} se |S| = 1).

*Prova.* x concorda com palavras de C_j só nas coordenadas S_j(x) = {i : x_i ∈ A_j}. Logo x está
descoberto sse x|S_j é descoberto por C_j|S_j para todo j. Somando sobre as partições dá a
contagem; e se para alguma partição cada S_j tem um ponto descoberto y_j, o x que junta os y_j é
descoberto. ∎

A conta exata foi conferida contra o verificador independente: um código de 14 palavras não
coberto (saído de um recozimento exploratório, não versionado) tinha 92 descobertos pela fórmula e
92 pelo `cobre_n2`; o teste `test_contagem_por_blocos_bate_forca_bruta_em_codigos_aleatorios`
confere a fórmula contra força bruta.

**Casos particulares.**

* *Partição clássica* (triagem, Achado 1): k ≤ n − 1 blocos, cada C_j um arranjo de força 2, isto
  é, f(C_j) ⊇ todos os pares. Pelo pombal algum S_j tem ≥ 2 elementos. K_7(6,4) ≤ 15 era 1+1+1+2+2.
* *Palavra constante*: um bloco de 1 símbolo com a palavra constante tem f = {|S| ≥ 2}. Mais
  geral, as a constantes de um bloco de a símbolos cobrem todo S com |S| ≥ a + 1 (pombal).
* *Limiares*: se f(C_j) ⊇ {|S| ≥ t_j} e Σ_j (t_j − 1) ≤ n − 1, o pombal fecha. Com
  g(a, n, t) = menor |D|, D ⊂ Z_a^n, com f(D) ⊇ {|S| = t},

      K_q(n, n−2) ≤ Σ_j g(a_j, n, t_j)  sempre que Σ a_j = q e Σ (t_j − 1) ≤ n − 1.

  Note g(a, n, t) ≥ K_a(t, t−2), g(a, n, a+1) = a (constantes) e g(a, n, 2) = CAN(2, n, a).
* O código de 14 **não** é de limiares puros: seria g(3,6,3) + g(4,6,4), e a CNF dá g(3,6,3) = 7
  (6 UNSAT, 7 SAT) e g(4,6,4) = 8 (7 UNSAT): limiares dão 15, a partição de novo. A mistura (A
  cobre 18 dos 20 triplos, B cobre os 2 que faltam) é o que economiza a palavra.

**Cotas inferiores para g que vêm de graça.** Toda escolha de blocos é uma cota superior; como
K_7(6,4) ≥ 14 (PR #56), cada instância dá uma cota inferior para g. Ex.: 3 constantes + bloco de 4
com t = 3 dá K_7(6,4) ≤ 3 + g(4,6,3), logo g(4,6,3) ≥ 11; 2 + g(5,6,4) ≥ 14 dá g(5,6,4) ≥ 12.

## 3. Ferramentas (`tools/exatos/familia/`)

| arquivo | o que faz |
|---|---|
| `blocos_sat.py` | CNF do Teorema 1: palavras one-hot por bloco, variáveis de projeção em pares P, variáveis U[j,S] = "C_j cobre S" com uma cláusula por ponto de A_j^S, e uma cláusula por partição ordenada. Quebra de simetria: palavras do bloco com a coordenada 0 não decrescente e precedência de valores nas colunas ≥ 1 (renomear símbolos de uma coluna dentro do bloco é isometria e não mexe na ordem das palavras). `--t T` calcula g(a,n,T); `--fixar` fixa colunas de um código dado. |
| `cobre_n2.c` | verificador independente para R = n − 2, qualquer q ≤ 62: busca em profundidade que poda assim que uma palavra atinge 2 concordâncias. Concorda com `tools/verify/verify` (0/117 649 no código de 14; 447 descobertos no código sem a última palavra, nos dois). |
| `propaga_fibras.py` | propaga cotas inferiores pelo Lema 1 de `FIBRAS_GERAL.md` (só lê o ledger). |

Validação da CNF (kissat 4.0.4, uma thread, máquina compartilhada):

| instância | esperado | saiu |
|---|---|---|
| K_7(6,4), blocos 3:6 + 4:8 | SAT (o código de 14 é dessa forma) | SAT em 1,5 s, código cobre Z_7^6 (`cobre_n2`: 0 descobertos) |
| K_7(6,4), 13 palavras: 3:6 + 4:7, 3:5 + 4:8, 1 + 3:6 + 3:6 | UNSAT (K_7(6,4) = 14) | UNSAT em 3 s, 2 s, 1 s |
| g(4,4,3) com 9 / 10 palavras | 10 (de K_7(4,2) = 19, ver seção 4) | UNSAT / SAT |
| g(5,4,3) com 13 / 14 palavras | 14 (de K_8(4,2) = 23) | UNSAT / SAT |

## 4. K_8(7,5), K_9(8,6), K_10(9,7): o que a construção alcança

Pela seção 6, um código de 15 palavras de K_8(7,5) fecharia a célula (lb 15). Varredura das
formas por blocos com 15 palavras (`blocos_sat.py` + kissat 4.0.4, uma thread; "bloco a:m" = a
símbolos, m palavras; 1:1 = constante):

| forma (q = 8, n = 7, M = 15) | resultado | tempo |
|---|---|---|
| 1:1 + 3:6 + 4:8 (o código de 14 + uma constante, livre) | UNSAT | 10 s |
| 1:1 + 3:7 + 4:7 | UNSAT | 9 s |
| 1:1 + 3:5 + 4:9 | UNSAT | 4 s |
| 1:1 + 3:4 + 4:10 | UNSAT | 79 s |
| 1:1 + 1:1 + 3:6 + 3:7 | UNSAT | 0 s |
| 2:3 + 3:6 + 3:6 | UNSAT | 1 s |
| o próprio código de 14 com uma 7ª coluna, + constante (`--fixar`) | UNSAT | 0,2 s |
| 4:7 + 4:8 | UNSAT | 391 s (VM) |
| 3:7 + 5:8 | UNSAT | 591 s (VM) |
| 3:6 + 5:9 | UNSAT | 2 169 s (VM) |
| 3:5 + 5:10 | INDEFINIDO (sem resposta em 12 000 s, VM) | — |
| 3:4 + 5:11 | INDEFINIDO (sem resposta em 12 000 s, VM) | — |
| 3:3 + 5:12 | INDEFINIDO (sem resposta em 12 000 s, VM) | — |
| 2:2 + 6:13 | INDEFINIDO (sem resposta em 12 000 s, VM) | — |

"VM" = `lote-s08-familia` (t2d-standard-8, spot), uma instância de kissat 4.0.4 por núcleo,
`timeout 12000`. Nenhum UNSAT desta tabela tem prova conferida (kissat rodou sem DRAT): são
OBSERVED. Nenhuma forma de 15 palavras saiu SAT.

Com 16 palavras a mesma forma existe: **1:1 + 3:7 + 4:8 é SAT** (5 s), um código de K_8(7,5) com
16 palavras que **não** é a partição (|Aut| = 8; `tools/verify/verify`: 0 de 2 097 152 descobertos,
sha256 `5887e70d…`), enquanto 1:1 + 3:6 + 4:9 é UNSAT (98 s). A partição 1+1+1+1+2+2 (6:6 nos
blocos de 2) sai SAT em 0 s, como devia.

    0000000 1111111 1122212 1222123 2212213 2211122 2121223 3333331
    4444444 4555555 5666566 5477677 6744645 6655754 7566767 7777476

Para q = 9, n = 8, M = 16 as formas com dois singletons, 1:1 + 1:1 + 3:6 + 4:8 e 1:1 + 1:1 + 3:7 +
4:7, são UNSAT (30 s e 35 s). Leitura: a estrutura (3,4) do código de 14 não se estende somando
constantes; o ganho de K_7 vem de as duas famílias se encaixarem exatamente em n = 6.
**UNSAT aqui é só dentro da forma** (palavras puras por bloco, com essa divisão do alfabeto);
não diz nada sobre códigos com palavras mistas.

### 4.1 K_7(5,3) com 16 palavras (ledger 15–17)

Um código de 16 palavras de K_7(5,3) bateria a cota publicada (17). Varredura das formas por
blocos com 16 palavras (q = 7, n = 5; mesma notação; local = container compartilhado, uma thread):

| forma (q = 7, n = 5, M = 16) | resultado | tempo |
|---|---|---|
| 3:4 + 4:12, 3:5 + 4:11, 3:6 + 4:10, 3:7 + 4:9, 3:8 + 4:8, 3:9 + 4:7 | UNSAT | ≤ 2 s cada |
| 2:3 + 5:13 | UNSAT | 128 s |
| 2:4 + 5:12 | UNSAT | 181 s |
| 2:5 + 5:11 | INDEFINIDO (2 400 s local; ≈ 10 000 s na VM, parcial: a VM foi destruída antes do timeout) | — |
| 2:6 + 5:10 | INDEFINIDO (900 s local; a rodada de 3 600 s morreu no restart do container) | — |
| 1:1 + 6:15 | INDEFINIDO (900 s local) | — |
| 1:1 + 3:6 + 3:9, 1:1 + 3:7 + 3:8 | UNSAT | 0 s |
| 1:1 + 2:3 + 4:12, 1:1 + 2:4 + 4:11, 1:1 + 2:5 + 4:10, 1:1 + 2:6 + 4:9 | UNSAT | ≤ 1 s cada |
| 1:1 + 1:1 + 5:14 | UNSAT | 1 596 s |
| 1:1 + 1:1 + 2:4 + 3:10, 1:1 + 1:1 + 1:1 + 4:13, 2:4 + 2:5 + 3:7 | UNSAT | 0 s |

Estado: OBSERVED (UNSAT sem prova conferida). Nenhum código de 16 palavras de K_7(5,3) foi
achado; as formas que ficaram indefinidas são as de bloco grande (5 ou 6 símbolos).

Depois (PR #56/#67) o ∄ 16 foi certificado por LRAT. A superior 17 deixou de ser só anunciada em
2026-10-06: o código de 17 palavras `data/codes/q7_n5_R3_M17.txt` saiu do recozimento simulado
`tools/exatos/busca_local/sa.c` (seed 12, ~14 s), tem perfil de fibras 3332222 nas cinco
coordenadas e é o teorema `CoveringK753.K_7_5_3_le_17`. No mesmo perfil, a sonda SAT
(`sonda.py`, CaDiCaL) ficou INDEFINIDA em 600 s com 1 coordenada fixada: aqui a busca local foi
mais barata que o SAT.

## 5. K_q(4,2), q = 16…20: a construção reduz tudo a g(b,4,3)

Com n = 4 o Teorema 1 dá uma classificação completa das construções por blocos:

* **3 blocos**: a partição ordenada (2,1,1) obriga cada bloco a cobrir todos os pares, ou seja,
  cada C_j é arranjo de força 2: é exatamente a partição clássica, com o defeito de v = 2 e 6
  (CAN(2,4,2) = 5, CAN(2,4,6) = 37). 4 ou mais blocos: a partição (1,1,1,1) fica descoberta.
* **2 blocos** (a, b): |S| = 1 e 3 obrigam os dois blocos a cobrir todos os triplos; um par
  coberto custa a² palavras naquele bloco. Se os dois blocos cobrem pares, |C| ≥ a² + b² ≥ q²/2.
  Senão um bloco cobre todos os pares (arranjo) e o outro só triplos:

      K_q(4,2) ≤ min_a [ CAN(2,4,a) + g(q−a, 4, 3) ],     g(b,4,3) ≥ K_b(3,1) = ⌈b²/2⌉.

g(b,4,3) é o menor código de Z_b^4 cujas quatro projeções em 3 coordenadas são códigos de raio 1.
Partir B em dois meio-blocos com arranjos dá g(b,4,3) ≤ t_1² + t_2² (t_1 + t_2 = b, sem 2 e 6),
que é a partição de novo. Valores (SAT, `blocos_sat.py --t 3`, e cotas inferiores de K_q(4,2)
exato via a = 3 ou 4):

| b | ⌈b²/2⌉ | meio-blocos | g(b,4,3) | como |
|---|---|---|---|---|
| 3 | 5 | 1+2 → 6 | **6** | SAT 6, UNSAT 5 |
| 4 | 8 | 2+2 → 10 | **10** | SAT 10, UNSAT 9; e 9 + g ≥ K_7(4,2) = 19 |
| 5 | 13 | 2+3 → 14 | **14** | SAT 14, UNSAT 13; e 9 + g ≥ K_8(4,2) = 23 |
| 6 | 18 | 3+3 → 18 | **18** | código de 18 (recozimento) e g ≥ K_6(3,1) |
| 7 | 25 | 3+4 → 25 | **25** | código de 25 (recozimento) e g ≥ K_7(3,1) |
| 10 | 50 | 5+5 → 50 | ≤ 50 | meio-blocos |
| 11 | 61 | 5+6 → 62 | 61 ou 62 | 61: INDEFINIDO (kissat sem resposta em 12 000 s, VM) |
| 12 | 72 | 5+7 → 74 | 72…74 | 73: INDEFINIDO (idem) |
| 13 | 85 | 6+7 → 86 | 85 ou 86 | 85: INDEFINIDO (idem) |

As três instâncias decisivas (g(11,4,3) ≤ 61, g(12,4,3) ≤ 73, g(13,4,3) ≤ 85: 47 700, 67 444 e
91 628 variáveis) rodaram 3 h 20 min cada na VM sem resposta. Nada se conclui delas: nem código
novo para K_16, K_17, K_18, K_20(4,2), nem inexistência.

**O que isso diz das cinco células abertas.** A construção por blocos bate a partição sse

| célula (lb–ub) | precisa de | daria |
|---|---|---|
| K_16(4,2) 86–87 | g(11,4,3) = 61 | 25 + 61 = **86 = Rodemich** (exato) |
| K_17(4,2) 97–99 | g(12,4,3) ≤ 73 | 25 + 73 = 98 |
| K_18(4,2) 109–111 | g(13,4,3) = 85 | 25 + 85 = 110 |
| K_19(4,2) 121–123 | g(12,4,3) ≤ 73 | 49 + 73 = 122 |
| K_20(4,2) 134–135 | g(13,4,3) = 85 | 49 + 85 = **134 = lb** (exato) |

Ou seja, "contornar o defeito de 6" vira uma pergunta sobre um único objeto: um código de raio 1
em cada uma das quatro projeções de Z_b^4, com b = 11, 12, 13, sem passar por um meio-bloco de 6.
O análogo para o defeito de 2 **não** se contorna: g(3), g(4), g(5) ficam exatamente em
"meio-blocos" (6, 10, 14), provado pela CNF (SAT/UNSAT acima) e, para b = 4, 5, também pelos
valores exatos de K_7(4,2) e K_8(4,2). É evidência, não prova, de que o de 6 também não se contorna.

## 6. Relação com o lema das fibras

**Perfil dos ótimos.** O código de 14 tem o perfil 2222222^6, o mais equilibrado possível
(M = 2q), e é a soma de dois blocos equilibrados. Para q ≥ 8 e M = q + 7 < 2q, pelo pombal toda
coordenada tem fibra ≤ 1; fibra 0 é excluída pelo Lema 1 com s = 0 (K_q(n−1, R−1) ≤ M, falso nas
células abaixo), então o perfil de um código de q + 7 palavras é de fibras ≥ 1 com pelo menos uma
fibra 1 por coordenada, e o Lema 1 com s = 1 leva esse código a um código **ótimo** de 14 palavras
de K_7(6,4) (para q = 8). Na construção por blocos, fibra 1 = um bloco de 1 símbolo com uma
palavra (a constante), e por isso (1, 3, 4) foi a primeira forma testada para q = 8.

**Cotas inferiores (hipótese de trabalho, não registradas).** O Lema 1 diz: código com M palavras
⇒ existe s ≤ ⌊M/q⌋ com K_{q−s}(n−1, R−1) ≤ M − s. `propaga_fibras.py` itera isso sobre o ledger:

| célula | lb no ledger | lb pelo lema | usa |
|---|---|---|---|
| K_8(7,5) | 14 | **15** | K_7(6,4) ≥ 14 (PR #56) e K_8(6,4) ≥ 15 |
| K_9(8,6) | 15 | **16** | K_8(7,5) ≥ 15 e K_9(7,5) ≥ 16 |
| K_10(9,7) | 16 | **17** | K_9(8,6) ≥ 16 e K_10(8,6) ≥ 17 |
| K_8(6,4) | 15 | **16** | só cotas publicadas: K_7(5,3) ≥ 15, K_8(5,3) ≥ 17 |
| K_9(7,5) | 16 | **17** | K_8(6,4) ≥ 16, K_9(6,4) ≥ 18 |
| K_10(8,6) | 17 | **18** | K_9(7,5) ≥ 17, K_10(7,5) ≥ 19 |
| K_13(8,6) | 25 | **26** | só cotas publicadas: K_12(7,5) ≥ 25, K_13(7,5) ≥ 29 |

Ex. K_8(7,5) com 14 palavras: 14 < 16, então alguma fibra tem s ≤ 1; s = 0 exigiria
K_8(6,4) ≤ 14 (lb 15) e s = 1 exigiria K_7(6,4) ≤ 13 (∄, PR #56). O `fib_encode.fibra_minima` do
branch das fibras confirma s_min · q > M em K_8(6,4), M = 15 e K_13(8,6), M = 25, só com o ledger.
**Ressalvas:** as três primeiras linhas dependem do ∄ 13 de K_7(6,4) (computacional, red team #62
"sobrevive com ressalva"); as quatro últimas usam só cotas do Kéri, o que é estranho para um
argumento tão curto: antes de registrar, conferir na fonte primária se o Kéri já tem esses
valores (o ledger pode estar com a cota transcrita de outra chave). Com elas, as folgas da
família K_q(q−1, q−3) caem de 2 para 1: 15–16, 16–17, 17–18, e um código de q + 7 palavras
fecharia cada uma.

## 7. O que foi tentado e não deu

* Script exploratório (não versionado, para manter o PR pequeno): blocos que são órbitas da rotação das coordenadas (mais constantes). Exaustivo
  para K_6(5,3) com ≤ 12 palavras (a ≤ 6, até 2 órbitas para a = 2): **nenhum** código, embora
  K_6(5,3) = 12 exista. A rotação é um prior errado aqui (o grupo do código de 14 não tem rotação).
* Recozimento exploratório (não versionado) com a contagem exata do Teorema 1 nas formas de blocos: lento demais na máquina compartilhada
  (≈ 6·10³ movimentos/s) e não reencontrou o de 14 em 10⁶ movimentos; a CNF acha em 1,5 s. Fica
  como avaliador exato, não como busca.
* **Erro operacional meu, registrado:** durante a sessão rodei `pkill -f "kissat -q"` para parar a
  minha fila. O padrão pega qualquer kissat com `-q` da máquina, inclusive de outros agentes. Não
  sei se matou algum. Regra que fica: parar processo pelo PID que você mesmo guardou, nunca por
  padrão de nome em máquina compartilhada.

## 8. Como reproduzir

    cd tools/exatos/familia
    cc -O2 -std=c99 -o cobre_n2 cobre_n2.c
    python3 blocos_sat.py gerar 7 6 3:6 4:8 --cnf k764.cnf          # 3519 variáveis, 26 293 cláusulas
    kissat -q k764.cnf > k764.out; python3 blocos_sat.py decodificar k764.cnf.mapa.json k764.out > k764.txt
    ./cobre_n2 7 6 k764.txt                                          # uncovered=0
    python3 blocos_sat.py gerar 0 4 5:13 --t 3 --cnf g5.cnf          # g(5,4,3) > 13: UNSAT
    python3 propaga_fibras.py 7,6,4=14 7,5,3=16

Testes: `python3 -m pytest -q -p no:cacheprovider tests/test_familia_blocos.py`.
