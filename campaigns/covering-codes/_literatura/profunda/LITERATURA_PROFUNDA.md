# Revisão profunda de literatura — 3 parâmetros (K_7(9,4), K_7(8,3), K_5(10,4))

Agente LA, leitura em 2026-10-03. Complementa `../LITERATURA_CC.md` (1ª revisão); não o substitui.
Rótulos: **LI** = li o texto/PDF/arquivo; **RESUMO** = só vi resumo, página de editora ou citação por terceiros; **MEDIDO** = conta/programa meu, reproduzível com `scripts/`.
**Regra:** "não encontrei predecessor" nunca vale como "não existe", e **nenhuma novidade é atribuída** (exige confirmação externa).

## 0. Resposta curta

| par | nossa cota | melhor anterior encontrada | estado | confiança |
|---|---|---|---|---|
| K_7(9,4) | 1285 (e 1351) | 1475 (Marosi v2/v3, 2026); antes disso 1843 (Kéri, edição 2006-01 e PDF 2009) | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES | média |
| K_7(8,3) | 1887 (e 1893) | 2337 (Kéri, edição 2006-01 e PDF 2009; Marosi não altera) | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES | média |
| K_5(10,4) | 625 = código linear [10,4,5]_5 | 875 (Bhandari–Durairajan 1996, via correção de Kéri 2006-09-19; a cota original "720" ele julgou erro de impressão) | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES, mas **fonte primária decisiva não lida** (ver §3) | baixa-média; não alegar novidade |

Três achados que mudam a leitura da 1ª revisão:

1. **K_5(10,4)=625 é um código linear [10,4,5]_5 com covering radius 4 achável por busca aleatória em menos de 1 s** (MEDIDO, §3.4). Isso torna improvável que o ingrediente "ℓ_5(6,4) ≤ 10" seja difícil e justifica cautela; mas o que eu **li** das tabelas (Kéri até 2011, Davydov–Marcugini–Pambianco até 2019/2023) não o registra.
2. **O 875 do Kéri para K_5(10,4) é reproduzido exatamente por uma soma direta amalgamada (ADS) de componentes tabelados:** 35·125/5 = 875 (K_5(5,2)=35 e K_5(6,2)=125, n = 5+6−1 = 10, R = 2+2 = 4). Ou seja, a lacuna entre 875 e 625 é uma lacuna "ADS vs. código linear", não "literatura vs. nada".
3. **Para q=7 as cotas do Kéri (2337 e 1843) são somas diretas, e as ADS equivalentes dariam números bem menores** (K_7(8,3): 1225; K_7(9,4): 931 etc.) **se** houvesse componentes normais. Isso **não** foi confirmado: minhas buscas (SA) por componentes que tornem a ADS válida **falharam** (§1.3). O risco real para a alegação da campanha é essa via; ela fica como resíduo principal, não como predecessor.

## 1. K_7(9,4) ≤ 1285 (e 1351)

### 1.1 Linha do tempo (ano → cota → autor → construção → fonte → LI/RESUMO)

| ano | cota superior | autor | construção | fonte primária | LI/RESUMO |
|---|---|---|---|---|---|
| 2005 | (componentes) K_7(4,2) ≤ 19, K_7(5,2) ≤ 97 | Kéri–Östergård | chave `n` no Kéri | Des. Codes Cryptogr. 37 (2005) 45–60, doi:10.1007/s10623-004-3804-8 — o artigo trata R ≤ 3 e 6 ≤ q ≤ 21 | RESUMO (resumo + referências na página Springer; texto pago) |
| 2006-01-26 | **1843** (LB 224) | Kéri (tabela) | chave `f` = soma direta 97·19 | `https://old.sztaki.hu/~keri/unmixed/bounds/6-21.pdf` (Last-Modified 2006-01-26) | **LI** (`pdftotext`) |
| 2009-10-15 | **1843** (LB 264, Haas–Halupczok–Schlage-Puchta) | Kéri | idem | `https://old.sztaki.hu/~keri/codes/6-21_tables.pdf`, sha256 em `fontes/` | **LI** |
| 2011-11-25 | 1843 | Kéri | `index.htm` não lista mudança em K_7(9,4) | `https://old.sztaki.hu/~keri/codes/index.htm` | **LI** |
| 2026-08-20 | 1743 | Marosi | busca local | arXiv:2608.19872 **v1** | **LI** (já na 1ª revisão; reconferi a linha da tabela) |
| 2026-08-23 / 09-02 | **1475** | Marosi | busca local/LNS (chave de saída `f`) | arXiv:2608.19872 **v2, v3**; anexo `K7_9_4_M1475.txt` | **LI** (tabela e §2; anexo só contado pela 1ª revisão) |
| 2026-10-02 | 1351 → **1285** | campanha | uniões de cosets de [9,3]_7 + retas + palavras soltas | repo (não é literatura) | — |

