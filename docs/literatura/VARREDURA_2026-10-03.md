# Varredura de literatura: códigos de cobertura (2026-10-03)

Acervo montado por `tools/literatura/varredura.py` e guardado em
`gs://factory-literatura-matematica` (layout no `README.md` do bucket e em
`tools/literatura/README.md`). Nada foi pago e nada foi publicado fora do bucket e deste PR.

Duas perguntas:

- **A. Estado da arte.** Alguém já publicou cota igual ou menor que as nossas nas oito
  células? Quais são as cotas inferiores conhecidas?
- **B. Técnicas.** O que, na literatura, pode acelerar nosso trabalho?

## Resposta curta

- **Nenhuma das quatro cotas novas foi igualada ou batida por nada que esta varredura
  achou.** As menores cotas publicadas seguem sendo **1475** para K_7(9,4) (Marosi, arXiv,
  set. 2026) e as das tabelas de Kéri (última revisão em 2011-11-21) para as outras sete
  células: **175**, **3125**, **6517**, **8575**, **42189**, **125** e **175**.
- O site de Kéri está no ar e é idêntico às últimas capturas do Wayback Machine (2017 a
  2024, sha256 igual). As tabelas não mudaram desde 2011.
- Desde 2011, só três fontes mexeram nessas células, e só em cota inferior ou em K_7(9,4):
  Gijswijt–Polak 2025 (K_5(11,4) ≥ 546), Marosi 2026 (K_7(9,4) ≤ 1475 e K_7(9,3) ≥ 2143) e
  a compilação pós-Kéri do Florath, que só repete essas.
- No texto completo de 541 PDFs e de 396 resenhas do zbMATH, as oito células só aparecem em
  quatro fontes: as tabelas de Kéri (versão atual e capturas de 2004 a 2020),
  Haas–Halupczok–Schlage-Puchta 2009 (que repete as UB de Kéri), a tese de Gijswijt (2005,
  repete 3125) e Marosi 2026. **Nenhuma menção traz valor abaixo dos nossos.**
- As cotas superiores das sete células que não são K_7(9,4) **não mudaram desde 2004**. A
  captura de 2004-10-18 das tabelas de Kéri já trazia 175, 3125, 6517, 8575, 42189, 125 e
  175 (ver abaixo).
- Uma sonda rápida de códigos lineares feita aqui achou, para K_5(10,5), uma base [10,3]_5
  com só 8 síndromes órfãs. Base mais remendo guloso deu **K_5(10,5) ≤ 170**, verificado no
  espaço inteiro. É abaixo dos 175 publicados e acima dos nossos 162. Vale como base para o
  remendo por ILP (seção "Sonda").
- **Rodada 2 (OpenAlex com chave, mesmo dia):** nível 1 completo de citações, nível 2 com
  corte e 22 buscas em texto completo. +154 obras (1949 → 2103), +39 PDFs (543 → 582).
  **Nada mudou no estado da arte**: nenhuma cota publicada ≤ 1134, ≤ 162, ≤ 2875 ou ≤ 5616,
  e nenhuma abaixo das cotas da tabela acima. Detalhes e limites (o texto completo do
  OpenAlex não acha números dentro de tabelas) na seção "Rodada 2".

## A. Estado da arte por célula

Fontes primárias, todas no bucket:

- **Kéri**: `tabelas/keri/4-5_tables.pdf` (q = 4, 5; sha256 no `tabelas/MANIFESTO.json`) e
  `tabelas/keri/6-21_tables.pdf` (q ≥ 6), de `https://old.sztaki.hu/~keri/codes/`. O índice
  (`index.htm`) lista a última atualização em **2011.11.21**. Cada linha da tabela é
  `n  chaveLB  LB–UB  chaveUB` para R = 1, 2, 3 (primeiro bloco) e R = 4 … 8 (segundo
  bloco). Os trechos abaixo são cópia literal do texto extraído com `pypdf` (o PDF tem
  espaçamento que o extrator às vezes cola).
- **Gijswijt–Polak**, *Semidefinite lower bounds for covering codes*, arXiv:2504.01932v2
  (IEEE Trans. Inf. Theory, DOI 10.1109/TIT.2026.3706793).
- **Marosi**, *New upper and lower bounds on covering codes K_q(n,R) for alphabets of size
  5 ≤ q ≤ 21*, arXiv:2608.19872v3 (2026-09-02, versão atual; a API do arXiv em 2026-10-03
  devolve v3 como última).

Chaves de Kéri usadas abaixo (texto literal das legendas):

- q = 4, 5, cota superior: `d (Bhandari–Durairajan, 1996)`. Cota inferior: `m
  (Haas–Halupczok–Schlage-Puchta, 2009)`, `y improved sphere-covering bound`.
- q ≥ 6, cota superior: `f direct sum`, `o ( ¨Osterg ˚ ard, 1999)`. Cota inferior: `m
  (Haas–Halupczok–Schlage-Puchta, 2009)`, `y improved sphere-covering bound`.

| célula | nossa | menor UB publicada | fonte da UB | maior LB publicada | fonte da LB | esfera |
|---|---|---|---|---|---|---|
| K_7(9,4) | **1134** | **1475** | Marosi 2026, Tabela 1 (antes: 1843, Kéri `f`) | 264 | Haas–Halupczok–Schlage-Puchta 2009 (`m`) | 221 |
| K_5(10,5) | **162** | **175** | Bhandari–Durairajan 1996 (`d`) | 41 | Haas–Halupczok–Schlage-Puchta 2009 (`m`) | 31 |
| K_5(11,4) | **2875** | **3125** | Bhandari–Durairajan 1996 (`d`) | 546 | Gijswijt–Polak 2025, Tabela 3 (antes: 535, Kéri `y`) | 509 |
| K_7(10,4) | **5616** | **6517** | soma direta (`f`) | 1007 | esfera melhorada (`y`) | 943 |
| K_7(9,3) | — | 8575 | soma direta (`f`) | 2143 | Marosi 2026, Tabela 2 (antes: 2077, `y`) | 2070 |
| K_7(10,3) | — | 42189 | soma direta (`f`) | 10577 | esfera melhorada (`y`) | 10235 |
| K_5(11,6) | — | 125 | Bhandari–Durairajan 1996 (`d`) | 29 | Haas–Halupczok–Schlage-Puchta 2009 (`m`) | 20 |
| K_7(10,6) | — | 175 | Östergård 1999 (`o`) | 39 | Haas–Halupczok–Schlage-Puchta 2009 (`m`) | 24 |

