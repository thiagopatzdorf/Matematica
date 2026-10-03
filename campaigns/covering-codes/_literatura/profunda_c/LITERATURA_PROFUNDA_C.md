# Literatura profunda C — K_7(9,4) ≤ 1137/1141, soma direta amalgamada, K_5(10,4) = 625

Agente LC, 2026-10-03. Complementa `../LITERATURA_CC.md`, `../profunda/` e `../profunda_b/`; não os substitui. Escrevi só em `profunda_c/`. Git não usado; US$0; nenhum código de terceiros executado (usei `numpy`, `scipy` e `pysat`/glucose4 como bibliotecas padrão, e dados baixados só foram lidos/contados).
Rótulos: **LI** = li o texto/arquivo hoje; **RESUMO** = só resumo/citação; **MEDIDO** = conta ou programa meu em `scripts/`, com log em `logs/`.
**Estados permitidos:** `PREDECESSOR_FOUND`, `NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES`, `AMBIGUOUS`. Nunca `NOVELTY_EXTERNALLY_CONFIRMED`. "Não encontrei" ≠ "não existe".

## 0. Resposta curta

| item | estado | confiança | em uma frase |
|---|---|---|---|
| K_7(9,4) ≤ **1137** | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES | média | melhor anterior lido: 1475 (Marosi v2/v3); sem v4, sem artigo posterior sobre q=7 até 2026-10-03 |
| K_7(9,4) ≤ **1141** | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES | média | idem (1141 > 1137, mesma fonte anterior) |
| K_7(9,4) via **ADS** (931 condicional) | AMBIGUOUS (resíduo) | baixa | a ADS (4,19,2)+[6,3]_7 daria 931 < 1137 **se** existir par válido; minha busca SAT exata para o par **não decidiu** (§1.4) |
| K_5(10,4) ≤ **625** | AMBIGUOUS | baixa | código linear [10,4,5]_5 achável por busca local em segundos; nenhuma tabela ℓ_5(6,4) alcançável; fonte primária decisiva (BD1996/CHLL) paywall/bloqueada |
| `STATE_OF_ART.md` | ver `CHECAGEM_STATE_OF_ART.md` | — | números conferem; 5 pontos de redação a corrigir |

Três achados novos desta rodada:
1. **O Marosi (v1–v3) não usa ADS**: o texto (v3 §2) lista como propagação só soma direta simples, `K(n+1,R) ≤ qK(n,R)`, `K(n+1,R+1) ≤ K(n,R)` e produto de alfabeto; `grep amalgam` → 0 nas três versões. Já o **Kéri usa ADS em q=7**: `K7(10,2) ≤ 420175`, Rivas Soriano, 2006-09-25, "Method: Amalgamated direct sum" (`index.htm`, LI) — e 420175 = 25·117649/7 = K_7(3,1)·K_7(8,1)/7 (código de Hamming perfeito [8,6]_7), conta MEDIDA. Logo ADS em q=7 é ferramenta estabelecida, e a ausência dela na célula (9,4) é **ausência de resultado, não de método**. Isso explica por que o resíduo ADS não pode ser descartado por leitura.
2. **O 1843 do Kéri para K_7(9,4) não vem de artigo**: Kéri–Östergård 2005 (DCC 37:45–60) cobre **R ≤ 3** (resumo, LI hoje: "6 ≤ q ≤ 21 and R ≤ 3"). A célula R = 4 é entrada de tabela web, chave `f` (soma direta simples 97·19). Portanto o "melhor anterior" pré-2026 para (9,4) é **um número de tabela**, e a literatura revisada por pares sobre essa célula é, nas fontes lidas, inexistente.
3. **A condição exata da ADS** (§1.3) é verificável célula a célula e eu a implementei e **validei contra força bruta** (18/18 testes concordam); o encaixe SAT funciona, mas não fecha o caso (§1.4).

---

## 1. K_7(9,4) ≤ 1137 e ≤ 1141

### 1.1 Linha do tempo (ano → cota → autor → construção → fonte → LI/RESUMO)

