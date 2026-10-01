#!/bin/bash
# usage: build1.sh Module  -> compiles ~/h/b/CoveringLean/Module.lean to its olean, log in ~/h/b/logs
M=$1
export PATH=$HOME/.elan/bin:$PATH
cd ~/h/b && mkdir -p logs
systemd-run --user --scope -q -p MemoryMax=28G -p MemorySwapMax=0 /usr/bin/time -v lake env lean -o .lake/build/lib/lean/CoveringLean/$M.olean CoveringLean/$M.lean > logs/$M.log 2>&1
echo "EXIT $?" >> logs/$M.log