A coluna "esfera" é a cota de esfera ⌈q^n / V_q(n,R)⌉, conferida contra `ledger/cells.json`.

### Trechos literais

**Kéri, `6-21_tables.pdf`, bloco "Bounds on K7(n, R)":**

```
n R = 1 R = 2 R = 3
9 u 733726–823543 e s 29889–94587 f y 2077–8575 f
10 u 4630843–5764801 e x 168042–420175 q y 10577–42189 f
n R = 4 R = 5 R = 6 R = 7 R = 8
9 m 264–1843 f m 52–323 f m 17–37 n 715 7
10 y 1007–6517 f m 160–1225 f m 39–175 o k 15–33 z 7
```

Daí: K_7(9,3) = 2077–8575 `f`; K_7(10,3) = 10577–42189 `f`; K_7(9,4) = 264–1843 `f`;
K_7(10,4) = 1007–6517 `f`; K_7(10,6) = 39–175 `o`.

**Kéri, `4-5_tables.pdf`, bloco "Bounds on K5(n, R)":**

```
n R = 4 R = 5 R = 6 R = 7 R = 8
10 y 162–875 d m 41–175 d m 16–45 d k 9 y 5
11 y 535–3125 d m 103–625 d m 29–125 d m 12–25 d 51
```

Daí: K_5(10,5) = 41–175 `d`; K_5(11,4) = 535–3125 `d`; K_5(11,6) = 29–125 `d`.
(K_5(10,4) = 162–875 `d`: nosso ledger já tem K_5(10,4) ≤ 625 provado no Lean.)

**Gijswijt–Polak, arXiv:2504.01932v2, Tabela 3 ("New lower bounds on K4(n, R) and
K5(n, R)"; colunas q, n, R, LB anterior, LB nova, UB conhecida):**

```
5 11 4 535 546 3125
```

Na Tabela 9 do mesmo artigo (valores do SDP antes do arredondamento), q = 5: n = 10, R = 5
dá `37.81` e n = 11, R = 6 dá `25.20`. Os dois ficam abaixo de 41 e de 29, que são de
Haas–Halupczok–Schlage-Puchta: **o SDP não melhora K_5(10,5) nem K_5(11,6)**.

**Marosi, arXiv:2608.19872v3, Tabela 1 (cotas superiores; colunas: célula, cotas
anteriores, esfera, UB nova, Δ, Δ%, chave anterior, método):**

```
K5(11,5) 103–625 86602−23 3.7%dL
K7(9,4) 264–1843 2211475−368 20.0%fL
```

(o extrator cola as colunas: `221 1475 −368`). Tabela 2 (cotas inferiores; colunas:
célula, esfera, LB anterior, LB nova):

```
K7(9,3) 2070 2077 (y)2143
```

Seção 6.4 do mesmo artigo: *"On the cells attempted whose previous bound is due to [6] (key
m, between 11% and 67% above the sphere-covering bound), the certified value is at most the
tabulated one."* Ou seja, o SDP do Marosi não sobe as cotas `m`, e K_7(9,4) ≥ 264 fica.
Nos certificados públicos dele (`tabelas/coldcase_lb_master.json`), K_7(9,4) dá 241 e
K_7(10,4) dá 985, os dois abaixo do tabelado.

As 26 cotas superiores da Tabela 1 do Marosi (`tabelas/coldcase_final_records.json`) não
incluem nenhuma das nossas células além de K_7(9,4). A única de q = 5 é K_5(11,5) ≤ 602.

**Kéri, captura do Wayback de 2004-10-18** (`tabelas/keri_wayback/20041018025843_codes_4-5_tables.pdf`
e `20041018023838_codes_6-21_tables.pdf`; as chaves eram outras):

```
10 y 162–720 d y 34–175 d f 10–45 d q 8–10 m 5
11 a 509–3125 d a 86–625 d a 20–125 d 8–25 d 5
9 u 733726–823543 e x 29871–94587 f y 2077–8575 f
10 u 4630843–5764801 e x 168042–545505 f y 10577–42189 f
9 x 224–1843 f y 36–343 c c 13–37 n 7 7
10 y 1007–6517 f a 126–1225 f y 26–175 o v 13–37 c 7 1
```

Ou seja, em 2004 as UB já eram 175, 3125, 8575, 42189, 1843, 6517 e 175 (e 125 para
K_5(11,6)). Só as cotas inferiores mudaram depois disso.

### O que as nossas cotas implicam pelas regras de Kéri (conta feita aqui)

- `c`: K_q(n+1,R+1) ≤ K_q(n,R). Dá K_7(10,5) ≤ 1134 (publicado: 980, Marosi) e
  K_5(11,6) ≤ 162 (publicado: 125). Nada novo.
- `e`: K_q(n+1,R) ≤ q·K_q(n,R). Dá K_7(10,4) ≤ 7938 (temos 5616) e K_5(12,4) ≤ 14375
  e K_7(11,4) ≤ 39312, fora do alcance das tabelas (q = 5 vai até n = 11; q = 7, até n = 10).
- Soma direta com códigos triviais não melhora nada nas tabelas.

### O que foi buscado para dizer "não achei"

