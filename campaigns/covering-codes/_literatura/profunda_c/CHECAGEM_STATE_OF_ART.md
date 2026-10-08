# Checagem de `STATE_OF_ART.md` (main) contra fontes primárias

Agente LC, leitura em 2026-10-03 (UTC ~20:00). **O arquivo não foi alterado**; este relatório só aponta.
Rótulos: **V-hoje** = reconferi eu mesmo hoje na fonte primária (arquivos em `fontes/`); **V-outro** = só consta em relatório de outro agente do repo (`LITERATURA_CC.md`, `profunda*/`), não reconferi; **SEM-FONTE** = a afirmação não tem fonte verificável por texto público; **PROCESSO** = diz o que foi feito, não é fato externo.
Regra: "não encontrei" nunca vira "não existe"; nada aqui confirma novidade.

## 1. Veredito curto

* Os **números centrais conferem**: 1475 (Marosi v2/v3), 1743 (v1), 1843 e 264 (Kéri), esfera 221, datas v1/v2/v3, linha da Tabela 1, hash e verificação do anexo. Nenhum número do arquivo foi desmentido.
* **Cinco problemas de redação/consistência**, nenhum de número (ver §3): (1) "Nada foi publicado" contradiz README/FINAL_AUDIT; (2) "busca exaustiva" para uma verificação de cobertura; (3) título "Estado da arte" sobre um conteúdo hedged; (4) falta dizer que 1843 é valor de **tabela web** (chave `f`, soma direta simples), não de artigo revisado, e que o Marosi é preprint cujo texto declara autoria assistida por Claude; (5) o bloco sobre coldcase/Florath depende de leituras de repositório que **não consegui reconferir** (git proibido a mim; API do GitHub bloqueada).
* Superlativos: **nenhum** afirma "recorde/novo/primeiro" para a nossa cota; o arquivo até proíbe "recorde mundial". A única ocorrência de "estado da arte" é o título.

## 2. Afirmação por afirmação

