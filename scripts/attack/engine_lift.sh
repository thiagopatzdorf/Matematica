#!/usr/bin/env bash
# engine_lift.sh -- gerador + avaliador para a base fina: para cada (coordenada de lift j, semente),
# roda coset_sa com t fixo a partir da base grossa refinada e AVALIA a base pelo remendo real
# (patch_opt curto), não pela contagem de órfãs. POR QUE: em K_7(10,4) duas bases com 3 órfãs
# deram remendos de 179 e 128 palavras -- a contagem não é o avaliador certo.
#
# Uso: engine_lift.sh q n R "H_grossa" sindromes_grossas.txt t "js" "seeds" secs_sa secs_patch dir
# Saída: dir/RESULT.tsv  (j seed orfas M arquivo)
set -euo pipefail
q=$1 n=$2 R=$3 HG=$4 SG=$5 t=$6 JS=$7 SEEDS=$8 SSA=$9 SP=${10} D=${11}
here=$(cd "$(dirname "$0")" && pwd); mkdir -p "$D"; cd "$D"
for j in $JS; do
  python3 "$here/expand_cosets.py" lift "$q" "$n" "$HG" "$SG" "$j" > "lift$j.txt"
  H=$(head -1 "lift$j.txt" | sed 's/H="\(.*\)"/\1/'); tail -n +2 "lift$j.txt" > "lift${j}_s.txt"
  for s in $SEEDS; do
    p="j${j}s${s}"
    "$here/../search/coset_sa" "$q" "$n" "$R" "$H" "$t" "$SSA" "$s" 1 0.2 "$p" "lift${j}_s.txt" > "$p.log" 2>&1 || true
    best=$(ls ${p}_t${t}_o*.txt 2>/dev/null | sed 's/.*_o\([0-9]*\).txt/\1 &/' | sort -n | head -1 | cut -d' ' -f2) || true
    [ -n "$best" ] || continue
    o=$(echo "$best" | sed 's/.*_o\([0-9]*\).txt/\1/')
    python3 "$here/expand_cosets.py" expand "$q" "$n" "$H" "$best" > "b_$p.txt"
    echo "{\"q\":$q,\"n\":$n,\"R\":$R,\"frozen\":\"$PWD/b_$p.txt\"}" > "p_$p.json"
    "$here/../search/patch_opt" "p_$p.json" --L 0 --W 400 --secs "$SP" --seed "$s" --out "P_$p" > "P_$p.log" 2>&1 || true
    M=$(grep SOLVED "P_$p.log" | tail -1 | sed 's/SOLVED M=\([0-9]*\).*/\1/'); f=$(grep SOLVED "P_$p.log" | tail -1 | sed 's/.*-> //')
    printf "%s\t%s\t%s\t%s\t%s\n" "$j" "$s" "$o" "${M:-NA}" "${f:-}" >> RESULT.tsv
    rm -f "b_$p.txt"
  done
done
