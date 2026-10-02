#!/usr/bin/env bash
# run_all.sh -- refaz toda a validação computacional de K_7(9,4) <= 1137 (CPU local, ~12 min em 4 núcleos).
# Requisitos: gcc com OpenMP, rustc, python3 + numpy. Sai com erro na primeira falha.
set -euo pipefail
cd "$(dirname "$0")"
W=../artifacts/k7_9_4_1137/code_1137.txt
B="${BUILD_DIR:-$(mktemp -d)}"
(cd ../artifacts/k7_9_4_1137 && sha256sum -c SHA256SUMS)
python3 validate_witness.py "$W" 1137
gcc -O2 -fopenmp -o "$B/verify_bruteforce" verify_bruteforce.c
gcc -O2 -fopenmp -o "$B/redundancy_check" redundancy_check.c
rustc -O -o "$B/verify_bfs" verify_bfs/main.rs
echo "== A: força bruta";      python3 measure.py "$B/verify_bruteforce" "$W"
echo "== B: união de bolas";   python3 measure.py python3 verify_balls.py "$W"
echo "== C: BFS multifonte";   python3 measure.py "$B/verify_bfs" "$W"
echo "== redundância";         python3 measure.py "$B/redundancy_check" "$W"
echo "== mutações";            python3 run_mutations.py "$W" "$B/verify_bfs" "$B/mut"
echo "== estrutura";           python3 structure_check.py "$W"
echo "PASS q=7 n=9 R=4 |C|=1137 covered=40353607 uncovered=0"
