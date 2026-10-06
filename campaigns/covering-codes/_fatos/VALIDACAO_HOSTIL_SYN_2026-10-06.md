# Validação hostil dos 10 teoremas `Syn_K*` (2026-10-06)

Medição própria, numa VM descartável (e2-highmem-4, sem acesso à internet), com `lake build CoveringSyn` do zero (Mathlib já compilado). Os 10 teoremas ficam fora do alvo padrão e do CI, então esta é a única compilação deles que temos.

- Lean: `leanprover/lean4:v4.34.1` (lido de `lean-toolchain` na VM)
- Checkout na VM: commit `1a5fa26` (o checkout da branch da PR #47 no momento da cópia; não é o commit do `main`)
- Início: 2026-10-06 01:25:48 UTC; fim: antes de 02:53 UTC (`syn_fim.txt` da VM é resíduo de uma tentativa anterior e não vale)
- Resultado: `Build completed successfully (9165 jobs)`, 0 ocorrências de `sorry`, 0 de `error:` no log

## `#print axioms` (10 de 10)

Todos: `[propext, Classical.choice, Quot.sound]`.

| teorema | arquivo |
|---|---|
| `Syn.K7_9_4_le_1351_syn` | `Syn_K1351.lean` |
| `Syn.K7_9_4_le_1285_syn` | `Syn_K1285.lean` |
| `Syn.K7_9_4_le_1141_syn` | `Syn_K1141.lean` |
| `Syn.K7_9_4_le_1137_syn` | `Syn_K1137.lean` |
| `Syn.K7_9_4_le_1134_syn` | `Syn_K1134.lean` |
| `Syn.K7_8_3_le_1887_syn` | `Syn_K1887.lean` |
| `Syn.K5_10_5_le_162_syn` | `Syn_K162.lean` |
| `Syn.K5_11_4_le_2875_syn` | `Syn_K2875.lean` |
| `Syn.K7_10_4_le_5616_syn` | `Syn_K5616.lean` |
| `Syn.K7_10_4_le_5607_syn` | `Syn_K5607.lean` |

## O que isto prova e o que não prova

- Prova: o kernel do Lean aceitou os 10 enunciados `∃ C : Finset (Fin n → ZMod q), C.card = M ∧ Covers R C` sem `sorry` e sem axioma além dos três padrão.
- Não prova: que o enunciado em Lean é o que se queria dizer (falta revisão humana dos enunciados), nem novidade em relação à literatura.
- Reprodução independente de medição: uma máquina, uma execução. Conta como medição própria, não como duas reproduções.
