# Snapshot científico (gerado por tools/campaign/snapshot_covering.py)

Commit-base: `986889eaaf52b9b79dffd3f3385775fd4eea4fb0`. Fonte: dados da campanha, não texto.

| Código | Tamanho | Estado do claim | Melhor registrada (Δ) | Verificadores (PASS/total) | Lean | Literatura |
|---|---|---|---|---|---|---|
| K_2(6,1) | 12 | PROVED (só ≤12; igualdade EXHAUSTIVE_BOUNDED) | 12 (−0, 0.0%) | 4/4 | PROVED_MEASURED (+ pesado declarado) | PREDECESSOR_FOUND (alta) |
| K_4(10,4) | 192 | INDEPENDENTLY_REPRODUCED | 208 (−16, 7.69%) | 4/4 | EXISTS_BUILD_NOT_REPRODUCED | AMBIGUOUS (média-baixa) |
| K_5(10,4) | 625 | INDEPENDENTLY_REPRODUCED | 875 (−250, 28.57%) | 4/4 | EXISTS_BUILD_NOT_REPRODUCED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (baixa-média) |
| K_5(7,2) | 500 | INDEPENDENTLY_REPRODUCED | 525 (−25, 4.76%) | 4/4 | EXISTS_BUILD_NOT_REPRODUCED | AMBIGUOUS (média) |
| K_5(9,3) | 1250 | INDEPENDENTLY_REPRODUCED | 1275 (−25, 1.96%) | 4/4 | EXISTS_BUILD_NOT_REPRODUCED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (média) |
| K_5(9,4) | 250 | INDEPENDENTLY_REPRODUCED | 255 (−5, 1.96%) | 4/4 | EXISTS_BUILD_NOT_REPRODUCED | AMBIGUOUS (média) |
| K_5(9,5) | 50 | INDEPENDENTLY_REPRODUCED | 55 (−5, 9.09%) | 4/4 | EXISTS_BUILD_NOT_REPRODUCED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (média) |
| K_7(8,3) | 1887 | PROVED | 2337 (−450, 19.26%) | 4/4 | PROVED_MEASURED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (média) |
| K_7(8,3) | 1893 | INDEPENDENTLY_REPRODUCED | 2337 (−444, 19.0%) | 4/4 | EXISTS_BUILD_NOT_REPRODUCED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (média) |
| K_7(9,4) | 1137 | PROVED | 1475 (−338, 22.92%) | 7/7 | PROVED_MEASURED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (média) |
| K_7(9,4) | 1141 | PROVED | 1475 (−334, 22.64%) | 7/7 | PROVED_MEASURED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (média) |
| K_7(9,4) | 1285 | PROVED | 1475 (−190, 12.88%) | 7/7 | PROVED_MEASURED | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (média) |
| K_7(9,4) | 1351 | PROVED | 1475 (−124, 8.41%) | 7/7 | PROVED_MEASURED (+ pesado declarado) | NO_PREDECESSOR_FOUND_IN_REVIEWED_SOURCES (baixa-média) |

Verificadores registrados: `verify-c`, `verify-cleanroom`, `verify-py-dilation`, `verify-rust`, `verify-val-balls`, `verify-val-bfs`, `verify-val-bruteforce`. Os `verify-val-*` só se aplicam a K_7(9,4) (q, n cravados no código).

Independência: verify-py-dilation tem o autor dos claims (PASS não conta); os `verify-val-*` têm o autor de verify.c (contam junto com ele, num componente só). O teorema Lean MEDIDO vem de `#print axioms` real na campanha; `CoveringHeavy` (~9,3 h de CPU) fica DECLARADO, não reproduzido.

Classificação: apparent improvement over the currently recorded bound; novelty not yet established. Nenhum código tem NOVELTY_EXTERNALLY_CONFIRMED.
