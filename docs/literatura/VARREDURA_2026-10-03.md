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
  OpenCitations.
- **Semantic Scholar** (429 sem chave) e **Google Scholar** (proibido) não foram usados.
- **zbMATH**: a busca por MSC `cc:94B75` devolve 505 documentos (o total que a API informa).
- A bibliografia do Lobstein (*Covering radius*, 1058 referências, janeiro de 2023) foi lida
  por entradas de 2012 em diante. Nenhuma trata de cotas de K_q(n,R) para q = 5 ou 7. Dela
  saiu Östergård–Weakley 2018 (item 15 acima).
- O nível 2 de citações não rodou. Com OpenCitations o rendimento já era baixo (96 obras
  novas para 701 sementes), e sem o OpenAlex o custo não compensava.

## Como reproduzir

```sh
git checkout feat/literatura
export LIT_DIR=$PWD/literatura-dados GCP_CREDENCIAL_DIR=<apps/factory/bin>
python3 tools/literatura/varredura.py tudo
```

O cache de respostas HTTP fica em `literatura-dados/cache/` (não vai para o bucket). Para
reconferir só as tabelas de Kéri e os trechos citados aqui, basta a etapa `tabelas`.