| data | UB | LB | autor | construção | fonte | LI / RESUMO |
|---|---|---|---|---|---|---|
| 2005 | (componentes) K_7(4,2) ≤ 19, K_7(5,2) ≤ 97 | — | Kéri–Östergård | chave `n` | DCC 37 (2005) 45–60, doi:10.1007/s10623-004-3804-8 (escopo R ≤ 3) | **RESUMO** (página Springer, abstract lido hoje; texto pago) |
| 2006-01-26 | 1843 | 224 | Kéri | soma direta 97·19 | `old.sztaki.hu/~keri/unmixed/bounds/6-21.pdf` | V-outro (`profunda/`); **não reconferi** |
| 2006-09-25 | — (K7(10,2) ≤ 420175 por ADS) | — | Rivas Soriano | ADS | `keri/codes/index.htm` | **LI** hoje |
| 2007-08-30 | — | 227 | Kéri compila | — | `index.htm` ("K7(9,4)>=227") | **LI** hoje |
| 2009-10-15 | **1843** | **264** | Kéri / Haas–Halupczok–Schlage-Puchta (LB, chave `m`) | soma direta (chave `f`) | `6-21_tables.pdf`, sha256 `6191ab94…`, linha `9 m 264–1843 f` | **LI** hoje |
| 2011-11-25 | 1843 | 264 | Kéri | sem mudança em (9,4) | `index.htm` (Last-Modified 25 Nov 2011) | **LI** hoje (sem entrada para K7(9,4) nas melhorias) |
| 2026-08-20 | **1743** | — | Marosi | rótulo "direct sum" na tabela da v1 | arXiv:2608.19872 v1 (resumo + linha 74) | **LI** hoje |
| 2026-08-23 | **1475** | 264 (sem melhora) | Marosi | `f`/`L` (busca local) | v2, Tabela 1, linha 170 | **LI** hoje |
| 2026-09-02 | **1475** | 264 | Marosi | idem | v3, Tabela 1, linha 119; anexo `K7_9_4_M1475.txt` sha256 `b3e60549…` | **LI** hoje; anexo **reverificado por mim**: 1475 distintas, 0 descobertas |
| 2026-10-02 | 1285 → 1141 → **1137** | — | esta campanha | cosets de [9,3]_7 + remendo | repo (não é literatura) | — |

Outros autores: Kéri (nenhuma entrada q=7, R=4 em `index.htm`); Florath (arXiv:2606.09600, "not new record bounds"; só certifica 2401 por propagação, V-outro); Gijswijt–Polak (só LB, q ≤ 5). Nada de 2026 além do Marosi toca q=7, n=9, R=4.

**O que pode ter aparecido de novo — checado hoje (2026-10-03):**
* **Marosi:** a página `arxiv.org/abs/2608.19872` lista só v1 (20 Aug 2026), v2 (23 Aug), v3 (2 Sep). `…v4` e `…v5` → 404. Sem journal-ref. Título atual: "New upper and lower bounds on covering codes K_q(n,R) for alphabets of size 5 ≤ q ≤ 21". O resumo da v3 diz "84 cases (83 distinct cells)" e "Twenty-six upper bounds"; a K7(9,4) não muda entre v2 e v3.
* **Outros artigos arXiv** (11 consultas à API, `logs/arxiv_api_2026-10-03.log`): o mais recente sobre covering codes é 2609.16078 (2026-09-13, binário R=2, saturating sets); 2608.24856 (2026-08-25, taxa assintótica de "generalized covering codes"), 2608.12595 (2026-08-12, nearly perfect), 2607.14840 (covering sequences), 2606.15379, 2606.16688 (K_8(4,2)=23), 2606.16669 (raios generalizados), 2606.09600 (Florath), 2511.02542 (cotas superiores para códigos lineares **binários**), 2305.11955 (R=3, codim 3t+1), 2310.02715, 2108.13609, 1808.09301, 1712.07078, 0904.3835. **Nenhum** trata K_q(n,R) com q=7 além do Marosi. Consultas por "Keri", "amalgamated direct sum", "normal code", "football pool", "length function", "saturating sets" não trouxeram artigo novo relevante (ruído: "Amalgamated direct sums of operator spaces" é análise funcional).
* **Limites:** a API do arXiv indexa por palavra; um artigo com vocabulário diferente passaria. Google Scholar, MathSciNet/zbMATH, periódicos pagos e páginas pessoais (Östergård, Kéri, Rivas Soriano, Davydov) não foram vistos.

