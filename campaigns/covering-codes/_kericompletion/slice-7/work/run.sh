#!/bin/bash
cd "$(dirname "$0")"
# id q n R ub  (ordem: pequenas primeiro)
while read q n R ub; do
  for tag in cal new; do
    if [ $tag = cal ]; then M=$ub; s=60; else M=$((ub-1)); s=130; fi
    f=../codes/q${q}_n${n}_R${R}_M${M}.txt
    echo "CMD nice -n 10 ./sa $q $n $R $M $s 1 0.4 $f" >> log.txt
    nice -n 10 ./sa $q $n $R $M $s 1 0.4 $f 2>>err_${q}_${n}_${R}.log | tee -a log.txt
  done
done <<EOF
2 11 3 16
2 12 1 380
5 6 3 25
3 9 2 219
7 6 3 77
3 10 5 12
3 11 4 81
2 19 7 16
3 14 7 27
7 7 2 2401
2 18 1 16384
2 21 5 256
2 22 4 1536
2 23 4 2048
2 20 1 63488
EOF
echo DONE >> log.txt
