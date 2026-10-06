# Sessão pesada: manual de quem toca o pipeline com dinheiro

Para o agente que abre uma sessão nova para **paralelizar, usar o Vertex AI e alocar infra por orçamento**.
Leia antes: [`AGENTS.md`](../AGENTS.md) (regras do repo), [`infinito/README.md`](../infinito/README.md) (o MCP) e
[`docs/infra/PESADO_IAM.md`](infra/PESADO_IAM.md) (o que falta para o lote rodar). Estado conferido em 2026-10-06.

## 1. A regra que vem antes de tudo

* **O Lean é a verdade.** Busca, LLM e VM produzem **candidatos**. Cota só muda depois do verificador exato
  (`tools/verify/verify`) e, se for teorema, do `lake build` verde, sem `sorry`, `native_decide` nem axioma novo.
  Um `INFEASIBLE` de busca não prova inexistência.
* **Nada é publicado sem o dono.** Zenodo, site, tag, release, merge, deploy, IAM e cota são do Thiago. O agente
  abre PR (não-rascunho quando pronto), com comando e contagem de testes no corpo, e para.
* **Nunca edite `ledger/cells.json` nem `ledger/ours.json` à mão**: saem de `ledger/build.py`.
* A URL pessoal do Infinito é a senha: nunca em issue, PR, log ou commit. Segredo se confere pelo tamanho.

## 2. As ferramentas

**MCP Infinito** (o seu, com teto por pessoa; tudo que custa é seco por padrão):

| tool | para quê | custa |
|---|---|---|
| `meus_creditos` | teto, gasto, reservado, disponível. **Primeira chamada de toda sessão** | não |
| `alvos` | células ranqueadas por chance de melhorar (`limite`, `max_espaco`) | não |
| `celula` | uma célula do ledger: cotas, fontes, nosso estado (`"K3(6,2)"` ou `"3,6,2"`) | não |
| `verificar_codigo` | verificador exato num arquivo de `data/codes/` | não |
| `papers_buscar`, `biblioteca_buscar` | arXiv, OpenAlex, Semantic Scholar, Zenodo; a biblioteca já guardada | não |
| `gemini` | modelo pelo **Vertex AI** (`INF_GEMINI_BACKEND=vertex`, `gemini-3.8-flash` em `locations/global`): reserva o pior caso, cobra os tokens medidos. **Resposta é hipótese, nunca prova** | sim |
| `pesado_tipos` | máquinas aceitas com a tarifa/h de cada uma, teto de `paralelo`, scripts da allowlist | não |
| `pesado` | lote de N VMs spot (`lake_build`, `verificar_grande`, `script`) | sim |
| `pesado_status` | andamento shard a shard; liquida o que terminou e apaga VM vencida | não |

**MCP da Factory** para o resto: `gcp_inventario`/`gcp_rest` (ler o projeto GCP; escrita só com o dono), `gcp_custo`
(fatura real), `executar` na factory-01 (clone de referência e trabalho longo com `nohup` e log em
`~/state/maestro/agentes/`; o cliente corta em ~60 s), `segredos` (nunca revela). **Não** use a Factory para criar
VM por fora do Infinito: o gasto tem de passar pelo ledger, senão o teto vira promessa.

## 3. O fluxo do orçamento ("falo 10 dólares e ele faz")

1. **O dono soma o dinheiro.** Ele (ou o maestro a pedido dele) chama, com a URL de administrador do Infinito:
   `admin_creditos(email="<e-mail da sessão>", somar_usd=10, motivo="campanha X")`. `somar_usd` soma ao teto atual;
   `teto_usd` fixa um valor absoluto; o motivo é obrigatório e vira evento no ledger. Administrador é quem está em
   `INF_ADMINS` (hoje o e-mail do Thiago) ou a URL do token de serviço (`INFINITO_TOKEN_ADMIN` no cofre da Factory).
   A sessão de agente usa a **própria** URL de colaborador, nunca a de administrador (administrador não tem teto).
2. **O agente vê o saldo**: `meus_creditos` → `disponivel_usd`.
3. **Pede seco**: `pesado("script", 1.0, {"nome": "...", "commit": "<sha na main>"}, paralelo=6)` sem `confirmar`
   devolve `tarifa_hora_usd`, `custo_maximo_usd` (= N × horas × tarifa) e `cabe`.
4. **Confirma** com `confirmar=true`: o lote inteiro é reservado **antes** de ligar a primeira VM. Se uma VM não sobe
   (cota, falta de capacidade spot), as outras são apagadas e a reserva volta.
