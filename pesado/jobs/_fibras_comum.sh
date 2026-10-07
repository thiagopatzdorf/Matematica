#!/bin/bash
# Base dos jobs `fibras-*` (não é chamável pelo pesado: o nome começa com "_", fora da regex da allowlist).
# Compila CaDiCaL e lrat-check nos commits dos certificados já publicados (FIBRAS_GERAL.md) e roda a fatia
# SHARD_INDEX/SHARD_TOTAL das instâncias de K_q(n,R) com M palavras, com prova LRAT conferida e descartada
# (fica o sha256 da CNF e da prova em cada linha JSONL). Uso, de dentro de um job:
#   Q=4 N=7 R=4 M=9 bash pesado/jobs/_fibras_comum.sh
set -eu
: "${Q:?}" "${N:?}" "${R:?}" "${M:?}" "${SHARD_INDEX:?}" "${SHARD_TOTAL:?}" "${SAIDA:?}"
ORDEM=${ORDEM:-min}
TEMPO=${TEMPO:-900}            # 1ª passada, por perfil
CUBOS=${CUBOS:-9}               # 2ª passada: cubos pela coordenada 1 das CUBOS primeiras palavras
TEMPO_CUBO=${TEMPO_CUBO:-20000}
J=${J:-$(nproc)}                 # processos de solver em paralelo neste shard
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
TRAB=${TRAB:-/var/tmp/fibras-$JOB_ID-$SHARD_INDEX}   # (TRAB=/dev/shm/... em disco lento: pd-standard grava ~5 MB/s e a prova LRAT tem centenas de MB)
# CNF e LRAT temporárias (descartadas depois de conferidas)
mkdir -p "$TRAB"
# Se o shard voltar (reboot da spot), o JSONL já gravado é reaproveitado: rodar.py pula o que fechou.
# 1ª passada: perfil inteiro com teto de TEMPO s. 2ª: o que ficou INDEFINIDO vai em cubos pela coordenada 1 das
# L primeiras palavras (fib_cubos; um perfil só conta como fechado com TODOS os cubos UNSAT, fecha_perfis.py).
COMUM=(--q "$Q" --n "$N" --R "$R" --M "$M" --ordem "$ORDEM" --prova --descartar -j "$J" --dir "$TRAB")
[ -n "${K:-}" ] && COMUM+=(--k "$K")
# PULAR: JSONL de rodadas anteriores (qualquer ordem); perfis já fechados com LRAT conferido não rodam de novo
[ -n "${PULAR:-}" ] && COMUM+=(--pular $PULAR)   # instâncias por prefixo de K tipos (menos instâncias, cada uma maior)
python3 tools/exatos/fibras/rodar.py "${COMUM[@]}" --fatia "$SHARD_INDEX/$SHARD_TOTAL" --tempo "$TEMPO" | tail -n 100
cp "$TRAB"/*.jsonl "$SAIDA/"
ABERTOS=$(python3 - "$TRAB" <<'PY'
import json, pathlib, sys
fech, todos = set(), set()
for arq in pathlib.Path(sys.argv[1]).glob("*.jsonl"):
    if "_L" in arq.name:
        continue
    for ln in open(arq):
        r = json.loads(ln)
        todos.add(r["inst"])
        # prova que não passou no lrat-check (ex.: disco cheio no meio da escrita) também volta, em cubos
        if r["resultado"] == "SAT" or (r["resultado"] == "UNSAT" and r.get("lrat_check") == "VERIFIED"):
            fech.add(r["inst"])
print(",".join(map(str, sorted(todos - fech))))
PY
)
if [ -n "$ABERTOS" ]; then
  echo "em cubos (L=$CUBOS): $ABERTOS"
  python3 tools/exatos/fibras/rodar.py "${COMUM[@]}" --inst "$ABERTOS" --cubos "$CUBOS" --tempo "$TEMPO_CUBO" | tail -n 100
  cp "$TRAB"/*.jsonl "$SAIDA/"
fi
python3 - "$SAIDA" <<'PY'
import json, pathlib, sys, collections
c = collections.Counter()
for arq in pathlib.Path(sys.argv[1]).glob("*.jsonl"):
    for ln in open(arq):
        r = json.loads(ln)
        c[r["resultado"] + ("" if r["resultado"] != "UNSAT" else "/" + str(r.get("lrat_check")))] += 1
print("resumo do shard:", dict(c))
PY