Antes de 2005 não achei cota para q=7, R=4 (o Kéri só tabula q ≥ 6 a partir de Kéri–Östergård 2005; edições anteriores do site não foram abertas, Wayback bloqueado).

### 1.2 Construções que implicam cota sem escrever K_7(9,4) (propagação)

Regras (direção conferida): (a) K_q(n+1,R) ≤ q·K_q(n,R); (b) K_q(n+1,R+1) ≤ K_q(n,R); (c) K_q(n,R+1) ≤ K_q(n,R); (d) soma direta K_q(n1+n2,R1+R2) ≤ K_q(n1,R1)·K_q(n2,R2). A chave `c` da tabela do Kéri é (b); `e` é (a); `f` é (d).

**Derivação passo a passo (MEDIDO, `scripts/closure.py`):** tomando as células q=7 da tabela do Kéri sem as duas células-alvo e fechando sob (a)–(d), o fecho devolve exatamente 2337 em (8,3) e **1843 em (9,4)**. Passo: K_7(9,4) ≤ K_7(5,2)·K_7(4,2) = 97·19 = **1843** (97 e 19 da chave `n`). Outras rotas: K_7(9,4) ≤ K_7(8,3) = 2337 (b); ≤ 7·K_7(8,4) = 7·343 = 2401 (a). Nenhuma regra incondicional (a)–(d) chega a ≤ 1475, muito menos a ≤ 1285 (MEDIDO). O 1475 do Marosi não vem de propagação (ele mesmo declara que o fecho sob as regras não melhora nada além da Obs. 1; LI v3 §3).

### 1.3 Via condicional: soma direta amalgamada (ADS)

Teorema (Lobstein–van Wee 1989, citado em Kéri `normality.pdf`, LI): se C1 é normal na coordenada de colagem e C2 também, o raio da ADS é ≤ R1+R2, e o tamanho é Σ_a |C1^a||C2^a|, que pode ser levado a ≤ K1·K2/q por permutação de símbolos quando uma das duas é balanceada. Aritmética com as cotas tabeladas (n = n1+n2−1, R = R1+R2):

| componentes | K1·K2/7 | célula |
|---|---|---|
| (4,2)+(6,2): 19·343/7 | **931** | (9,4) |
| (3,1)+(7,3): 25·343/7 | 1225 | (9,4) |
| (5,2)+(5,2): 97·97/7 | 1344,1 | (9,4) |
| (4,1)+(6,3): 123·77/7 | 1353 | (9,4) |

Se algum desses fosse realizável, seria predecessor **de 1351** e (o 931 e o 1225) até **de 1285**. **Não está confirmado**: a ADS só vale com normalidade. O próprio Kéri observa que, para q ≥ 3, d ≤ R+1+R/(q−1) para códigos normais (LI, `normality.pdf`, Teorema 5), o que descarta muitos candidatos.
Teste meu (MEDIDO, `scripts/ads.py`, `t2.py`, `t3.py`): construí C1 de 19 palavras em F_7^4 com raio 2 (SA, 0,35 s) e C2 = [6,3]_7 de raio 2 (colunas aleatórias); o teste exato "para todo (u,a,v), min_b (D1_b(u)+D2_b(v)+[a≠b]) ≤ R" falha para os 24 pares de coordenadas com C1 aleatório; SA sobre C1 (12 000 passos, 4 sementes) não passou de ~2,9·10^5 palavras descobertas em ~4·10^7. Para (3,1)+(7,3): ~2,3–3,8·10^5 descobertas. **Isto é falha de uma busca curta, não prova de impossibilidade.** Contraste: para q=5 o mesmo método existe e funciona na tabela (875 = 35·125/5, §3.2), então a via é real e **precisa de checagem por quem conhece Rivas Soriano / Östergård 1999**.

