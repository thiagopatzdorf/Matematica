# Mapa de arquivos: o que saiu da raiz e para onde foi

Em 2026-10-06 (branch `banho/higiene`) a raiz ficou só com o essencial: README, LICENSE, CITATION.cff,
CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, AGENTS.md e as configurações de build (Lean, Python, CI). Os
documentos soltos foram movidos com `git mv`, então `git log --follow <novo caminho>` mostra o histórico inteiro.

## Antigo → novo

| caminho antigo (raiz) | caminho novo | o que é |
|---|---|---|
| `VALIDATION.md` | `docs/validacao/VALIDATION.md` | validação da v0.5 (K_7(9,4) ≤ 1137) |
| `VALIDATION_v0.6.md` | `docs/validacao/VALIDATION_v0.6.md` | validação da v0.6 (1134, 162, 2875, 5616) |
| `REPRODUCE_1137.md` | `docs/validacao/REPRODUCE_1137.md` | passo a passo para refazer o 1137 |
| `LEAN_REVIEW.md` | `docs/validacao/LEAN_REVIEW.md` | revisão humana dos enunciados Lean |
| `LEAN_RED_TEAM.md` | `docs/validacao/LEAN_RED_TEAM.md` | ataques ao Lean (v0.5 e v0.6) |
| `K7_9_4_1137_CERTIFICATE.json` | `docs/certificados/K7_9_4_1137_CERTIFICATE.json` | registro da rodada do 1137 |
| `STATE_OF_ART.md` | `docs/literatura/STATE_OF_ART.md` | busca bibliográfica que sustenta "novo na literatura" |
| `nota.md` | `docs/historico/nota-cota-de-esfera.md` | texto da página das cotas de esfera (`/provas/paper`) |

## Referências que ficaram para o integrador

Estes arquivos são de outro agente do banho de loja e **não** foram editados aqui. Enquanto não forem
atualizados, `tests/test_docs_links.py` reprova os dois (o caminho antigo deixa de existir):

| arquivo | linha de hoje | troque por |
|---|---|---|
| `README.md` | "busca bibliográfica descrita em `STATE_OF_ART.md`" | `docs/literatura/STATE_OF_ART.md` |
| `docs/README.md` | "... e `STATE_OF_ART.md`." | `[STATE_OF_ART.md](literatura/STATE_OF_ART.md)` |

## Referências atualizadas nesta mudança

* `CONTRIBUTING.md` (STATE_OF_ART, LEAN_REVIEW);
* `docs/resultados.md` (LEAN_RED_TEAM, VALIDATION_v0.6);
* `candidates/STATE_OF_ART_2011_CELLS.md`;
* as referências cruzadas dentro dos próprios documentos movidos;
* `infinito/infinito_mcp/modulos/matematica.py` (allowlist `DOCS` da tool `documento`) e `infinito/Dockerfile`
  (os documentos já entram na imagem por `COPY docs`); o teste
  `test_documento_da_allowlist_aponta_para_arquivo_movido_ou_apagado` falha se a allowlist apontar para arquivo
  que não existe.

**Não** atualizado de propósito: `docs/certificados/K7_9_4_1137_CERTIFICATE.json` cita `LEAN_REVIEW.md`,
`LEAN_RED_TEAM.md` e `STATE_OF_ART.md` pelos nomes antigos. É o registro congelado da rodada de 2026; reescrever
o conteúdo de um certificado para acompanhar uma mudança de pasta apagaria o que ele registrou. Esta tabela é a
ponte.

## Pastas da raiz: avaliadas, não movidas

Mover estas pastas quebraria caminhos gravados em dados e código versionados (medido com `git grep`:
`ledger/provenance.json`, `data/structured/q7_n9_R4_M1134.json` e `tools/patch_setcover/` citam `candidates/`;
`verification/run_all.sh` cita `artifacts/`; `tests/test_repo_higiene.py` valida o JSON de `verification/`). Ficam
onde estão até alguém fazer a mudança com o ledger regenerado no mesmo PR.

| pasta | o que tem | proposta |
|---|---|---|
| `artifacts/` | só `k7_9_4_1137/` (o código 1137, formato e somas) | juntar com `candidates/` em `data/historico/` |
| `candidates/` | `k7_9_4_1134/` e a triagem das células de 2011 | idem; o `.md` da triagem iria para `docs/literatura/` |
| `audit/` | `k794-base-sweep/` (varredura de bases do 1137) | `docs/validacao/k794-base-sweep/` ou `data/historico/` |
| `verification/` | verificadores independentes e saídas da v0.5/v0.6 | manter (citado pelos docs de validação, pela arquitetura e pelo teste de higiene) |
| `evaluators/` | pacote Python `python3 -m evaluators` | manter: é código importável, o nome é o do módulo |
| `infinito/` | o servidor MCP Infinito | manter (CODEOWNERS e Dockerfile apontam para cá) |
