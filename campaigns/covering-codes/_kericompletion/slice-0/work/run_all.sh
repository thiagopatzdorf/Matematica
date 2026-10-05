#!/bin/bash
# SA em M=ub-1 por celula, 1 nucleo, tempo fixo. log em sa_log.txt
cd "$(dirname "$0")"
while read id q n R M secs; do
  echo "== $id M=$M secs=$secs seed=1 cmd: ./sa $q $n $R $M $secs 1 0.5 0.12" >> sa_log.txt
  nice -n 10 ./sa $q $n $R $M $secs 1 0.5 0.12 ../codes/found_q${q}_n${n}_R${R}_M${M}.txt >> sa_log.txt 2>&1
done <<'L'
K5(4,1) 5 4 1 50 60
K3(7,3) 3 7 3 11 60
K3(8,2) 3 8 2 80 60
K7(6,4) 7 6 4 14 90
K2(14,3) 2 14 3 63 60
K2(15,3) 2 15 3 111 60
K2(16,4) 2 16 4 63 60
K3(11,1) 3 11 1 9476 120
K5(8,2) 5 8 2 1624 120
K3(12,4) 3 12 4 174 90
K2(20,6) 2 20 6 63 90
K3(13,6) 3 13 6 35 90
K2(21,3) 2 21 3 3071 120
K2(22,3) 2 22 3 4095 120
K3(14,1) 3 14 1 177146 120
K2(23,1) 2 23 1 393215 120
L
echo DONE >> sa_log.txt
