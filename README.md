# Matemática: hub de descoberta com prova verificável

Um lugar onde **pessoas e agentes propõem problemas matemáticos e os resolvem por pipelines definidos**, e onde
só conta o que uma máquina confere de forma exata: um avaliador determinístico ou o kernel do Lean. Opinião de
modelo (ou de gente) não é prova aqui.

O primeiro domínio são os **códigos de cobertura**: o menor número `K_q(n,R)` de palavras de um código de
comprimento `n` sobre `q` símbolos tal que toda palavra do espaço fique a distância de Hamming ≤ `R` de alguma
delas. O modelo (candidato achado por busca, conferido por avaliador exato, certificado no Lean, publicado) vale para
qualquer problema em que **verificar é bem mais barato que achar**. Código de cobertura é o primeiro exemplo, não o último.

## Por que importa

* Cotas de `K_q(n,R)` aparecem em teoria da informação, testes combinatórios e apostas (o "football pool").
  Elas só mudam quando alguém acha um código menor, e isso é fácil de conferir e difícil de achar.
* O Lean vira o juiz final: as nossas cotas são teoremas, sem `sorry` e sem `native_decide`.
* Colaboradores convidados recebem crédito de infra (US$ 20 por pessoa, até 10 pessoas) pelo MCP Infinito, com teto
  aplicado em código.

## Estado atual (2026-10-03)

Números conferidos no repositório (`ledger/cells.json`, `data/codes/`, `tools/verify/check_all.sh`).

| o quê | valor |
|---|---|
| células `K_q(n,R)` no ledger (q de 2 a 21) | 1145, das quais 519 com valor exato e 626 abertas |
| células em que temos teorema Lean | 12 (11 abaixo da melhor cota superior publicada que achamos; `K_2(6,1) = 12` é o clássico, agora com prova no kernel) |
| códigos em `data/codes/` | 16, todos aprovados pelo verificador oficial em C |
| destaque | `K_7(9,4) ≤ 1134` (publicado antes: 1475, Marosi, arXiv:2608.19872v3) |
| Lean e Mathlib | Lean 4.34.1, Mathlib v4.34.1; `lake build` passa e roda no CI a cada push |
| axiomas | todo `#print axioms` mostra no máximo `propext, Classical.choice, Quot.sound` |

Novidade na literatura é afirmação nossa (busca bibliográfica descrita em `STATE_OF_ART.md`), não do Lean. Tabela
por célula, certificados e reprodução: [docs/resultados.md](docs/resultados.md).

## Contribua em 5 minutos

**Pessoa**

1. Clone e rode o verificador oficial em todos os códigos (precisa de `cc` e Python 3):

        git clone https://github.com/thiagopatzdorf/Matematica && cd Matematica
        tools/verify/check_all.sh

2. Veja onde há chance de melhorar e leia a célula escolhida:

        python3 ledger/targets.py --top 10

3. Abra uma issue dizendo qual célula ou problema você ataca (isso é a reivindicação) e siga o
   [CONTRIBUTING.md](CONTRIBUTING.md).

**Agente**

1. Leia o [AGENTS.md](AGENTS.md) (setup, comandos, o que nunca fazer).
2. Use o MCP Infinito (cota de infra por pessoa) para consultar o ledger e verificar códigos sem custo:
   [infinito/README.md](infinito/README.md).
3. Todo candidato passa pelo verificador exato antes de qualquer afirmação.

## Mapa do repositório

| caminho | o que é |
|---|---|
| `ledger/` | o ledger de células, o estado nosso e a proveniência (ver `ledger/README.md`) |
| `data/codes/`, `data/structured/` | os códigos (um por linha) e a descrição estruturada de cada um |
| `tools/verify/` | verificador oficial em C e `check_all.sh` |
| `tools/exatos/` | busca exata (SAT com prova LRAT, CP-SAT, busca exaustiva); `K_7(4,2) = 19` fechado assim |
| `tools/literatura/` | varredura de literatura |
| `scripts/` | geradores, loop de recordes (`scripts/loop/`), certificados por síndromes, publicação |
| `problems/` | o registro de problemas: cartões com estado, avaliador e histórico (ver `problems/README.md`) |
| `evaluators/` | avaliadores exatos com contrato único: códigos de cobertura, honestidade do Lean, ponte ledger–código–teorema |
| `site/`, `scripts/site/` | o mapa público da fronteira, gerado do ledger |
| `CoveringLean/` | as provas em Lean 4 (biblioteca e certificados) |
| `infinito/` | o MCP Infinito: ferramentas para colaboradores, com teto de crédito por pessoa |
| `paper/` | a nota (`main.tex`, `main.pdf`) |
| `docs/` | glossário, arquitetura, resultados, formato de código, triagens |
| `tests/` | a suíte de testes (`python3 -m pytest -q tests`) |

Lê-se melhor nesta ordem: [docs/GLOSSARIO.md](docs/GLOSSARIO.md), [docs/ARQUITETURA.md](docs/ARQUITETURA.md),
[docs/README.md](docs/README.md).

## Como citar

DOI conceitual: [10.5281/zenodo.23085769](https://doi.org/10.5281/zenodo.23085769) (aponta sempre para a versão
mais nova). Tag `v0.6.0`. Os metadados completos estão em `CITATION.cff` e `.zenodo.json`; o GitHub oferece o botão
"Cite this repository" a partir do primeiro. A nota está em [paper/main.pdf](paper/main.pdf).

## Licença e conduta

Licença conforme `LICENSE` e `CITATION.cff` (CC-BY-4.0). Participar implica seguir o
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Problema de segurança: [SECURITY.md](SECURITY.md).
