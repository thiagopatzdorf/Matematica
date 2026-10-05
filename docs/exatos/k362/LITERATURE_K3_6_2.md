# K_3(6,2): o que a literatura sabe (frente LITERATURA, 2026-10-05)

Operação K₃(6,2), M = 15. Pergunta: o que já foi publicado sobre `K_3(6,2)`, como a cota
inferior 15 foi provada, e que técnica já aplicada a esta célula serve para provar que **não
existe código ternário de comprimento 6, raio 2 e 15 palavras** (o que daria lb 16).

Este documento aprofunda a varredura de `docs/exatos/TRIAGEM_2026-10-04.md` sem repeti-la. As
consultas daquela triagem (acervo por regex, OpenAlex "football pool", API do arXiv, web) não
foram refeitas, só citadas. Nenhum número do ledger foi alterado. Nenhum crédito do Infinito foi
gasto (US$ 0,00; saldo conferido com `meus_creditos`).

Legenda: **CONHECIDO** = li a fonte (texto completo, tabela ou resenha, sempre dito qual);
**PROVÁVEL** = fonte secundária ou inferência que não confirmei no texto original;
**NÃO ENCONTRADO** = procurei e não achei, com as consultas; **POTENCIALMENTE NOVO** = não vi em
lugar nenhum e é barato de testar.

## Resumo em seis linhas

1. O intervalo publicado continua **15 ≤ K₃(6,2) ≤ 17**. Nada pós-2004 melhorou nenhum dos lados.
2. lb 15 vem de **Bertolo–Östergård–Weakley 2004** (*J. Combin. Des.* 12(3), 157–176,
   doi:10.1002/jcd.20008). O artigo é fechado e **não consegui ler o texto completo**. A resenha do
   zbMATH diz que ele traz cotas inferiores de dois tipos, por argumento combinatório e por busca
   em computador, e "discute um método computacional para melhorar cotas inferiores usado antes
   sobretudo em raio 1". **Qual dos dois tipos dá o 15, não sei dizer.**
3. Antes: **Blass–Litsyn 1998** provaram K₃(6,2) ≥ 14 (*Ars Combin.* 50, 297–302). A cota de esfera
   é 10.
4. O SDP de **Gijswijt–Polak** (arXiv:2504.01932v2, Tabela 7, p. 23) dá **13,1228**, ou seja, lb 14.
   Fica abaixo de BOW. O mesmo valor foi reproduzido com certificado racional exato no
   `coldcase` (Marosi): `cube_root 13.122857942908238`.
5. Dois trabalhos de 2026 atacam diretamente o caso de **16** palavras e nenhum fecha nada:
   **Florath** (notas de fracasso, `docs/failures/K_3_6_2.md` do covering-codes-lean) e
   **Raval** (Zenodo 10.5281/zenodo.22510341, v0.1.1). Raval exclui com certificado 6 de 38 ramos
   normalizados. Nenhum dos dois trata M = 15, mas **tudo o que eles provam para M ≤ 16 vale para M = 15**.
6. Não existe classificação publicada dos códigos de 17 palavras (Kéri, "K3(6,2) - unknown").

## CONHECIDO (com fonte lida)

### O intervalo e quem é o dono de cada lado

