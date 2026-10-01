#!/bin/bash
# adaptive scheduler (replaces runall.sh xargs -P 4): keeps up to JMAX K3 pieces compiling,
# but only while total running lean processes < NCPU and MemAvailable > MEMMIN_GB.
# skips pieces with EXIT 0 or currently compiling; retries a failed piece once.
cell=$1; JMAX=${2:-6}; NCPU=${3:-8}; MEMMIN=${4:-12}
cd ~/h/b; declare -A tries
while true; do
  todo=(); running=0
  for f in $(ls CoveringLean/K3_${cell}_P*.lean | sort -t P -k3 -n); do
    m=$(basename $f .lean)
    if grep -q "^EXIT 0" logs/$m.log 2>/dev/null; then continue; fi
    if pgrep -f "lean -o .*/$m.olean" >/dev/null; then running=$((running+1)); continue; fi
    todo+=($m)
  done
  if [ ${#todo[@]} -eq 0 ] && [ $running -eq 0 ]; then echo "ALLDONE $(date)"; break; fi
  nlean=$(pgrep -xc lean); avail=$(awk "/MemAvailable/{print int(\$2/1048576)}" /proc/meminfo)
  if [ ${#todo[@]} -gt 0 ] && [ $running -lt $JMAX ] && [ $nlean -lt $NCPU ] && [ $avail -gt $MEMMIN ]; then
    m=${todo[0]}; t=${tries[$m]:-0}
    if [ $t -ge 2 ]; then echo "GIVEUP $m"; todo=("${todo[@]:1}"); sleep 20; continue; fi
    tries[$m]=$((t+1)); echo "$(date +%T) start $m (running=$running nlean=$nlean avail=${avail}G)"
    nohup gen/build1.sh $m >/dev/null 2>&1 &
    sleep 15
  else sleep 20; fi
done
