# Snapshot científico (gerado por tools/campaign/snapshot_covering.py)

Commit-base: `bc452a571a75010516b9b59cbd741b689dd7d10e`. Fonte: dados da campanha, não texto.

| Código | Tamanho | Claim state | Melhor registrada (Δ) | Verificadores (PASS/total) | Lean (Kernel evidence) | Literatura |
|---|---|---|---|---|---|---|
| K_2(6,1) | 12 | PROVED (só ≤12; igualdade EXHAUSTIVE_BOUNDED) | 12 (−0, 0.0%) | 4/4 | PROVED_MEASURED (+ pesado relato de VM externa, log não persistido) | PREDECESSOR_FOUND (alta) |
| K_4(10,4) | 192 | INDEPENDENTLY_REPRODUCED | 208 (−16, 7.69%) | 4/4 | Kernel evidence: EXTERNAL_RUN_REPORTED | AMBIGUOUS (média-baixa) |
| K_5(10,4) | 625 | INDEPENDENTLY_REPRODUCED | 875 (−250, 28.57%) | 4/4 | Kernel evidence: EXTERNAL_RUN_REPORTED | AMBIGUOUS (baixa) |
| K_5(7,2) | 500 | INDEPENDENTLY_REPRODUCED | 525 (−25, 4.76%) | 4/4 | Kernel evidence: EXTERNAL_RUN_REPORTED | AMBIGUOUS (média) |
| K_5(9,3) | 1250 | INDEPENDENTLY_REPRODUCED | 1275 (−25, 1.96%) | 4/4 | Kernel evidence: EXTERNAL_RUN_REPORTED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (média) |
| K_5(9,4) | 250 | INDEPENDENTLY_REPRODUCED | 255 (−5, 1.96%) | 4/4 | Kernel evidence: EXTERNAL_RUN_REPORTED | AMBIGUOUS (média) |
| K_5(9,5) | 50 | INDEPENDENTLY_REPRODUCED | 55 (−5, 9.09%) | 4/4 | Kernel evidence: EXTERNAL_RUN_REPORTED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (média) |
| K_7(8,3) | 1887 | PROVED | 2337 (−450, 19.26%) | 4/4 | PROVED_MEASURED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (média) |
| K_7(8,3) | 1893 | INDEPENDENTLY_REPRODUCED | 2337 (−444, 19.0%) | 4/4 | Kernel evidence: EXTERNAL_RUN_REPORTED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (média) |
| K_7(9,4) | 1137 | PROVED | 1475 (−338, 22.92%) | 7/7 | PROVED_MEASURED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (média) |
| K_7(9,4) | 1141 | PROVED | 1475 (−334, 22.64%) | 7/7 | PROVED_MEASURED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (média) |
| K_7(9,4) | 1285 | PROVED | 1475 (−190, 12.88%) | 7/7 | PROVED_MEASURED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (média) |
| K_7(9,4) | 1351 | PROVED | 1475 (−124, 8.41%) | 7/7 | PROVED_MEASURED (+ pesado relato de VM externa, log não persistido) | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (baixa-média) |

Verificadores registrados: `verify-c`, `verify-cleanroom`, `verify-py-dilation`, `verify-rust`, `verify-val-balls`, `verify-val-bfs`, `verify-val-bruteforce`. Os `verify-val-*` só se aplicam a K_7(9,4) (q, n cravados no código).

Independência: verify-py-dilation tem o autor dos claims (PASS não conta); os `verify-val-*` têm o autor de verify.c (contam junto com ele, num componente só). O teorema Lean MEDIDO vem de `#print axioms` real na campanha; `CoveringHeavy` (~9,3 h de CPU) tem UMA medição externa do autor numa VM (`_fatos/medicao_heavy_vm.json`), não refeita em segundo ambiente nem reproduzível neste container, e o log bruto não foi persistido nem o id da instância capturado: Kernel evidence: EXTERNAL_RUN_REPORTED (eixo do kernel, abaixo de KERNEL_VERIFIED, que exige log guardado com hash de 64 hex e proveniência capturada pela ferramenta; muito abaixo de KERNEL_INDEPENDENTLY_REPRODUCED), abaixo de PROVED_MEASURED. Claim state: nenhum estado de claim mudou por isso.

Classificação: apparent improvement over the currently recorded bound; novelty not yet established. Nenhum código tem NOVELTY_EXTERNALLY_CONFIRMED.
