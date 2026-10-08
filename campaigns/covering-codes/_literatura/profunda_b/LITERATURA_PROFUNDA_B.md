# Revisão bibliográfica profunda B — 5 pares q=4,5 + K_2(6,1)

Agente LB, 2026-10-03. Escopo: (q,n,R) = (5,7,2), (4,10,4), (5,9,3), (5,9,5), (5,9,4) e a confirmação de K_2(6,1)=12. Não revisei K_5(10,4), K_7(9,4), K_7(8,3) (outro agente). Sem git, sem editar a campanha, US$0, nenhum código de terceiros executado (só scripts meus, listados em §8).

Rótulos: **LI** = li o texto/arquivo eu mesmo; **RESUMO** = só vi resumo/snippet/citação de terceiro; **MEDI** = calculei/verifiquei por conta. **"Não encontrei" nunca significa "não existe".** `NOVELTY_EXTERNALLY_CONFIRMED` não é atribuído a ninguém.

## 1. Resposta curta

| par | nossa | melhor tabelada (Kéri 2009-10-15) | estado | em uma frase |
|---|---|---|---|---|
| K_5(7,2) | 500 | 525 (chave o) | **AMBIGUOUS** | nenhum valor ≤500 achado; mas a ADS "otimista" 13·184/5 = 478,4 só não vale se os códigos não forem normais (não verificado) |
| K_4(10,4) | 192 | 208 (chave o) | **AMBIGUOUS** | 192 = 24·32/4 = 8·96/4 **exatamente** (soma direta amalgamada de células da própria tabela); depende de normalidade; 1 teste meu não confirmou |
| K_5(9,3) | 1250 | 1275 (chave d) | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES | mesmo a ADS otimista dá 1275 > 1250 |
| K_5(9,5) | 50 | 55 (chave d) | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES | ADS otimista dá 51 > 50 |
| K_5(9,4) | 250 | 255 (chave d) | **AMBIGUOUS** | ADS otimista 35·35/5 = 245 < 250 (se o código de 35 palavras valer consigo mesmo); 2 códigos meus de 35 palavras: 0 acertos em 3840 combinações |
| K_2(6,1) | 12 | 12 exato (Stanton–Kalbfleisch) | PREDECESSOR_FOUND | valor idêntico tabelado; exatidão **provada por mim** por busca exaustiva (§6); artigo de 1968 **não lido** |

Nada dos 5 pares é implicado por regra de propagação simples (§4.1): os valores derivados das células da própria tabela do Kéri são 625, 256, 1625, 65, 325, todos > nossos.

## 2. Verificação independente dos nossos códigos (MEDI)

Li `data/codes/*.txt` e `data/structured/*.json` e medi a cobertura por força bruta (`scripts/check.py`): para cada código, M palavras distintas, **raio de cobertura medido = R e 0 palavras descobertas**, para os 5 pares (500, 192, 1250, 50, 250).

Estrutura (medida):

| par | estrutura | raio da base linear sozinha | nota |
|---|---|---|---|
| (5,7,2) | 4 translados de um [7,3]_5 (4·125) | 3 | estabilizador por translação = 125 |
| (5,9,3) | 2 translados de um [9,4]_5 (2·625) | 4 | estabilizador 625 |
| (5,9,5) | 2 translados de um [9,2]_5 (2·25) | 6 | estabilizador 25 |
| (5,9,4) | 2 translados de um [9,3]_5 (2·125) | 5 | estabilizador 125 |
| (4,10,4) | 3 translados de um **[10,3]_4 linear sobre GF(4)** (3·64) | 5 | ver §5 |

Padrão comum: base linear com raio R+1; poucos translados baixam para R. É exatamente a família "união de cosets / método matricial" de Östergård; não é, por si só, evidência de predecessor ou de novidade.

## 3. Linha do tempo por par

Fonte comum das tabelas: Kéri, `old.sztaki.hu/~keri/codes/`, `4-5_tables.pdf` e `2_tables.pdf` (arquivos de 2009-10-15, **LI** por `pdftotext`, e renderização da página de K_5 conferida a olho), `index.htm` (site até 2011-11-21, **LI**). A lista "Improvements and corrections" do `index.htm` cobre de 2004-12-20 a 2011-11-21; **nenhuma entrada dela cita K5(7,2), K5(9,3), K5(9,4), K5(9,5) ou K4(10,4) como upper bound novo** (grep **MEDI**). Logo os 5 upper bounds são anteriores a 2004-12 ou nunca foram mexidos depois (o reajuste de K5(10,4)≤875 de 2006 é de outro par). Não consegui o histórico antes disso (Wayback devolveu 429/reset).

