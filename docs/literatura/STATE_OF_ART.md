# Estado da arte: K_7(9,4)

Revisão bibliográfica feita em 2026-10-02. Nada foi publicado e nada foi gasto.

**Pergunta:** qual é o menor upper bound publicado para K_7(9,4)? Ele é o tamanho
mínimo de um código 7-ário de comprimento 9 com raio de cobertura 4.
E existe **algum** resultado anterior com K_7(9,4) <= N para N <= 1137?

## Resposta curta

- **Menor upper bound encontrado na literatura revisada: K_7(9,4) <= 1475.**
  Fonte: Marosi, arXiv:2608.19872, já na **v2** (23 ago 2026) e mantido na **v3**
  (2 set 2026, versão atual; a v4 não existe, `arxiv.org/pdf/2608.19872v4` devolve 404).
  A linha da Tabela 1 diz: `K7(9,4)  264–1843  sphere 221  new UB 1475  Δ −368  20.0%  key f  via L`.
- **Não achei nenhum resultado com K_7(9,4) <= N para N <= 1137.** O menor valor
  encontrado, 1475, fica 338 acima de 1137.
- **Cota inferior** que acompanha esse valor: 264, de Haas–Halupczok–Schlage-Puchta 2009
  (chave `m` nas tabelas de Kéri). Marosi **não** melhora a cota inferior desta célula.
  A cota de esfera é 221.
- O intervalo publicado, segundo as fontes revisadas, é então **264 <= K_7(9,4) <= 1475**.

## Tabela de fontes

| fonte | public_bound (UB) | LB citada | publication_date | code_available? | verification_method (desta revisão) |
|---|---|---|---|---|---|
| Kéri, *Tables for bounds on covering codes*, `6-21_tables.pdf` — https://old.sztaki.hu/~keri/codes/6-21_tables.pdf | **1843** (chave `f`: direct sum) | 264 (`m`) | arquivo de 2009-10-15; índice do site com última data em 2011-11-25 | não (é construção) | PDF baixado (sha256 `6191ab94…805c62`), `pdftotext`, linha `9  m 264–1843 f` na tabela q=7, R=4 |
| Marosi, arXiv:2608.19872 **v1** — https://arxiv.org/pdf/2608.19872v1 (título da v1: "New upper bounds on covering codes K_q(n,R) for alphabets of size six and seven") | **1743** | (264–1843 anterior) | 2026-08-20 | sim, anc `K7_9_4_M1743.txt` (listado em `arxiv.org/src/2608.19872v1/anc`) | PDF da v1 + `pdftotext`: no resumo, "K7(9,4) ≤ 1743"; na tabela, `264–1843 → 1743, −100, direct sum` |
| Marosi, arXiv:2608.19872 **v2** — https://arxiv.org/pdf/2608.19872v2 | **1475** | 264 (sem melhora) | 2026-08-23 | sim (anc) | PDF da v2 + `pdftotext`: linha 170 da Tabela 1, `264–1843  221  1475  −368  20.0%  f  L` |
| Marosi, arXiv:2608.19872 **v3** (atual) — https://arxiv.org/pdf/2608.19872v3 | **1475** | 264 (sem melhora) | 2026-09-02 | **sim**: `arxiv.org/src/2608.19872v3/anc/K7_9_4_M1475.txt` | PDF da v3 + `pdftotext` (linha 119). Também **verifiquei o código de forma independente**: 1475 palavras distintas em Z_7^9, todas as 7^9 = 40.353.607 palavras cobertas no raio 4, zero descobertas. Script próprio em numpy, com dilatação de Hamming aplicada 4 vezes. sha256 do anc: `b3e60549…ac6ace` |
| Repositório **Mapika/coldcase** (GitHub, autor do artigo acima) — https://github.com/Mapika/coldcase | **1475** (o menor arquivo de K7(9,4) lá) | — | `cov/results/K7_9_4_M1475.txt` adicionado no commit `8a7947b` (2026-08-21); HEAD do master `56a8cce` (2026-08-24) | sim, de M1475 até M1843 (369 arquivos `.txt`/`.json`), mais logs `K7_9_4_1599.log` e `K7_9_4_1679.log`; o arquivo M1475 é byte a byte igual ao anc da v3 (`cmp`) | `git clone` público; `git ls-files`. O branch `research/symbolic-q82` (2026-08-29) também tem 1475 como mínimo. Mirror de Kéri em `cov/data/keri_third_party.csv`: `7,9,4 lower 264 / upper 1843` |
| Gijswijt–Polak, *Semidefinite lower bounds for covering codes*, arXiv:2504.01932 (v1 2025-04-02, v2 2026-06-19) — https://arxiv.org/abs/2504.01932 | — (só cotas inferiores) | nenhuma para q=7 | v2 2026-06-19 (IEEE Trans. Inf. Theory) | certificados em github.com/CoveringCodes (não inspecionado) | PDF + `pdftotext`: as tabelas só cobrem q = 2, 3, 4, 5. Não citam K_7(9,4) |
| Florath, *Formal Foundations and Proof-Carrying Certificates for q-ary Covering Codes in Lean 4*, arXiv:2606.09600 v1 — https://arxiv.org/abs/2606.09600 | — no texto | — | 2026-06-08 | — | PDF + `pdftotext`: não menciona K_7(9,4). O próprio artigo diz que os intervalos "are not claimed to be best known values" |
| Repositório **florath/covering-codes-lean** — https://github.com/florath/covering-codes-lean | **2401** (certificado em Lean, **não** é o melhor conhecido) | 221 (esfera) | HEAD `bbed9a6`, 2026-09-16 | sim (traço Lean) | `git clone --depth 1`; `CoveringCodes/Database/GeneratedTable/Chunk69.lean`: `{q:=7,n:=9,r:=4} lower 221 upper 2401`, via `lengthenFreeN 1` sobre o K7(8,4) de Vandermonde/síndrome |
| Busca ampla: WebSearch, Consensus e API do arXiv (`covering codes`, `covering radius`, ordenado por data, a partir de maio de 2026) | nada abaixo de 1475 | — | listagens até 2026-09-28 | — | Nenhum artigo mais novo que a v3 do Marosi trata de q=7. Em três candidatos recentes, `grep` não achou `K7(9`/`1475`/`1743`/`1843`: 2606.16688 (K_8(4,2)=23), 2608.12595 (nearly-perfect) e 2609.16078 (binário R=2). Os resultados da Consensus são de Davydov e Östergård sobre outros parâmetros (função de comprimento, q ≤ 5) |

