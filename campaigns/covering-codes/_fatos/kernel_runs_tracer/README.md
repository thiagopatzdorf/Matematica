# Teste ponta a ponta do kernel_run (claim k7-8-3-ub-1887)

Alvo `CoveringLean.Syn_K1887`, commit `1a5fa268dc916fde689e6aa801e591ac3c863b36`, duas VMs GCE distintas
(`kr-teste-a`, zona southamerica-east1-a, instância 5198467000349702121; `kr-teste-b`, zona -b, instância 1876810319497476070),
e2-highmem-4 sob demanda, sem service account. Cada VM clonou o commit, compilou, e coletou a proveniência com a ferramenta.
Os logs brutos (12 622 bytes cada, sha256 distintos) estão em `a/build.log` e `b/build.log` e, fora do Git, em
`gs://factory-cauteloso-telemetria/matematica/kernel-runs/<sha256>.log` (upload feito pela factory-01 com token de service account
em memória; tamanho conferido por GET de metadados). `prov.json` = pacote de proveniência gerado NA VM; `spec.json` = parâmetros do registro.
`a/spec_tentativa_copia_da_mesma_execucao.json` é a tentativa de registrar a execução A uma segunda vez sob outro run_id (não conta como 2ª).
Limites: "capturada" = pela ferramenta, não atestada; a janela das execuções é a do script da VM (inclui instalação do elan e `lake exe cache get`).