**Chaves do Kéri (LI):** d = Bhandari–Durairajan 1996; o = Östergård 1999; m = Östergård 1991; q = Rivas Soriano 2006–08; k = "usando q menor"; v = soma direta amalgamada.

Identificação das fontes primárias (por mim; as 3 não foram lidas):
* **BD1996** = M. C. Bhandari, C. Durairajan, "A note on bounds for q-ary covering codes", IEEE Trans. Inform. Theory 42(5) (1996) 1640–1642. **RESUMO** (abstract via busca): "Two strongly seminormal codes over Z_5 are constructed to prove a conjecture of Östergård ... A lower bound and an upper bound on K_q(n,R) are obtained. These give improvements in seven upper bounds and twelve lower bounds by Östergård for K_q(n,R) for q=3,4,5." Texto completo não lido.
* **Östergård 1999 (chave o)** = muito provavelmente P. R. J. Östergård, "New constructions for q-ary covering codes", Ars Combinatoria 52 (1999) 51–63 (**inferência**: o título bate com a bibliografia de Lobstein, entrada [797], e com a lista de publicações dele; nenhuma fonte que li liga essa chave a esse artigo explicitamente). **Não lido**; sem abstract.
* **Östergård 1991 (chave m)** = "Upper bounds for q-ary covering codes", IEEE IT 37 (1991) 660–664 (+ correção 1738), idem por inferência. Não lido.

### (5,7,2) — nossa 500
| ano | bound | autor | construção | fonte | LI/RESUMO |
|---|---|---|---|---|---|
| ≤2004 (provável 1999) | K5(7,2) ≤ 525 | Östergård (chave o) | não sei (busca/coset?); 525 = 21·25 | Kéri 4-5 PDF, linha n=7 R=2: `m 225–525 o` | tabela **LI**; artigo **não lido** |
| 2009-10-15 | 225 ≤ K5(7,2) | Haas–Halupczok–Schlage-Puchta (m) | inferior | idem | LI |
| 2026-06-19 | inferior 236 | Gijswijt–Polak v2 | SDP | (revisão anterior, Tab. 3) | herdado de LITERATURA_CC |
| 2026-08/09 | — | Marosi 2608.19872 v3 | só K5(11,5)≤602 para q=5 | `grep K5` no PDF v3 **MEDI** | LI |
| 2026-10-02 | 500 | nossa campanha | 4 translados de [7,3]_5 | `q5_n7_R2_M500.json` | MEDI |

### (4,10,4) — nossa 192
| ano | bound | autor | construção | fonte | LI/RESUMO |
|---|---|---|---|---|---|
| ≤2004 (provável 1999) | K4(10,4) ≤ 208 | Östergård (o) | não sei; **208 = 52·16/4 = 13·16** (ADS de K4(6,2)=52 com K4(5,2)=16, ou 13 translados de [10,2]_4) | Kéri 4-5 PDF: `m 59–208 o` | tabela LI |
| 2009 | inferior 59 | HHS (m) | | idem | LI |
| 2023 | repete 208 | Sum-rank paper arXiv:2311.07831 | cita 208 como estado da arte | texto **LI** (grep) | LI, secundário |
| 2026-10-02 | 192 | nossa campanha | 3 translados de [10,3]_4 | json | MEDI |

### (5,9,3) — nossa 1250
1275 = 51·125/5 = K5(4,1)·K5(6,2)/5, chave d (BD1996). Resto igual: Kéri `p 330–1275 d`; inferior 330 (Habsieger–Plagne, p); GP v2: 354. Nada pós-2011 achado. Nossa 1250 = 2 translados de [9,4]_5.

### (5,9,5) — nossa 50
55 = 11·25/5 = K5(4,2)·K5(6,3)/5, chave d (BD1996). Kéri `m 19–55 d`. Nossa 50 = 2 translados de [9,2]_5.

### (5,9,4) — nossa 250
255 = 51·25/5 = K5(4,1)·K5(6,3)/5, chave d (BD1996). Kéri `m 64–255 d`. Nossa 250 = 2 translados de [9,3]_5.