### 1.2 Propagação simples (herdada de `profunda/`)
Fecho sob (a) K(n+1,R) ≤ qK(n,R), (b) K(n+1,R+1) ≤ K(n,R), (c) K(n,R+1) ≤ K(n,R), (d) soma direta, partindo da tabela do Kéri sem a célula-alvo, devolve **1843** (97·19) em (9,4) e 2337 em (8,3) (`profunda/scripts/closure.py`, MEDIDO por LA; eu reconferi a aritmética). Nada chega a ≤ 1475.

### 1.3 Soma direta amalgamada (ADS) q = 7: derivação

**Definição e condição exata.** Seja F o alfabeto, |F| = q = 7. Tome C1 ⊂ F^{n1} e C2 ⊂ F^{n2} e uma coordenada de cada um. Escreva palavras de C1 como (u,a) (a = símbolo da coordenada escolhida, u ∈ F^{n1−1}) e de C2 como (b,v). Seja C1_a = {u : (u,a) ∈ C1}, C2_b = {v : (b,v) ∈ C2}. A ADS é
 C = { (u, a, v) : u ∈ C1_a, v ∈ C2_a } ⊂ F^{n1+n2−1}, |C| = Σ_a |C1_a|·|C2_a|.

Para (x, z, y) ∈ F^{n1−1} × F × F^{n2−1}: d((x,z,y), C) = min_a [ D1_a(x) + [a ≠ z] + D2_a(y) ], com D1_a(x) = d(x, C1_a), D2_a(y) = d(y, C2_a) (distâncias de Hamming nas n_i − 1 coordenadas restantes; ∞ se o conjunto é vazio). Portanto

**(E)** raio(C) ≤ R ⇔ ∀ x, y, z ∃ a : D1_a(x) + D2_a(y) + [a ≠ z] ≤ R.

(E) é **necessária e suficiente**; não usa "normalidade". Forma local: com s_a = D1_a(x) + D2_a(y), (E) falha exatamente quando existe z com s_z ≥ R+1 e s_a ≥ R para todo a ≠ z. A condição clássica (Graham–Sloane 1985 para q = 2; Lobstein–van Wee 1989 e Honkala para q-ário: "C1 e C2 normais/aceitáveis nas coordenadas de colagem ⇒ raio ≤ R1+R2") é **suficiente**; não li a definição q-ária nos artigos primários (Kéri `normality.pdf` foi lido por LA), e (E) dispensa isso. Para R = R1 + R2, se C1 tem raio R1 e C2 tem raio R2, **(E) pode falhar**, e é essa falha que os testes de LA/LB mediram.

**Tamanho.** Se C2 é **linear** [n2,k]_q e a coluna de colagem é não nula, cada C2_b tem q^{k−1} palavras, então |C| = q^{k−1}·|C1| = |C1||C2|/q **para qualquer C1** (balanceamento só é exigido de um lado). Com q = 7, k = 3: |C| = 49·|C1|.

**Envelope aritmético para K_7(9,4)** (n1 + n2 = 10, R1 + R2 = 4, cotas superiores q=7 do Kéri, lidas de `keri_6-21.pdf`; `scripts/ads_envelope.py`):

| split | K1·K2/7 | alcança |
|---|---|---|
| (4,2,19) + (6,2,343) | **931** | < 1137 e < 1141 |
| (3,1,25) + (7,3,343) | 1225 | > 1141 (não ameaça 1137/1141; ameaça só 1285/1351) |
| (5,2,97) + (5,2,97) | 1344,1 | idem |
| (4,1,123) + (6,3,77) | 1353 | idem |

Para 1137 e 1141 **só o 931 importa**: precisa C1 = (4, 19, 2)_7 (K_7(4,2) ≤ 19, chave `n`) e C2 = [6,3]_7 de raio 2 (`K7(6,2) = 343`, chave `p` = código linear). Para K_7(8,3): (3,1,25)+(6,2,343) → 1225 (< 1887).