5. **Acompanha** com `pesado_status(job)`: cada shard fecha com o tempo real; o job liquida quando todos fecham.
   Log e `$SAIDA` ficam no bucket de estado em `jobs/<job>/`.

Ordem de grandeza (2026-10-06): e2-highmem-8 spot ≈ **US$ 0,18/h por VM** com a margem do ledger. Com US$ 10 dá
~55 VM·h, por exemplo 6 VMs × 9 h. Hoje cabem **6 VMs por lote** (cota de IPs externos da região); o teto de código é
8 (`INF_PESADO_PARALELO_MAX`).

## 4. Paralelizar

* **Dentro do Claude Code**: subagentes (a ferramenta de agentes), um por frente independente, cada um no seu
  worktree/branch, com o mesmo contrato de PR. O maestro integra, roda a suíte inteira e só então abre o PR.
  Subagente que "rodou os testes" pode ter rodado só os novos: confira.
* **Workflow** (script de orquestração) **só quando o dono escrever "ultracode" ou "use a workflow"**.
* **Na nuvem**: `pesado(..., paralelo=N)`. O shard `i` recebe `SHARD_INDEX=i`, `SHARD_TOTAL=N`; o script divide o
  trabalho por aí (ex.: órbita `k` → shard `k % N`). Script novo entra por PR em `pesado/jobs/`
  ([contrato](../pesado/jobs/README.md)) e só roda depois do merge, porque a VM confere que o commit está na `main`.
  Rode `fumaca` (0,2 h) antes do primeiro job de uma campanha.
* **Gemini em paralelo**: várias chamadas de `gemini` são independentes; cada uma reserva o pior caso, então o teto
  nunca fura. Use para triagem de literatura e geração de candidatos, nunca para decidir cota.

## 5. Onde está o estado e o que está aberto (medido no repo em 2026-10-06)

* Estado: `ledger/` (fonte da verdade das cotas; `ledger/COBERTURA.md` é o placar gerado), `CoveringLean/` (os
  teoremas), `docs/exatos/` (frentes de valor exato), `docs/historico/`, releases do GitHub e o DOI no Zenodo.
* **K3(6,2)** (`docs/exatos/k362/`): **fechado** em `K_3(6,2) = 17` na v0.9.0 (13 099 certificados de Farkas para M = 16,
  red team #61, reprodução independente #66). A "fase 2" que aparece no diagnóstico do M = 15
  (`docs/exatos/k362/K3_M15_DIAGNOSIS.md`, item 6: dividir por canonical augmentation) ficou sem objeto para essa célula; a técnica é a
  Fase 0 do plano abaixo.
* **Plano de exatos em fases** (`docs/exatos/TRIAGEM_2026-10-04.md`, fim): Fase 0 local (`tools/exatos/orderly`,
  reproduzir valores conhecidos), Fase 1 ≤ US$ 20 e Fase 2 ≤ US$ 40 **em VMs spot com checkpoint por subárvore**,
  teto total sugerido US$ 60. É o primeiro cliente do `pesado` v2.
* **K2(14,5)**: PR #94 em rascunho (M = 10, 2 835 instâncias ainda sem certificado).
* **"S1–S15"**: no repo só aparece como as fatias `CoveringLean/K742Sat/S0..S29` da refutação de K7(4,2), já na `main`.
  Nenhuma issue nem documento chama algo de "onda S1–S15": **pergunte ao dono** o que é antes de gastar.
* **Banho de loja** (READMEs, filosofia, página `/matematica`, identidade visual): entrou na `main` pelos PRs #81–#90;
  o branch `banho/filosofia` ainda tem 3 commits fora da `main` (proposição da filosofia acompanhando o número de cotas).
* Issue aberta: #38 (`[problema] fatoracao-rsa-270`, proposta). 39 branches remotos sem merge: não reabra frente
  sem ler o último commit e o PR fechado dela.
* Infra: o `pesado` em produção está **parado** desde que a VM `lean-build2` foi apagada (2026-10-06); volta com o
  merge do PR do lote + IAM + deploy, todos do dono ([`docs/infra/PESADO_IAM.md`](infra/PESADO_IAM.md)).

## 6. Erros já pagos (não repita)

* `start`/`insert` do Compute devolve 200 com o erro **dentro** da operação (cota, capacidade): o executor já lê.
* Cota de IPs e de SSD trava antes da de CPU: o executor confere a cota e recusa sem cobrar.
* Exit 0 não é entrega: prova é o estado depois (o job `liquidado`, o arquivo no bucket, o `lake build` verde).
* Atrito (comando que não roda, regra que contradiz o código): issue com `atrito:` no título.
