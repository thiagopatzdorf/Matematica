# Revisão de literatura adversarial — covering codes (campanha piloto)

Agente Lit-CC, leitura em 2026-10-03. Rótulos: PROVADO / VERIFICADO (reconferido por mim por conta ou por 2+ leituras independentes) / OBSERVADO (li no texto/arquivo, uma leitura) / HIPÓTESE / DESCONHECIDO.
Regra seguida: nenhuma frase "o artigo diz X" sem versão. **Não alego novidade.** "Estritamente melhor" abaixo compara só com os números que EU li; não é afirmação de que ninguém publicou algo melhor.

## 1. Resposta curta

* O `1475` do README **está no texto** do Marosi (Tabela 1, linha `K7 (9,4) 264–1843 | 221 | 1475 | −368 | 20.0% | f | L`), nas versões **v2 (2026-08-23) e v3 (2026-09-02)**, e é o arquivo anexo `K7_9_4_M1475.txt` (1475 linhas, 1475 distintas, 9 dígitos; sha256 `b3e60549…ac6ace`). **A v1 (2026-08-20) dizia 1743** (resumo e tabela). Não existe v4 (404 em 2026-10-03). [OBSERVADO]
* A "edição" do Kéri: identificada. Ver §3.
* **Nenhuma cota superior publicada que eu tenha lido é ≤ 1285 para K_7(9,4), nem ≤ 1887 para K_7(8,3)**, nem ≤ as nossas nos outros 7 pares. Isso é `MELHORA_APARENTE_A_CONFIRMAR`, não novidade.
* O Marosi (v1–v3) **não** melhora K_7(8,3) (a célula nem está na Tabela 1). A cota publicada que li é a do Kéri: 2337. [OBSERVADO em v1, v2, v3]
* Aviso de método sobre a própria fonte: o Marosi declara (v3, "Use of artificial intelligence") que o manuscrito e o software foram escritos pelo sistema Claude sob direção dele. As tabelas dele conferem com o PDF do Kéri nas células que li (§3), mas é fonte de qualidade a monitorar, não oráculo. [OBSERVADO]

## 2. Tabela por par (melhor cota superior publicada que li)

| par | nossa | melhor publicada (fonte, versão, data) | comparação | classificação | inferior publicada |
|---|---|---|---|---|---|
| K_7(9,4) | 1285 | 1475, Marosi arXiv:2608.19872 **v3** (2026-09-02; igual na v2 de 2026-08-23); v1 = 1743; Kéri = 1843 | ESTRITAMENTE MELHOR (−190, −12,9%) | MELHORA_APARENTE_A_CONFIRMAR | 264 (Kéri, chave m, HHS 2009); Marosi não muda |
| K_7(9,4) | 1351 | 1475 (idem) | ESTRITAMENTE MELHOR (−124, −8,4%); pior que o nosso 1285 | MELHORA_APARENTE_A_CONFIRMAR | 264 |
| K_7(8,3) | 1887 | 2337, Kéri 6-21_tables.pdf, chave f (soma direta; 2337 = 123·19, conta VERIFICADA); Marosi v1–v3 não altera | ESTRITAMENTE MELHOR (−450, −19,3%) | MELHORA_APARENTE_A_CONFIRMAR | 471 (Marosi v2/v3 Tabela 2, certificado SDP); Kéri 457 |
| K_7(8,3) | 1893 | 2337 | ESTRITAMENTE MELHOR (−444); pior que o nosso 1887 | MELHORA_APARENTE_A_CONFIRMAR | 471 |
| K_5(7,2) | 500 | 525, Kéri 4-5_tables.pdf, chave o (Östergård 1999) | ESTRITAMENTE MELHOR (−25) | MELHORA_APARENTE_A_CONFIRMAR | 236 (Gijswijt–Polak v2, 2026-06-19, Tab. 3); Kéri 225 |
| K_4(10,4) | 192 | 208, Kéri 4-5, chave o | ESTRITAMENTE MELHOR (−16) | MELHORA_APARENTE_A_CONFIRMAR (q=4 fora do escopo do Marosi; busca fraca) | 62 (GP v2); Kéri 59 |
| K_5(9,3) | 1250 | 1275, Kéri 4-5, chave d (Bhandari–Durairajan 1996) | ESTRITAMENTE MELHOR (−25) | MELHORA_APARENTE_A_CONFIRMAR | 354 (GP v2); Kéri 330 |
| K_5(10,4) | 625 | 875, Kéri 4-5, chave d (index.htm: "720 é provável erro de impressão") | ESTRITAMENTE MELHOR (−250, −28,6%) vs Kéri; **NÃO COMPARADO** com tabelas de comprimento linear ℓ_5(6,4) | MELHORA_APARENTE_A_CONFIRMAR; é código linear [10,4]_5, pode ter predecessor em tabela que não achei | 177 (GP v2); Kéri 162 |
| K_5(9,5) | 50 | 55, Kéri 4-5, chave d | ESTRITAMENTE MELHOR (−5) | MELHORA_APARENTE_A_CONFIRMAR | 19 (Kéri m; GP v2 Tab. 9 dá 15,67, não melhora) |
| K_5(9,4) | 250 | 255, Kéri 4-5, chave d | ESTRITAMENTE MELHOR (−5) | MELHORA_APARENTE_A_CONFIRMAR | 64 (Kéri m; GP v2 61,18, não melhora) |
| K_2(6,1) | 12 | 12 (exato), Kéri 2_tables.pdf chave c = Stanton–Kalbfleisch 1968 (inferior: 1968 e 1969); Florath repo `reference-data/post-keri` 12–12 | IGUAL | PREDECESSOR_ENCONTRADO (valor tabelado; o artigo de 1968 **não foi lido**) | 12 |