**Procedimento exato (decisão por SAT) para "existe C1 com |C1| ≤ M1 tal que a ADS com um dado C2 tem raio ≤ 4?"**
1. Enumerar C2 = [6,3]_7 de raio ≤ 2: 6 pontos de PG(2,7) que cobrem o plano com combinações de ≤ 2 (1-saturante). Fixando um referencial (e1,e2,e3,(1,1,1)) ⊂ S: C(53,2) = 1378 candidatos, **88** de raio ≤ 2 (MEDIDO, `scripts/c2_classes.py`). Conjuntos sem 4 pontos em posição geral (cabem em uma reta + 1 ponto) não são saturantes (argumento: 5 em uma reta L + 1 ponto p cobre no máximo 5 das 8 retas por p fora de L), então a lista cobre toda classe linear. Escolher a coluna de colagem j (6 escolhas) → 528 pares (C2,j) (com redundância por simetria; não reduzi).
2. Perfis de C2: para cada y ∈ F^5 (16807), r(y) = (d(y,C2_b))_{b∈F} ∈ N^7. Sobram 49–113 perfis distintos por C2.
3. Para cada perfil r e cada z ∈ F: τ_a = max(0, R − r_a) (a ≠ z), τ_z = max(0, R + 1 − r_z). Guardar os τ **minimais** (161–231 por C2). Se algum τ = 0, nenhum C1 serve (não ocorreu em 528 pares).
4. Variáveis y_{c,a} (c ∈ F^3, a ∈ F: 2401). Para cada x ∈ F^3 e cada τ minimal: cláusula "∃ a com τ_a ≥ 1 e uma palavra (c,a) ∈ C1 com d(x,c) ≤ τ_a − 1" (uma variável auxiliar z_{x,a,t} ⇒ OR dos y na bola). Cardinalidade Σ y ≤ M1 (contador sequencial). Simetria: uma palavra com u = 0.
5. SAT ⇒ C1; montar a ADS (49·|C1| palavras) e **verificar por dilatação no espaço inteiro** (`scripts/ads_verify.py`, independente do SAT). UNSAT ⇒ só vale para este (C2, j, M1).

**Validação do codificador (MEDIDO, `scripts/test_encoding.py`, `logs/test_encoding.log`):** C1 aleatórios de 30–1200 palavras, C2 fixo: "cláusulas satisfeitas" ⇔ "ADS tem raio ≤ 4 por força bruta em F_7^9" em **18/18** casos (positivos e negativos, limiar entre 100 e 110 palavras aleatórias). Um SAT obtido (`ads_sat_0_0_60.json`, C1 de 59 palavras) virou uma ADS de **2891** palavras com raio exato 4 (verificada). Logo o codificador é correto nas duas direções nos casos testados.

### 1.4 Custo e resultado do teste de viabilidade

**Tamanho da instância (n1 = 4):** 2401 variáveis primárias + ≈ 9,6 mil auxiliares; 343 × 231 ≈ 79 mil cláusulas de ≤ 7 literais + definições com até 343 literais; contador de cardinalidade ≈ 2401·M1 auxiliares.
**Alvo:** M1 ≤ 19 (→ 931) ou M1 ≤ 23 (49·23 = 1127 < 1137; 49·24 = 1176 > 1137). Para batê-lo é preciso |C1| ≤ 23.

Resultados (glucose4 via `pysat`; orçamento em conflitos, ~1 mil conflitos/s para n1 = 4, ~10 mil/s para n1 = 3; `logs/ads_*`):

| instância | M1 testado | resultado | observação |
|---|---|---|---|
| (4,·)+[6,3]_7, C2 #0, j = 0 | ≤ 60, 55, 50 | **SAT** em ≤ 0,1 s | ADS ≈ 2450–2940 (inútil) |
| idem, j = 3 | ≤ 50 | **SAT** em 0,0 s | |
| idem (j = 0 e j = 3) | ≤ 48, 46, 42, 38 | UNKNOWN (80 mil conflitos, 49–132 s cada) | C2 #1, j = 3: ≤ 50 SAT em 0,1 s |
| idem, abortado | ≤ 40, 45 com 600 mil conflitos | sem resposta em > 30 min (abortei) | `*_ABORTADO.log` |
| (3,·)+[6,3]_7 → K_7(8,3), C2 #0, j = 0 | ≤ 38, ≤ 30 | UNKNOWN (1,2 milhão de conflitos, ~2 min cada) | alvo: M1 ≤ 38 → ADS ≤ 1862 < 1887 |
| idem, C2 #1 | ≤ 38, ≤ 30 | UNKNOWN | |

