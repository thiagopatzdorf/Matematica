# Auditoria dos 5 claims que entraram com o v0.7 (1134, 5607, 5616, 162, 2875)

Pergunta única: **a migração promoveu algum status além do que a evidência sustenta?**
Método: leitura dos registros em `claims/`, `formal/`, `verifier_runs/`, `verifiers/` (nada recalculado aqui;
as medições são as já registradas). Data: 2026-10-05.

## O que `PROVED` significa nesta campanha

`PROVED` = (a) o teorema Lean `Syn.*` foi construído no kernel, sem `sorry`, só com os axiomas
`propext`, `Classical.choice`, `Quot.sound`, **e** (b) dois ou mais verificadores de grupos de independência
distintos deram PASS (uncovered=0) sobre o witness. Para estes claims o enunciado é de **existência**:
"existe C em (Z_q)^n com |C| = M cobrindo com raio R".

`PROVED` **não** significa: enunciado Lean revisado por humano (isso é `FORMALLY_VERIFIED`; falta `statement_review`
em todos os cinco), reprodução externa (`EXTERNALLY_REPRODUCED`, vazio), nem **novidade** (ver coluna
"novelty"). A comparação com a literatura é `MELHORA_APARENTE_A_CONFIRMAR`: "menor que a tabela consultada",
não "recorde".

## Tabela

| claim | witness | verificadores PASS (grupo de independência) | Lean (módulo, build do zero, sorry, axiomas) | reprodução independente | fonte/upstream do witness | novelty checked? |
|---|---|---|---|---|---|---|
| k7-9-4-ub-1134 | w-q7-n9-r4-m1134 | 7: c, rust, cleanroom(go), py-dilation, val-bfs, val-balls, val-bruteforce | `Syn_K1134`: OK, limpo, sorry-free, axiomas padrão | só entre verificadores deste repo (nenhuma execução externa) | ledger do main P-1134 (ILP `ilp_sym.py`, não reexecutado) | **não**: melhor registrada 1475 (Marosi v2/v3); ADS 931 não resolvido |
| k7-10-4-ub-5607 | w-q7-n10-r4-m5607 | 4: c, rust, cleanroom, py-dilation | `Syn_K5607`: idem | idem | ledger P-5607 (sem comando registrado) | **não**: tabela Kéri 2009 diz 6517 |
| k7-10-4-ub-5616 | w-q7-n10-r4-m5616 | 4 (mesmos) | `Syn_K5616`: idem | idem | ledger P-5616 (sem comando) | **não**: idem 6517 |
| k5-10-5-ub-162 | w-q5-n10-r5-m162 | 4 (mesmos) | `Syn_K162`: idem | idem | ledger P-162 (`patch_opt`, não reexecutado) | **não**: tabela Kéri diz 175 |
| k5-11-4-ub-2875 | w-q5-n11-r4-m2875 | 4 (mesmos) | `Syn_K2875`: idem | idem | ledger P-2875 (sem comando) | **não**: tabela Kéri diz 3125 |

## Resultado

1. **Nenhum status foi promovido pela migração**: o histórico de cada claim mostra IDEA → INDEPENDENTLY_REPRODUCED →
   PROVED, e cada passo cita a guarda atendida. Lean e verificadores existem como registros com hash, não como
   texto na migração.
2. **"Independentes" tem limite**: `py-dilation` é do autor do claim (não conta); `val-*` e `c` compartilham
   lógica entre si (campo `compartilha_logica_com`). Os autores dos demais (rust, cleanroom) são agentes de
   modelo da mesma família: independência de código, não de pessoa nem de modelo.
3. **Ressalva real, não bloqueia o estado**: quatro dos cinco (5607, 5616, 162, 2875) apontam para o mesmo
   `log_sha256` de build Lean (`7da8f951…`). Confirmar que é um log único de várias construções (e não cópia) antes
   de qualquer reprodução independente do kernel.
4. **A busca que gerou os witnesses não é reproduzível aqui** (`executado_neste_run: false`; 3 sem comando).
   Isso não afeta a existência (o witness é o certificado), afeta só "como foi achado".
5. **Pendências para subir de nível**: `statement_review` humano/independente (→ FORMALLY_VERIFIED) e revisão
   externa de novidade. Nenhuma foi feita.
