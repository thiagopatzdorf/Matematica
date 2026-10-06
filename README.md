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

## Estado atual (2026-10-05, v0.9.0)

Números conferidos no repositório (`ledger/cells.json`, `data/codes/`, `tools/verify/check_all.sh`).

| o quê | valor |
|---|---|
| células `K_q(n,R)` no ledger (q de 2 a 21) | 1145, das quais 523 com valor exato e 622 abertas |
| células em que temos teorema Lean próprio | 14 (12 abaixo da melhor cota superior publicada que achamos; `K_2(6,1) = 12`, o clássico, e `K_7(4,2) = 19`, as duas inteiramente no kernel) |
| ledger certificado | A machine-checked ledger of covering-code upper bounds, with formally certified exact entries. 487 das 1145 cotas superiores são teorema do Lean (`CoveringLedger.todas_as_cotas`, a partir de `K ≤ \|C\|` genérico, regras de construção e witnesses); as inferiores seguem herdadas da literatura, exceto `K_2(6,1)` e `K_7(4,2)` (ver `ledger/COBERTURA.md`) |
| exatos novos da v0.9 (fora do kernel) | `K_3(6,2) = 17`, `K_7(6,4) = 14` e `K_7(5,3) = 17`, potencialmente novos (não achados na literatura que buscamos, ver `docs/exatos/NOVIDADE_V09.md`). As cotas inferiores são **certificado computacional verificado** (Farkas inteiro, VeriPB, LRAT), não teorema do Lean; `K_3(6,2)` tem reprodução independente, as duas de `K_7` passaram por red team com amostra reconferida. A cota superior de `K_7(6,4) ≤ 14` é código novo, formalizada no Lean; a de `K_7(5,3) ≤ 17` é só a anunciada na literatura. Ver `docs/exatos/` e a seção 12 do paper |
| códigos em `data/codes/` | 18, todos aprovados pelo verificador oficial em C (`tools/verify/check_all.sh`) |
| destaques | `K_7(9,4) ≤ 1134` (publicado antes: 1475, Marosi, arXiv:2608.19872v3); `K_7(10,4) ≤ 5607` (antes: 6517, Kéri); `K_7(4,2) = 19` (antes: 17–19), inteiramente no kernel: `K742.K_7_4_2_eq_19`, sem hipótese, com as 70 refutações LRAT reexecutadas no kernel (lib `CoveringK742Sat`, fora do CI: 284 módulos, 37,8 h de CPU; ver `docs/exatos/LEAN_K742.md`) |
| Lean e Mathlib | Lean 4.34.1, Mathlib v4.34.1; `lake build` passa e roda no CI a cada push (`CoveringK742Sat` e `CoveringLedger` ficam fora do CI pelo custo) |
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
| `tools/exatos/` | busca exata (SAT com prova LRAT, CP-SAT, busca exaustiva); `K_7(4,2) = 19` fechado assim e depois levado ao kernel |
| `tools/fatoracao/` | domínio de fatoração de inteiros: registro de números do desafio RSA, importador e avaliador exato (`p * q == N`); ver `docs/fatoracao/` |
| `tools/literatura/` | varredura de literatura |
| `scripts/` | geradores, loop de recordes (`scripts/loop/`), certificados por síndromes, publicação |
| `CoveringLean/` | as provas em Lean 4 (biblioteca e certificados) |
| `infinito/` | o MCP Infinito: ferramentas para colaboradores, com teto de crédito por pessoa |
| `paper/` | a nota (`main.tex`, `main.pdf`) |
| `docs/` | glossário, arquitetura, resultados, formato de código, triagens |
| `tests/` | a suíte de testes (`python3 -m pytest -q tests`) |

Lê-se melhor nesta ordem: [docs/GLOSSARIO.md](docs/GLOSSARIO.md), [docs/ARQUITETURA.md](docs/ARQUITETURA.md),
[docs/README.md](docs/README.md).

## Como citar

DOI conceitual: [10.5281/zenodo.23085769](https://doi.org/10.5281/zenodo.23085769) (aponta sempre para a versão
mais nova). Tag `v0.9.0`. Os metadados completos estão em `CITATION.cff` e `.zenodo.json`; o GitHub oferece o botão
"Cite this repository" a partir do primeiro. A nota está em [paper/main.pdf](paper/main.pdf).

## Licença e conduta

Licença conforme `LICENSE` e `CITATION.cff` (CC-BY-4.0). Participar implica seguir o
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Problema de segurança: [SECURITY.md](SECURITY.md).
