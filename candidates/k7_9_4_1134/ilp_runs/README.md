# ILP do remendo com simetria de reta (2026-10-03)

Modelo: `../ilp_sym.py 18 line <idx> <segundos>` sobre a base campeã de 1029 palavras
(T = 18 classes laterais). Remendo restrito a ser invariante por translação ao longo de
uma reta do código linear da base (órbitas de 7 palavras). HiGHS, máquinas t2d-standard-8.

## Resultado

| reta | 1 h (atq-1/atq-2) | longo (atq-3) |
|---|---|---|
| 10 | 105, dual 98 | **ótimo 105** (dual = primal, 12 879 s) |
| 18 | 105, dual 98 | **ótimo 105** (dual = primal, 12 120 s) |
| 3, 12, 14, 15, 16, 29, 31, 32 | 126–133, dual 98 | — |
| 7, 30, 33, 34 | 119–126, dual 91 | — |

Conclusão medida: **com simetria de reta 10 ou 18, o remendo mínimo é exatamente 105**,
então essa família não passa de 1134. As outras 12 retas testadas ficaram com primal
≥ 119 em 1 h; nenhuma foi levada ao ótimo. Abaixo de 1134 exige remendo sem essa
simetria (ou com simetria menor) ou outra base.

`lines_T18.jsonl`: saída bruta das duas corridas longas.
