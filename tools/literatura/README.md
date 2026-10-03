# Acervo de literatura: códigos de cobertura

`varredura.py` monta um acervo reprodutível de literatura sobre códigos de
cobertura (covering codes) e sobre as técnicas que usamos para atacar as
células K_q(n,R). O resultado vai para o bucket privado
`gs://factory-literatura-matematica` (southamerica-east1). O relatório de leitura
da primeira rodada está em `docs/literatura/VARREDURA_2026-10-03.md`.

## Como rodar

```sh
python3 -m venv .venv && .venv/bin/pip install pymupdf pypdf cryptography
# pdftotext é usado se existir; senão PyMuPDF, senão pypdf. cryptography só para `subir`.
export OPENALEX_API_KEY=...                                # opcional, ver "Limites"
export LIT_DIR=$PWD/literatura-dados                       # onde fica o acervo local
export GCP_CREDENCIAL_DIR=<apps/factory/bin da Factory>    # só para a etapa `subir`
.venv/bin/python tools/literatura/varredura.py tudo
# ou etapa por etapa:
.venv/bin/python tools/literatura/varredura.py tabelas sementes buscas expandir
.venv/bin/python tools/literatura/varredura.py arxivmeta baixar extrair mencoes relatorio subir
```

Cada etapa é idempotente. Toda resposta HTTP de API fica em `cache/` (gzip, chave =
sha1 da URL), os PDFs já baixados não são baixados de novo, e o `subir` só envia
arquivo cujo sha256 mudou (`meta/.subidos.json`). Para refazer uma etapa do zero,
apague o cache ou o arquivo de saída dela. A primeira rodada completa
(2026-10-03) levou cerca de 1 h na factory-01: 33 min na expansão por OpenCitations, 8 min
de PDFs (8 threads), 1 min de extração (PyMuPDF, 3 processos) e 2 min de envio.

As sementes, as consultas, os pesos de relevância e os cortes ficam em
`sementes.json`. Mudar a varredura é editar esse arquivo, não o código.

## Etapas

| etapa | o que faz | fonte |
|---|---|---|
| `sementes` | resolve DOIs, ids arXiv e cerca de 50 títulos-chave (casamento por similaridade ≥ 0,6) | OpenAlex (Crossref se faltar), arXiv |
| `buscas` | consultas por palavra-chave; entra quem passa do `limiar_inclusao` de relevância | OpenAlex, Crossref, arXiv API, zbMATH Open (inclui todo o MSC 94B75, "covering radius") |
| `expandir` | citações (referências e citantes) das obras com score ≥ `limiar_expansao`, `--niveis` níveis; só entram as que passam do limiar | OpenCitations + Crossref; OpenAlex quando há orçamento |
| `arxivmeta` | filtra por streaming o dump público de metadados do arXiv (4,5 GB, `gs://arxiv-dataset`, acesso anônimo por HTTP); só as linhas que casam ficam no disco | Kaggle/arXiv |
| `tabelas` | espelha o diretório inteiro das tabelas do Kéri (`old.sztaki.hu/~keri/codes/`), as versões arquivadas no Wayback Machine, a bibliografia do Lobstein e as tabelas pós-Kéri (coldcase, Florath) fixadas por commit | sites públicos |
| `baixar` | PDFs de acesso aberto: arXiv primeiro, depois os links OA do OpenAlex (Unpaywall); só aceita o que começa com `%PDF-` | arXiv, repositórios OA |
| `extrair` | texto com `pdftotext -layout` ou, sem ele, `pypdf` em subprocesso com timeout; as resenhas do zbMATH também viram texto pesquisável | — |
| `mencoes` | procura as células de `sementes.json` (`K7(9,4)`, `K_7(9,4)`, `K 7 (9, 4)`, `K(9,4)` com q no contexto) e os números-alvo (1475, 175, 3125, 6517, 8575, 42189) perto de "cover" e dos parâmetros | — |
| `relatorio` | contagens (obras, PDFs, OA x não OA) e a lista das obras relevantes sem acesso aberto | — |
| `subir` | envia tudo ao bucket pela JSON API do GCS, com token cunhado em memória por `gcp_credencial.token()`; nenhum segredo é impresso nem gravado | GCS |

## Layout no bucket

```
README.md                    descrição do layout
meta/works.jsonl             uma obra por linha: id, openalex, doi, arxiv, zbmath, título, autores,
                             ano, venue, oa_url, fontes, motivos (por que entrou), score, pdf_status
meta/arxiv_meta_filtrado.jsonl  linhas do dump do arXiv que casaram o filtro
meta/expandidas.json         obras cujas citações já foram expandidas
pdf/<id>.pdf                 PDFs de acesso aberto
txt/<id>.txt                 texto extraído; txt/<id>.zbmath.txt = resenha do zbMATH
tabelas/keri/                diretório inteiro do Kéri (PDF, PS, índice) + texto extraído
tabelas/keri_wayback/        cópias do Wayback Machine (cdx.json lista todas as capturas)
tabelas/MANIFESTO.json       url, sha256 e tamanho de cada tabela
buscas/<data>/               log.txt, consultas.json (contagens), mencoes.jsonl, mencoes_resumo.json,
                             sementes_nao_resolvidas.txt, pdf_falhas.json
relatorios/                  contagens_<data>.json, nao_acessiveis_<data>.json, o relatório em Markdown
```

O `id` é o id do OpenAlex (`W…`) quando existe; senão `arxiv_<id>` ou `zb_<id zbMATH>`.
Registros da mesma obra vindos de fontes diferentes são fundidos por DOI, arXiv ou
OpenAlex.

## Limites e o que fica de fora

- **Google Scholar: não usado.** Os termos de uso proíbem raspagem e a resposta
  é 403. Nada de proxy para contornar.
- **OpenAlex sem chave tem orçamento de US$ 0,10/dia por IP** (medido em 2026-10-03: ~100
  chamadas de busca esgotam o dia, depois só 429 até a meia-noite UTC). Ao primeiro 429 o
  script para de chamar o OpenAlex e segue com Crossref (busca e metadados), OpenCitations
  (arestas de citação) e Unpaywall (links OA). Com `OPENALEX_API_KEY` (chave gratuita, mas
  exige cadastro) a expansão pelo OpenAlex volta a valer.
- **Semantic Scholar: não usado.** Sem chave, devolve 429.
- **Artigos pagos sem cópia OA** ficam só com metadados (e resenha do zbMATH, quando
  existe). A lista dos relevantes está em `relatorios/nao_acessiveis_<data>.json`.
- **Nada foi pago.**
- Limites de taxa respeitados: arXiv 1 requisição a cada 3 s; OpenAlex no polite pool
  (`mailto`), ~5 req/s; zbMATH 1 req/s; Wayback 1 req a cada 1,5 s.
- O detector de menções acha texto, não tabela: em tabelas extraídas de PDF a célula
  costuma aparecer como linha solta ("`9 m 264–1843 f`"). Por isso as cotas das
  tabelas do Kéri foram lidas à mão e citadas linha a linha no relatório.
- O score de relevância é uma soma de pesos de palavras no título, no resumo e na
  resenha. É grosseiro de propósito: serve para cortar a expansão, não para ranquear
  a leitura.
