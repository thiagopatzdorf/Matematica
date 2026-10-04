#!/bin/bash
# Roda, numa VM de lote, as refutações sem quebra dos perfis dados (lista separada por vírgula).
#   bash tools/exatos/k742/lean/vm/rodar.sh 55,25,9 [jobs_preparo]
# Pré-requisito: este diretório com lean-toolchain, lakefile.toml (vm/lakefile.toml, sem Mathlib),
# CoveringLean/{LratK,LratKData,K742_Cnf}.lean e tools/exatos/k742/. Instala CaDiCaL e lrat-trim
# nas versões fixadas. Logs em logs/.
set -euo pipefail
PERFIS="$1"
JP="${2:-6}"
RAIZ="$(cd "$(dirname "$0")/../../../../.." && pwd)"
cd "$RAIZ"
mkdir -p logs bin
export PATH="$HOME/.elan/bin:$PATH"
if [ ! -x bin/cadical ] || [ ! -x bin/lrat-trim ]; then
  sudo apt-get update -q
  sudo apt-get install -y -q build-essential git python3
  rm -rf /tmp/cadical /tmp/lrat-trim
  git clone -q https://github.com/arminbiere/cadical /tmp/cadical
  (cd /tmp/cadical && git checkout -q c607304 && ./configure > /dev/null && make -j8 > /dev/null)
  cp /tmp/cadical/build/cadical bin/
  git clone -q https://github.com/arminbiere/lrat-trim /tmp/lrat-trim
  (cd /tmp/lrat-trim && git checkout -q b30f400 && ./configure > /dev/null && make > /dev/null)
  cp /tmp/lrat-trim/lrat-trim bin/
fi
export CADICAL="$RAIZ/bin/cadical" LRAT_TRIM="$RAIZ/bin/lrat-trim"
echo "[rodar] $(date -u +%FT%TZ) preparo de $PERFIS" | tee -a logs/rodar.log
echo "$PERFIS" | tr ',' '\n' | xargs -P "$JP" -I{} sh -c \
  '[ -s logs/prep_{}.json ] || python3 tools/exatos/k742/lean/preparar_semquebra.py --perfil {} \
     --saida CoveringLean/K742Sat/dados > logs/prep_{}.json.tmp 2> logs/prep_{}.err && \
   { [ -s logs/prep_{}.json ] || mv logs/prep_{}.json.tmp logs/prep_{}.json; }'
cat logs/prep_*.json | sort -t: -k4 > tools/exatos/k742/lean/semquebra_M18.jsonl
python3 tools/exatos/k742/lean/gerar_modulos.py --perfis "$PERFIS"
ALVOS=$(echo "$PERFIS" | tr ',' '\n' | sed 's/^/CoveringLean.K742Sat.S/; s/$/.Final/' | tr '\n' ' ')
echo "[rodar] $(date -u +%FT%TZ) lake build $ALVOS" | tee -a logs/rodar.log
set +e
lake build $ALVOS >> logs/build.log 2>&1
rc=$?
echo "[rodar] $(date -u +%FT%TZ) lake build rc=$rc" | tee -a logs/rodar.log
exit $rc
