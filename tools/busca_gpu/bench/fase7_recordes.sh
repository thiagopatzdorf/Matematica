#!/bin/bash
# Fase 7: ataques às células de recorde conhecido (alvo = recorde para empate, ou recorde-1 para bater).
set -u
cd ~/poc
G=./tabu_gpu4
r() {  # rotulo q n R M cadeias seg modo ciclo T0 Tmin
  echo "== $1: K$2($3,$4) M=$5 cad=$6 ${7}s modo=$8 ciclo=$9 T0=${10} Tmin=${11}"
  $G $2 $3 $4 $5 $6 $7 41 1 20000 ./f7_$1 $8 $9 ${10} ${11} > f7_$1.out
  grep -c ACHOU f7_$1.out | sed 's/^/sucessos: /'; grep ACHOU f7_$1.out | head -1; grep "^FIM" f7_$1.out
}
r k473_32_m2 4 7 3 32 240 360 2 4000000 2.0 0.05
r k473_32_m1 4 7 3 32 240 360 1 4000000 2.0 0.05
r k383_27_m2 3 8 3 27 240 240 2 2000000 2.0 0.05
r k383_26_m2 3 8 3 26 240 360 2 2000000 2.0 0.05
r k563_25_m0 5 6 3 25 240 120 0 1 1 1
r k563_24_m0 5 6 3 24 240 360 0 1 1 1
