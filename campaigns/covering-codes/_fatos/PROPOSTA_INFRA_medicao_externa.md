> **ATENDIDA em 2026-10-04 (infraestrutura, PR #1050 da Fábrica).** Em vez de um tipo `formal` com `measurement_kind: external`, a infraestrutura ganhou um eixo próprio,
> `kernel_runs/` (`factory_cauteloso.matematica.kernel`), com níveis `NONE < EXTERNAL_RUN_REPORTED < KERNEL_VERIFIED < KERNEL_INDEPENDENTLY_REPRODUCED`, que **não altera estado de claim**
> (as guardas não o leem). A execução desta VM está em `kernel_runs/kr-heavy-ddb16b7-lean-build2.json` no nível **EXTERNAL_RUN_REPORTED**: o log bruto não foi persistido e não há hash
> de 64 hex, então não chega a KERNEL_VERIFIED, e uma execução do próprio autor não é reprodução independente. Nenhum claim subiu. O texto abaixo é o pedido original, preservado.

# Proposta de infraestrutura: registro `external_measurement` para Lean medido fora do container

Data: 2026-10-04. Autor: Agente RB2. Não edita a infraestrutura; é um pedido.

## O que aconteceu

`_fatos/medicao_heavy_vm.json` traz o build completo de `lake build CoveringHeavy` (commit ddb16b7, Lean v4.34.1, VM e2-highmem-8, 9181 jobs, 220 folhas ok, 0 falhas, sem sorry/native_decide no log, `#print axioms` de cada teorema = só propext/Classical.choice/Quot.sound, log sha256 ca233f40f93e8eb1…). O migrate agora registra isso em `measured_external` nos 9 registros `f-heavy-*` / `f-k2-6-1-eq12`, com `axioms_status = MEASURED_ON_EXTERNAL_VM`.

## O que a guarda decide hoje (e por que não foi enfraquecida)

`model.validar_registro_formal` lê só `axioms`, `sorry_free`, `clean_build`, `lean_version`, `mathlib_commit`, `repo_commit`. Eles são preenchidos exclusivamente por `formal.registrar_formal` a partir de comando executado ali (`formal.py`: "nada aqui aceita sorry_free ou clean_build por parâmetro do chamador"). Copiar `clean_build: true` e `axioms: [...]` de um JSON para o registro faria a guarda aceitar, sem medir, um valor que ninguém na campanha mediu. Seria o caminho de PROVED por transcrição. Por isso `axioms` segue `null`, `clean_build` `false`, e os 7 claims de código (192, 625, 500, 1250, 250, 50, 1893) ficam em INDEPENDENTLY_REPRODUCED; `k2-6-1-lb-12`/`eq-12` ficam em EXHAUSTIVE_BOUNDED. O 1351 já é PROVED pelo teorema por síndromes.

Motivos adicionais: (1) o log completo (1,5 MB) não está versionado, só o prefixo do sha256; ninguém consegue conferir o hash; (2) é a medição do próprio autor, sem segundo ambiente.

## O que a infraestrutura precisaria

1. Tipo de registro `formal` com `measurement_kind: "external"` (ou coleção `formal_external/`), com campos obrigatórios: `log_sha256` completo, `log_uri` ou cópia versionada/anexo, `commit`, `lean_version`, `machine`, `axioms` por teorema, `jobs`, `failures`, `measured_by`, `measured_at`.
2. Guarda que trate esse tipo como DEGRAU PRÓPRIO: sustenta no máximo um estado novo (p. ex. `PROVED_EXTERNAL`) abaixo de PROVED, e só vira PROVED se houver (a) `reproducer` diferente do autor do claim (como `external_reproductions`, D-05) ou (b) re-execução local do `#print axioms` com a toolchain (já suportada por `formal.axiomas`) sobre os .olean restaurados do build externo.
3. `reproduce` com passo `external_measurement` que confere o sha256 do log e as linhas `#print axioms`, e marca `NÃO reproduzido localmente` (SKIPPED, nunca PASS).
4. Alternativa sem mudar a infra: a campanha refazer o build pela própria `formal.registrar_formal` numa máquina com RAM suficiente (US$ de VM, decisão do dono), ou provar os 7 códigos por síndromes (`scripts/syndrome/gen_syn.py`, minutos), que já é caminho medido no container.