(Linhas completas em `logs/ads_n4_j0_escada.log` e `logs/ads_n4_j3_escada.log`; as rodadas que não terminaram antes do fechamento foram interrompidas por mim e o que faltou **não** foi rodado.)

**Cota inferior rigorosa e fraca (MEDIDO, `scripts/ads_lp_bound.py`, `logs/lp_n4.log`):** a média de um C1 viável sobre as 343 translações de F^3 é um ponto fracionário viável com y_{c,a} = w_a constante; o LP resultante (7 variáveis w_a) dá |C1| ≥ 10,77 → ≥ 11 → |ADS| ≥ 539 no pior dos 528 pares (C2,j). **Isto não exclui 19 nem 23.**

**Leitura honesta:**
* O que foi **provado** (por construção + verificação): ADS com C1 de 59 palavras e C2 linear funciona (raio 4, 2891 palavras). Isso mostra que o método é implementável e correto, não que 931 exista.
* O que **não** foi decidido: se existe C1 com |C1| ≤ 23 para algum dos 528 pares. A fronteira que o CDCL puro atinge em minutos é |C1| ≈ 46–50 (ADS ≈ 2254–2450), muito acima de 23. Isso é **falha de busca, não impossibilidade**. Duas razões estruturais pelas quais o UNSAT em M1 ≈ 19–23 não sai barato: (i) simetria do lado de C1 de ordem 3!·7!^3 ≈ 7,8·10^11 (permutações dos 3 coordenadas e dos 7 símbolos em cada), sem quebra de simetria além de uma palavra em u = 0; (ii) C(2401, 19) ≈ 10^48 subconjuntos. Uma prova de UNSAT exigiria geração ortodoxa/quebra de simetria completa (ou SAT incremental com cubos), da ordem de CPU-dias, **não** de minutos, e ainda cobriria só C2 lineares (C2 não linear não foi explorado).
* Teste do alvo menor (K_7(8,3), n1 = 3, só 343 variáveis): UNKNOWN com 1,2 milhão de conflitos; também não decide.
* **Qual teste de LA ficou ainda mais fraco que o meu:** LA usou SA com pontuação "palavras descobertas" e ficou em ~2,9·10^5; o meu usa a condição exata (E) e prova correção, mas o resultado é o mesmo em substância: **inconclusivo**.

**Consequência para a alegação:** para 1137/1141 a via ADS só deixa em aberto o 931 (único split abaixo de 1141). Ninguém publicou um par normal (4,19,2)+[6,3]_7 que eu tenha lido, e o Marosi não usa ADS; mas **não consegui excluir que exista**. É o resíduo principal, e é decidível (finito) com mais CPU e quebra de simetria.

### 1.5 Estado
* **1137, 1141: `NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES`, confiança média.** Lido: Marosi v1–v3 (texto/tabelas), anexo 1475 (reverificado), Kéri 6-21 (2009) + `index.htm` + legenda de chaves, KÖ2005 (abstract), GP v2 (datas), Florath (resumo), Davydov et al. (0904.3835, 1808.09301, 2310.02715, 2108.13609, 2305.11955, 1712.07078 — nenhum q=7, n=9, R=4).
* **Resíduos:** (i) ADS 931 (acima); (ii) KÖ2005 e Rivas Soriano 2005–2008 em texto integral (como ADS foi usada em q=7); (iii) CHLL 1997 (cap. 3.x e 5.x ADS/normalidade); (iv) Kéri 2010 sobre normalidade de códigos ótimos (Lobstein bib [577]); (v) edições do Kéri anteriores a 2006 (Wayback fora do ar); (vi) `Mapika/coldcase` e Florath não reconferidos por mim.

---

## 2. `STATE_OF_ART.md`

