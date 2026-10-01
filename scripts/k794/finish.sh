#!/bin/bash
# waits for all 95 parts EXIT 0, then compiles assembly and Final (each logged with EXIT code)
cd ~/h/b
while [ $(grep -l "^EXIT 0" logs/K3_K7_9_4_P*.log | wc -l) -lt 95 ]; do
  if grep -q GIVEUP logs/pool_K7_9_4.log; then echo "ABORT: part gave up"; exit 1; fi
  sleep 20; done
echo "parts done $(date +%T)"
gen/build1.sh K3_K7_9_4; tail -1 logs/K3_K7_9_4.log
grep -q "^EXIT 0" logs/K3_K7_9_4.log || { echo "ABORT assembly"; exit 1; }
gen/build1.sh K3_K7_9_4_Final; tail -1 logs/K3_K7_9_4_Final.log
echo "FINISHED $(date +%T)"
