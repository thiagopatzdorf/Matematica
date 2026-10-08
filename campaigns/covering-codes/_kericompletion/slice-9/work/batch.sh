#!/bin/bash
# q n R ub secs
while read q n R ub secs; do
  M=$((ub-1))
  echo "== K$q($n,$R) M=$M secs=$secs seed=1 T0=0.5 T1=0.25" >> batch.log
  nice -n 10 ./sa $q $n $R $M $secs 1 0.5 0.25 ../codes/q${q}_n${n}_R${R}_M${M}.txt >> batch.log 2>&1
done <<EOF
3 7 1 186 150
3 8 3 27 200
2 14 2 248 240
2 16 5 28 240
3 9 1 1269 240
3 11 3 243 240
7 6 1 4435 240
5 8 4 65 240
2 19 1 31744 200
3 13 4 335 200
3 14 3 2187 200
7 7 1 31045 200
EOF
echo DONE >> batch.log
