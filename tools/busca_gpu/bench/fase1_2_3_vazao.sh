#!/bin/bash
# Fases 1-3 do PoC (2026-10-07) numa VM com T4: compila, base de CPU (tabu.c) e varredura de cadeias na GPU.
# Pré: ~/poc com tabu_gpu.cu, tabu.c, verify.c, bench_cpu.py; CUDA 12.0 (nvcc) e g++-12. Resultado em ~/poc/*.log.
set -u
cd ~/poc
nvcc -O3 --cudart shared -arch=sm_75 -ccbin g++-12 -DMAXC=640 -o tabu_gpu2 tabu_gpu.cu
gcc -O2 -o tabu_cpu tabu.c; gcc -O2 -std=c99 -o verify verify.c
echo "== CPU base: 8 procs tabu.c, K5(6,3) M=24, 40 s"
TABU_BIN=./tabu_cpu python3 bench_cpu.py 5 6 3 24 40 8 300
echo "== CPU: 4 procs"
TABU_BIN=./tabu_cpu python3 bench_cpu.py 5 6 3 24 40 4 400
for C in 40 80 160 240 480 960 1920; do
  echo "== GPU cadeias=$C, K5(6,3) M=24, 25 s"
  ./tabu_gpu2 5 6 3 24 $C 25 11 1 2000 ./h24_$C | egrep "FIM|ACHOU" | tail -2
done
echo "== alvo facil M=25: 8 procs CPU 120 s e 40 cadeias GPU"
TABU_BIN=./tabu_cpu python3 bench_cpu.py 5 6 3 25 120 8 100
./tabu_gpu2 5 6 3 25 40 60 7 1 2000 ./g25 | egrep "FIM"
