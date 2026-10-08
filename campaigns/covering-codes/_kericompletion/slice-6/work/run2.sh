#!/bin/bash
# cell: q n R ub
while read q n R ub; do
 M=$((ub-1))
 i=0
 for T in "0.35 0.15" "0.25 0.1"; do
  i=$((i+1))
  SA_OUT=found_q${q}_n${n}_R${R}_M${M}_s$i.txt nice -n 10 ./sa $q $n $R $M 50 $((i+10)) 3 $T >> log_q${q}_n${n}_R${R}.txt 2>&1
  echo "cmd: sa $q $n $R $M 110 seed=$((i+10)) cycles=3 T=$T" >> log_q${q}_n${n}_R${R}.txt
 done
done <<'EOF'
5 6 2 125
3 9 3 54
3 10 2 555
5 7 1 3125
2 17 1 8192
2 18 7 12
2 19 5 64
7 7 3 343
2 20 8 12
5 9 6 12
2 22 7 64
3 14 4 729
2 23 8 32
EOF
echo DONE > done.flag