**Observação sobre a chave d (MEDI):** todas as células d de K5 reproduzem a fórmula da soma direta amalgamada K_q(n1+n2−1, R1+R2) ≤ K1·K2/q com células vizinhas da própria tabela: (8,3)=325=13·125/5, (8,4)=65=13·25/5, (9,3)=1275, (9,4)=255, (9,5)=55, (10,4)=875=35·125/5, (10,5)=175=35·25/5, (10,6)=45=9·25/5, (11,4)=3125=125·125/5. Isso casa com o resumo de BD1996 ("strongly seminormal codes over Z_5"). É **inferência numérica**, não leitura do artigo. Nossos 3 pares q=5,n=9 batem 1275/255/55 por menos 25/5/5.

## 4. Propagação e construções que implicariam o bound

### 4.1 Regras simples, direção correta (MEDI, `scripts/prop.py`)
Regras de limitante superior (todas válidas para qualquer código): K(n,R+1) ≤ K(n,R); K(n+1,R) ≤ q·K(n,R); K(n+1,R+1) ≤ K(n,R); K(n1+n2,R1+R2) ≤ K(n1,R1)·K(n2,R2); K_q(n,R) ≤ K_{q+1}(n,R) (prova: troca o símbolo extra por 0, as distâncias a palavras do alfabeto menor não crescem). Fecho sobre as células de **upper bounds do Kéri** (tirando a célula-alvo):

| alvo | nossa | melhor derivável por regras simples | cadeia | tabela direta |
|---|---|---|---|---|
| K5(7,2) | 500 | 625 | K5(6,1)=625 | 525 |
| K4(10,4) | 192 | 256 | K4(9,3)=256 | 208 |
| K5(9,3) | 1250 | 1625 | K5(8,2)=1625 | 1275 |
| K5(9,5) | 50 | 65 | K5(8,4)=65 | 55 |
| K5(9,4) | 250 | 325 | K5(8,3)=325 | 255 |

Resposta à pergunta pedida ("K5(9,3) ≤ 5·K5(8,3)?"): 5·325 = 1625 > 1250. **Nenhum dos 5 é implicado por propagação trivial.** Via K6 (monotonia em q): K6(7,2)≤1296, K6(9,3)≤4752, K6(9,4)≤738, K6(9,5)≤144 (Kéri 6-21 PDF, LI), todos muito acima.

### 4.2 Soma direta amalgamada (ADS) "otimista": o ponto de atenção (MEDI)
ADS: K_q(n1+n2−1, R1+R2) ≤ K1·K2/q **se os dois códigos forem normais** (Graham–Sloane 1985 para q=2, texto **LI** em `mathweb.ucsd.edu/~ronspubs/85_01_covering_radius.pdf`, só binário; a versão q-ária é de Honkala e do BD1996, **não li**). Tratei-a como **envelope**: o menor valor que valeria **se** a normalidade valesse. Sobre as células do Kéri (excluindo o alvo):

| alvo | nossa | envelope ADS | pares (n,R,K) | leitura |
|---|---|---|---|---|
| K5(7,2) | 500 | **478,4** | (3,1,13)×(5,1,184) | abaixo da nossa se ambos normais (184 vem de Stanton–Horton–Kalbfleisch 1969, normalidade desconhecida) |
| K4(10,4) | 192 | **192,0** | (4,1,24)×(7,3,32) e (3,1,8)×(8,3,96) | **igual** à nossa |
| K5(9,3) | 1250 | 1275 | | acima: não implica |
| K5(9,5) | 50 | 51 | (4,1,51)×(6,4,5) | acima por 1 |
| K5(9,4) | 250 | **245** | (5,2,35)×(5,2,35) | abaixo se o código de 35 palavras for normal consigo mesmo |

Se esses envelopes fossem válidos o Kéri os teria listado (ele usa a chave v para ADS em K4(11,4..6)); não estão, o que sugere que os códigos usados **não** são normais no sentido exigido ou que ninguém aplicou. **Isso é inferência, não fato.** Testei duas dessas implicações construindo os códigos (scripts meus, sem terceiros), verificando a cobertura do código resultante diretamente (não depende de teoria):

* **K4(10,4)**: construí (7,32,3)_4 como código aditivo F2 de dimensão 5 (achei por amostragem aleatória, verificado) e (4,24,1)_4 balanceados por busca (SA). Testei a ADS em 7 coordenadas de C × 24 permutações de símbolos por par B×C, com 2 códigos C distintos e 331 códigos B (200+131, cada um achado por SA, fusão sempre na coordenada 0 de B): **55.608 combinações, 0 acertos** (`logs/ads2.log`; interrompi na 2a rodada de C). Não prova que não exista outra escolha de códigos (B só balanceado na coordenada 0; C só aditivo; B e C são amostras de classes de equivalência).
* **K5(9,4)**: construí dois (5,35,2)_5 (7 translados de ⟨g⟩, g=(1,1,1,1,0) e (1,1,2,2,0); cobertura verificada), e testei a ADS de cada um consigo mesmo em 16 pares de coordenadas × 120 permutações = **3840 testes, 0 acertos**.
* K5(7,2) (184 palavras) **não testado** (não consegui construir o (5,184,1)_5).

