#!/bin/bash
# Roda numa VM de lote (lote-gcp.py): compila os solvers, clona o branch e mede a amostra.
# Uso: bash vm.sh <branch> <procs>   -> resultados em ~/out/*.jsonl, marcador ~/FIM
set -ex
BR=${1:-feat/k3-6-1}; J=${2:-8}
cd ~
sudo apt-get update -q >/dev/null 2>&1
sudo apt-get install -y -q build-essential git python3 >/dev/null 2>&1
mkdir -p sat && cd sat
for r in arminbiere/cadical arminbiere/kissat marijnheule/drat-trim; do [ -d $(basename $r) ] || git clone -q --depth 1 https://github.com/$r; done
(cd cadical && git rev-parse HEAD > ../cadical.commit && [ -x build/cadical ] || (./configure >/dev/null && make -j8 >/dev/null))
(cd kissat && git rev-parse HEAD > ../kissat.commit && [ -x build/kissat ] || (./configure >/dev/null && make -j8 >/dev/null))
(cd drat-trim && git rev-parse HEAD > ../drat-trim.commit && make >/dev/null)
cd ~
[ -d Matematica ] || git clone -q -b "$BR" https://github.com/thiagopatzdorf/Matematica
cd Matematica && git pull -q && git rev-parse HEAD > ~/repo.commit
export CADICAL=~/sat/cadical/build/cadical LRAT_CHECK=~/sat/drat-trim/lrat-check
export KISSAT=~/sat/kissat/build/kissat
A=tools/exatos/k361/amostra.py
mkdir -p ~/out
case "${3:-amostra}" in
amostra)
python3 $A --v 5 --M 26 --todas --lrat --procs $J --tempo 600 --saida ~/out/v5_M26.jsonl
python3 $A --v 6 --M 66 --p 20 --sufixo igual --n 8 --procs $J --tempo 1800 --saida ~/out/v6_M66_p20.jsonl
python3 $A --v 6 --M 71 --p 22 --sufixo igual --n 16 --procs $J --tempo 1800 --saida ~/out/v6_M71_p22.jsonl
python3 $A --v 6 --M 72 --p 22 --sufixo igual --n 16 --procs $J --tempo 1800 --saida ~/out/v6_M72_p22.jsonl
;;
escada)  # o menor M com sequências (59) e o seguinte, com tempo longo: há tempo finito medível?
python3 $A --v 5 --M 26 --todas --lrat --procs 8 --tempo 600 --saida ~/out/v5_M26_lrat.jsonl
python3 $A --v 6 --M 59 --p 19 --todas --procs 2 --tempo 14400 --saida ~/out/v6_M59_cadical.jsonl &
python3 $A --v 6 --M 59 --p 19 --todas --procs 2 --tempo 14400 --motor kissat --saida ~/out/v6_M59_kissat.jsonl &
python3 $A --v 6 --M 60 --p 19 --n 2 --semente 2 --procs 2 --tempo 14400 --saida ~/out/v6_M60_cadical.jsonl &
python3 $A --v 6 --M 72 --p 18 --n 2 --semente 3 --procs 2 --tempo 14400 --saida ~/out/v6_M72_auto.jsonl &
wait
;;
esac
touch ~/FIM