### 1.4 Estado

* **1285: NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES.** Lido: Kéri 2_tables/4-5/6-21 (2009) + 6-21 (2006) + index.htm + normality.pdf; Marosi v1, v2, v3; Davydov et al. 0904.3835v1, 1808.09301, 2310.02715, 2108.13609, 1712.07078 (nenhum trata q=7, n=9, R=4); lista de 1058 referências de Lobstein (bib-a-jour.pdf, 2023, LI da lista, não dos artigos).
* **1351: idem**, com ressalva da ADS (5,2)+(5,2)=1344 e (4,1)+(6,3)=1353; já superada pela nossa própria 1285.
* Confiança: **média**. Resíduos: (i) Kéri–Östergård 2005 e Rivas Soriano 2005–2008 em texto integral (chave `q`); (ii) CHLL 1997, caps. de ADS/normalidade; (iii) decidir se existe par normal que realiza 931/1225/1344 (problema finito, decidível por busca exata: SAT/ILP sobre C1); (iv) Östergård 1999 (Ars Combin. 52) para saber se q=7 foi tentado por ADS.

## 2. K_7(8,3) ≤ 1887 (e 1893)

### 2.1 Linha do tempo

| ano | cota | autor | construção | fonte | LI/RESUMO |
|---|---|---|---|---|---|
| 2005 | K_7(4,1) ≤ 123 (chave `l`, "adjoint codes"), K_7(4,2) ≤ 19 (`n`) | Kéri–Östergård | adjunto/surjetivo/busca | DCC 37 (2005) 45–60 (escopo R ≤ 3, o que cobre esta célula) | RESUMO |
| 2006-01-26 | **2337** (LB 457) | Kéri | soma direta 123·19 | `unmixed/bounds/6-21.pdf` | **LI** |
| 2009-10-15 | **2337** | Kéri | idem | `codes/6-21_tables.pdf` | **LI** |
| 2011-11-25 | 2337 | Kéri | sem mudança listada | `index.htm` | **LI** |
| 2026-08/09 | 2337 (só LB 471 na Tab. 2) | Marosi v1–v3 | K_7(8,3) não está na Tabela 1 | arXiv:2608.19872 | **LI** |
| 2026-10 | 1893 → 1887 | campanha | 5 cosets de [8,3]_7 + 172 palavras | repo | — |

### 2.2 Propagação

Fecho (a)–(d) devolve **2337 = 123·19** (K_7(4,1)·K_7(4,2)); alternativas: K_7(8,3) ≤ K_7(7,2) = 2401 (b), ≤ 7·K_7(7,3) = 7·343 = 2401 (a). Nenhuma chega a 1887 (MEDIDO). A cota só depende de 123 e 19: verifiquei 123·19 = 2337 e construí um código K_7(4,2) ≤ 19 (SA) para os testes de ADS; **não** reconstruí o de 123.

### 2.3 Via condicional (ADS)

(3,1)+(6,2): 25·343/7 = **1225** < 1887; (4,1)+(5,2): 123·97/7 = 1704,4; (4,2)+(5,1): 19·769/7 = 2087. Teste meu (MEDIDO) para (3,1)+(6,2) com C1 de M palavras e raio 1 em F_7^3 e C2 = [6,3]_7 raio 2: o tamanho da ADS é 49·M, então só interessa M ≤ 38 (49·38 = 1862 < 1887). Melhor SA: M=38 → 490 palavras descobertas (de ~5,8·10^6) em 5000 passos, 2695 em 25 000 passos com outra semente; M=40 → 147; M=42 → 98; **nenhuma chegou a 0**. Resultado inconclusivo, não contraexemplo. Se existir, a cota "1887" seria batida por método publicado (ADS) com ingredientes publicados — por isso é o resíduo mais importante da campanha para este par.

### 2.4 Estado

**1887 e 1893: NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES.** Confiança **média**. Resíduos: mesmos de §1.4; mais o fato de que o artigo que gera 123 e 19 (Kéri–Östergård 2005) foi visto só em resumo.

## 3. K_5(10,4) ≤ 625 (código linear)

### 3.1 Notação (conferida)

