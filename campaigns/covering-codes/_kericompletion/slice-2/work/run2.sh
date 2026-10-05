#!/bin/bash
while read q n R ub secs; do
   seed=1; st=$(date +%s)
   r=$(nice -n10 ./sa2 $q $n $R $((ub-1)) $secs $seed 0.5 0.12 cand_q${q}_n${n}_R${R}_M$((ub-1)).txt 2>/dev/null)
   echo "q=$q n=$n R=$R M=$((ub-1)) seed=$seed secs(wall)=$secs T0=0.5 T1=0.12 res(final best)=$r wall=$(( $(date +%s)-st ))" >> log.txt
done <<'L'
7 4 1 123 150
2 13 3 42 150
2 14 1 1408 150
2 15 5 16 150
2 16 2 768 150
2 17 2 1536 200
2 18 5 64 200
5 8 1 15625 200
3 12 3 657 200
2 20 7 28 200
3 13 7 12 200
2 21 8 16 200
2 22 9 12 200
7 8 2 15129 240
5 10 6 45 200
L
echo DONE >> log.txt
