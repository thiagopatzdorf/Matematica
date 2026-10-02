#!/bin/bash
# xs.sh from to step offset T out : exactT nas classes (linhas) from..to de classes_sorted.jsonl, passo step
for ((i=$1+$4;i<=$2;i+=$3)); do A=$(sed -n "${i}p" classes_sorted.jsonl | python3 -c "import sys,json;print(json.load(sys.stdin)['A'])"); echo "# class $i"; ./bs exactT 7 9 4 $5 "$A" 200 20; done > $6