Ver **`CHECAGEM_STATE_OF_ART.md`**: 27 afirmações listadas; os números conferem (reproduzi o anexo 1475); apontei 1 discrepância (frase "Nada foi publicado" vs README/DOI), 1 imprecisão (verificação "exaustiva" ≠ "busca"), a falta de dizer que 1843 é tabela web e que o Marosi é preprint com autoria assistida por Claude, e o resíduo ADS não mencionado.

---

## 3. K_5(10,4) = 625

### 3.1 O que o código é (herdado e reconferido)
`data/codes/q5_n10_R4_M625.txt` tem 625 palavras distintas e **raio exato 4** (MEDIDO por mim hoje, dilatação sobre 5^10; `scripts/l5_6_4.py`, `logs/l5_6_4.log`); `profunda/` mostrou G·Hᵀ = 0, [10,4,5]_5, 10 pontos de PG(5,5). Equivale a **ℓ_5(6,4) ≤ 10** (10 pontos 3-saturantes em PG(5,5)); K_5(10,4) ≤ 5^4 = 625.

### 3.2 O que li (fontes e o que dizem sobre q = 5, R = 4)
| fonte | LI/RESUMO | o que traz | tem ℓ_5(6,4)? |
|---|---|---|---|
| Kéri `4-5_tables.pdf` e `index.htm` (2009/2011) | **LI** | K5(10,4) ≤ 875, chave `d`; `index.htm`: "2006.09.19 Correction: K5(10,4)<=875. (The bound 720 is probably a misprint in the cited reference.)" | não |
| Kéri `index.htm` | **LI** | **incorpora** resultados lineares de saturantes: "2009.09.16 K5(10,3)<=3125, from a 2-saturating set in PG(4,5). Author: Davydov and Östergård, 2000" | indício (§3.3) |
| Davydov–Giulietti–Marcugini–Pambianco, arXiv:0904.3835 (Adv. Math. Commun. 5 (2011) 119, doi:10.3934/amc.2011.5.119) | **LI** (texto) | tabelas de ℓ_q(r,R) para r ≤ 5 (R = 2,3) | não (r = 6) |
| Davydov–Marcugini–Pambianco, arXiv:1808.09301 v2 (DCC 87 (2019)) | **LI** (intro, Prop. 1–2, Teoremas 1–2) | r = tR (t ≥ 2) e r = tR + R/2 com **q quadrado**; "codes with R ≥ 4, r = tR, have not been extensively studied". Teorema 1(ii): ℓ_5(8,4) ≤ 4·5 + 1 = 21 (Δ = 0 para q = 5, R = 4, 5, t = 2) | **não** (r = 6 = R + R/2, mas q = 5 não é quadrado) |
| arXiv:2310.02715, 2108.13609, 2305.11955 (DMP 2021–2023) | **LI** (introdução + grep) | r = tR + 1 (aqui r = 6 ≠ 5) e R = 3, r = 3t+1 | não |
| arXiv:1712.07078 | **LI** | R = 3, r = 4,5 | não |
| arXiv:1007.0906 ("Matrix Algebras and Semidefinite Programming Techniques for Codes", tese, v1 2010-07-06) | baixado; só o cabeçalho conferido, **não lido** | SDP/LB, não UB lineares (inferido do título) | não verificado |
| Bhandari–Durairajan, IEEE IT 42 (1996) 1640–1642, doi:10.1109/18.532916 | **RESUMO** (IEEE → HTTP 418, tentei `iel1/…/00532916.pdf`; não contornei) | "Two strongly seminormal codes over Z_5 … conjecture of Östergård … improvements in seven upper bounds" | desconhecido |
| Lobstein–Pless, "The length function: a revised table", LNCS 781 (1994) | **RESUMO** (página Springer: tabela **binária**, 2 ≤ m ≤ 24, 2 ≤ r ≤ 12) | q = 2 apenas | não aplicável |
| Litsyn, `tablecr/index.html` | 403 (não contornei) | catálogo online de CHLL | desconhecido |
| Cohen–Honkala–Litsyn–Lobstein 1997 | não acessível | tabelas ℓ_q | desconhecido |

