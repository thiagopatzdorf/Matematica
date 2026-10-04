# Cobertura da certificação do ledger

A machine-checked ledger of covering-code upper bounds, with formally certified exact entries.

Gerado por `ledger/cobertura.py` a partir de `ledger/cells.json`; não edite à mão.
Estados (cumulativos, ver `ledger/README.md`): **C** = CLAIMED, **W** = WITNESS_CHECKED,
**F** = FORMALIZED, **I** = INDEPENDENTLY_REPRODUCED. As cotas inferiores são, quase todas,
herdadas da literatura (CLAIMED).

Total: 1145 células; exatas (inferior = superior): 520; exatas com as duas cotas no Lean daqui: 1.

| lado | CLAIMED | WITNESS_CHECKED | FORMALIZED | INDEPENDENTLY_REPRODUCED |
|---|---:|---:|---:|---:|
| ub | 1132 | 0 | 2 | 11 |
| lb | 1143 | 1 | 1 | 0 |

Cotas superiores com prova Lean externa da mesma cota (Florath, commit fixado, não reconstruída aqui, por isso não sobe o estado): 527.

## Por q

| q | células | ub C | ub W | ub F | ub I | lb C | lb W | lb F | lb I | exatas | ub Lean externo |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 285 | 284 | 0 | 1 | 0 | 284 | 0 | 1 | 0 | 107 | 116 |
| 3 | 84 | 84 | 0 | 0 | 0 | 84 | 0 | 0 | 0 | 44 | 50 |
| 4 | 60 | 59 | 0 | 0 | 1 | 60 | 0 | 0 | 0 | 31 | 33 |
| 5 | 60 | 53 | 0 | 0 | 7 | 60 | 0 | 0 | 0 | 27 | 28 |
| 6 | 52 | 52 | 0 | 0 | 0 | 52 | 0 | 0 | 0 | 25 | 24 |
| 7 | 52 | 48 | 0 | 1 | 3 | 51 | 1 | 0 | 0 | 23 | 25 |
| 8 | 52 | 52 | 0 | 0 | 0 | 52 | 0 | 0 | 0 | 23 | 25 |
| 9 | 52 | 52 | 0 | 0 | 0 | 52 | 0 | 0 | 0 | 22 | 22 |
| 10 | 52 | 52 | 0 | 0 | 0 | 52 | 0 | 0 | 0 | 20 | 21 |
| 11 | 36 | 36 | 0 | 0 | 0 | 36 | 0 | 0 | 0 | 17 | 16 |
| 12 | 36 | 36 | 0 | 0 | 0 | 36 | 0 | 0 | 0 | 19 | 18 |
| 13 | 36 | 36 | 0 | 0 | 0 | 36 | 0 | 0 | 0 | 17 | 17 |
| 14 | 36 | 36 | 0 | 0 | 0 | 36 | 0 | 0 | 0 | 18 | 17 |
| 15 | 36 | 36 | 0 | 0 | 0 | 36 | 0 | 0 | 0 | 19 | 17 |
| 16 | 36 | 36 | 0 | 0 | 0 | 36 | 0 | 0 | 0 | 18 | 18 |
| 17 | 36 | 36 | 0 | 0 | 0 | 36 | 0 | 0 | 0 | 17 | 16 |
| 18 | 36 | 36 | 0 | 0 | 0 | 36 | 0 | 0 | 0 | 18 | 16 |
| 19 | 36 | 36 | 0 | 0 | 0 | 36 | 0 | 0 | 0 | 17 | 16 |
| 20 | 36 | 36 | 0 | 0 | 0 | 36 | 0 | 0 | 0 | 19 | 16 |
| 21 | 36 | 36 | 0 | 0 | 0 | 36 | 0 | 0 | 0 | 19 | 16 |

## Células acima de CLAIMED

| célula | ub | estado ub | lb | estado lb | exata |
|---|---:|---|---:|---|---|
| K2(6,1) | 12 | FORMALIZED | 12 | FORMALIZED | sim |
| K4(10,4) | 192 | INDEPENDENTLY_REPRODUCED | 62 | CLAIMED | não |
| K5(7,2) | 500 | INDEPENDENTLY_REPRODUCED | 236 | CLAIMED | não |
| K5(9,3) | 1250 | INDEPENDENTLY_REPRODUCED | 354 | CLAIMED | não |
| K5(9,4) | 250 | INDEPENDENTLY_REPRODUCED | 64 | CLAIMED | não |
| K5(9,5) | 50 | INDEPENDENTLY_REPRODUCED | 19 | CLAIMED | não |
| K5(10,4) | 625 | INDEPENDENTLY_REPRODUCED | 177 | CLAIMED | não |
| K5(10,5) | 162 | INDEPENDENTLY_REPRODUCED | 41 | CLAIMED | não |
| K5(11,4) | 2875 | INDEPENDENTLY_REPRODUCED | 546 | CLAIMED | não |
| K7(4,2) | 19 | FORMALIZED | 19 | WITNESS_CHECKED | sim |
| K7(8,3) | 1887 | INDEPENDENTLY_REPRODUCED | 471 | CLAIMED | não |
| K7(9,4) | 1134 | INDEPENDENTLY_REPRODUCED | 264 | CLAIMED | não |
| K7(10,4) | 5607 | INDEPENDENTLY_REPRODUCED | 1007 | CLAIMED | não |