| # | afirmação do `STATE_OF_ART.md` | situação | evidência / observação |
|---|---|---|---|
| 1 | "Revisão feita em 2026-10-02" | PROCESSO | data do próprio arquivo; refiz hoje (10-03) e nada mudou nas fontes abaixo |
| 2 | "Nada foi publicado e nada foi gasto." | **DISCREPÂNCIA** | README: "Tag v0.5.0; DOI conceitual 10.5281/zenodo.23085769" e o `K_7(9,4) ≤ 1137` listado como v0.5; `FINAL_AUDIT.md` H: "já publicado na v0.5"; FINAL_AUDIT G: "~US$1,25 estimados" gastos na varredura. Se a frase fala só da revisão bibliográfica, deve dizer isso |
| 3 | Pergunta: existe resultado anterior com K_7(9,4) ≤ N, N ≤ 1137? | enunciado | não cobre 1141/1285/1351 (cobertos por monotonia, pois 1137 < 1141) |
| 4 | Menor UB encontrado: **1475**, Marosi arXiv:2608.19872, "já na v2 (23 ago 2026) e mantido na v3 (2 set 2026)" | **V-hoje** | `arxiv.org/abs/2608.19872`, Submission history: v1 20 Aug 2026 10:31 UTC, v2 23 Aug 12:16, v3 2 Sep 18:03. PDFs v2 (linha 170) e v3 (linha 119) têm a linha da Tabela 1 |
| 5 | "v3 é a versão atual; v4 não existe (404)" | **V-hoje** (hoje 2026-10-03) | `/pdf/2608.19872v4` e `v5` → 404; página lista só v1–v3. É afirmação **datada**: depende do dia |
| 6 | Linha da Tabela 1: `264–1843 / sphere 221 / new UB 1475 / Δ −368 / 20.0% / key f / via L` | **V-hoje** | idêntica em v3 (`pdftotext -layout`). "key f = direct sum" e "via L = local search" estão na legenda da Tabela 1 (v3, linhas 136–144) |
| 7 | "Não achei N ≤ 1137" | hedged, OK | consistente com minha varredura do arXiv até 2026-10-03 (§4 de `LITERATURA_PROFUNDA_C.md`) |
| 8 | "1475 fica 338 acima de 1137" | **V-hoje** (aritmética) | 1475 − 1137 = 338 |
| 9 | Cota inferior 264 = Haas–Halupczok–Schlage-Puchta 2009 (chave `m`); "Marosi não melhora a LB desta célula" | **V-hoje** | legenda do Kéri (`6-21_tables.pdf`): `m (Haas–Halupczok–Schlage-Puchta, 2009)`; Marosi v3: "No cell whose previous lower bound is due to [HHS] (key m) is improved"; K7(9,4) só aparece na Tabela 1 (grep), não na Tabela 2 |
| 10 | Cota de esfera 221 | **V-hoje** | V(9,4)=182791; 7^9/182791 = 220,77 → 221; igual à coluna "sphere" do Marosi |
| 11 | Intervalo publicado "264 ≤ K_7(9,4) ≤ 1475" | consequência de 6, 9 | ok **com** "nas fontes revisadas" |
| 12 | Kéri `6-21_tables.pdf`, sha256 `6191ab94…805c62`, linha `9 m 264–1843 f`, "arquivo de 2009-10-15; índice com última data 2011-11-25" | **V-hoje** | baixei hoje: sha256 `6191ab9410329cc1…` confere; `Last-Modified: 15 Oct 2009 10:05:06 GMT` (= 12:05 hora de Budapeste, por isso LITERATURA_CC diz 12:05); `index.htm` `Last-Modified: 25 Nov 2011 09:32 GMT` |
| 13 | 1843 "chave f: direct sum" | **V-hoje**, com ressalva | legenda do Kéri: `f direct sum`. É **soma direta simples** 97·19 (K_7(5,2)·K_7(4,2)). Ressalva ausente no arquivo: o artigo Kéri–Östergård 2005 (DCC 37:45–60) trata **R ≤ 3** (resumo lido hoje: "6 ≤ q ≤ 21 and R ≤ 3"); logo o 1843 (R = 4) **não é resultado de artigo**, é entrada de tabela web. "Publicado" na pergunta inicial precisa disso |
| 14 | Marosi v1: título "…alphabets of size six and seven", 1743, linha `264–1843 → 1743, −100, direct sum` | **V-hoje** | v1: resumo "K7(9,4) ≤ 1743"; linha 74 da tabela com anexo `K7_9_4_M1743.txt` e método "direct sum" (o rótulo da v1 diz "direct sum", não busca local; vale citar assim). Data: v1 20 Aug 2026 |
| 15 | v2: linha 170 `264–1843 221 1475 −368 20.0% f L` | **V-hoje** | |
| 16 | v3: reverificação independente do anexo `K7_9_4_M1475.txt`, sha256 `b3e60549…ac6ace`, 1475 distintas, 0 descobertas | **V-hoje** | baixei o anexo (`/src/2608.19872v3/anc/`, v2 e v3 respondem 200), sha256 `b3e6054913d7c040…`, rodei o snippet do arquivo: `1475 0`; 1475 linhas distintas. Reproduzido **por mim** |
| 17 | "foi reverificado aqui por **busca exaustiva**" (Conclusão) | redação | é verificação exaustiva de **cobertura** (dilatação sobre os 7^9 pontos), não busca. Sugestão: "verificação exaustiva de cobertura" |
| 18 | `Mapika/coldcase`: M1475 no commit `8a7947b` (2026-08-21), HEAD `56a8cce` (2026-08-24), 369 arquivos, `cmp` idêntico ao anc, branch `research/symbolic-q82` com mínimo 1475, mirror `keri_third_party.csv` | V-outro | não reconferi (sem git; a própria linha admite `gh api` 403). `LITERATURA_CC.md` (outro agente) dá o mesmo HEAD e 369 arquivos: **dois relatos concordam, mas são da mesma equipe**. Marcar "não reconferido nesta checagem" |
| 19 | Commit `56a8cce` "fala em Journal version" | SEM-FONTE (público) | só no repo; nada no arXiv (a página não tem journal-ref). Vale como lacuna declarada, que o arquivo já declara |
| 20 | Gijswijt–Polak arXiv:2504.01932: v1 2025-04-02, v2 2026-06-19; só LB; tabelas q ≤ 5 | **V-hoje** (datas) | histórico de submissão: v1 Wed 2 Apr 2025 17:42, v2 Fri 19 Jun 2026 09:46. "(IEEE Trans. Inf. Theory)" **não** consta na página do arXiv (sem journal-ref): SEM-FONTE aqui. "certificados em github.com/CoveringCodes": não reconferi |
| 21 | Florath arXiv:2606.09600 v1 2026-06-08, "not claimed to be best known values" | **V-hoje** | PDF: linha 1132 "claimed to be best known values" (negação na quebra de linha); resumo: "not new record bounds". O repo `florath/covering-codes-lean` (HEAD `bbed9a6`, `Chunk69.lean` com 2401): V-outro, não reconferi |
| 22 | Candidatos 2606.16688 (K_8(4,2)=23), 2608.12595 (nearly-perfect), 2609.16078 (binário R=2) | **V-hoje** (títulos/datas) | listagem da API do arXiv: "A Lean-Certified Proof of K_8(4,2)=23" (2026-06-15), "On Nearly-Perfect Covering Codes Beyond Radius One" (2026-08-12), "Further results on binary codes of covering radius 2…" (2026-09-13). O `grep` por `K7(9`/`1475` nesses PDFs: V-outro (reconferi só 2609.16078: sem ocorrência) |
| 23 | "Nenhum artigo mais novo que a v3 trata q=7; listagens até 2026-09-28" | **V-hoje**, atualizado | minhas 11 consultas à API (`logs/arxiv_api_2026-10-03.log`): o item mais recente sobre covering codes é 2609.16078 (2026-09-13); nada posterior a 2026-09-13 com q=7. Cobertura limitada a palavras-chave (ver `LITERATURA_PROFUNDA_C.md` §4) |
| 24 | "Resultados da Consensus são de Davydov e Östergård…" | SEM-FONTE | resultado de ferramenta, sem URL no arquivo |
| 25 | "1843 (Kéri, ≤ 2011) → 1743 → 1475" | **V-hoje**, incompleto | sequência certa; falta que 1843 já estava na edição de 2006-01-26 (V-outro, `profunda/`) e que o Kéri mantém LB 264 desde 2009-10 |
| 26 | "Não chame isto de 'recorde mundial'" | norma | correto e é o único uso do termo |
| 27 | Lacunas listadas (Scholar, GitHub API, periódico, páginas pessoais, teses, CoveringCodes, M1743 não baixado) | PROCESSO | honestas. **Eu** acrescento: M1743 existe (listagem `anc` da v1 responde 200; não baixei o arquivo) |

