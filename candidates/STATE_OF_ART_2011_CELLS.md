# Estado da arte: K_5(10,5), K_5(11,4), K_7(10,4)

Revisão bibliográfica feita em 2026-10-03, com o mesmo método usado para K_7(9,4)
(`STATE_OF_ART.md`). Nada foi publicado e nada foi gasto. Os candidatos abaixo
foram **verificados por força bruta e não foram publicados**:

| célula | nosso candidato | Kéri (tabelas, ≤ 2011) |
|---|---|---|
| K_5(10,5) | <= 163 | 41–175 |
| K_5(11,4) | <= 2875 | 535–3125 (a LB 546 vem de Gijswijt–Polak, não de Kéri; ver abaixo) |
| K_7(10,4) | <= 5616 | 1007–6517 |

## Resposta curta

| célula | menor UB encontrado na literatura revisada | fonte do UB | algum resultado publicado <= candidato? | melhor LB encontrada |
|---|---|---|---|---|
| K_5(10,5) | **175** | Kéri `4-5_tables.pdf`, chave `d` (o espelho no coldcase atribui a Bhandari–Durairajan 1996) | **não encontrado** (175 > 163) | 41 (Haas–Halupczok–Schlage-Puchta 2009, chave `m`) |
| K_5(11,4) | **3125** | Kéri `4-5_tables.pdf`, chave `d` (idem) | **não encontrado** (3125 > 2875) | **546** (Gijswijt–Polak, arXiv:2504.01932 / IEEE TIT 2025); Kéri tinha 535 |
| K_7(10,4) | **6517** | Kéri `6-21_tables.pdf`, chave `f` (direct sum) | **não encontrado** (6517 > 5616) | 1007 (Kéri, chave `y`, esfera melhorada) |

Nenhuma das três células aparece no artigo do Marosi (nenhuma versão), nos arquivos
ancilares dele, no repositório Mapika/coldcase, no Florath nem em qualquer outra fonte
revisada com um upper bound menor que o de Kéri.

## Tabela por fonte

| fonte (URL, versão/data) | K_5(10,5) | K_5(11,4) | K_7(10,4) | código? | como foi verificado |
|---|---|---|---|---|---|
| Kéri, `4-5_tables.pdf` — https://old.sztaki.hu/~keri/codes/4-5_tables.pdf (arquivo de 2009-10-15; índice do site com última data em 2011-11-25) | `m 41–175 d` | `y 535–3125 d` | — | não | PDF baixado (sha256 `2fc92770…bad12dd`), `pdftotext -layout`, tabela "Bounds on K5(n,R)", linhas n=10 e n=11 |
| Kéri, `6-21_tables.pdf` — https://old.sztaki.hu/~keri/codes/6-21_tables.pdf (2009-10-15) | — | — | `y 1007–6517 f` | não | PDF (sha256 `6191ab94…805c62`), tabela q=7, R=4, linha n=10 |
| Marosi, arXiv:2608.19872 **v1** (2026-08-20) — https://arxiv.org/pdf/2608.19872v1 | ausente | ausente | ausente | — | `pdftotext` + `grep 'K[57] \(n, R\)'`. A v1 só trata de q ∈ {6,7}; as células K7 citadas são (7,3), (8,4) e (9,4) |
| Marosi, arXiv:2608.19872 **v2** (2026-08-23) e **v3** (2026-09-02, atual; a v4 dá 404 em 2026-10-03) | ausente | ausente | ausente | anc sem arquivo destas células | `grep` em todas as menções a K5(·,·) e K7(·,·). As únicas K5 são (11,5) [UB 602] e (7,1), (8,1), (8,2) [LB]; as K7 com n=10 são (10,2) e (10,5) [UB 980], não (10,4). A §6.4 diz que nenhuma célula de chave `m` teve a LB melhorada. Pelo artigo, o fecho das regras de propagação "gives no further improvement beyond Remark 1" (que trata de K17(7,2)) |
| Repositório **Mapika/coldcase** — https://github.com/Mapika/coldcase (master `56a8cce`, 2026-08-24; branch `research/symbolic-q82` `c17a7ac`, 2026-08-29) | nenhum arquivo | nenhum arquivo | nenhum arquivo | — | `git ls-tree -r` nos dois branches: nenhum arquivo `K5_10_5*`, `K5_11_4*` ou `K7_10_4*` (de K5 só há `K5_11_5`; de K7 com n=10, só `K7_10_5`). `cov/sweep_targets.json` (191 alvos), `results/cov_sweep_state.json` (116 células), `cov/engine/attack_records.json`, `attack_records2.json`, `attack_sieges.json`, `results/cov_sweep.log` e `cov/lb/results/hiprec/sweep.log`: nenhuma entrada (q,n,R) igual a (5,10,5), (5,11,4) ou (7,10,4); o JSON foi lido com python. O espelho de Kéri `cov/data/keri_third_party.csv` dá 41–175, 535–3125 e 1007–6517 |
| Gijswijt–Polak, arXiv:2504.01932 (v1 2025-04-02, v2 2026-06-19; IEEE TIT 2025) — https://arxiv.org/abs/2504.01932 | LB não melhora (valor SDP 37.81 < 41) | **LB 535 → 546** (Tabela 3) | fora do escopo (q ≤ 5) | certificados em github.com/CoveringCodes (não inspecionado) | `pdftotext`: Tabela 3, linha `5 11 4 535 546 3125`; Tabela 9 (q=5), n=10 R=5 = 37.81. Só cotas inferiores |
| Florath, arXiv:2606.09600 v1 (2026-06-08) | não citada | não citada | não citada | — | `pdftotext` + `grep`. O artigo diz que não reproduz as tabelas nem dá os melhores valores conhecidos |
| **florath/covering-codes-lean** (HEAD `bbed9a6`, 2026-09-16) | certificado 31–625 | certificado 509–15625 | certificado 943–8575 | traço Lean | `GeneratedTable/Chunk50.lean` e `Chunk69.lean`: são cotas certificadas em Lean, mais fracas que as de Kéri, e **não** são as melhores conhecidas |
| Bibliografia de Lobstein, *Covering radius, a bibliography* (66 p., atualizada em 2023-01-10) — https://www.lri.fr/~lobstein/bib-a-jour.pdf | — | — | — | — | Baixada e passada no `pdftotext`; `grep` por quinary, 5-ary, q-ary covering e large alphabet. As entradas de K_q não binário são anteriores a 2011 (Bhandari–Durairajan 1996, Östergård 1991/1999, Gommard–Plagne K5(7,3), Kéri–Östergård 2005). Nenhuma entrada pós-2011 sobre K_5 ou K_7 de raio 4 ou 5 |
| Página de publicações do Östergård — https://users.aalto.fi/~pat/patric_pub.html | — | — | — | — | Lista com `grep covering`: não há artigo de 2011 em diante com tabelas q-árias para q=5 ou q=7 |
| Busca ampla: WebSearch (3 consultas), Consensus (2) e API do arXiv (8 consultas com "covering code(s)", quinary, q-ary, K_q, 2011–2026) | nada < 175 | nada < 3125 | nada < 6517 | — | Fora Marosi e Gijswijt–Polak, o que aparece trata de outra coisa: função de comprimento linear (Davydov, Bartoli, Marcugini, Pambianco), métricas sum-rank, NRT, inserção e deleção, ou casos binários. Nenhum resultado traz UB para estas três células |

