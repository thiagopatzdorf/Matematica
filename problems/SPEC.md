# Cartão de Problema v1

O registro de problemas do hub. Um **cartão** é um arquivo JSON em `problems/cartoes/<id>.json`
que descreve um problema, o melhor resultado conhecido, o nosso, o avaliador que decide, e o
histórico de tudo que aconteceu com ele. Pessoas e agentes propõem, reivindicam e resolvem; **cada
afirmação só avança de estado com evidência de um avaliador exato ou do kernel do Lean**.

As regras abaixo estão em código: `tools/problems/lifecycle.py` (máquina de estados),
`tools/problems/validate.py` (validador) e `problems/schema/cartao.schema.json` (editores). Se este
texto divergir do código, vale o código (os testes de `tests/test_problems*.py` pegam a divergência
de estados, tipos e campos).

## Campos

| campo | tipo | obrigatório | o que é |
|---|---|---|---|
| `formato` | `"cartao-problema/v1"` | sim | versão do cartão |
| `id` | slug `[a-z0-9-]{3,64}` | sim | estável para sempre; o arquivo se chama `<id>.json` |
| `titulo` | texto | sim | |
| `dominio` | slug | sim | ex.: `codigos-de-cobertura` |
| `tipo` | `cota_superior` \| `cota_inferior` \| `valor_exato` \| `construcao` \| `formalizacao` | sim | o que seria uma resposta |
| `enunciado` | texto | sim | autocontido |
| `enunciado_formal` | texto ou `null` | não | nome da declaração Lean que formaliza o enunciado |
| `estado` | um dos 10 do ciclo de vida | sim | sempre igual ao `para` da última entrada do histórico |
| `melhor_conhecido` | `{valor, fonte, ref, intervalo?}` | sim | o publicado. `valor` é `null` quando só se conhece um intervalo `{lb, ub}` (caso de `valor_exato`) |
| `nosso` | `{valor, estado, prova}` | sim | `estado` ∈ `nenhum` \| `computacional` \| `lrat` \| `lean`; `valor` é `null` se e só se `nenhum`; `prova` aponta a declaração Lean, o certificado ou o código |
| `avaliador` | `{id, como_rodar, custo_estimado_usd}` | sim | quem decide se um candidato vale; o custo é medido, em dólares (0 se roda local) |
| `celula_ledger` | `K<q>(<n>,<R>)` ou `null` | não | liga ao `ledger/cells.json` |
| `historico` | lista | sim | somente-anexa (abaixo) |

Cada entrada do histórico: `{quem, papel, quando (AAAA-MM-DD), de, para, evidencia, origem?}`. A
primeira é `de: null, para: proposto`. `origem: "importacao"` marca cartões semeados por script a
partir de fontes já auditadas (o ledger e os docs de `tools/exatos`); só nesse caso um mesmo
`quem` pode percorrer vários papéis, e a evidência exigida continua a mesma. Importação nunca
publica.

## Ciclo de vida

```
proposto → aceito → aberto → reivindicado → candidato → verificado → certificado → publicado
                       ↑          │              │            │
                       └──────────┴──────────────┘            └→ candidato (revisão falhou)
 de aberto a verificado:  → refutado            qualquer estado → arquivado
```

| de → para | quem (papel) | evidência exigida na entrada |
|---|---|---|
| (nada) → `proposto` | qualquer pessoa ou agente | nenhuma |
| `proposto` → `aceito` | mantenedor | nenhuma (o mantenedor confere duplicata e enunciado) |
| `aceito` → `aberto` | mantenedor | nenhuma; o cartão já tem de ter avaliador |
| `aberto` → `reivindicado` | qualquer | `expira_em` (AAAA-MM-DD), de 1 a 30 dias depois |
| `reivindicado` → `aberto` | sistema (expirou) ou mantenedor | `expira_em` vencido; sem aviso prévio |
| `aberto`/`reivindicado` → `candidato` | qualquer; se reivindicado, só quem reivindicou ou um mantenedor | `artefato` (caminho/URL) e `sha256` dele |
| `candidato` → `verificado` | avaliador (CI) ou mantenedor | `avaliador` igual ao do cartão, `veredito: "ok"` e a `saida` do avaliador exato, anexada |
| `verificado` → `certificado` | avaliador (CI) ou mantenedor | `kernel: "lean"` e `declaracao` aceita pelo kernel; `nosso.estado` tem de ser `lean` |
| `certificado` → `publicado` | **só o dono** | nenhuma (a decisão é dele) |
| `candidato`/`verificado` → `aberto`/`candidato` | mantenedor ou avaliador | o motivo (candidato rejeitado) |
| `aberto`…`verificado` → `refutado` | mantenedor | `contraexemplo` ou `ref` |
| qualquer → `arquivado` | mantenedor | `motivo` |

Consequências, todas conferidas por teste:

* não se chega a `certificado` sem passar por `verificado`, nem a `verificado` sem a saída do
  avaliador; `certificado` sem o kernel do Lean é recusado (resultado só com prova LRAT fica em
  `verificado`, como o K_7(4,2));
* a reivindicação é uma trava curta: expira sozinha (`lifecycle.expirar`), então ninguém segura um
  problema para sempre; passado o prazo qualquer um pode reivindicar de novo ou submeter candidato;
* `arquivado` é terminal; `refutado` só leva a `arquivado`;
* o histórico é refeito do zero a cada validação: um salto de estado, um `estado` que não bate com
  a última entrada ou uma evidência faltando reprovam o cartão.

## O que é "avaliador exato"

Um programa determinístico que, dado o candidato, devolve veredito sem juízo de ninguém (ex.:
`scripts/loop/verify_cover.py` confere se um código cobre `Z_q^n` com o raio `R`). Inexistência
(cota inferior) só vale com prova independente: LRAT conferido por dois verificadores, ou Lean.
Palpite, "parece correto" e saída que o autor resumiu à mão não são evidência.

## Como o cartão se liga ao ledger

`celula_ledger` aponta a célula; `ledger/cells.json` continua a fonte do valor publicado e do nosso
estado, e `tools/problems/seed_from_ledger.py` gera cartões a partir dele, sem digitar valor. O
teste reprova se um cartão semeado divergir do ledger (ou do doc citado). Onde os dois divergem
de verdade, o cartão diz: o K_7(4,2) está `17 ≤ K ≤ 19` no ledger e `= 19` em
`docs/exatos/FASE1_B_K742.md`; o cartão registra o intervalo em `melhor_conhecido` e o 19 em
`nosso`, com estado `verificado` (LRAT, sem Lean).