Observações que mudam leitura:
* As melhorias sobre o Kéri em K_5 e K_4 são pequenas (5–25 palavras) exceto K_5(10,4). Pequeno não é suspeito por si, mas é onde um predecessor em tabela de códigos lineares (que não li) mais provavelmente existe. [HIPÓTESE]
* README e paper dizem "K_2(6,1) ≥ 10 ≤ 12 no banco do Florath". O que li em `florath/covering-codes-lean` (commit `bbed9a6`, 2026-09-16): `reference-data/lean/non_mixed_covering_codes.csv` tem `2,6,1,10,12` (o que o Lean dele prova), e `reference-data/post-keri/…csv` tem `2,6,1,12,12` (a tabela de referência dele, citando Stanton–Kalbfleisch). As duas frases são verdadeiras, mas "Florath tem 10≤K≤12" sem dizer "no Lean dele" sugere que ele não conhece o 12 exato. [OBSERVADO]
* O paper Florath arXiv:2606.09600 v1 (2026-06-08): o resumo diz explicitamente "not new record bounds"; K_2(6,1) não aparece no texto (grep). [OBSERVADO]

## 3. Qual edição do Kéri (resolvido)

URL: `https://old.sztaki.hu/~keri/codes/` (http:// dá 404; https funciona). Índice do diretório lido em 2026-10-03:

| arquivo | Last-Modified | sha256 (baixado por mim) |
|---|---|---|
| 2_tables.pdf | 2009-10-15 09:52 | `cce0402d…b4d3ac` |
| 4-5_tables.pdf | 2009-10-15 10:43 | `2fc92770…bad12dd` |
| 6-21_tables.pdf | 2009-10-15 12:05 | `6191ab94…805c62` |
| 3_tables.pdf / mixed_tables.pdf | 2011-11-24 | (não baixados; q=3 e mistos, fora do nosso escopo) |
| index.htm | 2011-11-25 | `b70664cf…575fff` |

A lista "Improvements and corrections" do `index.htm` termina em **2011.11.21** (K3(13,4) e mistos, autor Rivas Soriano); os itens entre 2009-10-14 e 2011 não tocam células q=2,4,5,7 nossas. Logo, "Kéri 2011" no README/paper = o site de 2011-11, mas **as tabelas q=4, 5, 7 e 2 são os PDFs de 2009-10-15**. Recomendo citar "tabelas q=4,5,7 do Kéri, PDF de 2009-10-15, site atualizado até 2011-11-21". [OBSERVADO; datas são do índice Apache do servidor]

Valores lidos por mim no PDF (`pdftotext -layout`): K7(9,4) = `m 264–1843 f`; K7(8,3) = `y 457–2337 f`; K5(7,2) = `m 225–525 o`; K5(9,3) = `p 330–1275 d`; K5(10,4) = `y 162–875 d`; K5(9,5) = `m 19–55 d`; K5(9,4) = `m 64–255 d`; K4(10,4) = `m 59–208 o`; K2(6,1) = `c 12 c`. **Três transcrições independentes concordam** nessas 9 células: a minha, o `cov/bounds.json` do Marosi (coldcase) e o CSV do Florath. [VERIFICADO]
1843 = 97·19 e 2337 = 123·19 (conta VERIFICADA): ambas são somas diretas, não buscas. Isso explica por que um conjunto de cosets as bate.

## 4. Versões do Marosi (arXiv:2608.19872), leitura de cada PDF

* **v1, 2026-08-20** (título "…alphabets of size six and seven"): 9 células, só q∈{6,7}. K7(9,4) ≤ **1743**, K7(8,4) ≤ 329. Sem cotas inferiores.
* **v2, 2026-08-23** (título "…5 ≤ q ≤ 21"): 25 UB + 58 LB. K7(9,4) ≤ **1475**, K7(8,4) ≤ 316, K7(9,5) ≤ 316↓. K7(8,3) só aparece na Tabela 2 (LB 471).
* **v3, 2026-09-02**: 26 UB + 58 LB. K7(9,4) ≤ **1475** (igual), K7(9,5) ≤ 240. K7(8,3): idem v2. Afirma que fechando as regras de propagação não há outras melhorias além da Observação 1 (K17(7,2)).
* Em v2/v3 ele diz que, em 24 das 26 células, "uma busca por M−1 com o orçamento final não achou código". Isso é afirmação sobre a busca local dele, não limite: 1285 vem de outra família (uniões de cosets). [OBSERVADO]
* Repositório `Mapika/coldcase` (clonado raso, só leitura, HEAD `56a8cce`, 2026-08-24, igual ao commit citado no README): `cov/results/` tem 369 arquivos `K7_9_4_M*.txt`, mínimo **1475**; nenhum arquivo ou texto contém 1285, 1351 ou 1887 como tamanho de código. `cov/engine/lincov.c` busca uniões de cosets com M = c·q^k ("não aplicável" quando q^k não divide M; log `K7_9_4_1599.log`), ou seja, o `lincov` por si só não produz 1351/1285 (não múltiplos de 343). Nosso 1351/1285 = cosets + remendo. [OBSERVADO]
* Os anexos `K7_9_4_M1475.txt` (arXiv anc) e `cov/results/K7_9_4_M1475.txt` não foram executados por mim; só contei linhas.

## 5. Origem de M1285 e M1887 no repositório `/home/user/Matematica`

(`git log` **não consultado**: a ordem era não usar git. Usei só arquivos e o campo `provenance`.)

* **M1285**: `data/structured/q7_n9_R4_M1285.json` → gerador `scripts/search/gen.py` (21 linhas), entrada `data/search/p1285.json` (A = `652 132 256 141 231 402`, síndromes s1=98305, s2=38951, 36 representantes de reta com gerador `165653100`, 4 palavras soltas), comando `python3 scripts/search/gen.py data/search/p1285.json data/codes/q7_n9_R4_M1285.txt`, data 2026-10-02, agente `James.V1`. Nota textual: "copiado da VM lean-build2 (~/h/s2/b)". `commit`, `seed`, `repo_commit` = null. Estrutura: 3 cosets de [9,3]_7 + 36 retas + 4 palavras = 1029+252+4 = 1285 (conta VERIFICADA).
  * **Reprodutível?** Parcialmente. O arquivo é regenerável byte a byte a partir de `p1285.json` (teste `test_gen_py_regenerates_1285_byte_for_byte`, citado em `_fatos/PILOT_FACTS.md`; sha256 do arquivo `89cbd6b2…c50f31` conferido por mim; eu não rodei o gerador). **A busca que produziu `p1285.json` não é reprodutível**: nenhum comando, seed ou log de busca no repo; só o parâmetro final. [OBSERVADO]
  * A matriz A do 1285 coincide em 5 das 6 linhas com a do 1351 (`652 132 256 141 231`; última linha 402 vs 544): mesma família de núcleo. [OBSERVADO]
* **M1887**: `data/structured/q7_n8_R3_M1887.json` → "maestro (VM lean-build2, ~/h/s2/maestro): mesmos 5 cosets de [8,3]_7 do 1893 + 172 palavras", `command` = null, 2026-10-02, `James.V1`. Estrutura 5·343 + 172 = 1887. **Não reprodutível** (sem comando/seed/gerador; 172 palavras soltas). O arquivo da VM tem outra ordem (sha `557cf336…`) e o mesmo sha canônico. [OBSERVADO]
* **M1893**: `repo_commit 562fa42`, "busca anterior à v0.3; gerador não registrado". **M1351**: `lincov (Mapika/coldcase)` `56a8cce` para os 3 cosets + 322 palavras de remendo sem registro (= 46 retas, `structure.py`); `command` = null.
* **Por que README/paper citam 1351/1893 e não 1285/1887** (reconstrução por arquivos, HIPÓTESE sobre causa): (1) o único teorema Lean é de 1351 (`K7_9_4_le_1351_kernel`, 95 pedaços, ~12,4 CPU-h, medida de 2026-10-01); o README é redigido em volta do que o kernel aceitou. (2) O `nota.md` (mtime 2026-10-01 17:49) e o paper falam de 1351 e 1893; 1285 e 1887 só entram em `docs/code-format.md` (linhas 84–85) e nos JSON de 2026-10-02, e README/paper/nota não foram atualizados depois (grep: 0 ocorrências de 1285/1887 fora de `data/`, `scripts/`, `tests/`, `docs/`, campanha). (3) 1285 e 1887 vieram da VM `lean-build2` no dia seguinte, sem Lean. Consequência: o texto público diz "melhor que encontramos 1351" enquanto o repo tem 1285 verificado em C. [OBSERVADO]

## 6. Consultas e URLs (todas)

Abertas com sucesso:
* arxiv.org/abs/2608.19872 (histórico v1–v3); /pdf/2608.19872v1, v2, v3 (v4, v5 = 404); arxiv.org/src/2608.19872v3/anc (listagem), `.../anc/README.txt`, `.../anc/K7_9_4_M1475.txt`.
* github.com/Mapika/coldcase (clone raso anônimo via git proxy, HEAD 56a8cce; `gh api` e codeload deram 403 "não habilitado", então usei o caminho indicado pela ferramenta `add_repo`, só leitura).
* github.com/florath/covering-codes-lean (clone raso, HEAD bbed9a6, 2026-09-16); arxiv.org/abs|pdf/2606.09600 (v1 apenas).
* arxiv.org/abs|pdf/2504.01932 (v2, 2026-06-19; **v1 de 2025-04-02 não lida**); 2606.16688 (K8(4,2)=23, irrelevante); 0904.3835 (v1) e 1808.09301 (v2) de Davydov et al.; 2608.12595, 2605.19094, 2609.16078, 2606.15379 (grep por nossas células: 0 ocorrências).
* old.sztaki.hu/~keri/codes/ (índice), `2_tables.pdf`, `4-5_tables.pdf`, `6-21_tables.pdf`, `index.htm`.
* export.arxiv.org/api/query (≈14 buscas): `all:"codimension tR"`; `au:Davydov AND au:Marcugini AND abs:covering`; `abs:"covering code(s)"`; `ti:"covering codes"`; `all:"football pool"`; `abs:"K_q(n,R)"`; `abs:"covering code" AND abs:Lean`; `abs:"saturating set"`; `abs:"covering codes" AND abs:semidefinite|"local search"`; `abs:"covering radius" AND abs:"upper bound" AND abs:Hamming`; etc., filtrando data ≥ 2026-05. Resultado: nenhum trabalho novo (2026-06 a 2026-10-03) com cotas superiores para q∈{4,5,7} além do Marosi e do Florath.
* WebSearch (7): "Davydov Marcugini Pambianco linear nonbinary covering codes … ℓ_q(r,R)"; ""covering codes" new upper bound K_q(n,R) arXiv 2026 table Kéri improved"; ""K_7(9,4)" OR "K7(9,4)" covering code upper bound"; "quaternary covering codes K_4(10,4) upper bound 208 improved"; "quinary covering codes K_5(9,3) K_5(9,4) K_5(10,4) new upper bound linear code [10,4]_5 …"; "covering codes arXiv 2026 football pool … septenary q=7 local search tables"; duas sobre ℓ_5(6,4)/3-saturating PG(5,5).

**NÃO consegui abrir / não li:**
* Wayback Machine (`web.archive.org`, `archive.org/wayback/available`, CDX): 503 "Internet Archive: Temporarily Offline" / connection reset. Logo **não vi edições antigas** do Kéri nem verifiquei se a página mudou além do que o servidor atual serve.
* Cohen–Honkala–Litsyn–Lobstein, *Covering Codes* (1997), Östergård 1999, Bhandari–Durairajan 1996, Stanton–Kalbfleisch 1968 (conteúdo), Haas et al.: paywall/não buscados. Bibliografia de Lobstein: não consultada. Springer/IEEE: só resultado de busca.
* Tabelas de comprimento linear ℓ_q(r,R) com r=6, R=4, q=5: nas tabelas de 0904.3835 v1 (r=3,4,5) e na 1808.09301 v2 (r=tR, tR+R/2 só para q quadrado) **não há ℓ_5(6,4)**; não achei outra fonte. K_5(10,4)=625 fica sem comparação com a literatura de códigos lineares.
* Gijswijt–Polak v1; páginas HTML do arXiv; Lean `florath` em nível de prova (não compilei); qualquer GitHub além dos dois repos.
* Não executei código de terceiros (só `wc`, `sort -u`, `sha256sum`, `pdftotext`, `git clone`).

## 7. Perguntas abertas

1. O `1285` e o `1887` têm predecessor em literatura que não achei (livro de 1997, tabelas lineares, trabalho de Östergård/Rivas Soriano pós-2011 não indexado no arXiv)? DESCONHECIDO.
2. Por que a busca local do Marosi para em 1475 e uniões de cosets chegam a 1285? Gap de 190 palavras (12,9%). HIPÓTESE: a busca livre não encontra estrutura de coset; testável rodando o `lincov`/estrutura dele em k=3 com M não múltiplo de 343 — não feito.
3. K_5(10,4)=625 já é conhecido por [10,4]_5? Falta ℓ_5(6,4) em tabela (§6).
4. Os 10 códigos são verificados só em C por nós; verificar o 1285 com o `verify_cov.py` do Marosi (código de terceiros, não executado aqui) seria independência real.
5. Um autor externo reproduziria a busca do `p1285.json`? Sem comando/seed, não.

## 8. Cobertura honesta

Lido de verdade: três versões do Marosi (texto + tabelas), arquivo anexo 1475 (contagem), três PDFs do Kéri + `index.htm`, Gijswijt–Polak v2 (tabelas), Florath (resumo, repo, CSVs), repo coldcase (README, NOTES, logs, listas de arquivos, bounds.json), tabelas de Davydov et al. (parcial), campanha e scripts do repo. Não lido: livros e artigos antigos que originam as chaves d, o, f, m, p do Kéri; qualquer coisa fora do arXiv/GitHub/Kéri depois de 2011. A busca no arXiv cobre 2026-05 a 2026-10-03 com palavras "covering code(s)", "saturating set", "football pool", "K_q(n,R)"; um artigo que use outro vocabulário passaria. **"Não achei predecessor" ≠ "não existe".**