## Checagem de propagação a partir do que foi publicado

Usei as regras padrão K_q(n+1,R) <= q·K_q(n,R) e K_q(n+1,R+1) <= K_q(n,R), com os
melhores valores das fontes revisadas. Nenhuma derivação simples bate as tabelas:

- **K_5(10,5)**: <= K_5(9,4) = 255; <= 5·K_5(9,5) = 275. As duas ficam acima de 175.
- **K_5(11,4)**: <= K_5(10,3) = 3125 (igual à tabela); <= 5·K_5(10,4) = 4375.
- **K_7(10,4)**: <= K_7(9,3) = 8575; <= 7·K_7(9,4) = 7·1475 = 10325 (usando o 1475 do
  Marosi). As duas ficam acima de 6517.

Isso bate com a afirmação do Marosi de que o fecho das novas cotas não melhora mais
nada, e com os valores do banco Lean, que são todos mais fracos.

## Conclusão

Para as três células, o menor upper bound encontrado na literatura revisada é o das
tabelas de Kéri: **K_5(10,5) <= 175**, **K_5(11,4) <= 3125** e **K_7(10,4) <= 6517**.
Nenhum resultado **publicado** encontrado nesta revisão atinge ou fica abaixo dos
candidatos 163, 2875 e 5616. Isso **não prova** que tal resultado não exista; quer
dizer apenas que ele não apareceu nas fontes revisadas, com as lacunas listadas
abaixo. Não chame isto de "recorde mundial".

Correção de registro: no K_5(11,4), a cota inferior **546** é de Gijswijt–Polak.
As tabelas de Kéri trazem **535**. O intervalo atual que encontrei é 546–3125.

## O que NÃO foi possível checar

- **Google Scholar** e bases pagas (MathSciNet, zbMATH, Scopus): não consultados.
- **Teses** (por exemplo, de alunos de Östergård ou de Kéri) e anais de conferência
  fora do arXiv: não foram procurados de forma sistemática.
- **Páginas pessoais** de Davydov, Bertolo e Haas: não visitadas uma a uma. Davydov
  e Bertolo só apareceram nos resultados de busca, sempre com outros parâmetros
  (função de comprimento linear; K5(5,3) em 2006).
- **Bibliografia de Lobstein**: para depois de 2023-01-10, não há versão mais nova.
  A checagem foi por palavra-chave, não leitura completa das 66 páginas.
- **API do GitHub do coldcase** (issues, PRs, releases): 403 nesta sessão. Só vi o
  conteúdo via `git clone` público (master e `research/symbolic-q82`). Commits
  posteriores a 2026-08-29 também não foram vistos: um `git fetch` em 2026-10-03
  não trouxe nada novo no master.
- **Versão em periódico** do Marosi (o commit `56a8cce` fala em "Journal version"):
  não encontrada.
- `github.com/CoveringCodes` (certificados de Gijswijt–Polak): não inspecionado. Ele
  só traz cotas inferiores.
- A chave `d` de Kéri não foi conferida contra a legenda do PDF. A atribuição a
  Bhandari–Durairajan 1996 vem do espelho CSV do coldcase.
- Nada publicado depois de 2026-10-03.

Arquivos de trabalho (PDFs, clones e `pdftotext`) ficaram no scratchpad da sessão,
que é temporário.
