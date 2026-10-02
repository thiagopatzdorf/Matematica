#!/bin/sh
# rt_build_seeded.sh -- red team, ataque 7: compila uma cópia do base_search.c em que a semente
# do kit_rnd vem da variável RT_SEED (o binário oficial não aceita semente: kit_rs começa fixo).
# A amostra Y do exactT/exactT2 muda com a semente; o conjunto de trios <= T não pode mudar.
# Uso: rt_build_seeded.sh <dir_saida>   -> <dir_saida>/bs_seed
set -eu
here=$(cd "$(dirname "$0")" && pwd)
src="$here/../../search"
out=${1:?dir de saída}
mkdir -p "$out"
cp "$src/base_search.c" "$src/kit.h" "$out/"
# injeta a semente logo depois de "Kit K = {0};" no main
sed -i 's|^  Kit K = {0};$|  Kit K = {0}; if (getenv("RT_SEED")) kit_seed(strtoull(getenv("RT_SEED"), 0, 10));|' "$out/base_search.c"
grep -q 'RT_SEED' "$out/base_search.c" || { echo "falhou ao injetar semente" >&2; exit 1; }
gcc -O3 -march=native -o "$out/bs_seed" "$out/base_search.c" -lm
echo "$out/bs_seed"