| fato | fonte lida | onde |
|---|---|---|
| `K3(6,2)`: `i 15–17 u` | Kéri, *Tables for bounds on covering codes*, `3_tables.pdf` (cópia no acervo da factory-01, `tabelas/keri/3_tables.txt`) | p. 1, tabela R = 2, linha n = 6 |
| chave `i` (lb) = "Bertolo–Östergård–Weakly, 2004"; chave `u` (ub) = "Hämäläinen–Rankinen, 1991" | idem | p. 2, "Key to the tables for K3(n,R)" |
| BOW 2004 = *J. Combinatorial Designs* **12** (2004) 157–176, número 3 | Lobstein, *bib-a-jour* (jan 2023), item [103]; OpenAlex W1963788317; `references.bib` do Florath | — |
| Hämäläinen–Rankinen 1991 = *J. Combin. Theory Ser. A* **56** (1991) 84–95, doi:10.1016/0097-3165(91)90024-B | Lobstein [444]; OpenAlex W2044451186 | — |
| K₃(6,2) ≥ 14, K₃(7,3) ≥ 9, K₃(8,2) ≥ 54, K₃(8,3) ≥ 14, "melhorando 12, 7, 52 e 13" | Blass–Litsyn, *Several new lower bounds for football pool systems*, Ars Combin. 50 (1998) 297–302 — **resenha** zbMATH Zbl 0962.94041 (texto completo não lido) | resenha inteira |
| o "método de Blass–Litsyn" foi reutilizado por Haas para K₄(5,2) ≥ 14 e K₄(6,2) ≥ 32 | resenha zbMATH Zbl 1265.94096 (Haas, Ars Combin. 2011) | — |
| post-Kéri: `3,6,2,15,17,lit_bertolo_ostergard_weakly_2004,lit_hamalainen_rankinen_1991` | `reference-data/post-keri/non_mixed_covering_codes.csv` do covering-codes-lean, commit `bbed9a6` (2026-09-16), linha 303 | a nota do `.bib` diz que os rótulos foram conferidos só contra o Kéri: "Individual bounds were not independently rederived" |
| no Lean do Florath a célula está como **10 ≤ · ≤ 17** (lb = esfera, ub = código explícito de 17 palavras) | `CoveringCodes/Database/GeneratedTable/Chunk29.lean`, linhas 1256–1260 | — |

### O que BOW 2004 diz de si mesmo (resumo e resenha; texto completo não lido)

- Resumo (OpenAlex): tabela de `K_{2,3}(b,t;R)` para `b + t ≤ 13`, `R ≤ 3`, com "a general
  lower bound for R = 1".
- Resenha zbMATH (no acervo, `W1963788317.zbmath.txt`): *"A computer-aided method for improving
  lower bounds, which has earlier mainly been used for nonmixed codes with covering radius 1, is
  also discussed. […] The lower bounds obtained are categorized into two types: those obtained by
  combinatorial arguments and those obtained by computer search."*
