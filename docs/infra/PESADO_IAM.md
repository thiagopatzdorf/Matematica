# Pesado v2: o que a service account do Infinito precisa (pedido ao dono)

Medido em 2026-10-06 com leitura de política, **sem conceder nada**. Quem aplica é o dono (risco alto: IAM e gasto).

## O que ela tem hoje

SA do serviço Cloud Run `infinito-mcp`: `infinito-mcp@gen-lang-client-0503404929.iam.gserviceaccount.com`.

| onde a permissão poderia estar | o que tem (lido em 2026-10-06) |
|---|---|
| projeto (`getIamPolicy`) | só `roles/aiplatform.user` (o Gemini pelo Vertex) |
| bucket de estado `gen-lang-client-0503404929-infinito-estado` | `roles/storage.objectAdmin` |
| a própria SA (quem pode assinar como ela) | nada (política vazia): não consegue `signBlob` |
| imagem `bkp-lean-build2-20261006` | nada (política vazia) |
| instância `lean-build2` (`compute.instanceAdmin.v1` só nela) | **sumiu junto com a VM**, apagada em 2026-10-06 |

Conclusão: hoje ela **não tem nenhuma** das permissões de Compute abaixo; o `pesado` em produção está quebrado desde
que a `lean-build2` foi apagada (o executor antigo dá 404 na VM). Por que não `testIamPermissions`: essa chamada testa
quem chama, e daqui só dá para chamar como outra conta; a Policy Troubleshooter API está desligada no projeto (403).
Por isso a medição é pela leitura de cada política onde um papel poderia estar.

## O que o executor de lote chama, e a permissão de cada chamada

| chamada do `executor_lote.py` | permissão |
|---|---|
| ler cota (`regions.get`, `projects.get`) antes de criar | `compute.regions.get`, `compute.projects.get` |
| `instances.insert` (spot, imagem, IP externo efêmero, metadados, rótulos) | `compute.instances.create`, `compute.disks.create`, `compute.images.useReadOnly`, `compute.subnetworks.use`, `compute.subnetworks.useExternalIp`, `compute.networks.use`, `compute.networks.useExternalIp`, `compute.instances.setMetadata`, `compute.instances.setLabels` |
| acompanhar a operação do insert | `compute.zoneOperations.get` |
| `instances.get` e `getGuestAttributes` | `compute.instances.get`, `compute.instances.getGuestAttributes` |
| varredura de órfãs (`instances.list` por rótulo) | `compute.instances.list` |
| apagar no fim, no prazo ou órfã | `compute.instances.delete` |
| URL assinada para a VM subir log e saída (opcional) | `iam.serviceAccounts.signBlob` **na própria SA** (`roles/iam.serviceAccountTokenCreator` dela nela mesma) |

**Não precisa** de `iam.serviceAccountUser` em SA nenhuma: a VM sobe **sem service account** (decisão deste PR). Ela
não tem credencial; o resultado sobe por URL assinada de um objeto só, válida até o prazo do job.

## Proposta (o dono roda; nada disto foi aplicado)

Dois papéis customizados, para que a SA só toque em VM cujo nome começa por `inf-pesado-`:

    P=gen-lang-client-0503404929
    SA=infinito-mcp@$P.iam.gserviceaccount.com

    gcloud iam roles create infinitoPesadoVM --project=$P --title="Infinito pesado: VMs do lote" \
      --permissions=compute.instances.create,compute.instances.delete,compute.instances.get,\
    compute.instances.getGuestAttributes,compute.instances.setMetadata,compute.instances.setLabels,compute.disks.create

    gcloud iam roles create infinitoPesadoApoio --project=$P --title="Infinito pesado: apoio do lote" \
      --permissions=compute.instances.list,compute.zoneOperations.get,compute.regions.get,compute.projects.get,\
    compute.subnetworks.use,compute.subnetworks.useExternalIp,compute.networks.use,compute.networks.useExternalIp

    gcloud projects add-iam-policy-binding $P --member=serviceAccount:$SA \
      --role=projects/$P/roles/infinitoPesadoVM \
      --condition='title=so-inf-pesado,expression=resource.name.extract("/instances/{n}").startsWith("inf-pesado-") || resource.name.extract("/disks/{n}").startsWith("inf-pesado-")'

    gcloud projects add-iam-policy-binding $P --member=serviceAccount:$SA \
      --role=projects/$P/roles/infinitoPesadoApoio

    gcloud compute images add-iam-policy-binding bkp-lean-build2-20261006 --project=$P \
      --member=serviceAccount:$SA --role=roles/compute.imageUser

    # opcional: log completo e $SAIDA no bucket (sem isto, volta só o fim do log)
    gcloud iam service-accounts add-iam-policy-binding $SA --project=$P \
      --member=serviceAccount:$SA --role=roles/iam.serviceAccountTokenCreator

Inversa (templo): `remove-iam-policy-binding` dos mesmos quatro, depois `gcloud iam roles delete` dos dois papéis.

Se a condição por nome der trabalho na primeira criação (o Compute avalia o nome do disco de boot, que herda o nome
da instância), o atalho é `roles/compute.instanceAdmin.v1` no projeto, que é bem mais largo: prefira corrigir a
expressão a alargar o papel.

## Deploy (depois do merge, também do dono)

1. `docker build -f infinito/Dockerfile .` (a imagem agora leva `pesado/jobs/`) e novo deploy do `infinito-mcp`.
2. Trocar `INF_EXECUTOR=vm` por `INF_EXECUTOR=lote` (com `vm` o módulo recusa honestamente: não existe mais executor
   de VM fixa). O resto tem padrão; `INF_PESADO_PARALELO_MAX` limita o lote.
3. Prova barata: `pesado("script", 0.2, {"nome": "fumaca"}, paralelo=2, confirmar=true)` e `pesado_status` até
   `liquidado`; conferir no bucket `jobs/<job>/shard-0-saida.tar.gz` e, no Compute, que não sobrou `inf-pesado-*`.

## Cota e custo (medidos em 2026-10-06)

* Preço spot em São Paulo (Cloud Billing Catalog API): E2 US$ 0,00761/vCPU·h e US$ 0,001019/GiB·h; disco balanced
  US$ 0,15/GB·mês; IP externo US$ 0,005/h. Uma e2-highmem-8 com 100 GB: **US$ 0,152/h cru, US$ 0,182/h com a margem de
  20 %** que o ledger cobra. Lote de 8 × 1 h: reserva US$ 1,46, custo real ≈ US$ 1,21 se rodar a hora inteira.
* Cotas da região: `IN_USE_ADDRESSES` 8 (2 em uso) é o que trava primeiro, então **6 VMs** por lote hoje; `SSD_TOTAL_GB`
  1000 (370 em uso) também barra a 7ª VM com disco balanced de 100 GB. Para 8: subir a cota de IPs (ou pôr Cloud NAT na
  rede `default` e tirar o IP externo) e usar `INF_PESADO_TIPO_DISCO=pd-standard`. `CPUS_ALL_REGIONS` 96 (12 em uso).
* `E2_CPUS` aparece com limite 24 e uso 0 mesmo com VMs E2 ligadas; não sei se é imposto. Se o Compute recusar o
  4º shard e2-highmem-8 por essa cota, o executor apaga os já criados e devolve o erro; aí use `c2d-highmem-8`
  (cota `C2D_CPUS` 100).