Código linear [n,k]_q com covering radius R tem codimensão r = n−k e **K_q(n,R) ≤ q^k**. Aqui n=10, k=4, **r=6**, R=4: a coluna é um conjunto 3-saturante de 10 pontos em PG(5,5), isto é **ℓ_5(6,4) ≤ 10** (ℓ_q(r,R) = s_q(r−1,R−1); LI em 1808.09301 §1 e 2310.02715 §1). Não confundir com r=tR+R/2 (aqui r=6=4+2 pertence à família "tR+R/2, t=1", mas os resultados de 1808.09301 para ela exigem q **quadrado**, e 5 não é; LI).

### 3.2 O que é o nosso código (MEDIDO, `scripts/verifica_625.py`)

Arquivos `data/codes/q5_n10_R4_M625.txt` e `data/structured/q5_n10_R4_M625.json`:
* G (4×10) e H (6×10) do JSON satisfazem G·Hᵀ = 0; as 625 palavras do .txt são **exatamente** o espaço gerado por G (625 distintas, igualdade de conjuntos).
* **Linear [10,4,5]_5**, distribuição de pesos {0:1, 5:12, 6:52, 7:152, 8:192, 9:132, 10:84}; dual [10,6,4]; as 10 colunas de H são pontos projetivos distintos de PG(5,5).
* **Raio exatamente 4**: busca em camadas de síndromes (41 → 761 → 7297 → 15625 = 5^6 síndromes cobertas com ≤ 4 colunas; com ≤ 3 faltam 8328). Proveniência: `generator`/`command` nulos ("busca anterior à v0.3").

### 3.3 Linha do tempo

| ano | cota | autor | construção | fonte | LI/RESUMO |
|---|---|---|---|---|---|
| 1991 | componentes K_5(5,2) ≤ 35, K_5(6,2) ≤ 125 (compatível com [6,3]_5 de raio 2, ℓ_5(3,2) ≤ 6: achei 6 pontos de PG(2,5) por busca aleatória, MEDIDO; que o código de Östergård seja esse eu não li) | Östergård | chave `m` | IEEE Trans. IT 37 (1991) 660–664 | só pela chave no Kéri |
| 1996 | "720" (original) → **875** (correção Kéri 2006-09-19) | Bhandari–Durairajan | ADS (reproduzida: 35·125/5 = **875**, MEDIDO) | IEEE Trans. IT 42 (1996) 1640–1642, doi:10.1109/18.532916 | RESUMO (abstract; IEEE bloqueado 418) |
| 2000 | ℓ_5(5,3) ≤ 10 ([10,5]_5 raio 3, 3125) | Davydov–Östergård | conjunto 2-saturante em PG(4,5) | Eur. J. Combin. 21 (2000) 563–570, doi:10.1006/eujc.1999.0373; citado no `index.htm` ("K5(10,3) ≤ 3125, 2009.09.16") | RESUMO + citação do Kéri (LI) |
| 2009-10-15 | **875** (LB 162) | Kéri | chave `d` | `codes/4-5_tables.pdf` | **LI** |
| 2011-11-25 | 875 | Kéri | `index.htm`: "K5(10,4) ≤ 875 (720 provavelmente erro de impressão)" | idem | **LI** |
| 2019 | tabelas ℓ_q(r,R) com R ≥ 4 só para r=tR (t≥2) e r=tR+R/2 com q quadrado | Davydov–Marcugini–Pambianco | Line+Ovals; códigos | arXiv:1808.09301 v2 / DCC 87 (2019) 2771 | **LI** (intro e Props. 1–2) |

### 3.4 Propagação e comparação com a literatura de códigos lineares