- **Classificações em BOW** (Kéri, *survey-present.pdf*, slide "Bertolo, Östergård and Weakley
  (2004)", e *survey.pdf*, Tabela II): **K₂(9,2) = 16 com 4 classes de equivalência** e
  **K₃(5,2) = 8 com código único**. O código de K₃(5,2) aparece em *elte-szem-present.pdf*, com a
  nota "Unicitás bizonyítása: Bertolo et al., 2004, számítógéppel" (unicidade provada por
  computador).
- Nada nessas três fontes diz que BOW classificou códigos de 15, 16 ou 17 palavras para
  K₃(6,2).

### Classificações vizinhas (survey do Kéri, *Classification Results for Non-Mixed and Mixed Optimal Covering Codes*, ~2010)

| célula | valor | nº de classes | fonte da classificação |
|---|---|---|---|
| K₃(5,1) | 27 | 17 | Östergård–Weakley 2002 |
| K₃(5,2) | 8 | **1** (anormal) | BOW 2004 |
| K₃(6,3) | 6 | 28 (24 normais) | Kéri, "NEW" |
| K₃,₂(5,1;2), 5 ternárias + 1 binária, R = 2 | 12 | **1** | Kéri, Tabela VI, "NEW" |
| K₃,₂(4,2;2) | 10 | 4 | Kéri, Tabela VI |
| K₂(9,2) | 16 | 4 | BOW 2004 (o valor 16 é de Östergård–Weakley 2000, *J. Combin. Des.* 8, 391–401) |

Kéri, *normality-present.pdf* (último slide): "K3(6,2) - unknown". *elte-szem-present.pdf*,
problema 22: "Szűkítsük a 15 ≤ K3(6,2) ≤ 17 egyenlőtlenségpárban a felső és az alsó korlát
távolságát" (estreite a distância entre 15 e 17), deixado como problema aberto.

### Cotas por LP/SDP para esta célula

- **Gijswijt–Polak**, *Semidefinite lower bounds for covering codes*, arXiv:2504.01932v2 (título
  datado de 23 jun 2026; publicado na IEEE Trans. Inf. Theory, doi:10.1109/TIT.2026.3706793). PDF
  lido, sha256 `35800b9d8a37a526…`. Apêndice B, **Tabela 7 (p. 23)**, linha n = 6: R = 1
  **60,8568**; R = 2 **13,1228** (sem asterisco, ou seja, não melhora o Kéri). O SDP usa as
  desigualdades de esfera e não as de van Wee (texto logo acima da tabela). A Tabela 2 (p. 20),
  de cotas novas para K₃, não tem K₃(6,2). Ela tem **K₃(7,2) ≥ 27**, que antes era 26.
- **coldcase/Marosi** (`coldcase_lb_master.json`, cópia no acervo): `cert_q3_n6_R2.json`,
  `sdp_value = 2259.8795…` (racional exato `174849707341972771135730495121 /
  77371252455336267181195264`), `cube_root = 13.122857942908238`, `K_lower_bound = 14`,
  `improves_best_known = False`. É o mesmo SDP do GP, com certificado exato, e confirma o 13,12.
- **Florath**, notas de fracasso (`docs/failures/K_3_6_2.md`, sha256 `6adc325b18e6518c…`, lidas
  inteiras). Todas as tentativas são para **M = 16**, com protótipos Python/SciPy/OR-Tools e
  **sem certificado**:
  - LP de Delsarte por distâncias de pares: viável, sobreposição de pares de 528 a ~3197,33;
  - LP de segundo momento por tipo local: viável, distribuição `N = [0,0,16,56,48,0]`;
  - versões inteiras (CP-SAT, HiGHS): `UNKNOWN` ou tempo esgotado em 300 s;
  - LP ancorado (`000000` + âncora `111110` ou `111111`) de primeiro momento: viável, com
    1 229 440 e 1 074 400 variáveis;
  - formulação inversa (não-centros): peso máximo 4 é `INFEASIBLE` em 0,13 s; pesos 5 e 6, `UNKNOWN`;
  - "third-orbit residual LP": **pruned 0/34 (peso 5) e 0/26 (peso 6)**, cotas de 9,18 a 9,52
    contra 13 vagas.
  - Também registrado: o código de 17 tem posto afim 6, distribuição de distâncias
    `{3: 32, 4: 46, 5: 54, 6: 4}`, e **não** é a construção `9 + 9 − 1` por dois planos afins.
  - Direções sugeridas: momentos mais fortes com certificado, *cube-and-conquer* sobre órbitas
    do 4º centro com DRAT/LRAT, ou busca finita verificada.

### Raval 2026: seis ramos de M ≤ 16 excluídos com certificado

*Six Certified Branch Exclusions for the Ternary Covering Problem K_3(6,2)*, R. R. Raval, Zenodo
10.5281/zenodo.22510341 (conceito; v0.1.0 em 2026-09-06, **v0.1.1** em 2026-09-07), código em
`github.com/ruturajr-raval/ternary-covering-code-6-2` (HEAD `d0a7b4c`). Li `paper/main.tex`
inteiro (sha256 `9273e32b47c9e7f3…`) e o README.

- **Lema antipodal** (§3.1): num código de raio 2 com ≤ 16 centros, todo centro tem outro a
  distância ≥ 5. Prova: a esfera de raio 6 tem 64 palavras, e bolas a distância 4, 5 e 6 cobrem
  4, 12 e 22 delas; `15·4 = 60 < 64`.
- **Lema da esfera de raio 3** (§3.2): todo centro tem outro a distância ≤ 4 (a esfera tem 160
  palavras, e uma bola a distância 5 cobre ≤ 10 delas; `15·10 = 150 < 160`).
- Normalização: translada um centro para `000000`, a âncora é `1^d 0^{6−d}` com d ∈ {5,6}, e o
  terceiro centro tem peso ≤ 4, escolhido canonicamente por órbita do estabilizador do par. Saem
  **38 ramos** (24 com d = 5 e 14 com d = 6), uma partição completa e sem sobreposição.
- **Certificado dual** (Teorema 1): pesos inteiros `w ≥ 0` nos buracos `H` dos três centros
  fixos, com `K(c) ≤ Q` para todo centro admissível e `W > 13Q`. É uma solução dual viável do LP
  de cobertura residual com valor > 13.
- Tabela 1: ramos excluídos `011110` (W/Q = 80/6), `011120`, `011220`, `012220` (40/3 cada),
  `022220` (80/6) e `002222` (132/10 = 13,2). **Sobram 32 ramos abertos**, 19 com d = 5 e 13
  com d = 6.
- Dois verificadores independentes, em Python e em C++20, mais testes de mutação. Dados extras:
  um código de 18 palavras e um **quase-código de 16 palavras com 7 buracos**. O nosso `sa_cover`
  chegou a 7 e 9 buracos em M = 16 (TRIAGEM, E1), o que é consistente.
- O próprio artigo diz: "No new global bound is claimed".

## Como lb 15 foi provado, e se o método serve para M = 15

**O que dá para afirmar:** a prova é de BOW 2004 e é uma das duas categorias da resenha
(combinatória ou busca em computador). A melhor cota anterior era 14 (Blass–Litsyn 1998, método
depois reaproveitado por Haas para K₄). **O texto do BOW não foi lido**: Wiley devolveu 403 deste
container e da factory-01, Semantic Scholar e OpenAlex marcam "closed", e não há preprint na
página do Östergård (`users.aalto.fi/~pat/patric_pub.html`, conferida: a lista de relatórios
técnicos não tem a tabela de 2004).

**PROVÁVEL (não confirmado):** o 15 é cota "por busca em computador", com o método que a resenha
chama de "usado antes sobretudo em raio 1". Na linhagem de Östergård até 2004 esse método é o de
*subcódigos*: fixa-se uma coordenada, os três subcódigos `C_0, C_1, C_2` são classificados a
menos de equivalência (os pequenos, que são poucos), e a união é completada por programação
inteira ou busca. É o que Östergård–Wassermann 2002 (K₃(6,1) ≥ 65, JCTA 99) e depois
Linderoth–Margot–Thain 2009 fazem em raio 1 ("isomorphism pruning, subcode enumeration, and
linear programming-based bounding", resumo do LMT). Para raio 2 a restrição de fatia é a mesma
que este repo já usa (`GAPS2_K362.md`): a palavra `(a, y)` é coberta por `C_a` a distância ≤ 2
no sufixo ou por `C_b ∪ C_c` a distância ≤ 1.

**Reaproveitável para M = 15?** Na forma de 2004, provavelmente não chega lá. O próprio repo já
mediu (`GAPS2_RESULTADOS.md`):

- M = 14 → 863 instâncias, todas inviáveis com prova VeriPB. Isso **reproduz o 15 do BOW**, com
  certificado, pela redução de fatia.
- M = 15 → 12 049 instâncias, 11 000 delas no caso equilibrado `s* = 5`, com cauda dura de mais de
  30 min e sem prova.

O que faltava em 2004 e falta aqui é a mesma coisa: quebrar a simetria que sobra quando todas as
18 fibras têm 5 palavras.

## Técnicas de quebra de simetria e LP já aplicadas a ESTA célula

| técnica | quem | M | resultado |
|---|---|---|---|
| fatia por fibra mínima + forma canônica do conjunto `K` + PB/VeriPB | este repo (GAPS2) | 14 e 15 | 14: fechado com certificado; 15: amostra de 2 %, 6 duras |
| âncora `000000` + peso máximo + órbita do 3º centro (estabilizador do par) | Raval; Florath (só a âncora) | ≤ 16 | 38 ramos; peso máximo ≤ 4 impossível |
| dual inteiro do LP de cobertura residual (certificado curto e verificável à mão) | Raval | ≤ 16 | 6 de 38 ramos excluídos |
| LP de Delsarte / segundo momento / tipo local | Florath | 16 | viável, não poda |
| LP residual "inverso" por órbita do 3º centro | Florath | 16 | 0 de 60 podados (cota de ~9,5) |
| CP-SAT / MILP / CNF (CaDiCaL, Kissat) | Florath; Raval | 16 | só `UNKNOWN`; o Raval usa o CP-SAT só como oráculo de candidatos |
| SDP de Schrijver/Gijswijt–Polak | GP; coldcase | — | 13,1228 |

## PROVÁVEL CONHECIDO

- O livro de Kaski–Östergård, *Classification Algorithms for Codes and Designs* (Springer 2006),
  trata de classificação de códigos de cobertura na §7.2 (fonte: resumo de busca web, sumário não
  lido). Não sei se cita K₃(6,2).
- A construção de 17 palavras de Hämäläinen–Rankinen 1991 provavelmente sai dos métodos de
  códigos mistos daquele artigo. O texto (Elsevier, *open archive*) devolveu 403 aqui. O Florath
  mostra que não é `9 + 9 − 1`.
- Desigualdades elementares do livro de Cohen–Honkala–Litsyn–Lobstein: `K₃(7,3) ≤ K₃(6,2) ≤
  K₃(5,1) = 27` e `K₃(7,2) ≤ 3·K₃(6,2)`. Com as cotas atuais nenhuma aperta (11–12 ≤ · e
  27 ≤ 3·15). Ao fundir dois símbolos de uma coordenada sai `K₃,₂(5,1;2) = 12 ≤ K₃(6,2)`, também
  fraca. **Nenhuma relação com K₃(5,1) ou K₃(7,3) dá mais que 15.** Não achei na literatura uma
  relação que melhore.
- Lang–Quistorff–Schneider 2006 (programação inteira, chave `x` do Kéri) e
  Haas–Halupczok–Schlage-Puchta 2009 (chave `m`) não aparecem como donos de K₃(6,2) na tabela. A
  leitura natural é que os métodos deles não passam de 15 aqui.

## NÃO ENCONTRADO (com as consultas)

| procurado | consultas | resultado |
|---|---|---|
| texto completo do BOW 2004 | Wiley PDF (403, daqui e da factory-01); Semantic Scholar e OpenAlex (`CLOSED`); página do Östergård; web `"An updated table of binary/ternary mixed covering codes" pdf` e `Bertolo Östergård Weakley … preprint` | inacessível. **É a lacuna principal deste documento.** |
| classificação de códigos ótimos (15, 16 ou 17) de K₃(6,2) | survey do Kéri (Tabela II), *normality-present*, *elte-szem-present*; covering-codes-lean; Raval | não existe; "unknown" |
| melhoria de K₃(6,2) depois de 2004 | Kéri (tabela até 2011); post-Kéri do Florath (2026-09); GP Tabelas 2 e 7; Marosi (o artigo cobre só 5 ≤ q ≤ 21); OpenAlex `title-abstract-keywords has ("covering code" or "covering codes" or "football pool") and year >= 2019` (224 obras, li as 50 mais recentes) | nenhuma |
| `K_3(6,2)` em texto livre | WebSearch `"K_3(6,2)" covering code ternary lower bound`; Zenodo API `q="K_3(6,2)"` e `"K3(6,2)"`; OpenAlex fulltext `"covering radius 2" ternary "length 6"`; acervo da factory-01 (1 274 arquivos em `dados/txt` medidos hoje; a triagem contou 1 317), regex `K_?3 ?\(6, ?2\)` | só Blass–Litsyn (resenha), Raval e Florath |
| texto completo de Blass–Litsyn 1998, Östergård–Wassermann 2002 e Kéri–Östergård 2007 | ScienceDirect (403), Springer (redirect de login), acervo (só resenhas) | não lido |
| arXiv por data | API (`export.arxiv.org`): **429** nesta sessão; a triagem de 2026-10-04 já tinha feito essa consulta | não refeita |
| Infinito `biblioteca_buscar` | `"Bertolo"`, `"ternary"`, `"covering"`, vazio | **erro** `Extra data: line 2 column 1 (char 909)` em todas: a ferramenta está quebrada (vale uma issue `atrito:`). `papers_buscar` devolveu `HTTPError` para semanticscholar e arxiv |

## POTENCIALMENTE NOVO (barato de testar; ninguém publicou)

1. **Os lemas e os seis certificados do Raval valem para M = 15 sem mudar uma vírgula.** Os
   lemas usam `15·4 < 64` e `15·10 < 160`. Com 14 outros centros a folga só cresce (`56 < 64`,
   `140 < 160`). Os seis duais têm `W/Q ≥ 13,2 > 12`. Logo, em M = 15, **os mesmos 6 ramos caem,
   e para os outros 32 basta `W > 12Q`** (12 vagas e não 13), uma barra uma unidade mais baixa.
   Ninguém rodou o LP de cobertura residual dos 38 ramos com 12 vagas. É um LP por ramo, com 729
   pontos e ~200–270 centros, e custa segundos. **Se todos passarem de 12, lb 16 sai com 38
   certificados curtos, sem SAT.** Se não passarem, o ramo que falha já é a unidade de trabalho
   certa para PB/SAT (aprofundar para a órbita do 4º centro). Atenção: o "residual LP" do Florath
   (~9,5) é da formulação **inversa** e não do LP de cobertura sobre os buracos. Ele não diz nada
   sobre esta barra.
2. **Combinar a fatia do GAPS2 com a âncora do Raval.** O caso duro do GAPS2 é o equilibrado
   (`s* = 5`, 18 fibras iguais). A normalização do Raval quebra a simetria por **distância**
   (centro, antípoda ≥ 5, vizinho ≤ 4) e não por fibra, então não tem o defeito "o mesmo código em
   até 18 instâncias". Não vi ninguém usar as duas ao mesmo tempo: âncora para o caso
   equilibrado, fatia para os desequilibrados.
3. **Bancos de validação de mesmo porte** para a ferramenta orderly da Fase 0, todos com
   contagem publicada: K₃(5,2) = 8 (1 classe), K₃,₂(5,1;2) = 12 (1 classe), K₃(6,3) = 6
   (28 classes), K₂(9,2) = 16 (4 classes, espaço de 512 palavras, a escala de K₃(6,2)). Reproduzir
   as contagens prova que a geração sem isomorfos está certa antes de gastar em M = 15.

Nada disto é resultado. São hipóteses de trabalho para as frentes de núcleo de simetria e de LP.

## Fontes consultadas (resumo)

Kéri, tabelas (`3_tables`, `mixed_tables`, `biblio`, `survey`, `survey-present`,
`normality-present`, `elte-szem-present`; cópia no acervo da factory-01); Lobstein, *bib-a-jour*
(jan 2023); zbMATH Zbl 0962.94041, 1265.94096 e a resenha do BOW (acervo); OpenAlex W1963788317
(BOW, com os 14 citantes), W2044451186 (HR 1991), W1965348767 (ÖW 2002), W1977807973 (ÖW 2000)
e a busca de 2019 em diante; Gijswijt–Polak arXiv:2504.01932v2 (PDF); Marosi arXiv:2608.19872
(PDF atual, só q ≥ 5); Florath arXiv:2606.09600 (PDF) e covering-codes-lean `bbed9a6`
(`docs/failures/K_3_6_2.md`, `reference-data`, `Chunk29.lean`); Raval Zenodo 22510341/22647771
e GitHub `d0a7b4c` (`paper/main.tex`, README, dados); coldcase `lb_master.json` (acervo); Haas,
EJC 14 (2007) R27 (acervo, para o método de raio 1); página de publicações do Östergård.