## 3. Discrepâncias e pontos a corrigir (só relato)

1. **"Nada foi publicado"** (linha 3) vs README (tag, DOI Zenodo, "já publicado na v0.5" no FINAL_AUDIT). Escolher: "esta revisão não foi publicada" ou remover.
2. **"Estado da arte" no título** vs. conteúdo que diz "menor encontrado nas fontes revisadas". Sugestão neutra: "Literatura revisada: K_7(9,4)".
3. **Natureza das fontes** não dita: (a) 1843 é tabela web (key `f`), o artigo KÖ2005 cobre R ≤ 3; (b) Marosi 2608.19872 é **preprint** (sem periódico nas fontes lidas) e declara em "Use of artificial intelligence" (v3, linha 472) que manuscrito e software foram escritos pelo sistema Claude sob direção do autor — relevante para quem for citar "1475" como cota **publicada**.
4. **Atribuição da LB 264**: STATE/VALIDATION dizem HHS (correto, chave `m`); `FINAL_AUDIT.md` A/Respostas diz "cota inferior de Kéri" (impreciso: Kéri compila; a prova é de HHS 2009).
5. **"Busca exaustiva"** para a verificação do 1475 (ver #17).
6. **Data-dependência**: "v4 não existe" vale para 2026-10-02/03; trocar por "em 2026-10-03".
7. **Não coberto no arquivo, e relevante para a afirmação "nenhum ≤ 1137"**: a via condicional de **soma direta amalgamada** (ADS): com as cotas tabeladas q=7 o envelope é K_7(4,2)·K_7(6,2)/7 = 19·343/7 = **931 < 1137** (se existir par normal); o Kéri usa ADS em q=7 em outra célula (`K7(10,2) ≤ 420175`, Rivas Soriano 2006-09-25, = 25·117649/7), e o Marosi **não** usa ADS (v1–v3: nenhuma ocorrência de "amalgam"). Isso não é predecessor (não há código), mas é o resíduo principal de "não achei" — ver `LITERATURA_PROFUNDA_C.md` §1.3.

## 4. Adendo: mesma checagem nos outros arquivos pedidos (por amostra, fora do escopo estrito)

* `VALIDATION.md`, tabela de gates: "revisão bibliográfica | **PASS** (nenhum resultado ≤ 1137)". PASS para uma busca negativa soa a prova; o texto de `J` está bem hedged ("improves the smallest upper bound **we found in the reviewed literature**"), mas a linha PASS deveria dizer "nenhum encontrado". O cabeçalho "Status: VALIDATED" vale para o **código** (3 verificadores + Lean), não para a literatura.
* `README.md`: "`K_7(9,4)` | 1137 | anterior 1475" e "K_5(10,4) | 625 | 875" (sem fonte nem hedge na tabela; a ressalva "falta conferir as tabelas de comprimento de Davydov–Marcugini–Pambianco" está só um parágrafo abaixo); "Kéri 2011 tinha 1843" (o PDF é de 2009-10-15, o 1843 está na edição de 2006; "2011" é a data do site).
* `FINAL_AUDIT.md` A: "A cota publicada anterior era 1475" — sem "que encontramos".

## 5. Reprodução desta checagem

`fontes/`: `marosi_v1/2/3.pdf|txt`, `K7_9_4_M1475.txt`, `keri_6-21.pdf|txt`, `keri_index.htm|txt`, `2606.09600.pdf|txt`, `gp.pdf|txt`, `abs_marosi.html`, `ko2005.html`; hashes em `fontes/SHA256SUMS`. Comandos: `curl` + `pdftotext -layout` + `grep`; verificador do anexo = o snippet do próprio `STATE_OF_ART.md` (numpy), rodado por mim. Nenhum código de terceiros foi executado (o anexo é dado; o `numpy` é biblioteca padrão). Git não usado.
