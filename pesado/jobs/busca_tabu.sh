#!/bin/bash
# Busca tabu de códigos de cobertura nas células de pesado/jobs/busca_tabu.alvos, com duas ferramentas:
#   tabu  -> tools/busca_direta/tabu.c        (sem estrutura; 5o campo = M inicial)
#   grupo -> tools/busca_direta/tabu_grupo.c  (invariante por um grupo; 5o campo = nº de representantes)
# Linha do arquivo de alvos: "ferramenta q n R tamanho segundos sementes recorde [geradores]".
# O par (linha, semente) vai para o shard (contador % SHARD_TOTAL); dentro do shard roda um processo por
# vCPU. Cada código achado passa pelo verificador oficial (tools/verify/verify) aqui mesmo e o resumo
# ($SAIDA/resumo.tsv) lista só o que ele aceitou. Como o lote pode devolver só o fim do log (3 KB), o
# código de toda célula que ficou ABAIXO do recorde é impresso no log, palavra por palavra, por último.
# Resultado é hipótese até o PR que registra no ledger refazer a verificação.
# Ambiente (posto pelo lote): SHARD_INDEX, SHARD_TOTAL, JOB_ID, SAIDA.
set -eu
: "${SHARD_INDEX:=0}" "${SHARD_TOTAL:=1}" "${SAIDA:=./saida-busca-tabu}"
ALVOS="${ALVOS:-pesado/jobs/busca_tabu.alvos}"
mkdir -p "$SAIDA"
BIN="$(mktemp -d)"
cc -O3 -march=native -std=gnu99 -o "$BIN/tabu" tools/busca_direta/tabu.c
cc -O3 -march=native -std=gnu99 -DCNT16 -o "$BIN/tabu16" tools/busca_direta/tabu.c
cc -O3 -march=native -std=gnu99 -o "$BIN/grupo" tools/busca_direta/tabu_grupo.c
cc -O2 -o "$BIN/verify" tools/verify/verify.c
NP="$(nproc)"
echo "shard ${SHARD_INDEX}/${SHARD_TOTAL} job ${JOB_ID:-local} commit $(git rev-parse --short HEAD 2>/dev/null || echo ?) vCPU ${NP}"

tarefas="$BIN/tarefas"
: > "$tarefas"
k=0
lin=0
while read -r fer q n R tam seg sem rec ger; do
  case "$fer" in ''|\#*) continue ;; esac
  lin=$((lin + 1))
  for s in $(seq 1 "$sem"); do
    if [ $((k % SHARD_TOTAL)) -eq "$SHARD_INDEX" ]; then
      echo "$fer $q $n $R $tam $seg $((s + 1000 * SHARD_INDEX)) $rec L${lin} ${ger:-}" >> "$tarefas"
    fi
    k=$((k + 1))
  done
done < "$ALVOS"
echo "tarefas deste shard: $(wc -l < "$tarefas")"

roda() {
  local fer=$1 q=$2 n=$3 R=$4 tam=$5 seg=$6 s=$7 rec=$8 lin=$9 ger=${10:-}
  local d="$SAIDA/${q}_${n}_${R}" p
  mkdir -p "$d"
  p="$d/q${q}_n${n}_R${R}_${lin}_s${s}"
  echo "$rec" > "$d/recorde"
  if [ "$fer" = grupo ]; then
    "$BIN/grupo" "$q" "$n" "$R" "$tam" "$seg" "$s" "$p" "$ger" > "$p.out" 2> "$p.err" || true
  else
    local b="$BIN/tabu"
    [ "$tam" -ge 255 ] && b="$BIN/tabu16"
    "$b" "$q" "$n" "$R" "$tam" "$seg" "$s" "$p" > "$p.out" 2> "$p.err" || true
  fi
}
export -f roda
export BIN SAIDA
xargs -P "$NP" -L 1 bash -c 'roda "$@"' _ < "$tarefas"

# confere tudo que saiu; o resumo leva o menor M aceito por célula
printf 'celula\tM\trecorde\tarquivo\tsha256\n' > "$SAIDA/resumo.tsv"
abaixo=""
for d in "$SAIDA"/*_*_*/; do
  [ -d "$d" ] || continue
  d="${d%/}"
  IFS=_ read -r q n R <<< "$(basename "$d")"
  rec="$(cat "$d/recorde")"
  for f in $(ls "$d"/*_M*.txt 2>/dev/null | awk -F_M '{print $NF+0, $0}' | sort -n | cut -d' ' -f2-); do
    m="${f##*_M}"; m="${m%.txt}"
    if out="$("$BIN/verify" -q "$q" -n "$n" -r "$R" -m "$m" "$f" 2>&1)"; then
      printf 'K%s(%s,%s)\t%s\t%s\t%s\t%s\n' "$q" "$n" "$R" "$m" "$rec" "${f#"$SAIDA"/}" "${out##*sha256=}" >> "$SAIDA/resumo.tsv"
      [ "$m" -lt "$rec" ] && abaixo="$abaixo $f"
      break
    else
      echo "REPROVADO pelo verificador: $f"
    fi
  done
done
cut -f1-3 "$SAIDA/resumo.tsv"
for f in $abaixo; do
  echo "ABAIXO DO RECORDE: ${f#"$SAIDA"/}"
  cat "$f"
done