## Conclusão

Nas fontes revisadas, o menor upper bound encontrado na literatura é
**K_7(9,4) <= 1475**. Ele vem de Márk Marosi, arXiv:2608.19872, aparece desde a v2
(2026-08-23) e segue na v3 (2026-09-02). O código explícito está nos arquivos
ancilares e no repositório Mapika/coldcase, e foi reverificado aqui por busca
exaustiva. A sequência histórica, pelo que foi possível reconstruir, é esta:
1843 (Kéri, direct sum, ≤ 2011) → 1743 (Marosi v1, 2026-08-20) → 1475
(Marosi v2/v3). **Não encontrei, em nenhuma fonte revisada, um resultado com
K_7(9,4) <= N para N <= 1137.** Isso não prova que tal resultado não exista. Quer
dizer apenas que ele não apareceu nesta revisão, que tem as lacunas listadas abaixo.

Não chame isto de "recorde mundial": é o menor valor encontrado nas fontes revisadas.

## O que NÃO foi possível checar

- **Google Scholar**: não foi consultado diretamente (sem acesso por API). A busca
  foi feita só por WebSearch, Consensus e a API do arXiv.
- **API do GitHub para Mapika/coldcase**: o `gh api` foi recusado nesta sessão (403
  de permissão), então issues, PRs e releases do repositório não foram vistos. O
  conteúdo veio de `git clone` público (master e o branch `research/symbolic-q82`).
- **Versões/HTML posteriores a 2026-10-02**, ou submissões ainda não listadas no arXiv.
- **Periódico**: o commit `56a8cce` fala em "Journal version". Não achei versão
  publicada em periódico do artigo do Marosi e não sei se ela tem outro valor.