Conclusão honesta: **o envelope existe e não foi refutado em geral**; os poucos testes concretos não o confirmaram. Os 3 pares afetados ficam AMBIGUOUS.

### 4.3 Códigos lineares (tabelas Davydov et al.)
Li (LI) arXiv:0904.3835 (Davydov–Giulietti–Marcugini–Pambianco), Tabelas I, III, IV, e arXiv:1808.09301 v2, Teorema 1. Valores de ℓ_q(r,R) (menor comprimento de código linear com codimensão r e raio R): ℓ_4(3,2)=5, ℓ_5(3,2)=6; ℓ_4(4,3)=5, ℓ_5(4,3)=6; ℓ_4(5,3)=9, ℓ_5(5,3)=10; ℓ_4(4,2)=9 (Prop. 5.1); ℓ_q(4,2)=2q+1 para q≥5 é **problema aberto** (§5 do artigo). Um [n,n−r]_q de raio R dá K_q(n,R) ≤ q^{n−r}:

| alvo | melhor linear das tabelas lidas | tamanho | vs nossa |
|---|---|---|---|
| K5(7,2) | ℓ5(3,2)=6 ≤ 7, [7,4]_5 | 625 | 625 > 500 |
| K5(9,3) | ℓ5(4,3)=6 ≤ 9, [9,5]_5 (ℓ5(5,3)=10 > 9) | 3125 | > 1250 |
| K4(10,4) | ℓ4(5,3)=9 ≤ 9, [9,4]_4 raio 3 → K4(10,4) ≤ 256 | 256 | > 192 |
| K5(9,4), K5(9,5) | **não achei** ℓ5(5,4), ℓ5(6,4), ℓ5(7,5) em tabela alguma | — | sem comparação |

As bases lineares de nossos códigos têm raio R+1, então não aparecem como "linear de raio R". Lacuna declarada: tabelas de ℓ_5 para R=4,5 e codimensão 5–7 não foram achadas; não posso afirmar que não existam.

### 4.4 Outras fontes
* Marosi arXiv:2608.19872 v3 (2026-09-02, LI por grep): q=5 só tem K5(11,5) ≤ 602; nossas células não aparecem.
* arXiv (busca API, várias consultas, 2026-10): nenhum trabalho novo com upper bounds para q=4,5 nas células; a API deu timeout em 3 de 12 consultas ("covering codes AND quaternary/quinary", "tabu search"): **cobertura incompleta**.
* Bibliografia de Lobstein (jan/2023, 1058 refs, LI): filtrei entradas ≥2005 com termos q-ary/tabu/tabela/normal; nada novo sobre upper bounds q=4,5 além de Mendes–Monte Carmelo–Poggi 2010 (chave y), Kéri 2007/2010 (normalidade de códigos ótimos, [577], **não lido**; seria a fonte para decidir §4.2) e Colbourn–Kéri–Rivas Soriano–Schlage-Puchta 2010.
* Cohen–Honkala–Litsyn–Lobstein 1997: **não acessível**; é aí que moram as tabelas originais e possivelmente 208/525.

## 5. Atenção q=4: estrutura "xor" e equivalência (MEDI)

O formato estruturado marca `"group": "xor"` para q=4: cada dígito é lido como 2 bits e a soma é XOR, isto é, a soma de GF(4)=GF(2)².

* O código de 192 palavras **não é** aditivo (192 não é potência de 2) nem fechado por translação; é a união de **3 translados** de um subgrupo D de 64 palavras (estabilizador por translação, medido).
* D é **fechado por multiplicação por ω** (verificado) ⇒ D é **GF(4)-linear**, [10,3]_4. Raio de cobertura de D sozinho = 5; com 3 translados cai para 4. O segundo bloco do JSON (7 geradores) mostra que D ∪ (D+g7) é um subgrupo F2-linear de ordem 128 não-GF(4)-linear; o código completo **não** é invariante por ω (testado).
* O código não vem de Z_4 (o doc do repo diz o mesmo) e **não precisa** de estrutura para comparar com a literatura: o raio de cobertura em métrica de Hamming é invariante por qualquer permutação de símbolos em cada coordenada, então K_4(n,R) do Kéri (alfabeto {0,1,2,3} sem estrutura) e o nosso são o **mesmo** objeto. A estrutura GF(4) só importa para achar predecessor em tabelas de códigos lineares sobre GF(4): a base D é [10,3]_4 com raio 5, não 4, então não é uma entrada "linear de raio 4"; um [10,3]_4 de raio 4 (64 palavras) não é contradito pelo limite inferior 59, mas não achei ℓ_4(7,4) em tabela lida (§4.3).
* Não sei se o 208 de Östergård é de estrutura GF(4)/Z_4/aditiva. Sem o artigo, DESCONHECIDO.

