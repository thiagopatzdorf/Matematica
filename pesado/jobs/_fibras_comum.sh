#!/bin/bash
# Base dos jobs `fibras-*` (não é chamável pelo pesado: o nome começa com "_", fora da regex da allowlist).
# Compila CaDiCaL e lrat-check nos commits dos certificados já publicados (FIBRAS_GERAL.md) e roda a fatia
# SHARD_INDEX/SHARD_TOTAL das instâncias de K_q(n,R) com M palavras, com prova LRAT conferida e descartada
# (fica o sha256 da CNF e da prova em cada linha JSONL). Uso, de dentro de um job:
#   Q=4 N=7 R=4 M=9 bash pesado/jobs/_fibras_comum.sh
set -eu
: "${Q:?}" "${N:?}" "${R:?}" "${M:?}" "${SHARD_INDEX:?}" "${SHARD_TOTAL:?}" "${SAIDA:?}"
ORDEM=${ORDEM:-min}
TEMPO=${TEMPO:-20000}
FERR=/opt/fibras-solvers
CADICAL_SHA=c607304   # CaDiCaL 3.0.1, o mesmo dos certificados de K_7(5,3) e K_7(6,4)
DRAT_SHA=2e3b2dc      # drat-trim (lrat-check)
if [ ! -x "$FERR/cadical" ] || [ ! -x "$FERR/lrat-check" ]; then
  command -v g++ >/dev/null && command -v make >/dev/null || { apt-get update -qq && apt-get install -y -qq g++ make; }
  mkdir -p "$FERR/src"
  ( cd "$FERR/src" && rm -rf cadical drat-trim \
    && git clone -q https://github.com/arminbiere/cadical && git -C cadical checkout -q "$CADICAL_SHA" \
    && (cd cadical && ./configure >/dev/null && make -j"$(nproc)" >/dev/null) && cp cadical/build/cadical "$FERR/" \
    && git clone -q https://github.com/marijnheule/drat-trim && git -C drat-trim checkout -q "$DRAT_SHA" \
    && (cd drat-trim && make >/dev/null 2>&1) && cp drat-trim/lrat-check "$FERR/" )
fi
export CADICAL="$FERR/cadical" LRAT_CHECK="$FERR/lrat-check"
"$CADICAL" --version
TRAB=/var/tmp/fibras-$JOB_ID-$SHARD_INDEX   # CNF e LRAT temporárias (descartadas depois de conferidas)
mkdir -p "$TRAB"
# Se o shard voltar (reboot da spot), o JSONL já gravado é reaproveitado: rodar.py pula o que fechou.
python3 tools/exatos/fibras/rodar.py --q "$Q" --n "$N" --R "$R" --M "$M" --ordem "$ORDEM" \
  --fatia "$SHARD_INDEX/$SHARD_TOTAL" --prova --descartar --tempo "$TEMPO" -j "$(nproc)" --dir "$TRAB" | tail -n 200
cp "$TRAB"/*.jsonl "$SAIDA/"
python3 - "$SAIDA" <<'PY'
import json, pathlib, sys, collections
c = collections.Counter()
for arq in pathlib.Path(sys.argv[1]).glob("*.jsonl"):
    for ln in open(arq):
        r = json.loads(ln)
        c[r["resultado"] + ("" if r["resultado"] != "UNSAT" else "/" + str(r.get("lrat_check")))] += 1
print("resumo do shard:", dict(c))
PY
