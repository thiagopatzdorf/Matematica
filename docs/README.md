# Documentação

Na mesma ordem do README ([pt-BR](../README.pt-BR.md), [en](../README.md), [fr](../README.fr.md)): definições, princípios, proposições, demonstração e método. Comece pelo
glossário e pela filosofia; o resto se consulta quando precisar.

## Definições e princípios

| documento | para quê |
|---|---|
| [GLOSSARIO.md](GLOSSARIO.md) | os termos do projeto, em poucas linhas cada |
| [EXPLICANDO.md](EXPLICANDO.md) ([en](EXPLAINED.md), [fr](EXPLIQUE.md)) | o problema em quatro camadas: 30 segundos, ensino médio, graduação, pesquisa |
| [FILOSOFIA.md](FILOSOFIA.md) ([en](PHILOSOPHY.md), [fr](PHILOSOPHIE.md)) | colapso, reversão de entropia local, teorema do James: descoberta cara, verificação barata |

## Proposições

| documento | para quê |
|---|---|
| [resultados.md](resultados.md) | resultados por versão, tabelas, certificados e como reconstruir |
| [exatos/NOVIDADE_V09.md](exatos/NOVIDADE_V09.md) | a busca bibliográfica dos exatos da v0.9 e o que ela não achou |
| [exatos/NOVIDADE_V010.md](exatos/NOVIDADE_V010.md) | a busca bibliográfica de K₄(7,4) = 10 e K₄(6,3) ≥ 12 (v0.10) e a lacuna que a deixa aberta (Haas 2011) |
| [PROPAGACAO_COTAS.md](PROPAGACAO_COTAS.md) | o que muda por consequência quando uma cota cai |

## Demonstração

| documento | para quê |
|---|---|
| [code-format.md](code-format.md) | o formato `covering-code/v1` e o verificador oficial |
| [exatos/LEAN_K742.md](exatos/LEAN_K742.md) | `K_7(4,2) = 19` inteiramente no kernel do Lean |
| [exatos/REDTEAM_K742.md](exatos/REDTEAM_K742.md), [REDTEAM_K753.md](exatos/REDTEAM_K753.md), [REDTEAM_K764.md](exatos/REDTEAM_K764.md) | os red teams das cotas inferiores certificadas |
| [exatos/](exatos/) | triagens, famílias, relaxações LP e certificados das células exatas |

## Método

| documento | para quê |
|---|---|
| [ARQUITETURA.md](ARQUITETURA.md) | o fluxo ledger, alvos, geradores, avaliadores, certificados e publicação, com os arquivos reais |
| [exatos/TRIAGEM_2026-10-04.md](exatos/TRIAGEM_2026-10-04.md) | quais células abertas podem virar valor exato |
| [attack/SETCOVER_2026-10-04.md](attack/SETCOVER_2026-10-04.md) | ataque por set cover |
| [literatura/VARREDURA_2026-10-03.md](literatura/VARREDURA_2026-10-03.md) | varredura de literatura |
| [fatoracao/README.md](fatoracao/README.md) | o domínio de fatoração de inteiros: registro, avaliador, cartão e o critério de vitória do programa "bater o GNFS" |

## Infraestrutura

| documento | para quê |
|---|---|
| [infra/RUNNERS.md](infra/RUNNERS.md) | runners do CI e cota de vCPU |
| [infra/LAKE_CACHE.md](infra/LAKE_CACHE.md) | cache da Mathlib compartilhado entre worktrees |
| [SESSAO-PESADA.md](SESSAO-PESADA.md) | manual da sessão que gasta: orçamento no Infinito, lote de VMs, paralelismo, fios abertos |
| [infra/PESADO_IAM.md](infra/PESADO_IAM.md) | permissões, cota e custo do `pesado` em lote de VMs spot (pedido ao dono) |

## Mapa do repositório

| caminho | o que é |
|---|---|
| `ledger/` | o ledger de células, o estado nosso e a proveniência ([ledger/README.md](../ledger/README.md)) |
| `data/codes/`, `data/structured/` | os códigos (um por linha) e a descrição estruturada de cada um |
| `tools/verify/` | verificador oficial em C e `check_all.sh` |
| `tools/exatos/` | busca exata: SAT com prova LRAT, CP-SAT, busca exaustiva |
| `tools/fatoracao/` | domínio de fatoração de inteiros (avaliador `p * q == N`) |
| `scripts/` | geradores, loop de recordes, certificados por síndromes, publicação |
| `CoveringLean/` | as provas em Lean 4 |
| `infinito/` | o MCP Infinito: ferramentas para colaboradores, com teto de crédito por pessoa |
| `paper/` | a nota (`main.tex`, `main.pdf`) |
| `site/` | a página pública |
| `tests/` | a suíte (`python3 -m pytest -q tests`) |

Na raiz: [CONTRIBUTING.md](../CONTRIBUTING.md), [AGENTS.md](../AGENTS.md), [SECURITY.md](../SECURITY.md) e
[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md).
