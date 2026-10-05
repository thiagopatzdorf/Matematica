# Runners do CI e cota de vCPU (infra da campanha)

Registro de 2026-10-05 (agente de infraestrutura). Medição primeiro, mudança depois.

## 1. Fila do CI: o que foi medido

**Onde os jobs rodam.** Os três workflows (`ci.yml`, `lean-syn.yml`,
`verify-codes.yml`) pedem `runs-on: ubuntu-latest`, isto é, runner
**hospedado do GitHub**. O repositório é público, então esses minutos são
gratuitos e sem teto de minutos. Não há nenhum runner self-hosted registrado
(`GET repos/thiagopatzdorf/Matematica/actions/runners` → `total_count: 0`).

**Quanto os jobs esperaram** (`started_at − created_at` de cada job, 422 jobs
de 200 runs, de 2026-10-05T05:34Z a 21:52Z):

| medida | valor |
|---|---|
| mediana | 2 s |
| p90 | 7 s |
| máximo | 607 s (~10 min) |
| jobs com espera > 5 min | 6, todos entre 21:09Z e 21:18Z |
| jobs com espera > 15 min | 0 |

Concorrência do próprio repo no pico (21:19Z–21:23Z): 6 jobs ao mesmo tempo,
longe do limite de 20 jobs simultâneos de conta Free. O limite de concorrência
não era o gargalo.

**Causa.** Incidente crítico do GitHub Actions aberto às 19:11Z de
2026-10-05 ("delays when assigning GitHub-hosted runners to Actions jobs",
githubstatus.com). Às 21:32Z o GitHub publicou "Queued jobs are clearing, new
jobs are not delayed". As seis esperas longas caem exatamente nessa janela.

**Depois da mitigação** (runs de 21:33Z, 21:34Z e 21:52Z): espera de 1 a 5 s
por job.

## 2. O que foi decidido, e por quê

**Nenhum runner self-hosted foi registrado para este repo.** Motivos:

1. A fila foi causada por um incidente externo e já se resolveu; na
   operação normal a espera é de segundos. Não havia fila a cortar com
   hardware nosso.
2. **Repo público + runner self-hosted é risco de segurança.** Um PR de fork
   executa código arbitrário no runner (a política atual do repo exige
   aprovação só para quem contribui pela primeira vez:
   `approval_policy: first_time_contributors`). Os candidatos óbvios são
   máquinas compartilhadas:
   - `factory-ci` (spot): guarda na metadata `runner-token`, o token de
     registro de runner do `fabrica-de-sites`. Um job malicioso daqui poderia
     ler a metadata, registrar um runner falso lá e capturar segredos dos jobs
     da loja.
   - `factory-01`: guarda o cofre da Factory. Fora de questão.
3. Os minutos hospedados são grátis para repo público; um runner nosso custaria
   VM e manutenção para ganhar segundos.

**Se a fila voltar sem incidente do GitHub** (medir antes: rode o script da
seção 4), o caminho seguro é um runner **dedicado** e isolado:

- VM spot própria (sem service account, sem metadata de outros repos),
  runner efêmero (`--ephemeral`) registrado só para `thiagopatzdorf/Matematica`
  com label própria, por exemplo `matematica`;
- só para eventos de quem já tem escrita: `push` em `main` e
  `workflow_dispatch`, e PR apenas quando
  `github.event.pull_request.head.repo.full_name == github.repository`;
  PR de fork continua no `ubuntu-latest`;
- política de aprovação de fork apertada para `all_external_contributors`
  (`PUT repos/thiagopatzdorf/Matematica/actions/permissions/fork-pr-contributor-approval`).

O interruptor liga/desliga já existe no `fabrica-de-sites`
(`apps/factory/bin/runner-farm.py` e `factory-ci-vm.py`), e serve de molde
para essa VM dedicada, mas não deve apontar a `factory-ci` atual para este repo.

**Como desfazer:** nada foi criado no item 1, então não há o que desfazer.

## 3. Cota de vCPU do GCP (projeto `gen-lang-client-0503404929`)

Lido pela Compute API e pela Cloud Quotas API em 2026-10-05 ~21:55Z:

| cota | antes | pedido | depois | uso no momento |
|---|---|---|---|---|
| `CPUS_ALL_REGIONS` (global) | 64 | 96 | **96, aprovado na hora** | 32 |
| `CPUS` em southamerica-east1 | 200 | — | 200 | 32 |
| `T2D_CPUS` em southamerica-east1 | 24 | 96 e 48, **ambos negados** | 24 | **24, esgotada** (3 × `t2d-standard-8` spot `lote-k2145-*`) |
| `E2` em southamerica-east1 | 24 | (48 negado em 2026-10-04) | 24 | 8 |
| `PREEMPTIBLE_CPUS` em southamerica-east1 | 0 | — | 0 | spot conta na cota normal |

**O que esgota de fato é a família T2D na região (24), não o total.** Até o
pedido de T2D sair, há folga sem pedir nada em outras famílias spot da mesma
região: N2 (200), C2D (100), N4 e E4 (200 cada, cota por família), T2A/Arm
(96). Com `CPUS_ALL_REGIONS` em 96, o teto da conta passa a ser 96 vCPU no
total, somando todas as famílias.

Preferências de cota (Cloud Quotas API, `locations/global/quotaPreferences`):

- `cpus-all-regions-infinito-2026-10`: `preferredValue` 64 → 96, aprovado.
- `t2d-cpus-sa-east1-matematica-2026-10` (novo): 96 negado na hora; refeito
  com 48, também negado (a negação automática sai em ~3 s; não é revisão humana).

Aumento de cota não custa nada por si; o custo vem só das VMs ligadas.

**Como desfazer** (baixar de volta; valores abaixo do uso atual são recusados):

```
# PATCH com contactEmail obrigatório só para AUMENTO; para reduzir basta o valor
PATCH https://cloudquotas.googleapis.com/v1/projects/gen-lang-client-0503404929/locations/global/quotaPreferences/cpus-all-regions-infinito-2026-10?updateMask=quotaConfig.preferredValue
{"quotaConfig": {"preferredValue": "64"}}
```

O pedido de T2D foi negado pela via automática; o pedido manual vai pelo console, com
justificativa e histórico de cobrança:
https://console.cloud.google.com/iam-admin/quotas?project=gen-lang-client-0503404929
(filtro: `T2D CPUs`, região `southamerica-east1`).

## 4. Como medir a fila de novo

```
gh api 'repos/thiagopatzdorf/Matematica/actions/runs?per_page=50' --jq '.workflow_runs[].id' |
while read r; do
  gh api "repos/thiagopatzdorf/Matematica/actions/runs/$r/jobs" \
    --jq '.jobs[]|[.name,.created_at,.started_at]|@tsv'
done
# espera = started_at − created_at; compare com https://www.githubstatus.com antes de culpar o runner
```
