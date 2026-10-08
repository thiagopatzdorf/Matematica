#!/bin/bash
# cell q n R ub secs
while read q n R ub secs; do
  for seed in 1 2; do
   s=$((secs/2))
   st=$(date +%s)
   r=$(nice -n10 ./sa $q $n $R $((ub-1)) $s $seed 0.5 0.12 cand_q${q}_n${n}_R${R}_M$((ub-1)).txt 2>/dev/null)
   echo "q=$q n=$n R=$R M=$((ub-1)) seed=$seed secs=$s T0=0.5 T1=0.12 res(final best)=$r wall=$(( $(date +%s)-st ))" >> log.txt
  done
done <<'L'
3 6 1 73 180
7 4 1 123 240
2 13 3 42 240
2 14 1 1408 240
2 15 5 16 240
2 16 2 768 240
2 17 2 1536 240
2 18 5 64 240
5 8 1 15625 240
3 12 3 657 240
2 20 7 28 240
3 13 7 12 240
2 21 8 16 240
2 22 9 12 240
7 8 2 15129 300
5 10 6 45 240
L
echo DONE >> log.txt
