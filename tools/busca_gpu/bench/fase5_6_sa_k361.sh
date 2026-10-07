#!/bin/bash
# Fases 5-6: SA na GPU em K3(6,1) (calibração M=73 contra sa_cover em CPU e ataque a M=72).
# Pré: ~/poc com tabu_gpu.cu e tools/exatos/sa_cover.c.
set -u
cd ~/poc
nvcc -O3 --cudart shared -arch=sm_75 -ccbin g++-12 -DMAXC=640 -o tabu_gpu4 tabu_gpu.cu
gcc -O2 -o sa_cover sa_cover.c -lm
echo "== CPU base: 6 procs sa_cover K3(6,1) M=73"
for s in 1 2 3 4 5 6; do ( /usr/bin/time -f "cpu_sa seed=$s %es" ./sa_cover 3 6 1 73 240 $s ./cpu73_$s.txt 2>&1 | egrep "melhor|seed" ) & done
wait
G=./tabu_gpu4
r() {  # rotulo q n R M cadeias seg modo ciclo T0 Tmin
  echo "== $1: K$2($3,$4) M=$5 cad=$6 ${7}s modo=$8 ciclo=$9 T0=${10} Tmin=${11}"
  $G $2 $3 $4 $5 $6 $7 31 1 20000 ./f6_$1 $8 $9 ${10} ${11} > f6_$1.out
  grep -c ACHOU f6_$1.out | sed 's/^/sucessos: /'; grep ACHOU f6_$1.out | head -1; grep "^FIM" f6_$1.out
}
r cal_m1 3 6 1 73 240 60 1 2000000 2.0 0.05
r cal_m2 3 6 1 73 240 60 2 2000000 2.0 0.05
r m72_m1_2M 3 6 1 72 240 480 1 2000000 2.0 0.05
r m72_m1_20M 3 6 1 72 240 480 1 20000000 2.0 0.05
r m72_m2_2M 3 6 1 72 240 480 2 2000000 2.0 0.05