* Sob as regras (a)–(d) e a tabela K_5 do Kéri (R ≤ 4): menor soma direta em (10,4) = 1225 (K_5(5,2)²); a ADS (5,2)+(6,2) dá 875 (e é o que o Kéri lista). Propagar nosso 625: K_5(11,4) ≤ 5·625 = 3125 — **igual** ao `3125 d` da tabela, e K_5(10,4) ≤ K_5(10,3) = 3125 (c) não ajuda.
* Cota "linear" publicada que **eu derivo**: [10,5]_5 de raio 3 (Davydov–Östergård) ⊕ coluna extra de raio 1 = [11,5]_5 de raio 4 = 3125 (soma direta com (r,R)=(1,1)); isto dá ℓ_5(6,4) ≤ 11 e K_5(11,4) ≤ 3125, **exatamente o `d` do Kéri**. Verifiquei que meu programa acha [10,5]_5 raio 3 imediatamente (`scripts/sat10_5_3.log`).
* **Nenhuma tabela ℓ_5(6,4) encontrada.** 0904.3835v1 tem Tabelas I–IV para ℓ_q(r,R) com r ≤ 5 (R=2,3); 1808.09301 só r=tR e q quadrado; 1712.07078 só R=3, r=4,5; 2310.02715/2108.13609 só r=tR+1 (aqui r=6≠5). O catálogo online de Litsyn (CHLL) devolveu 403 e o Wayback está bloqueado pela política de saída; **não contornei**.
* **MEDIDO (heurístico, `scripts/sat.c`, código meu):** n=10, r=6, R=4: achado na 1ª tentativa (0,5 s). n=9: melhor SA deixa 192 síndromes (de 15625) sem cobertura, em 3 sementes × 2–3 reinícios, nunca 0. n=8: 1664. Cota de esfera: n ≥ 8 (soma de bolas 11 565 < 15 625 para n=7; 21 985 para n=8). Logo, **ℓ_5(6,4) ∈ [8,10]**, com 10 provável mas **não provado** (busca limitada). Se n=9 existisse, K_5(9,4) ≤ 125 e K_5(10,4) ≤ 625 por propagação (a) — mas o Kéri lista K_5(9,4) ≤ 255 e eu não achei.

### 3.5 Estado

**NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES.** Lido: Kéri 4-5 (2009) + index.htm; DGMP 0904.3835v1, 1808.09301, 2310.02715, 2108.13609, 1712.07078; Marosi (q ≥ 5, trata K5(11,5), não K5(10,4)); Lobstein 2023 (lista). **Não lido e decisivo:** (i) Bhandari–Durairajan 1996 (o "720" do original pode ser um 625 mal impresso, mas isto é só especulação: 720 ≠ 625); (ii) CHLL 1997 (tabelas de ℓ_q); (iii) Lobstein–Pless "The length function: a revised table" (LNCS 781, 1994); (iv) Davydov 1995 IEEE 41 e Davydov–Östergård 2000; (v) Östergård 1991/1999. Confiança de que **não há predecessor impresso**: **baixa-média**. Recomendação: tratar 625 como "reprodução verificada de um código linear simples", **sem** alegar novidade; pedir a quem tem acesso ao livro de 1997 e ao artigo de 1996 que confira ℓ_5(6,4).

## 4. Cobertura honesta (o que NÃO consegui abrir)

* Bloqueado/pago/inacessível: IEEE Xplore (BD 1996: 418), Springer texto integral (Kéri–Östergård 2005), ScienceDirect (Davydov–Östergård 2000: 403), core.ac.uk (Cloudflare), Litsyn `tablecr` (403), Wayback (`web.archive.org`: política de saída; `archive.org/wayback/available` responde mas o snapshot não), Google Books, CHLL 1997 em geral.
* Só por resumo/chave: Östergård 1991, 1999; Rivas Soriano 2005–2008; Kéri–Östergård 2005; Davydov 1995/2001; Lobstein–Pless 1994.
* `export.arxiv.org` limitou a taxa (429); as buscas feitas (saturating set + covering radius; length function + covering) listam só trabalhos 2018–2026 já conhecidos; 2609.16078 e 2606.16669 não tratam q=5, R=4 (a 1ª revisão fez grep).
* Não executei código de terceiros; só `pdftotext`, `curl`, e programas meus em `scripts/`.
* A tabela do Kéri tem alinhamento ambíguo em células com expoente de classificação (ex.: "715"); só usei valores que reconferi por três leituras (esta, 1ª revisão, Marosi/Florath) ou que o fecho (a)–(d) reproduz.

## 5. Arquivos

`literatura_profunda.csv` (resumo por par), `fontes/sha256_fontes_lidas.txt` (hashes dos PDFs lidos), `scripts/` (`closure.py`, `verifica_625.py`, `sat.c`, `ads.py`, `t2.py`, `t3.py` e logs). Nenhum arquivo fora de `profunda/` foi escrito; git não usado.