- **Páginas pessoais** (Östergård, Davydov, Bertolo, Kéri além de `old.sztaki.hu`):
  não foram visitadas uma a uma. Só apareceram nos resultados de busca. A
  bibliografia de Lobstein (`lri.fr/~lobstein/bib-a-jour.pdf`, jan 2023) não foi baixada.
- **Teses** e literatura fora do arXiv indexada só em bases pagas (Scopus,
  MathSciNet/zbMATH): não foram consultadas.
- O repositório `github.com/CoveringCodes` (certificados de Gijswijt–Polak) não foi
  inspecionado. Ele é de cotas inferiores e não afeta o upper bound.
- O código M1743 da v1 não foi baixado nem verificado; só o valor do PDF foi conferido.

## Como reproduzir

Arquivos de trabalho no scratchpad da sessão (temporários):

- PDFs v1, v2 e v3 + `pdftotext -layout`, depois `grep 'K7 (9, 4)'`.
- `curl https://arxiv.org/src/2608.19872v3/anc/K7_9_4_M1475.txt`, depois o verificador abaixo:

```python
import numpy as np
q,n,R=7,9,4
C=np.array([[int(c) for c in l.strip()] for l in open('K7_9_4_M1475.txt') if l.strip()])
cov=np.zeros(q**n,bool); cov[(C*(q**np.arange(n-1,-1,-1))).sum(1)]=True
A=cov.reshape((q,)*n)
for _ in range(R):
    B=A.copy()
    for ax in range(n): B|=A.any(axis=ax,keepdims=True)
    A=B
print(len(C), int((~A).sum()))   # -> 1475 0
```

---

# Entrada: códigos de cobertura de segunda ordem, K^(2)_q(n,r)

Revisão feita em 2026-10-06 para o diretório [`segunda_ordem/`](../../segunda_ordem/README.md). É um
problema **irmão** de K_q(n,R), fora do ledger e fora das contagens do Kéri.

**Pergunta:** existe tabela publicada de K^(2)_q(n,r) = min |C| com R_2(C) ≤ r (raio de cobertura
generalizado de ordem 2, códigos não necessariamente lineares) para n pequeno? E para códigos
lineares?

**Resposta curta: não achei nenhuma.** As fontes tratam de taxa assintótica ou de famílias
lineares específicas:

| fonte | o que traz | tabela de n pequeno? |
|---|---|---|
| Elimelech–Firer–Schwartz, IEEE TIT 67(12), 2021, arXiv:2012.06467 | define R_t para códigos lineares; cotas assintóticas; Exemplo 3: Hamming tem R_t = t | não (só o exemplo; conferido: o [7,4] tem R_2 = 2 pelos nossos verificadores) |
| Elimelech–Schwartz, arXiv:2210.00531 (ISIT 2023) | bolão de segunda ordem; κ_2(ρ,q) = 1 − H_{q²}(ρ) para códigos gerais | não |
| Li–Shangguan–Wei, arXiv:2608.24856 (2026) | taxa ótima para todo t, também para lineares | não |
| Yu–Schwartz, arXiv:2609.14477 (2026) | raio de empacotamento generalizado ≤ raio de cobertura generalizado | não |
| Alfarano–Marino–Neri–Trombetti, arXiv:2606.16669 (2026) | R_t de lineares via (ρ,t)-saturating sets; cotas e construções | não |
| Yohananov–Schwartz; Özbudak–Öztürk; Xiong–Yip; Li–Xiong; Luo et al. (2022–2026) | R_2 (e R_3) de BCH, Reed–Muller, Melas, Zetterberg, cíclicos | não: R_2 de um código fixo, não o mínimo sobre códigos |

Busca: OpenAlex ("generalized covering radius codes", 135 obras, 60 desde 2020, revistas de novo na auditoria; obras que citam
arXiv:2210.00531), Consensus e arXiv ("second-order covering codes football pool"). Não foram
consultados Google Scholar, teses nem bases pagas. Conclusão: os valores de `segunda_ordem/` são
plausivelmente os primeiros publicados para n pequeno, o que **não** prova que não existam em
outro lugar.
