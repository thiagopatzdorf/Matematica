#!/bin/bash
# cada celula: calibracao em M=ub (30s) e tentativa em M=ub-1 (190s), semente 1
while read id q n R ub; do
  for spec in "$ub 30" "$((ub-1)) 190"; do set -- $spec
    M=$1; S=$2
    echo "== $id M=$M secs=$S" >> log.txt
    nice -n 10 ./sa $q $n $R $M $S 1 found_q${q}_n${n}_R${R}_M${M}.txt >> log.txt 2>&1
  done
done < cells.txt
echo DONE >> log.txt