## 6. K_2(6,1) = 12

* **Tabela (LI):** Kéri `2_tables.pdf`, n=6, R=1: `c 12 c` (superscript 2 = nº de códigos ótimos inequivalentes). Chave c, **upper**: Stanton–Kalbfleisch 1968; **lower**: Stanton–Kalbfleisch 1968 e 1969.
* **Primária:** R. G. Stanton, J. G. Kalbfleisch, "Covering problems for dichotomized matchings", Aequationes Math. 1 (1968) 94–103, doi 10.1007/BF01817562. **NÃO LI.** A página da Springer devolve só prévia (referências e "84 acessos"); o PDF (`content/pdf/…`) responde com HTML de login. Não tentei espelhos não oficiais. O que sei dele vem do Kéri (**secundário**), e a segunda fonte, o CSV do Florath citado em LITERATURA_CC, também é secundária.
* **Prova própria (MEDI, `scripts/k261.py`):** busca exaustiva com ramificação sobre as 7 bolas que cobrem o primeiro ponto descoberto, palavra 0 fixada por simetria de translação, poda `descobertos > 7·restantes`: **com 11 palavras não existe cobertura (1.812.707 nós)**; **com 12 existe** (achado: 0,1,2,15,28,23,57,58,59,39,44,52). Portanto K_2(6,1) = 12 exato, independentemente de qualquer fonte. É o resultado clássico; o ponto aqui é que a exatidão agora é verificada por conta, não só citada.
* Estado: PREDECESSOR_FOUND (igualdade). Nota: "10 ≤ K ≤ 12" de LITERATURA_CC é o que o Lean do Florath prova, não o estado da arte.

## 7. Resíduos e confiança (resumo)

* Experimento q=4 (ADS 24×32): 55.608 combinações, 0 acertos (§4.2). Experimento q=5 (ADS 35×35): 3.840, 0 acertos.
* Confiança alta: valores das tabelas (3 transcrições concordam, LITERATURA_CC §3), nossa cobertura (medida), K_2(6,1)=12 (provado), nenhuma propagação simples basta.
* Confiança média: "nenhuma entrada do changelog 2004–2011 toca as células" (LI do `index.htm`, mas o texto é HTML bruto convertido).
* Confiança baixa / residual: (1) artigos primários BD1996, Östergård 1991/1999, Cohen et al. 1997, Kéri 2010 sobre normalidade, Stanton–Kalbfleisch 1968: **não lidos**; (2) se os códigos de 13, 24, 35, 51, 184 palavras são normais (decide §4.2); (3) tabelas de ℓ_5 para R=4,5; (4) arXiv API parcial; (5) Wayback indisponível.
* O que decidiria os 3 AMBIGUOUS: ler Kéri 2010 [577] e BD1996 (definição q-ária de normalidade e quais códigos ótimos pequenos são normais), ou construir/testar todas as classes de equivalência dos códigos de 24/32/13/35/184 palavras na ADS.

## 8. Reprodutibilidade

Scripts meus (nenhum código de terceiros) em `scripts/`: `check.py` (cobertura dos 5 códigos), `base.py` (raio das bases lineares), `prop.py` (fecho de regras + envelope ADS, usa só células lidas do Kéri), `k261.py` (K_2(6,1)), `sa.c` (busca de cobertura), `ads.py`/`ads2.py` (q=4), `q5ads.py`/`q5ads2.py` (q=5). Logs: `logs/`. URLs abertas: Kéri (`4-5_tables.pdf`, `2_tables.pdf`, `6-21_tables.pdf`, `index.htm`), arXiv 0904.3835, 1808.09301, 2311.07831, 2608.19872v3, Lobstein `lri.fr/~lobstein/bib-a-jour.pdf`, Graham–Sloane (UCSD), Springer (página do artigo de 1968, só prévia), search de Östergård/BD1996 (RESUMO). Não abertas: Wayback (429), `lobstein.fr` (erro de certificado; não desativei TLS).