- **Texto completo** de 541 PDFs de acesso aberto (de 543 baixados, 2 sem texto) e 396
  resenhas do zbMATH (outras 296 vêm vazias, "contents unavailable due to conflicting
  licenses"),
  procurando `K7(9,4)`, `K_7(9,4)`, `K_{7}(9,4)`, `K 7 (9, 4)`, `K(9,4)` com q = 7 no
  contexto, e o mesmo para as outras sete células, além dos números 1475, 1743, 1843, 175,
  3125, 6517, 8575 e 42189 a até 250 caracteres de "cover" e dos parâmetros n e R.
  Resultado em `buscas/2026-10-03/mencoes.jsonl` (55 achados). Fora as tabelas de Kéri, os
  achados que citam a célula pelo nome são:
  - Haas–Halupczok–Schlage-Puchta 2009 (EJC 16, #R133), Tabela 5 (q = 7; colunas: célula,
    k, esfera, LB antiga, LB nova, UB): `K7(9, 4) 5 221 227 264 1843` e
    `K7(10, 6) 4 24 27 39 175`. Tabela 3 (q = 5): `K5(10, 5) 5 31 34 41 175` e
    `K5(11, 6) 5 20 21 29 125`.
  - Gijswijt, tese de doutorado (2005; arXiv:1007.0906), Tabela 5.2 ("New lower bounds on
    K5(n,R)"): linha `11 4 3125 510 509 509`, com 3125 como melhor UB conhecida.
  - Marosi 2026: as linhas já citadas acima.
  - Os demais achados são números soltos (1743 numa página de referência, 175 numa
    bibliografia) sem relação com covering codes.
  - K_7(10,3) não aparece em nenhum texto além das tabelas de Kéri.
- **Metadados**: 1949 obras (OpenAlex, Crossref, arXiv, zbMATH Open, dump de
  metadados do arXiv), mais a expansão de um nível por citações (OpenCitations).
- **Tabelas**: diretório inteiro de Kéri, 2048 capturas do Wayback, tabelas pós-Kéri do
  Florath (`florath_post_keri_non_mixed.csv`, que para estas oito células só traz a LB 546
  de Gijswijt–Polak) e do coldcase.

## B. Técnicas: as que importam para nós

Ordem: primeiro o que muda a próxima rodada de busca, depois cotas inferiores e
formalização. "Ideia" é o experimento concreto que sai do artigo. **Só 12 destes têm PDF
aberto no acervo** (lista em "Cobertura"). Para os outros, o comentário se apoia no resumo e
na resenha do zbMATH, não no texto completo. DOI ou arXiv entre
parênteses; os registros estão em `meta/works.jsonl`.

### Construção e busca (cota superior)

1. **Marosi 2026**, *New upper and lower bounds on covering codes…* (arXiv:2608.19872).
   Busca local focada e LNS em que cada avaliação é uma contagem exata de cobertura no espaço
   inteiro, feita por uma transformada coordenada a coordenada. O código está em
   `github.com/Mapika/coldcase`. **Ideia:** rodar o `covengine` dele partindo dos nossos
   códigos (1134, 162, 2875, 5616) e, no sentido inverso, usar a transformada dele como
   avaliador do nosso remendo. É o concorrente direto e o código é público.
2. **Bhandari–Durairajan 1996**, *A note on bounds for q-ary covering codes*
   (10.1109/18.532916). É a origem de 175, 3125 e 125 (chave `d`), por códigos fortemente
   seminormais sobre Z_5. **Ideia:** batemos duas cotas `d` e já temos K_5(10,4) ≤ 625
   contra 875 `d`. As outras células `d` de q = 5 (lidas da `4-5_tables`) são o alvo mais barato:
   K_5(8,3) ≤ 325, K_5(9,3) ≤ 1275, K_5(8,4) ≤ 65, K_5(9,4) ≤ 255, K_5(9,5) ≤ 55,
   K_5(10,6) ≤ 45, K_5(11,5) ≤ 625 (já 602 pelo Marosi) e K_5(11,7) ≤ 25, além de
   K_5(11,6) ≤ 125, que já tentamos. Mesma base de classes laterais e mesmo remendo.
3. **Östergård 1991**, *Upper bounds for q-ary covering codes* (10.1109/18.79926).
   Seminormalidade e as construções que propagam um código seminormal para (n+1, R) e
   (n+2, R+1); tabelas para q = 3, 4, 5. **Ideia:** testar se os nossos 162 e 2875 são
   (fortemente) seminormais. Se forem, as mesmas construções do artigo dão cotas em células
   vizinhas sem busca nenhuma.
4. **Östergård–Weakley 1999**, *Constructing covering codes with given automorphisms*
   (10.1023/A:1008326409439). Tabu search restrita a códigos com um grupo de automorfismos
   prescrito, que não precisa ser o grupo todo (K(13,1) ≤ 704). **Ideia:** é a
   generalização da nossa invariância por translação ao longo de uma reta. Testar grupos
   maiores: translação por um subespaço de dimensão 2, translação × permutação cíclica das
   coordenadas, ou o estabilizador da base de classes laterais. O ILP encolhe por |G| e a
   verificação continua por BFS.
5. **Blokhuis–Lam 1984**, *More coverings by rook domains* (10.1016/0097-3165(84)90010-4).
   O "matrix method": C = {x : Mx ∈ S}. **Ideia:** é exatamente a nossa base de classes
   laterais (S = conjunto de síndromes). O artigo e o seguimento do Östergård 1991 mostram
   como escolher M para que S seja pequeno. A busca do remendo pode rodar no espaço de
   síndromes F_q^r, com q^(n−r) vezes menos estados, sempre que o remendo também for união
   de classes laterais.
6. **Östergård 1997**, *Constructing covering codes by tabu search* (J. Combin. Des. 5,
   10.1002/(SICI)1520-6610(1997)5:1<71::AID-JCD7>3.0.CO;2-E) e **Davies–Royle 1997**,
   *Graph domination, tabu search and the football pool problem*
   (10.1016/S0166-218X(96)00049-2). A vizinhança padrão é: escolha uma palavra descoberta e
   mova um codeword que a cubra com uma troca de coordenada; com lista tabu. **Ideia:**
   trocar o SA do remendo por tabu com essa vizinhança e medir lado a lado (mesmo tempo,
   mesma base).
7. **Kéri–Östergård 2005**, *Bounds for covering codes over large alphabets*
   (10.1007/s10623-004-3804-8). Origem das chaves `n` de q ≥ 6. **Ideia:** ler as
   construções para q = 7 e conferir se alguma vira base melhor que a soma direta das
   células `f` (K_7(10,4), K_7(9,3) e K_7(10,3) ainda são somas diretas).
8. **Graham–Sloane 1985**, *On the covering radius of codes* (10.1109/TIT.1985.1057039), e
   **Honkala 1994**, *On the normality of multiple covering codes*
   (10.1016/0012-365X(94)90164-3). Soma direta amalgamada (ADS) e normalidade. **Ideia:**
   as três células `f` de q = 7 vêm de soma direta. Com as cotas novas (nossas e do Marosi)
   nos componentes, refazer o fecho das regras de Kéri (`c`, `e`, `f`, `j`, ADS) e ver se
   alguma célula cai. O Marosi relata que o fecho das cotas dele não deu nada novo; o fecho
   com as nossas ainda não foi feito.
9. **Caprara–Fischetti–Toth 1999**, *A heuristic method for the set covering problem*
   (10.1287/opre.47.5.730). Heurística lagrangiana para set cover com milhões de linhas.
   **Ideia:** o remendo é um set cover. A relaxação lagrangiana dá, ao mesmo tempo, uma cota
   inferior para o tamanho do remendo (diz quando parar de buscar) e soluções primais
   melhores que gulosas.
10. **Linderoth–Margot–Thain 2009**, *Improving bounds on the football pool problem by
    integer programming and high-throughput computing* (10.1287/ijoc.1090.0334). ILP com
    branching orbital para K_3(6,1). **Ideia:** é o molde para o nosso ILP com simetria:
    tratar o remendo como ILP sobre órbitas e podar ramos isomorfos.
11. **Ostrowski–Linderoth–Rossi–Smriglio 2011**, *Orbital branching*
    (10.1007/s10107-009-0273-x), e **Margot 2003**, *Exploiting orbits in symmetric ILP*
    (10.1007/s10107-003-0394-6). Corte de simetria dentro do branch-and-bound. **Ideia:**
    quando o ILP do remendo herda o grupo da base, ramificar em órbitas em vez de variáveis.
12. **Margot 2009**, *Symmetry in integer linear programming* (10.1007/978-3-540-68279-0_17).
    Panorama de orbitopes, isomorphism pruning e orbital fixing. É o mapa para escolher
    entre os três acima.
13. **Kaibel–Pfetsch 2008**, *Packing and partitioning orbitopes* (10.1007/s10107-006-0081-5).
    Só vale se a formulação tiver colunas intercambiáveis (atribuição). No set cover puro do
    remendo não tem; fica como referência.
14. **McKay 1998**, *Isomorph-free exhaustive generation* (10.1006/jagm.1997.0898), e
    **Kaski–Östergård 2006**, *Classification Algorithms for Codes and Designs*
    (10.1007/3-540-28991-7). Aumento canônico. **Ideia:** a varredura das 7737 classes de
    [9,3]_7 já fez isso. O próximo passo é aplicar a mesma enumeração a bases com t ≠ 3
    classes laterais e a [10,4]_7 e [11,5]_5.

15. **Östergård–Weakley 2018**, *Switching of covering codes* (Discrete Math. 341,
    1778–1788; achado na bibliografia do Lobstein, ref. [812]). Troca local de um pedaço do
    código por outro que cobre o mesmo conjunto. **Ideia:** é um movimento de vizinhança
    grande para o remendo (trocar um bloco inteiro de palavras de uma vez) e uma forma de
    gerar códigos não equivalentes do mesmo tamanho a partir dos nossos.

### Códigos lineares e conjuntos saturantes (a base)

16. **Davydov 1995**, *Constructions and families of covering codes and saturated sets of
    points in projective geometry* (10.1109/18.476339). Construções q^m-concatenadas e
    famílias infinitas de códigos lineares com raio R. **Ideia:** um código linear
    [n, n−r]_q com raio R dá K_q(n,R) ≤ q^(n−r), e um conjunto R-saturante de n pontos em
    PG(r−1,q) é a mesma coisa. A sonda feita aqui (seção "Sonda") achou para K_5(10,5)
    uma base [10,3]_5 com 8 síndromes órfãs.
17. **Davydov–Giulietti–Marcugini–Pambianco 2011**, *Linear nonbinary covering codes and
    saturating sets in projective spaces* (10.3934/amc.2011.5.119). Tabelas e cotas da
    função comprimento ℓ_q(r,R). **Ideia:** conferir, para q = 5 e 7 e r = 5 a 8, que
    ℓ_q(r,R) é conhecido. Isso diz de antemão se uma base linear de um único coset existe.
18. **Giulietti 2013**, *The geometry of covering codes: small complete caps and saturating
    sets in Galois spaces* (Surveys in Combinatorics, 10.1017/CBO9781139506748.003).
    Panorama do lado geométrico.
19. **Davydov–Östergård 2001**, *Linear codes with covering radius R = 2, 3 and codimension
    tR* (10.1109/18.904551), e **Bartoli–Davydov–Giulietti–Marcugini–Pambianco 2019**,
    *New bounds for linear codes of covering radii 2 and 3* (10.1007/s12095-018-0335-0).
    A nota de Kéri de 2009-09-16 diz, literalmente: "K5(10,3)<=3125, from a
    2-saturating set in PG(4,5)".
    **Ideia:** para R = 3 (K_7(9,3), K_7(10,3)), procurar 3-saturantes em PG(4,7) e
    PG(5,7) como base.
20. **Héger–Nagy 2021**, *Short minimal codes and covering codes via strong blocking sets in
    projective spaces* (10.1109/TIT.2021.3123730). Conjuntos ρ-saturantes para ρ grande via
    blocking sets fortes. **Ideia:** é a família que mira raio alto (R = 4 a 6, os nossos).
    Dá candidatos de base para K_5(10,5) e K_5(11,6).
21. **Denaux 2021**, *Constructing saturating sets in projective spaces using subgeometries*
    (10.1007/s10623-021-00951-y), e **Nagy 2018**, *Saturating sets in projective planes and
    hypergraph covers* (10.1016/j.disc.2018.01.011). As construções usam q quadrado ou q
    grande; para q = 5 e 7 a utilidade é baixa. Ficam como referência.

### Cotas inferiores

22. **Gijswijt–Polak 2025**, *Semidefinite lower bounds for covering codes*
    (arXiv:2504.01932). SDP com redução de simetria e certificados racionais. Dá K_5(11,4) ≥ 546.
23. **Haas–Halupczok–Schlage-Puchta 2009**, *Lower bounds for q-ary codes with large
    covering radius* (EJC, 10.37236/222). Matrizes de partição e um jogo. É a fonte de
    264, 41, 29 e 39 (chave `m`). **Ideia:** o intervalo publicado nessas células é largo
    (264 contra 1134); nada no horizonte fecha esse buraco, então o critério de parada da
    busca não pode ser "atingir a LB".
24. **van Wee 1988**, *Improved sphere bounds on the covering radius of codes*
    (10.1109/18.2632), e **van Wee 1991**, *Bounds on packings and coverings by spheres in
    q-ary and mixed Hamming spaces* (10.1016/0097-3165(91)90010-E). Contagem de excesso: a
    chave `y` de K_7(10,4), K_7(9,3) e K_7(10,3).
25. **Honkala 1991**, *Modified bounds for covering codes* (10.1109/18.75253), e **Hou 1990**,
    *New lower bounds for covering codes* (10.1109/18.53754). Refinamentos da contagem de
    excesso.

### Panoramas, tabelas e formalização

26. **Cohen–Honkala–Litsyn–Lobstein 1997**, *Covering Codes* (North-Holland). O livro de
    referência, com as tabelas que Kéri estendeu.
27. **Cohen–Litsyn–Lobstein–Mattson 1997**, *Covering radius 1985–1994*
    (10.1007/s002000050061), e **Cohen–Karpovsky–Mattson 1985**, *Covering radius —
    survey and recent results* (10.1109/TIT.1985.1057043).
28. **Bertolo–Östergård–Weakley 2004**, *An updated table of binary/ternary mixed covering
    codes* (10.1002/jcd.20008). Método de matriz e tabu aplicados a códigos mistos, com
    detalhe de implementação reaproveitável.
29. **Kéri–Östergård 2006**, *Further results on the covering radius of small codes*
    (10.1016/j.disc.2006.04.038). Técnicas para provar K exato com computador.
30. **Florath 2026**, *Formal Foundations and Proof-Carrying Certificates for q-ary Covering
    Codes in Lean 4* (arXiv:2606.09600). **Ideia:** é o vizinho direto dos nossos
    certificados por síndromes no kernel do Lean. Vale comparar formato e custo e,
    possivelmente, propor as nossas quatro cotas ao banco dele.
31. **Hämäläinen–Honkala–Litsyn–Östergård 1995**, *Football pools — a game for
    mathematicians* (10.2307/2974552). Introdução curta, boa para explicar o problema a quem
    chega.

## Sonda de bases lineares (feita nesta varredura)

Pergunta: existe um código **linear** [n, n−r]_q com raio ≤ R? Se existir, K_q(n,R) ≤
q^(n−r), e é uma base de uma classe lateral só. Método: busca local em matrizes de
verificação H = [I_r | A], 300 s por caso (`sonda/linear_probe.py` no bucket), com objetivo
igual ao número de síndromes a distância > R no grafo de Cayley de F_q^r gerado por
{a·h_i}. É heurística: "não achou" não prova que não existe.

| célula | código linear testado | tamanho se existir | menor nº de síndromes órfãs achado | de |
|---|---|---|---|---|
| K_5(10,5) | [10,3]_5, r = 7 | 125 | **8** | 78 125 |
| K_7(10,4) | [10,4]_7, r = 6 | 2401 | 2316 | 117 649 |
| K_7(10,3) | [10,5]_7, r = 5 | 16 807 | 1542 | 16 807 |
| K_7(9,3) | [9,4]_7, r = 5 | 2401 | 3030 | 16 807 |
| K_5(11,4) | [11,4]_5, r = 7 | 625 | 14 288 | 78 125 |
| K_7(10,6) | [10,2]_7, r = 8 | 49 | 172 512 | 5 764 801 |

(K_7(9,4) com [9,3]_7 já foi varrido de forma exaustiva em `audit/k794-base-sweep`.)

**O caso que vale seguir é K_5(10,5).** Duas sementes independentes de 900 s pararam em 8
órfãs, com H diferentes (`sonda/melhor_5_10_5_s11.json` e `_s12.json`). As 8 classes
órfãs somam 1000 palavras. Um remendo guloso ingênuo (`sonda/remendo_guloso.py`: candidatos
aleatórios perto das descobertas, escolhe o que cobre mais) fechou com 45 palavras:

```
{"q": 5, "n": 10, "R": 5, "M": 170, "base": 125, "remendo": 45, "descobertas": 0}
```

O script verifica por dilatação de Hamming no espaço inteiro (5^10 palavras, 0
descobertas). Conferi também com o verificador oficial do repositório:

```
$ tools/verify/verify q5_n10_R5_M170.txt
Q=5 n=10 R=5 M=170 points=9765625 uncovered=0 sha256=1aa2e30763fc8c37310e24e174352784d939b4fd1e6e19bfb03e51a902b69cb3
```

O código está em `sonda/K5_10_5_guloso.txt` no bucket. **Isso dá K_5(10,5) ≤ 170, abaixo
dos 175 publicados**, mas acima dos nossos 162, então não entra no ledger. A poda gulosa
(`sonda/podar.py`) não achou nenhuma palavra redundante. Nada disso passou pelo
certificador do Lean.

O melhor candidato do guloso cobria 45 das 1000 palavras, então o remendo ótimo tem pelo
menos ⌈1000/45⌉ = 23 palavras, se 45 for mesmo o máximo (não foi provado). O guloso gastou
45, e a cauda dele é ruim: as últimas 15 palavras cobriram ≤ 7 cada. **Ideia:** dar esta
base ao remendo por ILP ou SA que vocês já têm. Um remendo de ≤ 36 palavras bate os 162.

## Cobertura e o que ficou de fora

| item | número |
|---|---|
| obras em `meta/works.jsonl` | 1949 |
| por fonte (com sobreposição) | OpenAlex 986, Crossref 903, zbMATH 722, arXiv API 358, dump do arXiv 131 |
| com DOI / com arXiv | 1553 / 451 |
| obras com score ≥ 6 | 1165 |
| sementes resolvidas | 50 de 52 (não resolvidas: *The covering radius of codes and normality*, *Nonbinary codes with covering radius one*) |
| expansão por citação | 1 nível, 701 obras-semente, +96 obras (OpenCitations + Crossref) |
| PDFs baixados | 543 (cerca de 400 do arXiv, o resto de links OA via Unpaywall e Crossref); 541 com texto |
| obras sem PDF | 843 sem link OA, 388 com link que falhou (paywall, HTML ou 403) |
| obras relevantes (score ≥ 6) sem PDF | 738, em `relatorios/nao_acessiveis_2026-10-03.json` |
| resenhas do zbMATH | 692 (396 com texto; 296 vêm "contents unavailable due to conflicting licenses") |
| tabelas | 82 arquivos no `tabelas/MANIFESTO.json`: Kéri inteiro, 2048 capturas listadas no CDX do Wayback, Lobstein, coldcase, Florath |
| tamanho local | ~440 MB com o cache (o cache não vai para o bucket) |

**O que não foi acessível, e por quê:**

- **Os clássicos de técnica estão quase todos atrás de paywall.** Das 50 obras-semente,
  só 12 têm PDF aberto (Marosi, Gijswijt–Polak, Florath, Haas–Halupczok–Schlage-Puchta,
  Davydov–Giulietti–Marcugini–Pambianco 2011, Héger–Nagy, Denaux, Nagy 2018, Bonini–Borello–
  Byrne, Gordon–Kuperberg–Patashnik, Knuth, Borodachov et al.). Ficaram sem PDF, entre
  outros: Bhandari–Durairajan 1996, Östergård 1991 e 1997, Östergård–Weakley 1999,
  Kéri–Östergård 2005 e 2006, Davydov 1995, Davies–Royle 1997, Blokhuis–Lam 1984, Graham–Sloane
  1985, Linderoth–Margot–Thain 2009, a família do branching orbital e o livro de 1997.
  Para esses, o relatório usa resumo e resenha (zbMATH ou Crossref) e o que se sabe da
  área. **Os comentários "Ideia" dos itens sem PDF não vêm de leitura do texto completo.**
- **OpenAlex sem orçamento.** Desde 2026, sem chave o OpenAlex dá US$ 0,10 por dia por IP,
  e uma busca custa 10 créditos. As sementes e as 10 primeiras consultas esgotaram o dia
  (429, "Insufficient budget", volta à meia-noite UTC). O script detecta isso e passa para
  Crossref, OpenCitations e Unpaywall. A chave é gratuita, mas exige cadastro: **é decisão
  do Thiago** criar uma e pôr no cofre. O script lê `OPENALEX_API_KEY`. Com ela dá para
  rodar o nível 2 da expansão e os citantes pelo OpenAlex, que cobre mais que o
  OpenCitations. Na rodada 2 isso foi feito pelo conector MCP, sem chave na máquina.
- **Semantic Scholar** (429 sem chave) e **Google Scholar** (proibido) não foram usados.
- **zbMATH**: a busca por MSC `cc:94B75` devolve 505 documentos (o total que a API informa).
- A bibliografia do Lobstein (*Covering radius*, 1058 referências, janeiro de 2023) foi lida
  por entradas de 2012 em diante. Nenhuma trata de cotas de K_q(n,R) para q = 5 ou 7. Dela
  saiu Östergård–Weakley 2018 (item 15 acima).
- O nível 2 de citações não rodou. Com OpenCitations o rendimento já era baixo (96 obras
  novas para 701 sementes), e sem o OpenAlex o custo não compensava. **Resolvido na rodada 2** (seção abaixo), pelo conector do OpenAlex.

## Rodada 2 — OpenAlex com chave

O conector MCP do OpenAlex (chave pessoal do Thiago) passou a existir na sessão do agente,
não na factory-01. Divisão usada: o agente lista ids pelo conector (o que gasta orçamento);
a factory-01 completa cada obra pelo GET de obra única, que é grátis (medido:
`x-ratelimit-credits-used: 0` com o orçamento do dia zerado), pelo modo novo
`varredura.py --de-jsonl`. As listas de ids e o log das consultas estão em
`tools/literatura/openalex/2026-10-03/` e em `gs://factory-literatura-matematica/buscas/2026-10-03-openalex/`.
Nada foi escrito no OpenAlex (nenhuma curadoria).

### Contagens, antes e depois

| item | rodada 1 | rodada 2 |
|---|---|---|
| obras em `meta/works.jsonl` | 1949 | **2103** (+154) |
| com fonte OpenAlex | 986 | 1226 |
| PDFs | 543 | **582** (+39; 37 de obras novas) |
| textos (PDF, resenha, tabela) lidos pelo caçador de menções | — | 1314 |

De onde vieram as 154 obras novas (`buscas/2026-10-03-openalex/obras_novas.json`):

| origem | consulta no conector | ids listados | entraram no corte | novas |
|---|---|---|---|---|
| nível 1, quem cita | `works where it cites (41 sementes de cobertura)`, 15 páginas, mais as sementes de técnica (ILP com simetria, set cover, isomorfismo) com filtro de tópico | 797 (712 + 86, sem repetir) | 478 | 84 |
| nível 1, referências | `referenced_works` das 51 sementes com id OpenAlex | 1364 | 254 | 32 |
| nível 2, quem cita | 105 candidatas do nível 1, filtro de tópico | 233 (de 1407 sem filtro) | 131 | 27 |
| texto completo | 22 consultas (tabela abaixo) | 28 | 28 | 8 |
| técnicas 2015–2026 | 6 consultas por título/resumo | 18 | 18 | 3 |

Corte de relevância (`decide_inclusao`): score de resumo ≥ 4, ou citar ≥ 2 sementes, ou
achado de texto completo. Rejeitadas: 550 referências, 318 citantes de nível 1, 102 de
nível 2 (lista em cada `de_jsonl_*.json`). 55 referências das sementes não existem mais no
OpenAlex (404: ids fundidos ou apagados).

**Decisões de corte, tomadas sozinho:**

- Sementes de técnica genérica (Dancing links, Caprara–Fischetti–Toth, Margot, McKay,
  orbitopes etc.) têm milhares de citantes de pesquisa operacional. Listei só os que dizem
  covering code/radius, football pool, saturating set, covering design, unicost,
  Hamming, orbital branching, orbitope ou symmetry breaking no título/resumo (185), e
  paginei as 2 primeiras páginas por citação (86 ids).
- Nível 2: "relevante" = obra nova de nível 1 com score ≥ 6 ou que cita ≥ 2 sementes
  (105). Os citantes delas sem filtro somam 1407, quase todos fora do tema (PIR,
  escalonamento, Petri). Com o mesmo filtro de tópico ficaram 233. O orçamento de ~1500
  obras novas não foi atingido (+154).
- Busca por número no texto completo: com 121 resultados para
  `(175 OR 162 OR 125) AND quinary…`, li as 50 primeiras (reordenadas por relevância) e
  parei: depois da 25ª já era só ruído.

### Texto completo: o que o índice do OpenAlex cobre e o que não cobre

Medido antes de interpretar qualquer "zero":

- **Só obras de acesso aberto têm o corpo indexado.** Das 41 sementes de cobertura, 13 têm
  `has_fulltext` (todas abertas: Marosi, Florath, Haas–Halupczok–Schlage-Puchta,
  Davydov–Giulietti–Marcugini–Pambianco 2011, Kéri–Östergård 2006, van Wee 1991 (artigo e
  tese), Héger–Nagy, Denaux, Nagy, Bonini–Borello–Byrne, Habsieger 1997,
  Torres-Jiménez). Dos 712 citantes, 193. **Nenhum dos clássicos pagos (Bhandari–Durairajan,
  Östergård 1991/1997, Kéri–Östergård 2005…) está no índice de texto completo.** A
  promessa de "cobrir o que está atrás de paywall" não se cumpriu para esta área.
- **Números dentro de tabela não são achados.** Controle positivo: Marosi 2026
  (W7203953290) tem 1475 e 1843 na Tabela 1, e Haas–Halupczok–Schlage-Puchta 2009
  (W1482458295) tem `K7(9, 4) 5 221 227 264 1843` na Tabela 5. A consulta
  `full text has (1843 or 1475 or 2143 or 8575 or 602)` restrita a essas duas obras devolve
  **0**. Já palavras do corpo (`Bhandari`, `Durairajan`) e anos (`1996`, `2009`, `2011`) são
  achados. Então "zero achados" para um valor de tabela **não é evidência de ausência**;
  o que vale é o caçador de menções rodando sobre o PDF.

Consultas feitas (todas `search_in=fulltext`; log completo com ids em
`fulltext_consultas.json`):

| consulta | resultados | veredito |
|---|---|---|
| `"covering radius" AND 1475` | 15 | falso positivo (Cohen et al., ISIT 1995; tabelas de arcos em PG(2,q); física) |
| `("covering code" OR "covering codes") AND 1475` | 20 | 4 preprints Zenodo **nossos** (K_7(9,4) ≤ 1137/1141/1351, citam 1475 do Marosi); resto falso positivo |
| `(covering code\|codes\|radius) AND 6517` | 0 | — |
| `… AND 8575` | 4 | falso positivo (Ozeki 2001, q = 3; relatórios NBS) |
| `… AND 42189` | 0 | — |
| `… AND 1843` | 14 | falso positivo |
| `… AND 1134` | 32 | falso positivo (Bartoli et al. 2017, tabelas para q ≥ 11; Ozeki) |
| `… AND (2875 OR 5616)` | 15 | falso positivo |
| `… AND 3125 AND (quinary OR q=5 OR K5)` | 6 | falso positivo (código de Lee; Bartoli et al. 2017) |
| `… AND (175 OR 162 OR 125) AND (quinary OR q=5 OR K5 OR K_5)` | 121 | lidos 50; só Gommard–Plagne 2003 (K_5(7,3) ≤ 100, outra célula) e Haas et al. 2009 (já no acervo) |
| `… AND (175\|8575\|42189\|6517\|1843\|1475) AND (septenary\|q=7\|K7)` | 49 | van Wee 1991 (tese, já no acervo), Zenodo nossos, resto falso positivo |
| `"football pool" AND (ternary OR quinary OR q-ary OR septenary OR nonbinary)` | 46 | clássicos ternários e mistos; nenhum valor das nossas células |
| `"K7(9,4)" OR "K_7(9,4)" OR …` | 30 | 5 Zenodo nossos; 25 ruído de tokenização |
| `"K5(10,5)" OR "K5(11,4)" OR "K7(10,4)" …` | 0 | — |
| `(covering code\|codes) AND Kéri AND table`, ≥ 2011 | 28 | ver abaixo (Filippini, Seuranen, Castoldi, coldcore) |
| `covering radius AND (q=5\|q=7) AND upper bound AND K_q(n,R)`, ≥ 2011 | 13 | só Marosi 2026 |
| `… AND K_q(n,R)`, ≥ 2012 | 9 | Marosi, Florath (artigo e software), Monte Carmelo 2012, Zenodo nossos |
| `… AND (septenary\|7-ary\|GF(7)\|F_7\|Z_7)`, ≥ 2005 | 10 | nenhum com cota de K_7(n,R) |
| `saturating set AND (PG(5,7)\|PG(4,7)\|PG(6,5)\|PG(5,5)\|PG(6,7)\|PG(7,5))` | 1 | falso positivo (Pavese, 4-general sets) |
| `coldcase OR covengine OR coldcore`, ≥ 2025 | 36 | Marosi (coldcore e o artigo de 2026); resto oceanografia ("cold-core eddies") |
| OQL: cita uma semente de cobertura **e** texto tem um dos 9 números | 2 | falso positivo (Colbourn–Lanus 2018, CPHF; Cohen et al. 1995) |
| restrito a 9 candidatas (coldcore, Riasat–Mahdavifar 2026, Filippini, Seuranen…): números e `quinary\|K7…` | 1 / 4 | nenhum número das células; coldcore cita K5/K7 mas não traz "covering radius" nem os números (sondado, PDF fechado atrás do Cloudflare do SSRN) |

### Achados de estado da arte

**Nenhuma cota publicada ≤ 1134 (K_7(9,4)), ≤ 162 (K_5(10,5)), ≤ 2875 (K_5(11,4)) ou
≤ 5616 (K_7(10,4)).** A tabela da seção A continua valendo sem mudança.

O caçador de menções, rodado sobre os 1314 textos, deu 33 achados. Só um vem de obra que
entrou nesta rodada:

- **Colbourn–Kéri–Rivas Soriano–Schlage-Puchta 2010**, *Covering and radius-covering
  arrays: Constructions and classification* (DAM, 10.1016/j.dam.2010.03.008, PDF aberto).
  Tabela `CANr(s, n, 7)` (colunas r = 0 a 3). Na diagonal s = n o arranjo é um código de
  cobertura e os valores repetem Kéri. Trecho literal (texto extraído, quebras trocadas por
  espaço):

  ```
  10,9 a 40353607 a d 733726−5420281 z d 29889−420175 e d 2077−42189 e
  10,10 a 2824752491 a g 4630843−5764801 g g 168042−420175 g g 10577−42189 g
  ```

  e, na linha 9,9: `g 733726−823543 g g 29889−94587 g g 2077−8575 g`. Ou seja,
  K_7(9,3) ≤ 8575 e K_7(10,3) ≤ 42189, as mesmas UB de Kéri. Não há coluna r ≥ 4.

Os demais achados novos do texto completo e dos PDFs são falsos positivos: 1134 como
tamanho de arco completo em PG(2,q) (Bartoli et al., arXiv 1404.0469), 1475 numa tabela de
covering perfect hash families (Colbourn–Lanus 2018).

Duas fontes que pareciam ameaça e não são:

- **Bartoli–Davydov–Marcugini–Pambianco**, *Tables, bounds and graphics of short linear
  codes with covering radius 3 and codimension 4 and 5* (arXiv 1712.07078). Resumo:
  "`ℓq(5, 3) < 2.785 ∛(q² ln q) if 11 ≤ q ≤ 401`". As tabelas começam em q = 11; o 1134 e o
  3125 do texto são valores de q grande. Não toca K_7(9,3) nem K_7(10,3).
- **Davydov–Marcugini–Pambianco 2019**, *New covering codes of radius R, codimension tR
  and tR + R/2* (DCC, 10.1007/s10623-019-00649-2). Texto: "`ℓq(r,R) = sq(r −1,R−1) ≤
  Rq(r−R)/R + q(r−2R)/R + ∆q(r,R), r = tR`" com "`∆q(r,R) = 0 if t = 2, q = 5, R = 4,5`".
  Para q = 5, R = 4 isso dá comprimento ≤ 4·5 + 1 = 21 com codimensão 8: é família de
  códigos longos, não diz nada sobre n ≤ 11.

### Técnicas novas (2015–2026) que não estavam entre os 31

Só o que é de fato novo em relação à lista da seção B. PDF aberto indicado onde há; sem
PDF, o comentário vem do resumo.

32. **Marosi 2026b**, *coldcore: a GPU framework for exhaustive-coverage combinatorial
    optimization* (SSRN, 10.2139/ssrn.7404672). O motor por trás do item 1, como biblioteca
    (palavras-chave do OpenAlex: GPU, covering codes, dominating sets, set cover, dynamic
    programming, CUDA). PDF atrás do desafio do Cloudflare do SSRN; não lido.
    **Ideia:** mesma do item 1, agora com o motor separado do artigo.
33. **Marenco–Rey 2026**, *An initial polyhedral study of the football pool problem*
    (Discrete Optimization, 10.1016/j.disopt.2026.100946; sem PDF aberto). Facetas do
    politopo de cobertura do grafo de Hamming. **Ideia:** desigualdades válidas para o ILP
    do remendo, além das de cobertura simples.
34. **Naszvadi–Ádám–Koniorczyk 2025**, *Reduction and efficient solution of ILP models of
    mixed Hamming packings yielding improved upper bounds* (Mathematics 13, 2633;
    10.3390/math13162633, OA, o download falhou). Redução do ILP por simetria em espaços de
    Hamming mistos. **Ideia:** a mesma redução vale para cobertura (o dual do empacotamento);
    comparar com a nossa redução por translação.
35. **Gao–Yao–Weise–Li 2015**, *An efficient local search heuristic with row weighting for the
    unicost set covering problem* (EJOR, 10.1016/j.ejor.2015.05.038), e **Wang–Ouyang–Zhang–Yin
    2017**, *…hyperedge configuration checking and weight diversity* (Sci. China Inf. Sci.,
    10.1007/s11432-015-5377-8). O remendo é exatamente um unicost set cover.
    **Ideia:** pesos de linha e configuration checking são o estado da arte de busca local
    para USCP; trocar o SA do remendo por isso e medir lado a lado, junto com o tabu do item 6.
36. **Pfetsch–Rehn 2018**, *A computational comparison of symmetry handling methods for
    mixed integer programs* (MPC, 10.1007/s12532-018-0140-y), e **van Doornmalen–Hojny
    2024**, *A unified framework for symmetry handling* (Math. Prog.,
    10.1007/s10107-024-02102-2, OA). Comparação medida de orbital fixing, orbitopes e
    simetria em SCIP. **Ideia:** escolher pela medição deles, não pelo panorama do item 12.
37. **Anders–Codel–Heule 2026**, *Orbitopal fixing in SAT* (LNCS, 10.1007/978-3-032-22752-2_5,
    OA). **Ideia:** se o remendo virar instância SAT (cardinalidade ≤ k), quebra de
    simetria dentro do solver.
38. **Davydov–Marcugini–Pambianco 2019–2024** (DCC 2019, AMC 2022, DCC 2024, AMC 2023;
    PDFs no acervo). Construções de códigos lineares q-ários de raio R e codimensão tR,
    tR+1 e 3t+1. Como mostrado acima, dão códigos longos; **não servem de base para
    n ≤ 11**. Ficam como referência para quem for atrás de ℓ_q(r,R).
39. **Florath 2026b**, *A Lean-certified proof of K_8(4,2) = 23* (arXiv 2606.16688), e
    o depósito Zenodo com o certificado Lean da prova SDP de Gijswijt–Polak para
    K_2(13,1) ≥ 607 (10.5281/zenodo.21024792). **Ideia:** primeiro certificado de cota
    *inferior* por SDP checado em Lean; é o formato a copiar se um dia certificarmos uma LB.
40. **Riasat–Mahdavifar 2026**, *New covering bounds and constructions for Hamming and
    Grassmann spaces* (ISIT 2026, 10.1109/isit62367.2026.11654080; fechado). Palavras-chave:
    binary codes. Sem texto completo no índice; não dá para dizer se toca q = 5 ou 7.

Também apareceram e **não** entram como técnica: arranjos de cobertura ordenados
(Castoldi et al. 2023, espaço NRT, não Hamming), códigos de cobertura em métrica de soma
de posto e de Lee, e o resto da família de covering arrays.

### O que falhou ou ficou de fora

- **PDFs:** das 154 obras novas, 37 têm PDF. Nesta rodada 33 links abertos falharam (403/HTML/desafio
  anti-robô, lista em `pdf_falhas.json`), entre eles Naszvadi et al. 2025 (MDPI),
  coldcore (SSRN), Filippini 2016 (ETH), Seuranen 2011 (Aalto) e Kizhakkepallathu 2015
  (Aalto). Não insisti com outro user-agent: desafio anti-robô não se contorna.
- **Texto completo do OpenAlex** não cobre artigo pago desta área e não acha número de
  tabela (controle acima). A busca por número continua valendo só sobre os nossos PDFs.
- **Riasat–Mahdavifar 2026** e **Marenco–Rey 2026** (fechados, recentes) não foram lidos.
- O nível 2 só expandiu quem cita; as referências das obras de nível 1 não foram seguidas.

## Como reproduzir

```sh
git checkout feat/literatura
export LIT_DIR=$PWD/literatura-dados GCP_CREDENCIAL_DIR=<apps/factory/bin>
python3 tools/literatura/varredura.py tudo
```

O cache de respostas HTTP fica em `literatura-dados/cache/` (não vai para o bucket). Para
reconferir só as tabelas de Kéri e os trechos citados aqui, basta a etapa `tabelas`.
