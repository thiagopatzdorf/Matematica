#!/bin/sh
# Roda verify-rust em todo data/codes/*.txt; parametros lidos do NOME pelo script.
# Uso (da raiz do repo): sh tools/verify-rust/run_all.sh
set -u
export PATH="$HOME/.cargo/bin:$PATH"
root=$(cd "$(dirname "$0")/../.." && pwd)
(cd "$root/tools/verify-rust" && cargo build --release --offline -q) || exit 3
bin="$root/tools/verify-rust/target/release/verify-rust"
rc=0
for f in "$root"/data/codes/q*_n*_R*_M*.txt; do
  b=$(basename "$f" .txt)
  q=${b#q}; q=${q%%_*}; n=${b#*_n}; n=${n%%_*}; R=${b#*_R}; R=${R%%_*}; M=${b#*_M}
  s=$(date +%s.%N)
  out=$("$bin" --q "$q" --n "$n" --R "$R" --M "$M" "$f" 2>&1); c=$?
  e=$(date +%s.%N)
  printf '%s exit=%s %.2fs  %s\n' "$b" "$c" "$(echo "$e - $s" | bc)" "$out"
  [ "$c" -eq 0 ] || rc=1
done
exit $rc