**Resultado:** nenhuma tabela lida contém ℓ_5(6,4). Não achei fonte que implique K_5(10,4) ≤ 625 ou menos.

### 3.3 Evidências indiretas (rotuladas como tal)
* **A favor de "não havia predecessor impresso conhecido do Kéri até 2011":** o Kéri **incorporou em 2009** o K5(10,3) ≤ 3125 de uma saturante linear (Davydov–Östergård 2000), e o seu mapeamento de chaves tem "p = linear code". Se uma tabela de ℓ_q com ℓ_5(6,4) ≤ 10 estivesse em CHLL 1997, seria natural vê-la em K5(10,4) em 2009–2011. **Inferência**, não prova: o Kéri pode não ter lido a linha.
* **Contra confiar nisso:** (a) o "720" original de BD1996 para K5(10,4) é **valor não explicado** (≠ 625; ≠ 875; o Kéri o chamou erro de impressão); (b) o código é **fácil de achar por busca local**: `profunda/` achou em 0,5 s; eu repeti com um hill-climb de 1 coluna (`scripts/l5_ls.py`, 3 sementes: raio 4 após 2, 22 e 33 iterações, 1,6–17 s, `logs/l5_ls_n10.log`), enquanto **amostragem puramente aleatória não acha** (300 conjuntos de 10 colunas: todos de raio 5, `logs/l5_6_4.log`). Ou seja, não é "trivial a olho", mas qualquer varredura heurística de saturantes em PG(5,5) o acharia; (c) a razão de volume (soma de bolas de raio 4 em n = 10 = 62201 contra 5^6 = 15625, fator ≈ 4) é folgada. Para n = 9 o mesmo hill-climb parou em 208–224 síndromes descobertas em 50 s (`logs/l5_ls_n9.log`; consistente com os 192 de `profunda/`; **não** é prova de ℓ_5(6,4) = 10).
* **Derivação que eu fiz com tabela lida:** ℓ_5(5,3) = 10 (Davydov–Östergård 2000, via Kéri) + soma direta com uma coluna extra dá ℓ_5(6,4) ≤ 11 → K5(11,4) ≤ 3125 (= a entrada `d` do Kéri). O passo de 11 para 10 **não** está em fonte lida.

### 3.4 Estado
**AMBIGUOUS, confiança baixa.** Razão: (i) nenhum predecessor achado, (ii) mas a construção é elementar (busca local de segundos) e provavelmente tabelável, (iii) as fontes decisivas (BD1996 texto, CHLL 1997, Lobstein–Pless q-ário se existir, Davydov 1995 IEEE 41) estão atrás de paywall ou 403. **Recomendação:** tratar 625 como "reprodução verificada de um código linear simples"; não alegar novidade; pedir a quem tiver o livro de 1997 e o artigo de 1996 que confira a linha ℓ_5(6,4) e o "720".

---

## 4. Cobertura honesta (o que NÃO consegui)
* Bloqueado/pago: IEEE Xplore (418), Springer texto integral, Litsyn (403), Wayback (já indisponível para os outros agentes; não tentei de novo), academia.edu (403), CHLL 1997, Google Scholar, MathSciNet/zbMATH.
* Não reconferido por mim: `Mapika/coldcase` (commits, 369 arquivos), `florath/covering-codes-lean` (2401), `CoveringCodes` (GP), edições do Kéri de 2006-01-26, normality.pdf.
* A busca no arXiv usa 11 consultas por palavra-chave; vocabulário diferente passa.
* Instâncias SAT: um C2 / poucos C2 e j = 0 ou 3; **não** varri os 528 pares com orçamento suficiente; só C2 lineares.
* `AMBIGUOUS` aqui significa "não decidi", não "provavelmente existe".

## 5. Arquivos
`literatura_profunda_c.csv` (resumo), `CHECAGEM_STATE_OF_ART.md`, `scripts/` (`ads_exact.py`, `ads_verify.py`, `ads_lp_bound.py`, `ads_envelope.py`, `c2_classes.py`, `test_encoding.py`, `l5_6_4.py`, `arxiv_q.py`), `logs/`, `fontes/` (+ `SHA256SUMS`). Nada fora de `profunda_c/` foi escrito.
