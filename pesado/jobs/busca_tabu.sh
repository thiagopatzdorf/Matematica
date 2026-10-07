#!/bin/bash
# Busca tabu direta (tools/busca_direta/tabu.c) nas células de pesado/jobs/busca_tabu.alvos.
# Cada linha do arquivo de alvos: "q n R M_inicial segundos sementes". O par (linha, semente) vai para o
# shard (contador % SHARD_TOTAL); dentro do shard roda um processo por vCPU. Tudo que sai vai para
# $SAIDA/<q>_<n>_<R>/ e cada código achado passa pelo verificador oficial (tools/verify/verify) aqui
# mesmo; o resumo ($SAIDA/resumo.tsv) lista só o que o verificador aceitou. Resultado é hipótese até o
# PR que registra no ledger refazer a verificação.
# Ambiente (posto pelo lote): SHARD_INDEX, SHARD_TOTAL, JOB_ID, SAIDA.
set -eu
: "${SHARD_INDEX:=0}" "${SHARD_TOTAL:=1}" "${SAIDA:=./saida-busca-tabu}"
ALVOS="${ALVOS:-pesado/jobs/busca_tabu.alvos}"
mkdir -p "$SAIDA"
BIN="$(mktemp -d)"
cc -O3 -march=native -std=gnu99 -o "$BIN/tabu" tools/busca_direta/tabu.c
cc -O3 -march=native -std=gnu99 -DCNT16 -o "$BIN/tabu16" tools/busca_direta/tabu.c
cc -O2 -o "$BIN/verify" tools/verify/verify.c
NP="$(nproc)"
echo "shard ${SHARD_INDEX}/${SHARD_TOTAL} job ${JOB_ID:-local} commit $(git rev-parse --short HEAD 2>/dev/null || echo ?) vCPU ${NP}"

tarefas="$BIN/tarefas"
: > "$tarefas"
k=0
while read -r q n R M seg sem; do
  case "$q" in ''|\#*) continue ;; esac
  for s in $(seq 1 "$sem"); do
    if [ $((k % SHARD_TOTAL)) -eq "$SHARD_INDEX" ]; then echo "$q $n $R $M $seg $((s + 1000 * SHARD_INDEX))" >> "$tarefas"; fi
    k=$((k + 1))
  done
done < "$ALVOS"
echo "tarefas deste shard: $(wc -l < "$tarefas")"

roda() {
  local q=$1 n=$2 R=$3 M=$4 seg=$5 s=$6 b="$BIN/tabu"
  [ "$M" -ge 255 ] && b="$BIN/tabu16"
  local d="$SAIDA/${q}_${n}_${R}"
  mkdir -p "$d"
  "$b" "$q" "$n" "$R" "$M" "$seg" "$s" "$d/q${q}_n${n}_R${R}_s${s}" > "$d/s${s}.out" 2> "$d/s${s}.err" || true
}
export -f roda
export BIN SAIDA
xargs -P "$NP" -L 1 bash -c 'roda "$@"' _ < "$tarefas"

# confere tudo que saiu; o resumo leva o menor M aceito por célula
printf 'celula\tM\tarquivo\tsha256\n' > "$SAIDA/resumo.tsv"
for d in "$SAIDA"/*_*_*/; do
  [ -d "$d" ] || continue
  d="${d%/}"
  IFS=_ read -r q n R <<< "$(basename "$d")"
  for f in $(ls "$d"/*_M*.txt 2>/dev/null | awk -F_M '{print $NF+0, $0}' | sort -n | cut -d' ' -f2-); do
    m="${f##*_M}"; m="${m%.txt}"
    if out="$("$BIN/verify" -q "$q" -n "$n" -r "$R" -m "$m" "$f" 2>&1)"; then
      printf 'K%s(%s,%s)\t%s\t%s\t%s\n' "$q" "$n" "$R" "$m" "${f#"$SAIDA"/}" "${out##*sha256=}" >> "$SAIDA/resumo.tsv"
      break
    else
      echo "REPROVADO pelo verificador: $f"
    fi
  done
done
cat "$SAIDA/resumo.tsv"
