#!/bin/bash
# Roda numa VM de lote (lote-gcp.py): compila os solvers, clona o branch e mede a amostra.
# Uso: bash vm.sh <branch> <procs>   -> resultados em ~/out/*.jsonl, marcador ~/FIM
set -ex
BR=${1:-feat/k3-6-1}; J=${2:-8}
cd ~
sudo apt-get update -q >/dev/null 2>&1
sudo apt-get install -y -q build-essential git python3 >/dev/null 2>&1
mkdir -p sat && cd sat
for r in arminbiere/cadical marijnheule/drat-trim; do [ -d $(basename $r) ] || git clone -q --depth 1 https://github.com/$r; done
(cd cadical && git rev-parse HEAD > ../cadical.commit && [ -x build/cadical ] || (./configure >/dev/null && make -j8 >/dev/null))
(cd drat-trim && git rev-parse HEAD > ../drat-trim.commit && make >/dev/null)
cd ~
[ -d Matematica ] || git clone -q -b "$BR" https://github.com/thiagopatzdorf/Matematica
cd Matematica && git pull -q && git rev-parse HEAD > ~/repo.commit
export CADICAL=~/sat/cadical/build/cadical LRAT_CHECK=~/sat/drat-trim/lrat-check
A=tools/exatos/k361/amostra.py
mkdir -p ~/out
python3 $A --v 5 --M 26 --todas --lrat --procs $J --tempo 600 --saida ~/out/v5_M26.jsonl
python3 $A --v 6 --M 66 --p 20 --n 8 --procs $J --tempo 1800 --saida ~/out/v6_M66_p20.jsonl
python3 $A --v 6 --M 71 --p 22 --n 16 --procs $J --tempo 1800 --saida ~/out/v6_M71_p22.jsonl
python3 $A --v 6 --M 72 --p 22 --n 16 --procs $J --tempo 1800 --saida ~/out/v6_M72_p22.jsonl
touch ~/FIM
