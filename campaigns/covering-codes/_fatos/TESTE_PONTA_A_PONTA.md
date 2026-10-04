# Teste ponta a ponta do `kernel_run` (claim `k7-8-3-ub-1887`, 2026-10-04)

Pergunta: a infraestrutura de execuções de kernel (`factory_cauteloso.matematica.kernel`) funciona com execuções REAIS em máquinas
distintas, ou só com fixtures? Resposta medida abaixo. Evidência bruta em `_fatos/kernel_runs_tracer/{a,b}/` (leia o `README.md` de lá).

## O que foi feito

1. Duas VMs GCE distintas, sob demanda, `e2-highmem-4`, sem service account: `kr-teste-a` (zona `southamerica-east1-a`, instância
   `5198467000349702121`) e `kr-teste-b` (zona `-b`, instância `1876810319497476070`).
2. Cada uma rodou `tools/kernel_run_na_vm.sh` (clona o commit `1a5fa268dc916fde689e6aa801e591ac3c863b36`, `lake exe cache get`, `lake build
   CoveringLean.Syn_K1887` com log bruto, e gera o pacote de proveniência com `python3 -m factory_cauteloso.matematica.kernel ... provenance`).
   O teorema coberto é `Syn.K7_8_3_le_1887_syn` (registro formal `f-syn-1887`).
3. Os logs (12 622 bytes cada, sha256 distintos) foram enviados ao bucket `gs://factory-cauteloso-telemetria/matematica/kernel-runs/<sha256>.log`
   (a factory-01, com token de service account em memória); o tamanho foi conferido por GET de metadados do objeto.
4. `tools/campaign/migrate_covering.py` registra as duas execuções com `kernel.registrar_execucao` + `ArmazenadorPreEnviado` (ator `agente-kr`, papel
   `FORMALIZER`, `--raiz-fontes` = o repositório), lendo só arquivos versionados: refazer a migração dá o mesmo resultado (`recorded_at` à parte).
   A cadeia anterior ficou em `_autopsia/audit-pre-regeneracao-6/` (com `SHA256SUMS`) antes da migração.

## Resultado

| execução | nível calculado pela infraestrutura |
|---|---|
| A (`kr-1887-syn-1a5fa26-kr-teste-a`) | `KERNEL_VERIFIED` |
| A + B | `KERNEL_INDEPENDENTLY_REPRODUCED` (par = A, B) |
| claim `k7-8-3-ub-1887` | `Claim state: PROVED / Kernel evidence: KERNEL_INDEPENDENTLY_REPRODUCED` |
| os 10 claims do CoveringHeavy | continuam `EXTERNAL_RUN_REPORTED` |

Nenhum estado de claim mudou (21 PROVED, 7 INDEPENDENTLY_REPRODUCED, 2 EXHAUSTIVE_BOUNDED, 4 REFUTED, antes e depois): as guardas de estado não leem
`kernel_runs/`; o eixo do kernel é outro eixo.

## Tentativas de quebrar (todas viram teste em `tests/test_campaign_kernel_migration.py`, classe `TracerRunsTest`)

| tentativa | resultado |
|---|---|
| repetir o mesmo `run_id` | recusada: já existe (registro intacto) |
| `prov.json` adulterado (id de instância trocado) | recusada: `bundle_sha256` não confere |
| B sem proveniência (host/toolchain só declarados) | registra como `EXTERNAL_RUN_REPORTED`; não pareia |
| tamanho do log errado | recusada: tamanho informado != tamanho do log local |
| nome de objeto sem o sha256 | recusada: o nome deve conter o sha256 do log |
| A registrado de novo sob outro `run_id` | registra como `KERNEL_VERIFIED`, mas NÃO forma par independente (mesmo host/log) |
| log de B com a proveniência de A (mistura) | registra como `KERNEL_VERIFIED` (a instância é a de A), mas não forma par |

Os testes que precisam registrar algo usam uma cópia da campanha DENTRO do repo (`campaigns/_tmp-*`, mesma profundidade de
`campaigns/covering-codes`); a campanha real nunca é escrita.

## Achado lateral

`audit` numa cópia da campanha FORA do repo (ex.: `/tmp`) dá `sustentada=False` por "stale: o sujeito não existe mais em disco": os sujeitos
(fontes, witnesses) são caminhos relativos ao repositório (`data_root: ../..`). A campanha só é auditável dentro do repo; por isso as cópias
dos testes ficam dentro dele.

## Limites (o que este teste NÃO prova)

* **capturada != atestada.** A proveniência é capturada pela ferramenta NA VM (metadata do GCE, `lean`/`lake`/`git`), mas quem registra não está na
  VM e a ferramenta não prova que o arquivo veio de lá; `host.id` e o `numeric_instance_id` do pacote continuam sendo o que o pacote diz.
* O objeto no bucket não é verificado pela ferramenta (`verification.modo = pre_enviado`): vale a palavra de `conferido_por` (sessão Claude
  2026-10-04 via factory-01; GET de metadados confirmou 12 622 bytes). A hora exata do GET não foi registrada.
* Quem rodou, quem registrou e quem escreveu os claims é o mesmo agente (Claude). "Independente" é técnico (duas instâncias, dois logs, mesmo
  commit e fontes), não outra pessoa. O enunciado formal continua sem revisão humana e a novidade não foi avaliada.
* A janela de cada execução é a do script da VM (inclui instalação do elan e `lake exe cache get`), não só o `lake build`.
* Cobre um claim (Syn_K1887, 4 folhas). O CoveringHeavy continua com uma única execução histórica sem log persistido.

## Custo

2 VMs `e2-highmem-4` sob demanda, ~12 min cada mais a criação; mantidas `TERMINATED` (disco cobrado, sem computação). Sem GPU, sem chamada paga a modelo.
